from .._imports import *
from .._imports import _is_application_admin_email
from ai_assessments.results_helpers import get_ai_assessment_results, get_ai_candidate_results
from api.utils.batch_utils import generate_batch_id, generate_batch_name
from ..models import CandidateSubmission, QualificationRequest, FaceUpdateRequest
from .assessment_views import _is_valid_pan
from django.core.files.base import ContentFile
import base64


def _get_filtered_warning_logs(warning_logs):
    """
    Filters warning logs to align with report_utils logic:
    Hides the first 3 face detection lost events.
    """
    if not isinstance(warning_logs, list):
        return []
    
    filtered = []
    face_lost_count = 0
    for log in warning_logs:
        # Handle both dict (from API response/JSONField) and potentially other formats
        evt = log.get('event_type') if isinstance(log, dict) else str(log)
        if evt in ['no_face_detection', 'face_detection_lost', 'face_detection_lost_rechecked']:
            face_lost_count += 1
            if face_lost_count <= 3:
                continue
        filtered.append(log)
    return filtered


def _save_identity_violation_screenshot(invitation, snapshot_base64, event_type):
    """
    Saves a base64 snapshot as an IntegrityScreenshot record.
    """
    try:
        from ..models import IntegrityScreenshot
        if not snapshot_base64 or not isinstance(snapshot_base64, str):
            return
            
        if ',' in snapshot_base64:
            snapshot_base64 = snapshot_base64.split(',', 1)[1]
        
        img_data = base64.b64decode(snapshot_base64)
        filename = f"identity_violation_{invitation.id}_{int(timezone.now().timestamp())}.jpg"
        
        IntegrityScreenshot.objects.create(
            invitation=invitation,
            event_type=event_type,
            webcam_screenshot=ContentFile(img_data, name=filename)
        )
        print(f"[Integrity] Saved {event_type} screenshot for invitation {invitation.id}")
    except Exception as e:
        print(f"Failed to save identity violation screenshot: {e}")


@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_invitations_and_send_email_view(request, assessment_id: int):
    """
    Create candidate invitation(s) for an assessment and send email(s) immediately.

    Body:
    {
      "candidates": [
        {
          "name":"...",
          "email":"...",
          "pan_number":"...",
          "phone":"...",
          "start_time": "...iso...",
          "end_time":"...iso...",
          "time_zone":"...",
          "start_grace_minutes": 30
        },
        ...
      ]
    }
    """
    try:
        try:
            assessment = Assessment.objects.get(id=assessment_id)
        except Assessment.DoesNotExist:
            return Response({'error': 'Assessment not found.'}, status=status.HTTP_404_NOT_FOUND)

        # --- RBAC ownership check ---
        # Prevent users from inviting candidates to assessments outside their invite tree.
        # This blocks Admin A from using Admin B's assessment_id even if they share a company.
        req_user_profile = getattr(request.user, 'profile', None)
        if req_user_profile:
            scoped_ids = get_scoped_user_ids(req_user_profile)
            if scoped_ids is not None:
                # scoped_ids = None means platform superadmin (can access all)
                if assessment.user_profile_id not in scoped_ids:
                    return Response(
                        {'error': 'You do not have permission to invite candidates to this assessment.'},
                        status=status.HTTP_403_FORBIDDEN
                    )

        data = request.data or {}
        candidates = data.get('candidates', [])

        # Enforce Single Mode restriction: cannot invite if invited > 0 or if more than 1 candidate in request
        if getattr(assessment, 'assessment_mode', 'multiple') == 'single':
            if int(getattr(assessment, 'invited', 0) or 0) > 0:
                return Response({'error': 'This is a single-candidate assessment and an invitation has already been sent.'}, status=status.HTTP_400_BAD_REQUEST)
            if len(candidates) > 1:
                return Response({'error': 'Single Mode assessment: Only one candidate can be invited at a time.'}, status=status.HTTP_400_BAD_REQUEST)

        if not isinstance(candidates, list) or len(candidates) == 0:
            return Response({'error': 'candidates must be a non-empty array.'}, status=status.HTTP_400_BAD_REQUEST)

        frontend_base = getattr(settings, 'FRONTEND_BASE_URL', None) or os.environ.get('FRONTEND_BASE_URL') or 'http://localhost:3000'

        results = []
        sent_count = 0
        fail_count = 0
        
        # Unique batch for this invitation event
        batch_id = generate_batch_id()
        batch_name = generate_batch_name(assessment.display_name or assessment.name)

        for idx, c in enumerate(candidates, start=1):
            payload = dict(c or {})
            name = (payload.get('name') or '').strip()
            email = (payload.get('email') or '').strip().lower()
            pan_number = (payload.get('pan_number') or payload.get('pan') or '').strip().upper() or None
            phone = (payload.get('phone') or '').strip() or None
            start_time_raw = (payload.get('start_time') or '').strip() or None
            end_time_raw = (payload.get('end_time') or '').strip() or None
            time_zone = (payload.get('time_zone') or '').strip() or None
            start_grace_minutes_raw = payload.get('start_grace_minutes', None)

            if not name:
                return Response({'error': f'Candidate #{idx}: name is required.'}, status=status.HTTP_400_BAD_REQUEST)
            if not email:
                return Response({'error': f'Candidate #{idx}: email is required.'}, status=status.HTTP_400_BAD_REQUEST)
            if pan_number and not _is_valid_pan(pan_number):
                return Response({'error': f'Candidate #{idx}: pan_number is invalid.'}, status=status.HTTP_400_BAD_REQUEST)

            start_time = parse_datetime(start_time_raw) if start_time_raw else None
            end_time = parse_datetime(end_time_raw) if end_time_raw else None
            try:
                start_grace_minutes = int(start_grace_minutes_raw) if start_grace_minutes_raw is not None else 0
            except Exception:
                start_grace_minutes = 0
            start_grace_minutes = max(0, start_grace_minutes)

            is_auto_schedule = bool(payload.get('is_auto_schedule', False))

            invitation = CandidateInvitation.objects.create(
                assessment=assessment,
                user_profile=req_user_profile,
                created_by=req_user_profile,
                name=name,
                email=email,
                pan_number=pan_number,
                phone=phone,
                start_time=start_time,
                end_time=end_time,
                time_zone=time_zone,
                start_grace_minutes=start_grace_minutes,
                status='draft',
                is_auto_schedule=is_auto_schedule,
                batch_id=batch_id,
                batch_name=batch_name
            )

            start_link = f"{frontend_base.rstrip('/')}/take-assessment/{invitation.token}"
            subject = f"{assessment.display_name or assessment.name or 'Assessment'} - Invitation"

            # Read validity mode from payload
            validity_mode = (payload.get('validity_mode') or '').strip() or 'exact_window'
            
            # Mapping validity_mode to user-friendly label
            validity_labels = {
                'exact_window': 'Particular date + time window',
                'date_anytime': 'Particular date (whole day / date range)',
                'one_week': '1 week from start'
            }
            validity_type_label = validity_labels.get(validity_mode, 'Particular date + time window')

            # Convert UTC times to candidate's local timezone for display
            display_tz = time_zone or ''
            local_start = start_time
            local_end = end_time
            try:
                from zoneinfo import ZoneInfo
                if time_zone and start_time:
                    local_start = start_time.astimezone(ZoneInfo(time_zone))
                if time_zone and end_time:
                    local_end = end_time.astimezone(ZoneInfo(time_zone))
            except Exception:
                pass

            # Build schedule blocks based on validity mode
            if validity_mode == 'exact_window':
                # Show: Date, Start Window (start to last valid start), End Time (extended deadline)
                # entry_deadline = start_time + grace_minutes  -> last moment candidate can start
                # actual_end    = end_time + grace_minutes     -> absolute hard stop
                try:
                    entry_deadline_local = (local_start + timedelta(minutes=start_grace_minutes)) if local_start and start_grace_minutes > 0 else local_end
                    actual_end_local     = (local_end + timedelta(minutes=start_grace_minutes))   if local_end and start_grace_minutes > 0 else local_end
                except Exception:
                    entry_deadline_local = local_end
                    actual_end_local     = local_end

                display_date       = local_start.strftime('%B %d, %Y') if local_start else ''
                display_start_from = local_start.strftime('%I:%M %p').lstrip('0') if local_start else ''
                display_start_to   = entry_deadline_local.strftime('%I:%M %p').lstrip('0') if entry_deadline_local else ''
                display_duration   = getattr(assessment, 'total_time', None)

                # Plain-text body
                schedule_text = ''
                if display_date:
                    schedule_text = (
                        "Assessment Schedule:\n"
                        f"  Date: {display_date}\n"
                    )
                    if start_grace_minutes > 0:
                        schedule_text += f"  Start Window: {display_start_from} \u2013 {display_start_to}\n"
                    else:
                        schedule_text += f"  Start Time: {display_start_from}\n"
                    if display_duration:
                        schedule_text += f"  Duration: {display_duration}\n"
                    if display_tz:
                        schedule_text += f"  Time Zone: {display_tz}\n"
                    schedule_text += "\n"

                # HTML body
                schedule_html = ''
                if display_date:
                    schedule_html = '<table style="border-collapse:collapse;margin:16px 0;">'
                    schedule_html += (
                        '<tr>'
                        '<td style="padding:6px 16px 6px 0;color:#475569;font-weight:600;">📅 Date</td>'
                        f'<td style="padding:6px 0;">{display_date}</td>'
                        '</tr>'
                    )
                    if start_grace_minutes > 0:
                        schedule_html += (
                            '<tr>'
                            '<td style="padding:6px 16px 6px 0;color:#475569;font-weight:600;">🕐 Start Window</td>'
                            f'<td style="padding:6px 0;">{display_start_from} &ndash; {display_start_to}</td>'
                            '</tr>'
                        )
                    else:
                        schedule_html += (
                            '<tr>'
                            '<td style="padding:6px 16px 6px 0;color:#475569;font-weight:600;">🕐 Start Time</td>'
                            f'<td style="padding:6px 0;">{display_start_from}</td>'
                            '</tr>'
                        )
                    if display_duration:
                        schedule_html += (
                            '<tr>'
                            '<td style="padding:6px 16px 6px 0;color:#475569;font-weight:600;">⏳ Duration</td>'
                            f'<td style="padding:6px 0;">{display_duration}</td>'
                            '</tr>'
                        )
                    if display_tz:
                        schedule_html += (
                            '<tr>'
                            '<td style="padding:6px 16px 6px 0;color:#475569;font-weight:600;">🌐 Time Zone</td>'
                            f'<td style="padding:6px 0;">{display_tz}</td>'
                            '</tr>'
                        )
                    schedule_html += '</table>'

            else:
                # date_anytime or one_week: Show Start Date, End Date, Available 12:00 AM to 11:59 PM
                display_start_date = local_start.strftime('%B %d, %Y') if local_start else ''
                display_end_date = local_end.strftime('%B %d, %Y') if local_end else ''

                schedule_text = ''
                if display_start_date:
                    schedule_text = (
                        "Assessment Schedule:\n"
                        f"  Start Date: {display_start_date}\n"
                    )
                    if display_end_date and display_end_date != display_start_date:
                        schedule_text += f"  End Date: {display_end_date}\n"
                    if display_tz:
                        schedule_text += f"  Time Zone: {display_tz}\n"
                    schedule_text += "\n"

                schedule_html = ''
                if display_start_date:
                    schedule_html = '<table style="border-collapse:collapse;margin:16px 0;">'
                    schedule_html += (
                        '<tr>'
                        '<td style="padding:6px 16px 6px 0;color:#475569;font-weight:600;">📅 Start Date</td>'
                        f'<td style="padding:6px 0;">{display_start_date}</td>'
                        '</tr>'
                    )
                    if display_end_date and display_end_date != display_start_date:
                        schedule_html += (
                            '<tr>'
                            '<td style="padding:6px 16px 6px 0;color:#475569;font-weight:600;">📅 End Date</td>'
                            f'<td style="padding:6px 0;">{display_end_date}</td>'
                            '</tr>'
                        )
                    if display_tz:
                        schedule_html += (
                            '<tr>'
                            '<td style="padding:6px 16px 6px 0;color:#475569;font-weight:600;">🌐 Time Zone</td>'
                            f'<td style="padding:6px 0;">{display_tz}</td>'
                            '</tr>'
                        )
                    schedule_html += '</table>'

            text_body = (
                f"Hi {name},\n\n"
                f"You have been invited to take an assessment.\n\n"
                f"Assessment: {assessment.display_name or assessment.name or 'Assessment'}\n\n"
                f"{schedule_text}"
                f"Start link: {start_link}\n\n"
                "Good luck!"
            )

            html_body = f"""
                <div style="font-family: Arial, sans-serif; line-height: 1.6; color: #111; max-width: 600px;">
                  <p>Hi <strong>{name}</strong>,</p>
                  <p>You have been invited to take an assessment.</p>
                  <p><strong>Assessment:</strong> {assessment.display_name or assessment.name or 'Assessment'}</p>
                  {schedule_html}
                  <p style="margin: 24px 0;">
                    <a href="{start_link}" target="_blank"
                       style="background:#2563eb;color:#fff;padding:12px 24px;border-radius:10px;text-decoration:none;font-weight:700;display:inline-block;">
                      Start Assessment
                    </a>
                  </p>
                  <p style="font-size:12px;color:#475569;">If the button doesn't work, copy this link: <br/>{start_link}</p>
                  <hr style="border:none;border-top:1px solid #e2e8f0;margin:24px 0;" />
                  <p style="font-size:12px;color:#94a3b8;">This is an automated message from VerifiHire AI. Please do not reply to this email.</p>
                </div>
            """

            try:
                msg = EmailMultiAlternatives(
                    subject=subject,
                    body=text_body,
                    from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', None),
                    to=[email],
                )
                msg.attach_alternative(html_body, "text/html")
                msg.send(fail_silently=False)
                invitation.status = 'sent'
                invitation.last_error = None
                invitation.save(update_fields=['status', 'last_error', 'updated_at'])
                sent_count += 1
            except Exception as mail_err:
                invitation.status = 'failed'
                invitation.last_error = str(mail_err)
                invitation.save(update_fields=['status', 'last_error', 'updated_at'])
                fail_count += 1

            results.append(
                {
                    'id': invitation.id,
                    'name': invitation.name,
                    'email': invitation.email,
                    'pan_number': invitation.pan_number,
                    'phone': invitation.phone,
                    'token': str(invitation.token),
                    'status': invitation.status,
                    'start_link': start_link,
                    'error': invitation.last_error,
                }
            )

        # Update simple invited counter
        try:
            assessment.invited = int(getattr(assessment, 'invited', 0) or 0) + sent_count
            assessment.total_candidates = max(int(getattr(assessment, 'total_candidates', 0) or 0), int(getattr(assessment, 'invited', 0) or 0))
            assessment.save(update_fields=['invited', 'total_candidates'])
        except Exception:
            pass

        return Response(
            {
                'message': 'Invitations processed.',
                'sent': sent_count,
                'failed': fail_count,
                'results': results,
            },
            status=status.HTTP_200_OK if fail_count == 0 else status.HTTP_207_MULTI_STATUS
        )
    except Exception as e:
        import traceback
        print(f"Error in create_invitations_and_send_email_view: {str(e)}")
        print(traceback.format_exc())
        return Response({'error': f'An error occurred while sending invitations: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['GET'])
@permission_classes([AllowAny])
def get_invitation_public_view(request, token):
    """
    Public endpoint for candidates: fetch assessment + questions using a CandidateInvitation token.
    """
    try:
        from api.models import SecuritySession
        if SecuritySession.token_has_permanent_revocation(token):
            return Response({'error': 'Access permanently revoked due to policy violation.'}, status=status.HTTP_403_FORBIDDEN)

        session_id = request.headers.get('X-Session-ID') or request.GET.get('session_id')
        check_only = request.GET.get('check_only', 'false').lower() in ('true', '1', 'yes')

        # ── Session lock with heartbeat-based timeout ──────────────────────
        # A session lock is considered STALE if the owning tab hasn't sent a
        # heartbeat in the last SESSION_LOCK_TIMEOUT_SECONDS seconds.
        # A stale lock is automatically released so the candidate can resume
        # on a new browser / laptop without contacting support.
        SESSION_LOCK_TIMEOUT_SECONDS = 30

        def _is_session_lock_stale(inv_obj):
            """Return True if the existing lock has no recent heartbeat."""
            if not inv_obj.claimed_session_id:
                return True
            last_seen = getattr(inv_obj, 'claimed_session_last_seen', None)
            if not last_seen:
                # Legacy lock with no heartbeat record — treat as stale
                return True
            elapsed = (timezone.now() - last_seen).total_seconds()
            return elapsed > SESSION_LOCK_TIMEOUT_SECONDS

        if not check_only and session_id:
            with transaction.atomic():
                try:
                    inv = CandidateInvitation.objects.select_for_update().select_related('assessment').get(token=token)
                except CandidateInvitation.DoesNotExist:
                    return Response({'error': 'Invitation not found.'}, status=status.HTTP_404_NOT_FOUND)

                if inv.claimed_session_id and inv.claimed_session_id != session_id:
                    if not _is_session_lock_stale(inv):
                        # Lock is fresh — another tab is actively running
                        return Response(
                            {'error': 'This assessment is already in use. If this is not you, please contact our support team.'},
                            status=status.HTTP_409_CONFLICT
                        )
                    # Lock is stale — old tab closed without cleanup; hand it to new tab
                    inv.claimed_session_id = session_id
                    inv.claimed_session_last_seen = timezone.now()
                    inv.save(update_fields=['claimed_session_id', 'claimed_session_last_seen'])
                elif not inv.claimed_session_id:
                    inv.claimed_session_id = session_id
                    inv.claimed_session_last_seen = timezone.now()
                    inv.save(update_fields=['claimed_session_id', 'claimed_session_last_seen'])
                else:
                    # Same session — update heartbeat
                    inv.claimed_session_last_seen = timezone.now()
                    inv.save(update_fields=['claimed_session_last_seen'])
        else:
            try:
                inv = CandidateInvitation.objects.select_related('assessment').get(token=token)
            except CandidateInvitation.DoesNotExist:
                return Response({'error': 'Invitation not found.'}, status=status.HTTP_404_NOT_FOUND)

            # check_only: only block if another session is actively using the exam right now
            if inv.claimed_session_id and session_id and inv.claimed_session_id != session_id:
                if not _is_session_lock_stale(inv):
                    return Response(
                        {'error': 'This assessment is already in use. If this is not you, please contact our support team.'},
                        status=status.HTTP_409_CONFLICT
                    )

        assessment = inv.assessment

        def _hhmmss_to_seconds(value: str) -> int:
            try:
                parts = [int(x) for x in (value or '').split(':')]
                if len(parts) == 2:
                    h, m = 0, parts[0]
                    s = parts[1]
                elif len(parts) == 3:
                    h, m, s = parts
                else:
                    return 0
                return max(0, h * 3600 + m * 60 + s)
            except Exception:
                return 0

        def _make_aware_if_needed(dt):
            if not dt:
                return None
            try:
                return timezone.make_aware(dt, timezone.get_current_timezone()) if timezone.is_naive(dt) else dt
            except Exception:
                return dt

        start_time = _make_aware_if_needed(getattr(inv, 'start_time', None))
        end_time = _make_aware_if_needed(getattr(inv, 'end_time', None))
        try:
            grace_minutes = int(getattr(inv, 'start_grace_minutes', 0) or 0)
        except Exception:
            grace_minutes = 0
        grace_minutes = max(0, grace_minutes)

        # Build schedule info for error responses
        _tz = getattr(inv, 'time_zone', None) or ''
        _schedule_info = {}
        try:
            from zoneinfo import ZoneInfo
            _local_start = start_time.astimezone(ZoneInfo(_tz)) if _tz and start_time else start_time
            _local_end = end_time.astimezone(ZoneInfo(_tz)) if _tz and end_time else end_time
        except Exception:
            _local_start = start_time
            _local_end = end_time
        if _local_start:
            _schedule_info['start_date'] = _local_start.strftime('%B %d, %Y')
            _schedule_info['start_time_display'] = _local_start.strftime('%I:%M %p')
        if _local_end:
            _schedule_info['end_date'] = _local_end.strftime('%B %d, %Y')
            _schedule_info['end_time_display'] = _local_end.strftime('%I:%M %p')
        if _tz:
            _schedule_info['time_zone'] = _tz

        # Window Enforcement (Run before submission check so expiry takes priority)
        now = timezone.now()
        
        # 1. Start window check (only if not started yet)
        if inv.started_at is None:
            if start_time and now < start_time:
                return Response({'error': 'This exam has not started yet.', 'schedule': _schedule_info}, status=status.HTTP_403_FORBIDDEN)
            
            # last_valid_start logic
            extended_deadline = (end_time + timedelta(minutes=grace_minutes)) if end_time and grace_minutes > 0 else end_time
            _entry_duration = _hhmmss_to_seconds(getattr(assessment, 'total_time', '') or '')
            if extended_deadline and _entry_duration > 0:
                last_valid_start = extended_deadline - timedelta(seconds=_entry_duration)
            else:
                last_valid_start = extended_deadline

            if last_valid_start and now > last_valid_start:
                return Response({'error': 'The start window for this exam has expired.', 'schedule': _schedule_info}, status=status.HTTP_410_GONE)

        # 2. Hard expiry check (Run for everyone, even if submitted)
        # If today > end_time + grace, it's definitely expired.
        submit_deadline = (end_time + timedelta(minutes=grace_minutes)) if end_time and grace_minutes > 0 else end_time
        if submit_deadline and now > submit_deadline:
            return Response({'error': 'This assessment link has expired.', 'schedule': _schedule_info}, status=status.HTTP_410_GONE)

        # 3. Submission check (If not expired, then check if already done)
        if inv.status == 'submitted':
            return Response({'error': 'Your exam has been completed.'}, status=status.HTTP_409_CONFLICT)

        # Compute the extended deadline (end_time + grace) used to cap expires_at.
        # This allows late starters (within grace window) to still use full assessment
        # duration, but hard-stops anyone at the extended deadline.
        _raw_end_time = getattr(inv, 'end_time', None)
        _raw_end_time = _make_aware_if_needed(_raw_end_time)
        _grace = max(0, int(getattr(inv, 'start_grace_minutes', 0) or 0))
        extended_deadline_calc = (_raw_end_time + timedelta(minutes=_grace)) if _raw_end_time and _grace > 0 else _raw_end_time

        # Start timer on first access (persisted). Cap by the extended deadline.
        now = timezone.now()
        duration_seconds = _hhmmss_to_seconds(getattr(assessment, 'total_time', '') or '')
        if duration_seconds <= 0:
            duration_seconds = 0

        # --- PRE-CHECK ONLY: Skip starting the timer and generating permutations ---
        check_only = request.GET.get('check_only', 'false').lower() in ('true', '1', 'yes')

        if not check_only:
            newly_started = False
            if inv.started_at is None:
                newly_started = True
                inv.started_at = now
                expires_at = now + timedelta(seconds=duration_seconds) if duration_seconds else None
                # All candidates who reach here have enough time for the full duration.
                # Cap by the extended deadline as a safety net (should equal now + duration for valid starters).
                # Example: window 2:30-2:50, grace 30min -> extended deadline = 3:20.
                # - Start at 2:30 -> expires at 2:50 (20 min). Start at 3:00 -> expires at 3:20 (20 min).
                if extended_deadline_calc:
                    expires_at = min(expires_at, extended_deadline_calc) if expires_at else extended_deadline_calc
                inv.expires_at = expires_at
            else:
                # Ensure existing expires_at is capped by extended deadline (in case schedule changed after start)
                if extended_deadline_calc:
                    if inv.expires_at and inv.expires_at > extended_deadline_calc:
                        inv.expires_at = extended_deadline_calc
                    elif inv.expires_at is None:
                        inv.expires_at = extended_deadline_calc

        # If expired, block access
        # NOTE: Since the frontend implements a "transition" stage where the timer is paused between objective and coding, 
        # a strict backend check against a calculated `expires_at` logic locks out users who legitimately waited 
        # on the transition screen. The frontend manages its own strict countdown interval for submissions.
        # if inv.expires_at and now >= inv.expires_at:
        #     return Response({'error': 'This assessment link has expired.'}, status=status.HTTP_410_GONE)

        aq_qs = (
            AssessmentQuestion.objects.filter(assessment=assessment)
            .select_related('question')
            .order_by('order')
        )

        # Shuffle questions + options ONCE per invitation (persisted)
        aq_list = list(aq_qs)
        aq_by_id = {aq.id: aq for aq in aq_list}

        if not check_only:
            if not inv.question_order:
                ids = [aq.id for aq in aq_list]
                random.shuffle(ids)
                inv.question_order = ids

            if not isinstance(inv.option_map, dict) or not inv.option_map:
                inv.option_map = {}

        def _build_shuffled_options(aq: AssessmentQuestion):
            qtype = (aq.question_type or '').strip().upper()
            # TF defaults
            if qtype == 'TF' and not any([aq.option_a, aq.option_b, aq.option_c, aq.option_d]):
                base = [('A', 'True'), ('B', 'False')]
            else:
                base = []
                if aq.option_a: base.append(('A', aq.option_a))
                if aq.option_b: base.append(('B', aq.option_b))
                if aq.option_c: base.append(('C', aq.option_c))
                if aq.option_d: base.append(('D', aq.option_d))

            if not base:
                return [], {}

            shuffled = base[:]
            random.shuffle(shuffled)
            new_labels = ['A', 'B', 'C', 'D'][: len(shuffled)]
            mapping = {}
            options = []
            for new_label, (orig_label, text) in zip(new_labels, shuffled):
                mapping[new_label] = orig_label
                options.append({'key': new_label, 'text': text})
            return options, mapping

        questions = []
        changed = False
        for qid in inv.question_order:
            aq = aq_by_id.get(int(qid)) if qid is not None else None
            if not aq:
                continue

            key = str(aq.id)
            mapping = inv.option_map.get(key) if isinstance(inv.option_map, dict) else None
            if not mapping:
                options, mapping = _build_shuffled_options(aq)
                inv.option_map[key] = mapping
                changed = True
            else:
                # build options in the stored shuffled order (A..D)
                options = []
                for new_label in ['A', 'B', 'C', 'D']:
                    orig_label = mapping.get(new_label)
                    if not orig_label:
                        continue
                    text = getattr(aq, f"option_{orig_label.lower()}", None)
                    if text is None and (aq.question_type or '').strip().upper() == 'TF':
                        text = 'True' if orig_label == 'A' else 'False' if orig_label == 'B' else None
                    if text:
                        options.append({'key': new_label, 'text': text})

            questions.append(
                {
                    'id': aq.id,
                    'order': aq.order,
                    'skill': aq.skill,
                    'question_type': aq.question_type,
                    'difficulty': aq.difficulty,
                    'time_limit': aq.time_limit,
                    'question': aq.question.question if aq.question else None,
                    'options': options,
                }
            )

        # Coding questions (no shuffle; keep order)
        acq_qs = (
            AssessmentCodingQuestion.objects.filter(assessment=assessment)
            .select_related('coding_question')
            .order_by('order')
        )
        coding_questions = []
        for acq in acq_qs:
            cq = acq.coding_question
            coding_questions.append(
                {
                    'id': acq.id,
                    'coding_question_id': cq.id if cq else None,
                    'order': acq.order,
                    'title': acq.title,
                    'description': acq.description,
                    'languages': acq.languages or [],
                    'allowed_languages': acq.allowed_languages or [],
                    'mode': acq.mode,
                    'starter_code': acq.starter_code,
                    'template_code': acq.template_code,
                    'time_limit_ms': acq.time_limit_ms,
                    'memory_limit_mb': acq.memory_limit_mb,
                }
            )

        if not check_only and (changed or newly_started):
            inv.save(update_fields=['started_at', 'expires_at', 'question_order', 'option_map', 'updated_at'])

        # Fetch existing partial submission
        submission = getattr(inv, 'submission', None)
        submitted_coding_ids = []
        coding_answers = {}
        if submission and submission.answers:
            for k, v in submission.answers.items():
                if k.startswith('acq_'):
                    try:
                        qid_str = k.split('_', 1)[1]
                        submitted_coding_ids.append(int(qid_str))
                        if isinstance(v, dict):
                            coding_answers[qid_str] = {
                                'code': v.get('submitted_code'),
                                'language': v.get('language')
                            }
                    except:
                        pass

        return Response(
            {
                'invitation': {
                    'id': inv.id,
                    'name': inv.name,
                    'email': inv.email,
                    'pan_number': inv.pan_number,
                    'phone': inv.phone,
                    'token': str(inv.token),
                    'started_at': inv.started_at.isoformat() if inv.started_at else None,
                    'expires_at': inv.expires_at.isoformat() if inv.expires_at else None,
                    'status': inv.status,
                },
                'assessment': {
                    'id': assessment.id,
                    'name': assessment.name,
                    'display_name': assessment.display_name,
                    'role': assessment.role,
                    'experience_level': assessment.experience_level,
                    'total_questions': assessment.total_questions,
                    'total_time': assessment.total_time,
                    'coding_total_time': assessment.coding_total_time,
                    'coding_question_count': assessment.coding_question_count,
                    'objective_time_limit': assessment.objective_time_limit,
                    'coding_time_limit': assessment.coding_time_limit,
                    'has_objective_cutoff': assessment.has_objective_cutoff,
                    'min_objective_pass_percentage': assessment.min_objective_pass_percentage,
                    'weightage_objective': assessment.weightage_objective,
                    'weightage_coding': assessment.weightage_coding,
                },
                'questions': questions,
                'coding_questions': coding_questions,
                'submitted_coding_ids': submitted_coding_ids,
                'coding_answers': coding_answers,
                'remaining_seconds': int((inv.expires_at - now).total_seconds()) if inv.expires_at else None,
            },
            status=status.HTTP_200_OK
        )
    except Exception as e:
        import traceback
        print(f"Error in get_invitation_public_view: {str(e)}")
        print(traceback.format_exc())
        return Response({'error': f'An error occurred while fetching invitation: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def submit_invitation_answers_view(request, token):
    """
    Candidate submits answers for an invitation token.

    Body:
    {
      "answers": { "<assessment_question_id>": "A" | ["A","C"] }
    }
    """
    try:
        try:
            inv = CandidateInvitation.objects.select_related('assessment').get(token=token)
        except CandidateInvitation.DoesNotExist:
            return Response({'error': 'Invitation not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Single-use: cannot submit twice
        if inv.status == 'submitted':
            return Response({'error': 'Your exam has been completed.'}, status=status.HTTP_409_CONFLICT)

        # Enforce expiry on submit as well (prevents submitting after time window)
        now = timezone.now()
        try:
            end_time = getattr(inv, 'end_time', None)
            end_time = timezone.make_aware(end_time, timezone.get_current_timezone()) if end_time and timezone.is_naive(end_time) else end_time
        except Exception:
            end_time = getattr(inv, 'end_time', None)

        # If not started yet, don't accept submit
        if inv.started_at is None:
            return Response({'error': 'Exam has not been started.'}, status=status.HTTP_403_FORBIDDEN)

        # Compute extended deadline for submit check (end_time + grace_minutes).
        try:
            _submit_grace = max(0, int(getattr(inv, 'start_grace_minutes', 0) or 0))
        except Exception:
            _submit_grace = 0
        extended_deadline_submit = (end_time + timedelta(minutes=_submit_grace)) if end_time and _submit_grace > 0 else end_time

        # Allow 2 minutes network skew grace on top of expires_at
        if inv.expires_at and now > (inv.expires_at + timedelta(minutes=2)):
            return Response({'error': 'Time is over. Submission is closed.'}, status=status.HTTP_410_GONE)
        # Hard stop at extended deadline (end_time + grace_minutes)
        if extended_deadline_submit and now > (extended_deadline_submit + timedelta(minutes=2)):
            return Response({'error': 'Time is over. Submission is closed.'}, status=status.HTTP_410_GONE)

        data = request.data or {}
        answers = data.get('answers', None)
        if answers is None or not isinstance(answers, dict):
            return Response({'error': 'answers must be a dict.'}, status=status.HTTP_400_BAD_REQUEST)

        assessment = inv.assessment
        valid_aq_ids = set(
            AssessmentQuestion.objects.filter(assessment=assessment).values_list('id', flat=True)
        )
        # Filter to only valid question ids
        cleaned = {}
        for k, v in answers.items():
            try:
                aqid = int(k)
            except Exception:
                continue
            if aqid not in valid_aq_ids:
                continue
            cleaned[str(aqid)] = v

        # Auto evaluate
        PASS_PERCENT = int(os.environ.get('PASS_PERCENT', '60') or 60)

        aq_qs = AssessmentQuestion.objects.filter(assessment=assessment).select_related('question').order_by('order')
        total = aq_qs.count()
        score = 0

        def _norm_choice(v):
            if v is None:
                return ''
            return str(v).strip().upper()

        for aq in aq_qs:
            qid = str(aq.id)
            submitted = cleaned.get(qid, None)
            qtype = (aq.question_type or '').strip().upper()

            # Map submitted labels back to original labels if options were shuffled
            mapping = None
            try:
                mapping = (inv.option_map or {}).get(str(aq.id), None)
            except Exception:
                mapping = None

            if qtype == 'MSQ':
                submitted_list = submitted if isinstance(submitted, list) else []
                raw = [_norm_choice(x) for x in submitted_list if _norm_choice(x)]
                if mapping and isinstance(mapping, dict):
                    raw = [mapping.get(x, x) for x in raw]  # newLabel -> origLabel
                submitted_set = sorted(raw)
                correct_set = sorted([_norm_choice(x) for x in (aq.correct_answers or []) if _norm_choice(x)])
                if submitted_set and submitted_set == correct_set:
                    score += 1
            else:
                submitted_choice = _norm_choice(submitted)
                if mapping and isinstance(mapping, dict):
                    submitted_choice = _norm_choice(mapping.get(submitted_choice, submitted_choice))
                correct_choice = _norm_choice(aq.correct_answer)
                if submitted_choice and correct_choice and submitted_choice == correct_choice:
                    score += 1

        # Calculate Objective Score
        percentage = (float(score) / float(total) * 100.0) if total > 0 else 0.0
        
        # We need to fetch existing coding scores if any (for combined result)
        # But since this is a fresh get_or_create or update, we should check existing fields
        # However, `submission` object is created/fetched below. Let's do it after get_or_create.

        submission, created = CandidateSubmission.objects.get_or_create(
            invitation=inv,
            defaults={
                "is_qualified": False,
                "result": "pending",
            }
        )
        
        # Store intermediate stats in answers instead of main fields to hide from dashboard
        submission.answers = cleaned
        submission.answers['_objective_stats'] = {
            'score': score,
            'total': total,
            'percentage': percentage
        }
        
        # Main fields stay at 0 until finalization
        submission.objective_score = 0
        submission.objective_total = 0
        submission.objective_percentage = 0.0

        # Combine with Coding Scores (preserve existing coding score if present)
        # coding_score defaults to 0 if not set
        
        # Weighted Scoring Logic
        # FIX: Check for None explicitly because 0 is a valid weight!
        w_obj = assessment.weightage_objective if assessment.weightage_objective is not None else 50
        w_cod = assessment.weightage_coding if assessment.weightage_coding is not None else 50
        
        # Normalize weights to ensure they sum to 100 (just in case)
        if w_obj + w_cod == 0:
            w_obj = 50
            w_cod = 50
            
        # Determine if we should use weights or simple average/sum
        # If it's a mixed assessment (both obj and coding exist), use weights.
        # If only objective, weight is effectively 100% objective.
        # If only coding, weight is effectively 100% coding.
        
        has_coding = assessment.coding_question_count > 0
        has_objective = assessment.total_questions > assessment.coding_question_count # Approximation
        
        # If strict "mixed" type isn't explicitly stored, infer from counts
        # (Note: total_questions includes objective questions only in some legacy logic, but usually total = obj + cod)
        # Let's trust the weights provided by the creator.
        
        obj_term = (submission.objective_percentage * w_obj)
        cod_term = (submission.coding_percentage * w_cod)
        
        # Special case: if one section doesn't exist, we might want to normalize to 100% based on the other?
        # BUT the requirement says "mixed, object-only, coding-only formulas".
        # Mixed: (obj * w_obj + cod * w_cod) / 100.
        # If obj-only: w_obj=100, w_cod=0.
        # If cod-only: w_obj=0, w_cod=100.
        # So the formula (obj% * w_obj + cod% * w_cod) / 100 works for all if weights are set correctly.
        
        # Centralized scoring logic
        from api.models import AssessmentCodingQuestion
        has_coding_final = AssessmentCodingQuestion.objects.filter(assessment=assessment).exists()
        _update_submission_scoring_logic(submission, finalize=not has_coding_final)
        
        submission.save(update_fields=[
            'answers', 
            'objective_score', 'objective_total', 'objective_percentage',
            'coding_score', 'coding_total', 'coding_percentage',
            'score', 'total', 'percentage', 'final_percentage', 
            'is_qualified', 'result'
        ])
        
        # Update assessment counters (best-effort)
        try:
            if created:
                assessment.submitted = int(getattr(assessment, 'submitted', 0) or 0) + 1
                assessment.evaluated = int(getattr(assessment, 'evaluated', 0) or 0) + 1
                if submission.result == 'selected':
                    assessment.shortlisted = int(getattr(assessment, 'shortlisted', 0) or 0) + 1
                assessment.save(update_fields=['submitted', 'evaluated', 'shortlisted'])
        except Exception:
            pass

        # Only mark as submitted if there are no coding questions
        # If coding questions exist, the frontend will call /coding/finalize/ next, which handles the final status.
        from api.models import AssessmentCodingQuestion
        has_coding = AssessmentCodingQuestion.objects.filter(assessment=assessment).exists()
        
        if not has_coding:
            inv.status = 'submitted'
            inv.save(update_fields=['status'])
            
            # ── TRIGGER EMAILS ──
            from api.tasks import send_custom_assessment_result_task, send_regret_email_task
            
            # 1. Qualified Email (5 min delay) - only if auto-schedule is ON
            if submission.result == 'selected':
                send_custom_assessment_result_task.apply_async(args=[inv.id], countdown=300)
            
            # 2. Regret Email (24 hour delay) - ALWAYS send for rejected, regardless of flag
            elif submission.result == 'rejected':
                send_regret_email_task.apply_async(args=[inv.id], countdown=86400)

        return Response(
            {
                'message': 'Submitted successfully.',
                'submission_id': submission.id,
                'score': submission.score,
                'total': submission.total,
                'percentage': submission.percentage,
                'result': submission.result,
            },
            status=status.HTTP_200_OK
        )
    except Exception as e:
        import traceback
        print(f"Error in submit_invitation_answers_view: {str(e)}")
        print(traceback.format_exc())
        return Response({'error': f'An error occurred while submitting: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def verify_identity_view(request, token):
    """
    Periodic identity check during assessment.
    Compares current webcam snapshot against registered baseline in CandidateDetails.
    """
    try:
        inv = CandidateInvitation.objects.get(token=token)
        if inv.status == 'submitted':
             return Response({'message': 'Exam already submitted'}, status=status.HTTP_200_OK)

        snapshot = request.data.get('webcam_screenshot')
        if not snapshot:
            return Response({'error': 'Snapshot required'}, status=status.HTTP_400_BAD_REQUEST)

        # 1. Get the registered baseline identity
        # We use CandidateDetails which was filled at the start.
        details = CandidateDetails.objects.filter(token=token).first()
        if not details:
            return Response({'error': 'Candidate details not found'}, status=status.HTTP_404_NOT_FOUND)

        person_id = details.pan_number # Baseline is registered under PAN in DeepFace
        
        # 2. Verify with DeepFace
        verify_result = verify_face_with_deepface(person_id, snapshot)
        is_verified = verify_result.get('verified', False)
        distance = verify_result.get('distance', 1.0)
        match_score = max(0.0, 1.0 - distance)

        # 3. Update Integrity Record
        integrity, _ = CandidateIntegrity.objects.get_or_create(invitation=inv)
        
        # Append to identity logs
        logs = integrity.identity_verification_logs if isinstance(integrity.identity_verification_logs, list) else []
        logs.append({
            'timestamp': timezone.now().isoformat(),
            'verified': is_verified,
            'match_score': round(match_score * 100, 2)
        })
        integrity.identity_verification_logs = logs
        
        # If mismatch detected, update the overall flag
        if not is_verified:
            integrity.identity_verified = False
            # Save a violation screenshot for the report
            _save_identity_violation_screenshot(inv, snapshot, "Identity Mismatch (Periodic)")
        
        integrity.save()

        return Response({
            'success': True,
            'verified': is_verified,
            'match_score': match_score
        }, status=status.HTTP_200_OK)

    except CandidateInvitation.DoesNotExist:
        return Response({'error': 'Invitation not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        import traceback
        print(f"Error in verify_identity_view: {str(e)}")
        print(traceback.format_exc())
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def update_standard_integrity_view(request, token):
    """
    Candidate sends video/audio violation events directly.
    """
    try:
        inv = CandidateInvitation.objects.get(token=token)
        
        # Don't penalize if exam is already submitted
        if inv.status == 'submitted':
            return Response({'message': 'Exam already submitted'}, status=status.HTTP_200_OK)

        data = request.data or {}
        event_type = data.get('event_type')
        timestamp = data.get('timestamp') or timezone.now().isoformat()

        if not event_type:
            return Response({'error': 'Event type required'}, status=status.HTTP_400_BAD_REQUEST)

        integrity, _ = CandidateIntegrity.objects.get_or_create(invitation=inv)

        penalty = 0
        if event_type == 'tab_switch':
            integrity.tab_switches += 1
            # 1st switch = 5% penalty, 2nd switch = +20% penalty (75% total)
            if integrity.tab_switches == 1:
                penalty = 5
            elif integrity.tab_switches == 2:
                penalty = 20 
            else:
                penalty = 10 
        elif event_type == 'phone_detection':
            integrity.phone_detections += 1
            penalty = 10 # 10% penalty as per new guidance
        elif event_type == 'multiface_detection':
            integrity.multiface_detections += 1
            penalty = 10 # 10% penalty for multiple faces
        elif event_type in ['no_face_detection', 'face_detection_lost']:
            integrity.no_face_detections += 1
            # First 3 are grace warnings (0 penalty)
            if integrity.no_face_detections > 3:
                penalty = 5
            else:
                penalty = 0
        else:
            return Response({'error': 'Unknown event type'}, status=status.HTTP_400_BAD_REQUEST)

        # Revised: Removed grace system for first 3 logs to ensure score matches warnings
        logs = integrity.warning_logs if isinstance(integrity.warning_logs, list) else []
        logs.append({
            'event_type': event_type,
            'timestamp': timestamp,
            'penalty_applied': penalty
        })
        integrity.warning_logs = logs

        if penalty > 0:
            integrity.integrity_score = max(0.0, integrity.integrity_score - penalty)
        
        # Always create an IntegrityScreenshot record to ensure it appears in the report log,
        # even if the visual snapshot is missing.
        screenshot_b64 = data.get('screenshot')
        webcam_b64 = data.get('webcam_screenshot')
        
        try:
            integrity_snap = IntegrityScreenshot(
                invitation=inv,
                event_type=event_type,
                timestamp=timezone.now()
            )
            
            if screenshot_b64 or webcam_b64:
                # Remove header if present (data:image/png;base64,...)
                if screenshot_b64:
                    if ';' in screenshot_b64 and 'base64,' in screenshot_b64:
                        header, imgstr = screenshot_b64.split(';base64,')
                        ext = header.split('/')[-1]
                    else:
                        imgstr = screenshot_b64
                        ext = 'png'

                    img_data = base64.b64decode(imgstr)
                    fname = f"integrity_{inv.id}_{event_type}_{int(timezone.now().timestamp())}.{ext}"
                    integrity_snap.screenshot.save(fname, ContentFile(img_data), save=False)
                    
                if webcam_b64:
                    if ';' in webcam_b64 and 'base64,' in webcam_b64:
                        header, imgstr = webcam_b64.split(';base64,')
                        ext = header.split('/')[-1]
                    else:
                        imgstr = webcam_b64
                        ext = 'png'

                    webcam_data = base64.b64decode(imgstr)
                    cname = f"cam_{inv.id}_{event_type}_{int(timezone.now().timestamp())}.{ext}"
                    integrity_snap.webcam_screenshot.save(cname, ContentFile(webcam_data), save=False)

            integrity_snap.save()
        except Exception as se:
            import traceback
            print(f"Failed to save screenshot: {str(se)}")
            print(traceback.format_exc())

        integrity.save()
        
        return Response({
            'message': 'Integrity logged',
            'integrity_score': integrity.integrity_score,
            'warnings_used': len(_get_filtered_warning_logs(logs))
        }, status=status.HTTP_200_OK)

    except CandidateInvitation.DoesNotExist:
        return Response({'error': 'Invitation not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        import traceback
        print("Integrity Error:", traceback.format_exc())
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def _update_submission_scoring_logic(submission, finalize=False):
    """
    Recalculates coding score and updates submission fields based on stored answers.
    Doesn't save the submission object (caller should save).
    """
    inv = submission.invitation
    # Fetch all coding questions for this assessment
    from api.models import AssessmentCodingQuestion
    acqs = AssessmentCodingQuestion.objects.filter(assessment=inv.assessment)
    
    total_possible_points = 0
    candidate_total_points = 0
    
    submission_answers = submission.answers or {}
    
    difficulty_map = {
        'easy': 1,
        'medium': 2,
        'hard': 3
    }

    for acq in acqs:
        # 1. Calculate Total Possible for this question
        diff_key = (acq.difficulty or 'medium').lower()
        multiplier = difficulty_map.get(diff_key, 2)
        total_possible_points += (100 * multiplier)
        
        # 2. Calculate Candidate Score for this question
        ans_key = f"acq_{acq.id}"
        ans_data = submission_answers.get(ans_key)
        
        if ans_data:
            passed = int(ans_data.get('passed_count', 0))
            total_tests = int(ans_data.get('total_tests', 0))
            
            if total_tests > 0:
                base_score_ratio = passed / total_tests
                weighted_score = (base_score_ratio * 100) * multiplier
                candidate_total_points += weighted_score

    # 3. Final Percentage
    if total_possible_points > 0:
        coding_percentage = (candidate_total_points / total_possible_points) * 100
    else:
        coding_percentage = 0.0
    
    # 4. Handle Objective Stats (from answers if hidden)
    obj_stats = submission_answers.get('_objective_stats', {})
    if obj_stats:
        current_obj_score = obj_stats.get('score', 0)
        current_obj_total = obj_stats.get('total', 0)
        current_obj_perc = obj_stats.get('percentage', 0.0)
    else:
        # Fallback to current fields (for legacy or finalize-only assessments)
        current_obj_score = submission.objective_score
        current_obj_total = submission.objective_total
        current_obj_perc = submission.objective_percentage

    # 5. Combined Percentage Calculation
    assessment = inv.assessment
    w_obj = assessment.weightage_objective if assessment.weightage_objective is not None else 50
    w_cod = assessment.weightage_coding if assessment.weightage_coding is not None else 50
    
    if w_obj + w_cod == 0:
        w_obj = 50
        w_cod = 50

    obj_term = (current_obj_perc * w_obj)
    cod_term = (coding_percentage * w_cod)
    
    final_percentage = (obj_term + cod_term) / 100.0
    final_percentage_rounded = round(final_percentage)

    # 6. Final Assignment to Submission (Only if finalizing)
    if finalize:
        submission.objective_score = current_obj_score
        submission.objective_total = current_obj_total
        submission.objective_percentage = current_obj_perc

        submission.coding_score = int(candidate_total_points)
        submission.coding_total = int(total_possible_points)
        submission.coding_percentage = coding_percentage

        submission.score = submission.objective_score + submission.coding_score
        submission.total = submission.objective_total + submission.coding_total
        submission.percentage = final_percentage_rounded
        submission.final_percentage = final_percentage
    else:
        # Hide progress from dashboard
        submission.coding_score = 0
        submission.coding_percentage = 0.0
        submission.score = 0
        submission.percentage = 0
        submission.final_percentage = 0.0
        submission.result = 'pending'
    
    if finalize:
        # --- RIGOROUS HIRING STANDARDS ---
        # Enforce minimum thresholds for individual sections
        custom_min = getattr(inv.assessment, 'min_pass_percentage', None)
        if custom_min is not None and float(custom_min) > 0:
            MIN_MCQ_THRESHOLD = float(custom_min)
            MIN_CODING_THRESHOLD = float(custom_min)
            min_pass = float(custom_min)
        else:
            MIN_MCQ_THRESHOLD = 60.0
            MIN_CODING_THRESHOLD = 50.0
            min_pass = 60.0

        # Check FaceUpdateRequest overrides
        from api.models import FaceUpdateRequest
        latest_req = FaceUpdateRequest.objects.filter(submission=submission).order_by('-requested_at').first()
        
        integrity_approved_override = False
        face_approved_override = False
        request_rejected_disqualification = False
        
        if latest_req:
            if latest_req.status == 'approved':
                if latest_req.integrity_flagged and latest_req.integrity_approved:
                    integrity_approved_override = True
                if latest_req.face_approved or latest_req.face_approved is None:
                    face_approved_override = True
            elif latest_req.status == 'rejected':
                request_rejected_disqualification = True

        MIN_INTEGRITY_THRESHOLD = 70.0
        
        # 7. Get Integrity Score
        integrity_score = 100.0
        is_identity_mismatch = False
        try:
            if hasattr(inv, 'integrity') and inv.integrity:
                 integrity_score = float(inv.integrity.integrity_score)
                 # Continuous Identity Check
                 if not getattr(inv.integrity, 'identity_verified', True):
                     is_identity_mismatch = True
            
            # Baseline Identity Check (from registration)
            details = CandidateDetails.objects.filter(token=inv.token).first()
            if details:
                if getattr(details, 'identity_mismatch_detected', False) or getattr(details, 'identity_mismatch', False):
                    is_identity_mismatch = True
        except Exception:
            pass

        # Apply overrides
        passed_integrity = (integrity_score >= MIN_INTEGRITY_THRESHOLD) or integrity_approved_override
        if face_approved_override:
            is_identity_mismatch = False

        # 8. Check Section Pass/Fail
        # Candidate must pass BOTH the overall threshold AND section-specific minimums
        
        # 9. Determine Result (Status)
        is_malpractice = (integrity_score < 70) and not integrity_approved_override
        
        # 10. Check Qualification
        passed_overall = final_percentage_rounded >= min_pass
        passed_mcq = submission.objective_percentage >= MIN_MCQ_THRESHOLD
        passed_coding = submission.coding_percentage >= MIN_CODING_THRESHOLD

        has_mcq = (submission.objective_total > 0)
        has_coding = (submission.coding_total > 0)
        
        is_zero_score = (final_percentage_rounded <= 0) or (submission.score == 0 and (has_mcq or has_coding))

        if is_zero_score or request_rejected_disqualification:
            submission.is_qualified = False
            submission.result = 'rejected'
        elif not passed_overall:
            submission.is_qualified = False
            submission.result = 'rejected'
        elif has_mcq and not passed_mcq:
            submission.is_qualified = False
            submission.result = 'rejected'
        elif has_coding and not passed_coding:
            submission.is_qualified = False
            submission.result = 'rejected'
        elif not passed_integrity or is_identity_mismatch:
            submission.is_qualified = False
            submission.result = 'hold'
        else:
            submission.is_qualified = True
            submission.result = 'selected'
    else:
        # Default intermediate status if not already set
        if submission.is_qualified is None:
            submission.is_qualified = False
        if not submission.result or submission.result in ('selected', 'rejected', 'hold'):
            submission.result = 'pending'


def _acq_allowed_languages(acq):
    allowed = []
    try:
        if isinstance(getattr(acq, 'allowed_languages', None), list):
            allowed = [str(v).strip().lower() for v in (acq.allowed_languages or []) if str(v).strip()]
    except Exception:
        allowed = []
    if allowed:
        return allowed
    langs = []
    try:
        if isinstance(getattr(acq, 'languages', None), list):
            langs = [str(v).strip().lower() for v in (acq.languages or []) if str(v).strip()]
    except Exception:
        langs = []
    if langs:
        return langs
    try:
        if getattr(acq.coding_question, 'language', None):
            return [str(acq.coding_question.language).strip().lower()]
    except Exception:
        pass
    return []


def _acq_merge_code(acq, user_code: str) -> str:
    """Return user code as-is for full program mode."""
    return "" if user_code is None else str(user_code)


def _evaluate_coding_question(acq, code, lang):
    """Helper to merge code, fetch test cases, and call executor for an ACQ."""
    from api.models import CodingTestCase
    exec_lang = lang or (acq.allowed_languages[0] if acq.allowed_languages else (acq.languages[0] if acq.languages else 'python3'))
    merged_code = _acq_merge_code(acq, code)

    schema_sql = None
    database_engine = None
    tcs = []
    if acq.coding_question:
        if exec_lang == 'sql':
            schema_sql = acq.coding_question.schema_sql
            database_engine = acq.coding_question.database_engine
        
        tcs_objs = CodingTestCase.objects.filter(question_id=acq.coding_question.id).order_by("id")
        for tc in tcs_objs:
            tcs.append({
                "id": tc.id,
                "stdin": tc.stdin or "",
                "expected_stdout": tc.expected_stdout or "",
                "is_hidden": tc.is_hidden,
            })

    result = _call_executor(
        language=exec_lang,
        source_code=merged_code,
        stdin="",
        time_limit_ms=getattr(acq, 'time_limit_ms', 3000),
        memory_mb=getattr(acq, 'memory_limit_mb', 256),
        schema_sql=schema_sql,
        database_engine=database_engine,
        testcases=tcs,
    )

    # Attach is_hidden from input tcs to output results for frontend redaction
    if result.get("ok") and "results" in result:
        for i, res in enumerate(result["results"]):
            if i < len(tcs):
                res["is_hidden"] = tcs[i].get("is_hidden", False)

    return result


def _call_executor(language: str, source_code: str, stdin: str, time_limit_ms: int, memory_mb: int, schema_sql: str = None, database_engine: str = None, testcases: list = None) -> dict:
    payload = {
        "language": language,
        "source_code": source_code,
        "stdin": stdin or "",
        "time_limit_ms": max(500, int(time_limit_ms or 3000)),
        "memory_mb": max(32, int(memory_mb or 256)),
        "schema_sql": schema_sql,
        "database_engine": database_engine,
        "testcases": testcases,
    }
    try:
        resp = requests.post(
            f"{EXECUTOR_BASE_URL}/execute",
            json=payload,
            timeout=max(5, int(payload["time_limit_ms"] / 1000) + 45),
        )
    except requests.RequestException as e:
        return {"ok": False, "error": f"Executor request failed: {str(e)}"}
    try:
        data = resp.json()
    except Exception:
        data = {"ok": False, "error": f"Non-JSON response from executor (status {resp.status_code})"}
    if resp.status_code >= 400 or not data.get("ok"):
        return {"ok": False, "error": data.get("error") or f"Executor error (status {resp.status_code})"}
    return data


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def invitation_coding_run_view(request, token):
    """
    Lightweight run for coding question inside an assessment invitation.
    Body:
    {
      "acq_id": <AssessmentCodingQuestion id>,
      "code": "...",
      "language": "python"
    }
    """
    try:
        try:
            inv = CandidateInvitation.objects.select_related('assessment').get(token=token)
        except CandidateInvitation.DoesNotExist:
            return Response({'error': 'Invitation not found.'}, status=status.HTTP_404_NOT_FOUND)

        acq_id = request.data.get('acq_id')
        code = request.data.get('code', '')
        lang = (request.data.get('language') or '').strip().lower()

        if not acq_id:
            return Response({'error': 'acq_id is required.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            acq = AssessmentCodingQuestion.objects.select_related('coding_question', 'assessment').get(id=int(acq_id))
        except AssessmentCodingQuestion.DoesNotExist:
            return Response({'error': 'Coding question not found.'}, status=status.HTTP_404_NOT_FOUND)

        if acq.assessment_id != inv.assessment_id:
            return Response({'error': 'Coding question does not belong to this assessment.'}, status=status.HTTP_403_FORBIDDEN)

        allowed_langs = _acq_allowed_languages(acq)
        if allowed_langs and lang and lang not in allowed_langs:
            return Response({'error': f'Language not allowed. Allowed: {", ".join(allowed_langs)}'}, status=status.HTTP_400_BAD_REQUEST)
        exec_lang = lang or (allowed_langs[0] if allowed_langs else None)
        if not exec_lang:
            return Response({'error': 'language is required.'}, status=status.HTTP_400_BAD_REQUEST)

        merged_code = _acq_merge_code(acq, code)

        # Prepare SQL specific params from the linked CodingQuestion
        schema_sql = None
        database_engine = None
        tcs = []
        
        if acq.coding_question:
            if exec_lang == 'sql':
                schema_sql = acq.coding_question.schema_sql
                database_engine = acq.coding_question.database_engine
            
            # Fetch visible test cases for validation
            tcs_objs = CodingTestCase.objects.filter(question_id=acq.coding_question.id, is_hidden=False).order_by("id")
            for tc in tcs_objs:
                tcs.append({
                    "id": tc.id,
                    "stdin": tc.stdin or "",
                    "expected_stdout": tc.expected_stdout or "",
                })

        result = _call_executor(
            language=exec_lang,
            source_code=merged_code,
            stdin="",
            time_limit_ms=getattr(acq, 'time_limit_ms', 3000),
            memory_mb=getattr(acq, 'memory_limit_mb', 256),
            schema_sql=schema_sql,
            database_engine=database_engine,
            testcases=tcs,
        )
        status_code = status.HTTP_200_OK if result.get('ok') else status.HTTP_400_BAD_REQUEST
        return Response(result, status=status_code)
    except Exception as e:
        import traceback
        print(f"Error in invitation_coding_run_view: {str(e)}")
        print(traceback.format_exc())
        return Response({'error': f'An error occurred while running code: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def invitation_coding_submit_view(request, token):
    """
    Submit (final) for a coding question inside an assessment invitation.
    Currently returns executor result; persistence/scoring is not implemented.
    Body:
    {
      "acq_id": <AssessmentCodingQuestion id>,
      "code": "...",
      "language": "python"
    }
    """
    try:
        try:
            inv = CandidateInvitation.objects.select_related('assessment').get(token=token)
        except CandidateInvitation.DoesNotExist:
            return Response({'error': 'Invitation not found.'}, status=status.HTTP_404_NOT_FOUND)

        acq_id = request.data.get('acq_id')
        code = request.data.get('code', '')
        lang = (request.data.get('language') or '').strip().lower()

        if not acq_id:
            return Response({'error': 'acq_id is required.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            acq = AssessmentCodingQuestion.objects.select_related('coding_question', 'assessment').get(id=int(acq_id))
        except AssessmentCodingQuestion.DoesNotExist:
            return Response({'error': 'Coding question not found.'}, status=status.HTTP_404_NOT_FOUND)

        if acq.assessment_id != inv.assessment_id:
            return Response({'error': 'Coding question does not belong to this assessment.'}, status=status.HTTP_403_FORBIDDEN)

        allowed_langs = _acq_allowed_languages(acq)
        if allowed_langs and lang and lang not in allowed_langs:
            return Response({'error': f'Language not allowed. Allowed: {", ".join(allowed_langs)}'}, status=status.HTTP_400_BAD_REQUEST)
        exec_lang = lang or (allowed_langs[0] if allowed_langs else None)
        if not exec_lang:
            return Response({'error': 'language is required.'}, status=status.HTTP_400_BAD_REQUEST)

        # Use helper for evaluation
        result = _evaluate_coding_question(acq, code, lang)

        if inv.status == 'submitted':
            return Response({'error': 'Your exam has been completed.'}, status=status.HTTP_409_CONFLICT)


        # Persistence logic
        if result.get("ok"):
            # Create or update CandidateSubmission
            submission, created = CandidateSubmission.objects.get_or_create(
                invitation=inv,
                defaults={
                    "answers": {},
                    "score": 0,
                    "total": 0,
                    "percentage": 0,
                    "final_percentage": 0.0,
                    "is_qualified": False,
                    "result": "pending",
                },
            )
            
            # Update answers for this question
            passed_count = result.get("passed_count", 0)
            total_tests_exec = result.get("total_tests", 0)
            
            answers = submission.answers or {}
            question_key = f"acq_{acq.id}"
                        
            # Store full test case results (including actual stdout and pass/fail status)
            test_cases_results = result.get("results", [])
            
            answers[question_key] = {
                "acq_id": acq.id,
                "question_id": acq.coding_question_id,
                "submitted_code": code,
                "language": exec_lang,
                "passed_count": passed_count,
                "total_tests": total_tests_exec,
                "test_cases": test_cases_results,
                "difficulty": acq.difficulty or 'medium', 
                "submitted_at": timezone.now().isoformat(),
            }
            submission.answers = answers
            
            # Recalculate score live so recruiters see progress
            _update_submission_scoring_logic(submission)
            submission.save()

            try:
                assessment = inv.assessment
                if created:
                    assessment.submitted = int(getattr(assessment, 'submitted', 0) or 0) + 1
                    assessment.evaluated = int(getattr(assessment, 'evaluated', 0) or 0) + 1
                    # shortlisted is ONLY updated during finalization
                    assessment.save(update_fields=['submitted', 'evaluated'])
            except Exception:
                pass
            result["submission_id"] = submission.id

        # Redact hidden test cases for the candidate response
        if "results" in result:
            for r in result["results"]:
                if r.get("is_hidden"):
                    # Only keep status and message, redact raw details
                    r["stdin"] = "REDACTED"
                    r["stdout"] = "REDACTED"
                    r["stderr"] = "REDACTED"
                    r["expected_stdout"] = "REDACTED"

        status_code = status.HTTP_200_OK if result.get('ok') else status.HTTP_400_BAD_REQUEST
        return Response(result, status=status_code)
    except Exception as e:
        import traceback
        print(f"Error in invitation_coding_submit_view: {str(e)}")
        print(traceback.format_exc())
        return Response({'error': f'An error occurred while submitting code: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def invitation_coding_finalize_view(request, token):
    """
    Finalize a coding-only invitation by creating a CandidateSubmission so that
    the result/rating page can be shown. Does nothing if an MCQ submission already exists.
    """
    try:
        try:
            inv = CandidateInvitation.objects.select_related('assessment').get(token=token)
        except CandidateInvitation.DoesNotExist:
            return Response({'error': 'Invitation not found.'}, status=status.HTTP_404_NOT_FOUND)

        # If already submitted, return success idempotently
        if inv.status in ('submitted', 'expired'):
             submission = getattr(inv, 'submission', None)
             if submission:
                 return Response({'ok': True, 'submission_id': submission.id}, status=status.HTTP_200_OK)

        # Ensure assessment has zero non-coding questions; otherwise enforce normal submit
        # Ensure assessment has zero non-coding questions; otherwise enforce normal submit
        # FIX: Allow mixed assessments (which have both). Only block if it's purely MCQ and somehow hit this endpoint?
        # Actually, if it has coding questions, we MUST allow this endpoint.
        # So we only block if has_mcq AND NOT has_coding.
        has_mcq = AssessmentQuestion.objects.filter(assessment=inv.assessment).exists()
        has_coding = AssessmentCodingQuestion.objects.filter(assessment=inv.assessment).exists()
        
        if has_mcq and not has_coding:
            return Response({'error': 'This assessment requires question answers submission.'}, status=status.HTTP_400_BAD_REQUEST)

        now = timezone.now()
        try:
            end_time = getattr(inv, 'end_time', None)
            end_time = timezone.make_aware(end_time, timezone.get_current_timezone()) if end_time and timezone.is_naive(end_time) else end_time
        except Exception:
            end_time = getattr(inv, 'end_time', None)

        if inv.started_at is None:
            return Response({'error': 'Exam has not been started.'}, status=status.HTTP_403_FORBIDDEN)
        
        # Use extended deadline (end_time + grace_minutes) for hard stop
        try:
            _finalize_grace = max(0, int(getattr(inv, 'start_grace_minutes', 0) or 0))
        except Exception:
            _finalize_grace = 0
        extended_deadline_finalize = (end_time + timedelta(minutes=_finalize_grace)) if end_time and _finalize_grace > 0 else end_time

        # Allow 2 minutes grace period for auto-submit delays / network skew
        if inv.expires_at and now > (inv.expires_at + timedelta(minutes=2)):
            return Response({'error': 'Time is over. Submission is closed.'}, status=status.HTTP_410_GONE)
        if extended_deadline_finalize and now > (extended_deadline_finalize + timedelta(minutes=2)):
            return Response({'error': 'Time is over. Submission is closed.'}, status=status.HTTP_410_GONE)

        # Get or create submission (it might exist from per-question submits)
        submission, created = CandidateSubmission.objects.get_or_create(
            invitation=inv,
            defaults={
                "answers": {},
                "score": 0,
                "total": 0,
                "percentage": 0,
                "final_percentage": 0.0,
                "is_qualified": False,
                "result": "pending",
            },
        )
        
        # --- NEW: Process code_map if provided ---
        code_map = request.data.get('code_map', {})
        if code_map:
            submission_answers = submission.answers or {}
            changed = False
            for acq_id_str, info in code_map.items():
                ans_key = f"acq_{acq_id_str}"
                # If question not evaluated yet, do it now
                if ans_key not in submission_answers:
                    try:
                        acq = AssessmentCodingQuestion.objects.get(id=int(acq_id_str), assessment=inv.assessment)
                        code = info.get('code', '')
                        lang = info.get('language', '')
                        
                        # Only evaluate if code is not empty/placeholder
                        if code.strip() and not code.strip().startswith('// Your code here'):
                            print(f"[DEBUG] Evaluating ACQ {acq.id} (Lang: {lang})")
                            res = _evaluate_coding_question(acq, code, lang)
                            print(f"[DEBUG] Result for ACQ {acq.id}: {res}")

                            
                            # Always save the submission attempt, even if evaluation 
                            test_cases_results = res.get("results", []) if res.get('ok') else []
                            submission_answers[ans_key] = {
                                "acq_id": acq.id,
                                "question_id": acq.coding_question_id,
                                "submitted_code": code,
                                "language": lang or (acq.allowed_languages[0] if acq.allowed_languages else 'python3'),
                                "passed_count": res.get("passed_count", 0) if res.get('ok') else 0,
                                "total_tests": res.get("total_tests", 0) if res.get('ok') else 0,
                                "test_cases": test_cases_results,
                                "difficulty": acq.difficulty or 'medium', 
                                "submitted_at": timezone.now().isoformat(),
                                "execution_error": res.get("error") if not res.get('ok') else None
                            }
                            changed = True
                    except Exception as e:
                        print(f"Error auto-evaluating {acq_id_str}: {str(e)}")
            
            if changed:
                submission.answers = submission_answers
                submission.save(update_fields=['answers'])

        # Use helper for scoring (Finalize is True here as this is the final finish)
        _update_submission_scoring_logic(submission, finalize=True)
        submission.save()

        is_qualified = submission.is_qualified

        try:
            assessment = inv.assessment
            # Increment counters only if not already counted? Evaluation logic is idempotent here largely
            assessment.submitted = int(getattr(assessment, 'submitted', 0) or 0) + 1
            assessment.evaluated = int(getattr(assessment, 'evaluated', 0) or 0) + 1
            if is_qualified:
                assessment.shortlisted = int(getattr(assessment, 'shortlisted', 0) or 0) + 1
            assessment.save(update_fields=['submitted', 'evaluated', 'shortlisted'])
        except Exception:
            pass
        
        # Mark invitation as submitted
        inv.status = 'submitted'
        inv.save(update_fields=['status'])

        # ── TRIGGER EMAILS ──
        from api.tasks import send_custom_assessment_result_task, send_regret_email_task
        
        # 1. Qualified Email (5 min delay) - only if auto-schedule is ON
        if submission.result == 'selected':
            send_custom_assessment_result_task.apply_async(args=[inv.id], countdown=300)
        
        # 2. Regret Email (24 hour delay) - ALWAYS send for rejected, regardless of flag
        elif submission.result == 'rejected':
            send_regret_email_task.apply_async(args=[inv.id], countdown=86400)

        # Update submitted_at to the true final submission time (coding finalized)
        # For mixed assessments, the submission record was created during objective submit
        # so submitted_at was set then. We update it now to reflect the real end time.
        from django.utils import timezone as tz_now
        submission.submitted_at = tz_now.now()
        submission.save(update_fields=['submitted_at'])

        return Response({'ok': True, 'submission_id': submission.id}, status=status.HTTP_200_OK)
    except Exception as e:
        import traceback
        print(f"Error in invitation_coding_finalize_view: {str(e)}")
        print(traceback.format_exc())
        return Response({'error': f'An error occurred while finalizing coding submission: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['GET'])
@permission_classes([AllowAny])
def get_invitation_result_view(request, token):
    """
    Fetch computed result for an invitation token (after submit).
    """
    try:
        try:
            inv = CandidateInvitation.objects.select_related('assessment').get(token=token)
        except CandidateInvitation.DoesNotExist:
            return Response({'error': 'Invitation not found.'}, status=status.HTTP_404_NOT_FOUND)

        submission = getattr(inv, 'submission', None)
        if not submission:
            return Response({'error': 'No submission found for this invitation.'}, status=status.HTTP_404_NOT_FOUND)

        a = inv.assessment

        # Get details
        latest_details = CandidateDetails.objects.filter(invitation=inv).order_by('id').last()
        original_identity_photo_url = None
        first_details = None
        if latest_details and latest_details.email:
            first_details = CandidateDetails.objects.filter(email__iexact=latest_details.email.strip()).order_by('id').first()
        if not first_details and inv.email:
            first_details = CandidateDetails.objects.filter(email__iexact=inv.email.strip()).order_by('id').first()
        
        if first_details and first_details.snapshot:
            original_identity_photo_url = first_details.snapshot
        else:
            link = None
            if latest_details and latest_details.email:
                link = IdentityLink.objects.filter(email__iexact=latest_details.email.strip()).order_by('id').first()
            if not link and inv.email:
                link = IdentityLink.objects.filter(email__iexact=inv.email.strip()).order_by('id').first()
            if not link and latest_details and latest_details.pan_number:
                norm_pan = re.sub(r'[^A-Z0-9]', '', latest_details.pan_number.strip().upper())
                if norm_pan:
                    link = IdentityLink.objects.filter(pan_number=norm_pan).order_by('id').first()

            if link and link.snapshot_image:
                original_identity_photo_url = request.build_absolute_uri(link.snapshot_image.url) if request else link.snapshot_image.url

        return Response(
            {
                'invitation': {
                    'id': inv.id,
                    'name': inv.name,
                    'email': inv.email,
                    'token': str(inv.token),
                },
                'assessment': {
                    'id': a.id,
                    'name': a.name,
                    'display_name': a.display_name,
                    'total_questions': a.total_questions,
                    'total_time': a.total_time,
                },
                'result': {
                    'score': submission.score,
                    'total': submission.total,
                    'percentage': submission.percentage,
                    'final_percentage': submission.final_percentage,
                    
                    'objective_score': submission.objective_score,
                    'objective_total': submission.objective_total,
                    'objective_percentage': submission.objective_percentage,
                    
                    'coding_score': submission.coding_score,
                    'coding_total': submission.coding_total,
                    'coding_percentage': submission.coding_percentage,
                    
                    'weightage_objective': a.weightage_objective,
                    'weightage_coding': a.weightage_coding,

                    'status': submission.result,
                    'is_qualified': submission.is_qualified,
                    'submitted_at': submission.submitted_at.isoformat() if submission.submitted_at else None,
                    'rating': getattr(submission, 'rating', None),
                    'feedback': getattr(submission, 'feedback', None),

                    # Mismatch fields inside result
                    'identity_mismatch_detected': (latest_details.identity_mismatch_detected or latest_details.identity_mismatch) if latest_details else False,
                    'identity_mismatch_reason': latest_details.identity_mismatch_reason if latest_details else None,
                    'original_identity_photo_url': original_identity_photo_url,
                    'candidate_photo_url': latest_details.snapshot if latest_details else None,
                    'photo_update_approved': latest_details.photo_update_approved if latest_details else False,
                    'photo_update_approved_by': latest_details.photo_update_approved_by if latest_details else None,
                    'photo_update_approved_at': latest_details.photo_update_approved_at.isoformat() if (latest_details and latest_details.photo_update_approved_at) else None,
                    'photo_update_reason': latest_details.photo_update_reason if latest_details else None,
                    'previous_registered_face_url': request.build_absolute_uri(latest_details.previous_registered_face_backup.url) if (latest_details and latest_details.previous_registered_face_backup) else None,
                    'photo_update_status': latest_details.photo_update_status if latest_details else 'none',
                    'photo_update_admin_note': latest_details.photo_update_admin_note if latest_details else None,
                },
                'integrity': {
                    'integrity_score': getattr(inv.integrity, 'integrity_score', 100.0) if hasattr(inv, 'integrity') else 100.0,
                    'warning_logs': _get_filtered_warning_logs(getattr(inv.integrity, 'warning_logs', [])) if hasattr(inv, 'integrity') else []
                },
                # Mismatch fields at top-level
                'identity_mismatch_detected': (latest_details.identity_mismatch_detected or latest_details.identity_mismatch) if latest_details else False,
                'identity_mismatch_reason': latest_details.identity_mismatch_reason if latest_details else None,
                'original_identity_photo_url': original_identity_photo_url,
                'candidate_photo_url': latest_details.snapshot if latest_details else None,
                'photo_update_approved': latest_details.photo_update_approved if latest_details else False,
                'photo_update_approved_by': latest_details.photo_update_approved_by if latest_details else None,
                'photo_update_approved_at': latest_details.photo_update_approved_at.isoformat() if (latest_details and latest_details.photo_update_approved_at) else None,
                'photo_update_reason': latest_details.photo_update_reason if latest_details else None,
                'previous_registered_face_url': request.build_absolute_uri(latest_details.previous_registered_face_backup.url) if (latest_details and latest_details.previous_registered_face_backup) else None,
                'photo_update_status': latest_details.photo_update_status if latest_details else 'none',
                'photo_update_admin_note': latest_details.photo_update_admin_note if latest_details else None,
            },
            status=status.HTTP_200_OK
        )
    except Exception as e:
        import traceback
        print(f"Error in get_invitation_result_view: {str(e)}")
        print(traceback.format_exc())
        return Response({'error': f'An error occurred while fetching result: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def results_overview_view(request):
    """
    Recruiter overview: list recent results (submissions).
    """
    try:
        user_profile = getattr(request.user, 'profile', None)
        company_id = user_profile.company_id if user_profile and user_profile.company else None
        scoped_ids = get_scoped_user_ids(user_profile) if user_profile else []

        if scoped_ids is None:
            # Application Admin: all results across ALL companies (platform superadmin)
            if company_id:
                qs = CandidateSubmission.objects.filter(
                    invitation__assessment__user_profile__company_id=company_id,
                    is_deleted=False
                ).select_related('invitation', 'invitation__assessment').order_by('-submitted_at')
            else:
                qs = CandidateSubmission.objects.filter(
                    is_deleted=False
                ).select_related('invitation', 'invitation__assessment').order_by('-submitted_at')
        elif company_id and scoped_ids:
            from django.db.models import Q
            # Role-scoped: results for candidates either invited by this user's hierarchy OR taking an assessment created by this user's hierarchy
            qs = CandidateSubmission.objects.filter(
                Q(invitation__user_profile_id__in=scoped_ids) | Q(invitation__assessment__user_profile_id__in=scoped_ids),
                is_deleted=False
            ).select_related('invitation', 'invitation__assessment').order_by('-submitted_at')
        else:
            qs = CandidateSubmission.objects.none()

        # Date filtering
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')

        if start_date:
            qs = qs.filter(submitted_at__date__gte=start_date)
        if end_date:
            qs = qs.filter(submitted_at__date__lte=end_date)
        
        # Combine and limit
        active_deletions = set()
        try:
            from ..models import DeletionRequest
            for dr in DeletionRequest.objects.filter(status='pending'):
                active_deletions.add(f"CandidateSubmission_{dr.object_id}")
                active_deletions.add(f"{dr.content_type}_{dr.object_id}")
        except Exception:
            pass

        # Gather submission IDs with a pending qualification request
        pending_qual_submission_ids = set()
        pending_qual_ai_ids = set()
        try:
            pending_qual_submission_ids = set(
                QualificationRequest.objects.filter(
                    status=QualificationRequest.STATUS_PENDING,
                    content_type=QualificationRequest.CONTENT_STANDARD,
                ).values_list('submission_id', flat=True)
            )
            pending_qual_ai_ids = set(
                QualificationRequest.objects.filter(
                    status=QualificationRequest.STATUS_PENDING,
                    content_type=QualificationRequest.CONTENT_AI,
                ).values_list('ai_submission_id', flat=True)
            )
        except Exception:
            pass


        # Optimization: Fetch results into a list and pre-build a map for candidate details
        results_slice = list(qs[:5000])
        inv_ids = [s.invitation_id for s in results_slice]
        
        details_map = {}
        identity_links_by_email = {}
        identity_links_by_pan = {}
        first_details_by_email = {}
        if inv_ids:
            # Fetch most recent details for each invitation in one query
            details_qs = CandidateDetails.objects.filter(invitation_id__in=inv_ids).order_by('id')
            emails_to_fetch = set()
            pans_to_fetch = []
            for d in details_qs:
                details_map[d.invitation_id] = d
                if d.email:
                    emails_to_fetch.add(d.email.lower().strip())
                if d.pan_number:
                    norm_pan = re.sub(r'[^A-Z0-9]', '', d.pan_number.strip().upper())
                    if norm_pan:
                        pans_to_fetch.append(norm_pan)
            
            for s in results_slice:
                if s.invitation and s.invitation.email:
                    emails_to_fetch.add(s.invitation.email.lower().strip())
            
            emails_to_fetch = list(emails_to_fetch)
            
            # Fetch the first CandidateDetails (oldest snapshot) for each email in one query
            if emails_to_fetch:
                f_details = CandidateDetails.objects.filter(email__in=emails_to_fetch).order_by('id')
                for fd in f_details:
                    email_key = fd.email.lower().strip()
                    if email_key not in first_details_by_email:
                        first_details_by_email[email_key] = fd
            
            # Fetch by email first, ordering by id ascending to get the first one created
            if emails_to_fetch:
                links_email = IdentityLink.objects.filter(email__in=emails_to_fetch).order_by('id')
                for link in links_email:
                    if link.email.lower().strip() not in identity_links_by_email:
                        identity_links_by_email[link.email.lower().strip()] = link
            
            # Fetch by PAN as fallback, ordering by id ascending
            if pans_to_fetch:
                links_pan = IdentityLink.objects.filter(pan_number__in=pans_to_fetch).order_by('id')
                for link in links_pan:
                    if link.pan_number not in identity_links_by_pan:
                        identity_links_by_pan[link.pan_number] = link

        results = []
        for s in results_slice:
            inv = s.invitation
            a = inv.assessment

            # Fetch PAN and Phone from mapped CandidateDetails, fallback to invitation
            latest_details = details_map.get(inv.id)
            
            pan = latest_details.pan_number if latest_details else inv.pan_number
            phone = latest_details.phone if latest_details else inv.phone

            # Ensure empty strings instead of null for CSV compatibility
            pan = pan or ""
            phone = phone or ""

            # Check CandidateDetails for original image first, then fallback to identity link
            original_identity_photo_url = None
            first_details = None
            if latest_details and latest_details.email:
                first_details = first_details_by_email.get(latest_details.email.lower().strip())
            if not first_details and inv.email:
                first_details = first_details_by_email.get(inv.email.lower().strip())

            if first_details and first_details.snapshot:
                original_identity_photo_url = first_details.snapshot
            else:
                link = None
                if latest_details and latest_details.email:
                    link = identity_links_by_email.get(latest_details.email.lower().strip())
                if not link and inv.email:
                    link = identity_links_by_email.get(inv.email.lower().strip())
                if not link and latest_details and latest_details.pan_number:
                    norm_pan = re.sub(r'[^A-Z0-9]', '', latest_details.pan_number.strip().upper())
                    if norm_pan:
                        link = identity_links_by_pan.get(norm_pan)

                if link and link.snapshot_image:
                    original_identity_photo_url = request.build_absolute_uri(link.snapshot_image.url) if request else link.snapshot_image.url

            results.append(
                {
                    'submission_id': s.id,
                    'invitation_id': inv.id,
                    'submitted_at': s.submitted_at.isoformat() if s.submitted_at else None,
                    'candidate': {
                        'name': inv.name,
                        'email': inv.email,
                        'pan_number': pan,
                        'phone': phone,
                    },
                    'assessment': {
                        'id': a.id,
                        'display_name': a.display_name,
                        'name': a.name,
                        'weightage_objective': a.weightage_objective,
                        'weightage_coding': a.weightage_coding,
                        'min_pass_percentage': a.min_pass_percentage,
                    },
                    'score': s.score,
                    'total': s.total,
                    'percentage': s.final_percentage if s.final_percentage is not None else s.percentage,
                    
                    'objective_score': s.objective_score,
                    'objective_total': s.objective_total,
                    'objective_percentage': s.objective_percentage,
                    
                    'coding_score': s.coding_score,
                    'coding_total': s.coding_total,
                    'coding_percentage': s.coding_percentage,
                    'batch_id': inv.batch_id,
                    'batch_name': inv.batch_name,

                    'status': s.result,
                    'termination_reason': (s.answers or {}).get('_termination', {}).get('reason') if isinstance(s.answers, dict) else None,
                    'termination_detail': (s.answers or {}).get('_termination', {}).get('detail') if isinstance(s.answers, dict) else None,
                    'qual_pending': s.id in pending_qual_submission_ids,
                    'delete_requested': f"CandidateSubmission_{s.id}" in active_deletions,
                    'answers': getattr(s, 'answers', {}),
                    'integrity': {
                        'integrity_score': getattr(inv.integrity, 'integrity_score', 100.0) if hasattr(inv, 'integrity') else 100.0,
                        'warning_logs': _get_filtered_warning_logs(getattr(inv.integrity, 'warning_logs', [])) if hasattr(inv, 'integrity') else []
                    },
                    'activity_logs': list(inv.activity_logs) if isinstance(inv.activity_logs, list) else [],
                    'regret_email_sent': s.regret_email_sent,
                    'created_at': inv.created_at.isoformat() if inv.created_at else None,

                    # Identity mismatch fields
                    'identity_mismatch_detected': (latest_details.identity_mismatch_detected or latest_details.identity_mismatch) if latest_details else False,
                    'identity_mismatch_reason': latest_details.identity_mismatch_reason if latest_details else None,
                    'original_identity_photo_url': original_identity_photo_url,
                    'candidate_photo_url': latest_details.snapshot if latest_details else None,
                    'photo_update_approved': latest_details.photo_update_approved if latest_details else False,
                    'photo_update_approved_by': latest_details.photo_update_approved_by if latest_details else None,
                    'photo_update_approved_at': latest_details.photo_update_approved_at.isoformat() if (latest_details and latest_details.photo_update_approved_at) else None,
                    'photo_update_reason': latest_details.photo_update_reason if latest_details else None,
                    'previous_registered_face_url': request.build_absolute_uri(latest_details.previous_registered_face_backup.url) if (latest_details and latest_details.previous_registered_face_backup) else None,
                    'photo_update_status': latest_details.photo_update_status if latest_details else 'none',
                    'photo_update_admin_note': latest_details.photo_update_admin_note if latest_details else None,
                }
            )


        results.extend(get_ai_assessment_results(
            scoped_ids, company_id, start_date, end_date, request, active_deletions, pending_qual_ai_ids
        ))
        results.extend(get_ai_candidate_results(
            scoped_ids, company_id, start_date, end_date, active_deletions, pending_qual_ai_ids, request=request
        ))

        # Also include non-submitted invitations (Standard Assessments)
        if company_id:
            if scoped_ids is None:
                inv_qs = CandidateInvitation.objects.filter(
                    assessment__user_profile__company_id=company_id,
                    submission__isnull=True
                ).select_related('assessment')
            else:
                inv_qs = CandidateInvitation.objects.filter(
                    Q(user_profile_id__in=scoped_ids) | Q(assessment__user_profile_id__in=scoped_ids),
                    submission__isnull=True
                ).select_related('assessment')
            
            if start_date:
                inv_qs = inv_qs.filter(created_at__date__gte=start_date)
            if end_date:
                inv_qs = inv_qs.filter(created_at__date__lte=end_date)
            
            now = timezone.now()
            for inv in inv_qs[:300]:
                a = inv.assessment
                # Use the actual stored status (e.g., 'failed', 'draft', 'sent')
                # Override to 'not_attempted' only if the assessment window has expired
                inv_status = inv.status or 'sent'
                if inv.end_time and now > inv.end_time and inv_status not in ('failed',):
                    inv_status = 'not_attempted'
                
                results.append({
                    'submission_id': None,
                    'invitation_id': inv.id,
                    'submitted_at': None,
                    'created_at': inv.created_at.isoformat() if inv.created_at else None,
                    'candidate': {
                        'name': inv.name,
                        'email': inv.email,
                    },
                    'assessment': {
                        'id': a.id,
                        'display_name': a.display_name,
                        'name': a.name,
                        'weightage_objective': a.weightage_objective,
                        'weightage_coding': a.weightage_coding,
                        'min_pass_percentage': a.min_pass_percentage,
                    },
                    'score': 0,
                    'total': 0,
                    'percentage': 0,
                    'objective_score': 0,
                    'objective_total': 0,
                    'objective_percentage': 0,
                    'coding_score': 0,
                    'coding_total': 0,
                    'coding_percentage': 0,
                    'status': inv_status,
                    'integrity': {
                        'integrity_score': None,
                        'warning_logs': []
                    },
                    'activity_logs': inv.activity_logs
                })

        # Re-sort combined results by submitted_at (fallback to created_at for invites)
        results.sort(key=lambda x: str(x.get('submitted_at') or x.get('created_at') or ''), reverse=True)

        return Response({'count': len(results), 'results': results}, status=status.HTTP_200_OK)
    except Exception as e:
        import traceback
        print(f"Error in results_overview_view: {str(e)}")
        print(traceback.format_exc())
        return Response({'error': f'An error occurred while fetching results: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@method_decorator(csrf_exempt, name='dispatch')
class CandidateSubmissionDeleteView(generics.DestroyAPIView):
    """
    Deletes a candidate submission.
    SECURED: Requires authentication and strictly scopes deletion to the user's company hierarchy.
    """
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        user_profile = getattr(user, 'profile', None)
        if not user_profile:
            return CandidateSubmission.objects.none()

        scoped_ids = get_scoped_user_ids(user_profile)

        if scoped_ids is None:
            # Application Admin: can delete any submission across all companies
            return CandidateSubmission.objects.all()

        # Company-scoped users: can only delete submissions for assessments 
        # created by someone within their allowed hierarchy
        return CandidateSubmission.objects.filter(
            invitation__assessment__user_profile_id__in=scoped_ids
        )

    def destroy(self, request, *args, **kwargs):
        user_profile = getattr(request.user, 'profile', None)
        if not user_profile or not user_profile.company:
            return super().destroy(request, *args, **kwargs)

        instance = self.get_object()

        # Block deletion for pending assessments
        if instance.result == 'pending':
            from rest_framework.response import Response
            from rest_framework import status
            return Response(
                {'error': 'Cannot delete a pending assessment. Please wait for the candidate to finish or time out.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Use centralized helper to handle policy and workflow
        response, handled = handle_deletion_request(
            user_profile=user_profile,
            company=user_profile.company,
            content_type='CandidateSubmission',
            object_id=instance.id,
            object_repr=f"Standard Assessment Submission: {instance.invitation.name} ({instance.invitation.email})",
            reason=request.data.get('reason')
        )
        
        if handled:
            return response

        # If not handled by helper (e.g. Superadmin), perform direct deletion
        return super().destroy(request, *args, **kwargs)



@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def submit_rating_view(request, token):
    """
    Candidate submits rating/feedback after submission.
    Body: { "rating": 1-5, "feedback": "optional" }
    """
    try:
        try:
            inv = CandidateInvitation.objects.select_related('assessment').get(token=token)
        except CandidateInvitation.DoesNotExist:
            return Response({'error': 'Invitation not found.'}, status=status.HTTP_404_NOT_FOUND)

        submission = getattr(inv, 'submission', None)
        if not submission:
            return Response({'error': 'No submission found for this invitation.'}, status=status.HTTP_404_NOT_FOUND)

        data = request.data or {}
        rating = data.get('rating', None)
        feedback = (data.get('feedback') or '').strip() or None

        # Prevent multiple ratings for the same submission
        if submission.rating is not None:
            return Response({'error': 'Rating already submitted for this invitation.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            rating_int = int(rating)
        except Exception:
            return Response({'error': 'rating must be an integer between 1 and 5.'}, status=status.HTTP_400_BAD_REQUEST)

        if rating_int < 1 or rating_int > 5:
            return Response({'error': 'rating must be between 1 and 5.'}, status=status.HTTP_400_BAD_REQUEST)

        submission.rating = rating_int
        submission.feedback = feedback
        submission.save(update_fields=['rating', 'feedback'])

        return Response({'message': 'Thanks for your feedback.'}, status=status.HTTP_200_OK)
    except Exception as e:
        import traceback
        print(f"Error in submit_rating_view: {str(e)}")
        print(traceback.format_exc())
        return Response({'error': f'An error occurred while saving rating: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def backfill_assessment_questions_view(request):
    """
    Backfill existing AssessmentQuestion records with data from their linked Question records.
    This is useful if AssessmentQuestion records were created before the snapshot fields were added.
    
    Expected request body (JSON):
    {
        "assessment_id": 1  // Optional: backfill only this assessment, or omit to backfill all
    }
    """
    try:
        assessment_id = request.data.get('assessment_id', None)
        
        # Get AssessmentQuestion records that need backfilling
        if assessment_id:
            aq_records = AssessmentQuestion.objects.filter(
                assessment_id=assessment_id
            ).select_related('question')
        else:
            # Backfill all records with NULL question_type
            aq_records = AssessmentQuestion.objects.filter(
                question_type__isnull=True
            ).select_related('question')
        
        updated_count = 0
        for aq in aq_records:
            q = aq.question
            if not q:
                continue
            
            # Update all fields from the linked Question
            aq.question_type = getattr(q, 'question_type', '') or ''
            aq.difficulty = getattr(q, 'difficulty', '') or ''
            aq.time_limit = getattr(q, 'time_limit', None) or 120
            aq.option_a = getattr(q, 'option_a', None) or ''
            aq.option_b = getattr(q, 'option_b', None) or ''
            aq.option_c = getattr(q, 'option_c', None) or ''
            aq.option_d = getattr(q, 'option_d', None) or ''
            aq.correct_answer = getattr(q, 'correct_answer', None) or ''
            aq.correct_answers = getattr(q, 'correct_answers', None) or []
            aq.skill = getattr(q, 'topic', '') or aq.skill or ''
            
            aq.save()
            updated_count += 1
        
        return Response(
            {
                'message': f'Successfully backfilled {updated_count} AssessmentQuestion records.',
                'updated_count': updated_count,
            },
            status=status.HTTP_200_OK
        )
        
    except Exception as e:
        import traceback
        print(f"Error in backfill_assessment_questions_view: {str(e)}")
        print(traceback.format_exc())
        return Response(
            {'error': f'An error occurred while backfilling: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def submit_objective_section(request, token):
    """
    Submits and grades ONLY the objective section.
    Used for split assessments where objective performance gates the coding section.
    Does NOT mark the invitation as 'submitted' unless it fails the cutoff.
    """
    try:
        try:
            inv = CandidateInvitation.objects.select_related('assessment').get(token=token)
        except CandidateInvitation.DoesNotExist:
            return Response({'error': 'Invitation not found.'}, status=status.HTTP_404_NOT_FOUND)

        if inv.status in ('submitted', 'qualified'):
            return Response({'error': 'Assessment already submitted.'}, status=status.HTTP_400_BAD_REQUEST)

        # Get answers: { "question_id": "A" ... }
        answers = request.data.get('answers', {})
        
        # Calculate Objective Score
        assessment = inv.assessment
        
        aq_qs = AssessmentQuestion.objects.filter(assessment=assessment)
        total_obj_questions = 0
        score = 0
        
        def _norm(v): return str(v).strip().upper() if v else ''
        
        for aq in aq_qs:
            qid_str = str(aq.id)
            if qid_str not in answers:
                total_obj_questions += 1
                continue
            
            total_obj_questions += 1
            user_val = answers[qid_str]
            
            # De-shuffle
            mapping = (inv.option_map or {}).get(qid_str)
            if mapping:
                if isinstance(user_val, list):
                   user_val = [mapping.get(x, x) for x in user_val]
                else:
                   user_val = mapping.get(user_val, user_val)
            
            # Grade
            qtype = (aq.question_type or '').strip().upper()
            if qtype == 'MSQ':
                u_list = sorted([_norm(x) for x in (user_val if isinstance(user_val, list) else [])])
                c_list = sorted([_norm(x) for x in (aq.correct_answers or [])])
                if u_list == c_list:
                    score += 1
            else:
                if _norm(user_val) == _norm(aq.correct_answer):
                    score += 1
                    
        percentage = (score / total_obj_questions * 100.0) if total_obj_questions > 0 else 0.0
        
        # Save to Submission
        submission, created = CandidateSubmission.objects.get_or_create(
            invitation=inv,
            defaults={
                "is_qualified": False,
                "result": "pending",
            }
        )
        # Store intermediate stats in answers to hide from dashboard
        submission.answers = answers # Store current state
        submission.answers['_objective_stats'] = {
            'score': score,
            'total': total_obj_questions,
            'percentage': round(percentage, 2)
        }
        
        # Main fields stay at 0 until finalization
        submission.objective_score = 0
        submission.objective_total = 0
        submission.objective_percentage = 0.0
        submission.save()
        
        from api.models import AssessmentCodingQuestion
        has_coding = AssessmentCodingQuestion.objects.filter(assessment=assessment).exists()

        # --- ENHANCED GATING LOGIC ---
        # Respect 'has_objective_cutoff' toggle and 'min_objective_pass_percentage'
        is_cutoff_enforced = getattr(assessment, 'has_objective_cutoff', False)
        # Use assessment's pass percentage, fallback to 60.0 if not set or 0
        min_mcq_gate = float(getattr(assessment, 'min_objective_pass_percentage', 60.0) or 60.0)
        if min_mcq_gate <= 0: min_mcq_gate = 60.0

        should_schedule_result_email = False
        
        # Determine MCQ pass status
        if is_cutoff_enforced:
            passed_mcq = percentage >= min_mcq_gate
        else:
            passed_mcq = True # Proceed regardless of score if toggle is OFF

        # NOTE: Integrity check no longer stops the candidate early (Option 1)
        # This allows candidates to finish the whole assessment even if flagged.
        # The 'Hold' status will be applied at the very end of the final section.
        
        if not passed_mcq:
            # Stopped only if MCQ cutoff is enabled and failed
            passed = False 
            next_stage = 'finish'
            message = "You did not meet the minimum requirement for the objective section. Your assessment is now complete."
            
            # Finalize immediately
            inv.status = 'submitted'
            inv.save()
            
            # Recalculate (will likely set to 'rejected')
            _update_submission_scoring_logic(submission, finalize=True)
            submission.save()
            
            # Schedule result email/report
            should_schedule_result_email = True
        else:
            # Proceed to next stage
            passed = True
            if has_coding:
                message = "Objective section completed. Proceeding to coding section."
                next_stage = 'coding'
            else:
                message = "Objective section completed successfully."
                next_stage = 'finish'
                inv.status = 'submitted'
                inv.save()
                should_schedule_result_email = True
            
            # If they have coding, finalize=False (result stays 'pending')
            # If no coding, finalize=True (result calculated now)
            _update_submission_scoring_logic(submission, finalize=(next_stage == 'finish'))
            submission.save()
        
        # Reload to get updated fields from _update_submission_scoring_logic
        submission.refresh_from_db()

        if should_schedule_result_email:
            from api.tasks import send_custom_assessment_result_task
            send_custom_assessment_result_task.apply_async(args=[inv.id], countdown=300)

        return Response({
            'success': True,
            'passed': passed,
            'score': score,
            'total': total_obj_questions,
            'percentage': percentage,
            'final_percentage': submission.final_percentage,
            'next_stage': next_stage,
            'message': message
        })

    except Exception as e:
        import traceback
        print(f"Error in submit_objective_section: {str(e)}")
        print(traceback.format_exc())
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def save_all_candidate_details_view(request):
    """
    Save candidate details before starting the assessment.
    Expected payload:
    {
        "token": "uuid-string",
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@example.com",
        "phone": "1234567890",
        "pan_number": "ABCDE1234F",
        "pan_file": <file>,
        "snapshot": "base64-encoded-image-string"
    }
    """
    try:
        token = request.data.get('token')
        session_id = request.data.get('session_id') or request.headers.get('X-Session-ID')
        if not token:
            return Response(
                {'error': 'Token is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate token exists in CandidateInvitation
        with transaction.atomic():
            try:
                invitation = CandidateInvitation.objects.select_for_update().get(token=token)
            except CandidateInvitation.DoesNotExist:
                return Response(
                    {'error': 'Invalid token'},
                    status=status.HTTP_404_NOT_FOUND
                )
                
            if invitation.claimed_session_id and session_id and invitation.claimed_session_id != session_id:
                return Response({'error': 'This assessment is already in use. If this is not you, please contact our support team.'}, status=status.HTTP_409_CONFLICT)
                
            if not invitation.claimed_session_id and session_id:
                invitation.claimed_session_id = session_id
                invitation.save(update_fields=['claimed_session_id'])

        # Extract data
        full_name = request.data.get('full_name', '').strip()
        first_name = request.data.get('first_name', '').strip()
        last_name = request.data.get('last_name', '').strip()

        # If full_name is provided, use it to derive first/last if they are empty
        if full_name:
            parts = full_name.split(' ', 1)
            if not first_name: first_name = parts[0]
            if not last_name and len(parts) > 1: last_name = parts[1]
        
        # If we only have first/last, construct full_name for validation check
        if not full_name and first_name:
            full_name = f"{first_name} {last_name}".strip()

        # Final check: if we still don't have first_name but have full_name...
        # this is just to be absolutely safe
        if not first_name and full_name:
            first_name = full_name
            last_name = ""

        email = request.data.get('email', '').strip()
        phone = request.data.get('phone', '').strip()
        pan_number = request.data.get('pan_number', '').strip().upper()
        snapshot = request.data.get('snapshot', '').strip()
        pan_file = request.FILES.get('pan_file')

        # Validation
        missing_fields = []
        if not full_name: missing_fields.append('full_name')
        if not email: missing_fields.append('email')
        if not phone: missing_fields.append('phone')
        if not pan_number: missing_fields.append('pan_number')
        if not snapshot: missing_fields.append('snapshot')
        
        # Split full name into first and last name for storage
        if full_name:
            parts = full_name.split(' ', 1)
            first_name = parts[0]
            last_name = parts[1] if len(parts) > 1 else ""
        else:
            first_name = ""
            last_name = ""

        if missing_fields:
            return Response(
                {'error': f"The following fields are required: {', '.join(missing_fields)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate PAN format (5 letters, 4 digits, 1 letter)
        if not re.match(r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$', pan_number):
            return Response(
                {'error': 'Invalid PAN number format'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate email format
        if not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
            return Response(
                {'error': 'Invalid email format'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate phone (10 digits)
        if not re.match(r'^[0-9]{10}$', phone):
            return Response(
                {'error': 'Invalid phone number format (must be 10 digits)'},
                status=status.HTTP_400_BAD_REQUEST
            )

        entered_with_consent = request.data.get('entered_with_consent', False)
        if isinstance(entered_with_consent, str):
            entered_with_consent = entered_with_consent.lower() == 'true'

        # 1. Normalize credentials
        norm_email = email.lower().strip()
        # Clean the input PAN of any spaces or junk for robust comparison
        norm_pan = re.sub(r'[^A-Z0-9]', '', pan_number.strip().upper())
        if len(norm_pan) == 10:
            norm_pan = normalize_pan_format(norm_pan)
        
        person_id = f"{norm_pan}"
        
        # 2. Strict Email-to-PAN Verification
        # To prevent malpractice, we ensure that an email address cannot be used with a 
        # different PAN if it has already been registered in the system.
        existing_email_link = IdentityLink.objects.filter(email=norm_email).first()
        email_pan_mismatch = False
        mismatch_reasons = []

        if existing_email_link and existing_email_link.pan_number != norm_pan:
            _save_identity_violation_screenshot(invitation, snapshot, "Email-PAN Mismatch")
            email_pan_mismatch = True
            mismatch_reasons.append(f"Email-PAN Mismatch: Email {norm_email} is already linked to a different candidate identity in the system (PAN: {existing_email_link.pan_number}).")

        # 3. Biometric Verification (Lookup by PAN)
        identity_link = IdentityLink.objects.filter(pan_number=norm_pan).first()
        
        verify_status = False
        match_score = 0.0
        face_mismatch_detected = False
        
        if identity_link:
            # Verification: Compare current snapshot with the registered identity face
            verify_result = verify_face_with_deepface(person_id, snapshot)
            
            # RECOVERY: If reference face is missing from filesystem, attempt to restore it
            if not verify_result.get('verified') and "No registered identity found" in str(verify_result.get('message', '')):
                recovered = False
                if identity_link.snapshot_image:
                    try:
                        identities_dir = os.path.join(settings.MEDIA_ROOT, 'identities', person_id)
                        os.makedirs(identities_dir, exist_ok=True)
                        with open(os.path.join(identities_dir, "canonical.jpg"), "wb") as f:
                            f.write(identity_link.snapshot_image.read())
                        # Retry verification
                        verify_result = verify_face_with_deepface(person_id, snapshot)
                        if verify_result.get('verified'):
                            recovered = True
                    except Exception as e:
                        print(f"Face recovery failed for {person_id}: {e}")
                
                if not recovered:
                    # Fallback: Re-register current face if reference is lost
                    reg_result = register_face_with_deepface(person_id, snapshot)
                    if reg_result.get('success'):
                        verify_result = {'verified': True, 'distance': 0.0}
                        # Also update the stored snapshot_image if it was missing
                        try:
                            if not identity_link.snapshot_image:
                                if ',' in snapshot: snapshot_b64 = snapshot.split(',', 1)[1]
                                else: snapshot_b64 = snapshot
                                snapshot_data = base64.b64decode(snapshot_b64)
                                identity_link.snapshot_image = ContentFile(snapshot_data, name=f"snapshot_{person_id}.jpg")
                                identity_link.save(update_fields=['snapshot_image'])
                        except: pass

            verify_status = verify_result.get('verified', False)
            distance = verify_result.get('distance', 1.0)
            match_score = max(0.0, 1.0 - distance)

            if verify_status == False:
                # Capture Violation Screenshot
                _save_identity_violation_screenshot(invitation, snapshot, "Identity Face Mismatch")
                face_mismatch_detected = True
                mismatch_reasons.append("Identity Face Mismatch: The captured face does not match the registered candidate's face.")
        else:
            # Linkage: Register the candidate's face for the first time
            reg_result = register_face_with_deepface(person_id, snapshot)
            if reg_result.get('success'):
                # Convert base64 snapshot to file for Django model
                snapshot_file = None
                if snapshot:
                    try:
                        if ',' in snapshot:
                            header, snapshot_b64 = snapshot.split(',', 1)
                        else:
                            snapshot_b64 = snapshot
                        snapshot_data = base64.b64decode(snapshot_b64)
                        snapshot_file = ContentFile(snapshot_data, name=f"snapshot_{person_id}.jpg")
                    except Exception as e:
                        print(f"Error decoding snapshot for IdentityLink: {e}")

                IdentityLink.objects.create(
                    email=norm_email,
                    pan_number=norm_pan,
                    pan_image=pan_file,
                    snapshot_image=snapshot_file,
                )
                verify_status = True
                match_score = 1.0
            else:
                error_msg = reg_result.get('message', 'Could not establish identity link. Please ensure your face is clearly visible.')
                # Fallback to saving details even if DeepFace service registration failed to ensure manual review
                verify_status = False
                match_score = 0.0
                face_mismatch_detected = True
                mismatch_reasons.append(f"Identity Verification System Error: {error_msg}")

        # Combine all mismatch reasons
        mismatch_reason = " | ".join(mismatch_reasons) if mismatch_reasons else None
        has_any_mismatch = email_pan_mismatch or face_mismatch_detected or (not verify_status if identity_link else False)

        # Create or update candidate details
        candidate_details, created = CandidateDetails.objects.update_or_create(
            token=token,
            email=email,
            defaults={
                'invitation': invitation,
                'first_name': first_name,
                'last_name': last_name,
                'phone': phone,
                'pan_number': pan_number,
                'snapshot': snapshot,
                'pan_file': pan_file,
                'entered_with_consent': entered_with_consent,
                'identity_mismatch_detected': has_any_mismatch,
                'face_match_score': match_score,
                'identity_mismatch': has_any_mismatch,
                'mismatch_score': match_score,
                'identity_mismatch_reason': mismatch_reason,
            }
        )

        if has_any_mismatch:
            # Check if we already logged a mismatch for this invitation to avoid duplicates
            already_logged = any(log.get('action') == 'Identity Mismatch Detected' for log in (invitation.activity_logs or []))
            if not already_logged:
                _append_invitation_activity_log(
                    invitation,
                    action='Identity Mismatch Detected',
                    details=f"Candidate identity mismatch detected: {mismatch_reason or 'Face/Email/PAN mismatch'}.",
                    category='security'
                )

        return Response({
            'success': True,
            'message': 'Candidate details saved successfully',
            'id': candidate_details.id,
            'created': created,
            'created_at': candidate_details.created_at.isoformat(),
        }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

    except Exception as e:
        import traceback
        print(f"Error in save_all_candidate_details_view: {str(e)}")
        print(traceback.format_exc())
        return Response(
            {'error': f'Failed to save candidate details: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )



@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def verify_pan_backend_view(request):
    """
    Backend view for PAN card automated verification via OCR.
    """
    try:
        pan_number_raw = request.data.get('pan_number', '').strip().upper()
        # Clean the input PAN of any spaces or junk for robust comparison
        pan_number = re.sub(r'[^A-Z0-9]', '', pan_number_raw)
        
        # User entered normalization (AAAAA 9999 A)
        # Handle cases where user might have put O instead of 0 in numeric part or vice versa
        if len(pan_number) == 10:
             pan_number = normalize_pan_format(pan_number)

        pan_file = request.FILES.get('pan_file')

        if not pan_number or not pan_file:
            return Response({'error': 'PAN number and file are required'}, status=status.HTTP_400_BAD_REQUEST)

        # Basic validation of PAN format
        if not re.match(r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$', pan_number):
             return Response({'error': 'Invalid PAN number format'}, status=status.HTTP_400_BAD_REQUEST)

        # Check file type
        is_pdf = pan_file.content_type == 'application/pdf' or pan_file.name.lower().endswith('.pdf')
        is_image = pan_file.content_type.startswith('image/')

        if not (is_image or is_pdf):
            return Response({'error': 'File must be an image or PDF for OCR verification'}, status=status.HTTP_400_BAD_REQUEST)

        # 1. Face Detection Check (Mandatory)
        # If PDF, convert first page to image for face detection
        face_check_file = pan_file
        if is_pdf:
            from .ocr_utils import pdf_page_to_png_bytes
            # Extract PDF content
            if hasattr(pan_file, 'temporary_file_path'):
                pdf_content = open(pan_file.temporary_file_path(), 'rb').read()
            else:
                pan_file.seek(0)
                pdf_content = pan_file.read()
                pan_file.seek(0)
            
            face_check_file = pdf_page_to_png_bytes(pdf_content, page_num=0)
            if not face_check_file:
                 return Response({'error': 'Could not process PDF for face detection'}, status=status.HTTP_400_BAD_REQUEST)

        face_detected, face_count = detect_face_in_image(face_check_file)
        if not face_detected:
            return Response({
                'success': True, 
                'verified': False, 
                'reason': 'no_face',
                'message': 'Invalid Document: No human face detected in the PAN card. Please upload a clear image of your original PAN card showing your face photograph.',
            }, status=status.HTTP_200_OK)

        # 2. Perform OCR / Extraction
        if is_pdf:
            extracted_text, success = extract_text_from_pdf(pan_file, target_pan=pan_number)
        else:
            extracted_text, success = extract_text_from_image(pan_file, target_pan=pan_number)
        
        # Clean extracted text for comparison
        clean_extracted = re.sub(r'[^A-Z0-9]', '', (extracted_text or "").upper())
        
        # Extract Name
        extracted_name = extract_name_from_text(extracted_text)

        # Find ALL potential PANs on the document (loose pattern)
        loose_pattern = re.compile(r'[A-Z0-9]{5}[0-9A-Z]{4}[A-Z0-9]{1}')
        raw_matches = re.findall(loose_pattern, clean_extracted)
        all_potential_pans = [normalize_pan_format(m) for m in raw_matches]

        # Step 1: Direct containment check (fast)
        if pan_number in clean_extracted:
             return Response({
                'success': True, 
                'verified': True, 
                'message': 'PAN verification successful',
                'extracted_pan': pan_number,
                'extracted_name': extracted_name
            }, status=status.HTTP_200_OK)

        # Step 2: Advanced Fuzzy Window Search (Check every 10-char slice)
        potential_matches = [clean_extracted[i:i+10] for i in range(len(clean_extracted) - 9)]
        found_fuzzy = False
        
        for p in potential_matches:
            norm = ""
            for i, char in enumerate(p):
                if 5 <= i <= 8: # Numeric section
                    if char in "OQ": norm += "0"
                    elif char in "I|L": norm += "1"
                    elif char == "S": norm += "5"
                    elif char == "Z": norm += "2"
                    elif char == "B": norm += "8"
                    elif char == "G": norm += "6"
                    else: norm += char
                else: norm += char
            
            if norm == pan_number:
                found_fuzzy = True
                break
        
        if found_fuzzy:
            return Response({
                'success': True, 
                'verified': True, 
                'message': 'PAN verification successful (Fuzzy)',
                'extracted_pan': pan_number,
                'extracted_name': extracted_name
            }, status=status.HTTP_200_OK)

        # Step 3: Determine failure reason
        # Check if the document has typical PAN card markers (comprehensive list)
        pan_keywords = [
            "INCOME", "TAX", "PERMANENT", "ACCOUNT", "NUMBER", "GOVT", "INDIA", 
            "DEPT", "DOB", "HOLDER", "DATE", "BIRTH", "CARD", "FATHER", "SIGNATURE", "DEPARTMENT"
        ]
        is_likely_pan = any(kw in clean_extracted for kw in pan_keywords)

        if len(all_potential_pans) > 0:
            reason = 'mismatch'
            if is_likely_pan:
                msg = "Mismatch: The PAN number on the document does not match your entry. Please enter a valid PAN or upload a clear card."
            else:
                msg = "Incorrect Document: This document seems to have a PAN-like number but is not a valid PAN card. Please upload a genuine PAN card."
        else:
            reason = 'unclear'
            if is_likely_pan:
                msg = "Could not find your PAN number on the card. Please upload a clear, high-quality image of your PAN card."
            else:
                msg = "Invalid Document: We could not find any PAN markers. Please upload a clear image of your correct PAN card."

        return Response({
            'success': True, 
            'verified': False, 
            'reason': reason,
            'message': msg,
            'extracted_pan': all_potential_pans[0] if all_potential_pans else None,
            'extracted_name': extracted_name,
            'debug_info': clean_extracted[:100]
        }, status=status.HTTP_200_OK)

    except Exception as e:
        import traceback
        from django.conf import settings
        log_file = os.path.join(settings.BASE_DIR, "backend_errors.txt")
        try:
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(f"[{timezone.now()}] ERROR in verify_pan_backend_view: {str(e)}\n")
                f.write(traceback.format_exc())
                f.write("-" * 30 + "\n")
        except:
            pass
        print(f"Backend PAN Verification Error: {e}")
        return Response({
            'success': False,
            'error': f'Failed to verify PAN: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

TERMINAL_CLOSE_LIMIT = 3


def _invitation_terminal_close_chances_left(invitation):
    count = int(getattr(invitation, 'terminal_close_count', 0) or 0)
    return max(0, TERMINAL_CLOSE_LIMIT - count)


def _append_invitation_activity_log(invitation, action, details='', **extra_fields):
    """Append a structured activity log entry with optional metadata."""
    log_entry = {
        'timestamp': timezone.now().isoformat(),
        'action': action,
        'details': details or '',
    }
    for key in ('category', 'termination_reason', 'termination_label'):
        val = extra_fields.get(key)
        if val:
            log_entry[key] = val
    logs = list(invitation.activity_logs) if isinstance(invitation.activity_logs, list) else []
    logs.append(log_entry)
    invitation.activity_logs = logs
    invitation.save(update_fields=['activity_logs'])
    print(f"[CANDIDATE_ACTIVITY] {invitation.email} | {action}: {details}")


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def invitation_activity_logs_view(request, invitation_id):
    """Recruiter: fetch fresh activity logs for an invitation (e.g. terminated exams)."""
    try:
        inv = CandidateInvitation.objects.get(id=invitation_id, is_deleted=False)
        logs = list(inv.activity_logs) if isinstance(inv.activity_logs, list) else []
        return Response({'activity_logs': logs})
    except CandidateInvitation.DoesNotExist:
        return Response({'error': 'Invitation not found.'}, status=status.HTTP_404_NOT_FOUND)


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def record_terminal_close_strike_view(request, token):
    """
    Atomically increment terminal-close strikes for this invitation (server authority).
    """
    try:
        with transaction.atomic():
            invitation = CandidateInvitation.objects.select_for_update().get(
                token=token,
                is_deleted=False,
            )
            previous = int(invitation.terminal_close_count or 0)
            if previous < TERMINAL_CLOSE_LIMIT:
                invitation.terminal_close_count = previous + 1
                close_count = invitation.terminal_close_count
            else:
                close_count = previous

            chances_left = _invitation_terminal_close_chances_left(invitation)
            if close_count > previous:
                if chances_left > 0:
                    detail = (
                        f'Secure Agent terminal closed ({close_count}/{TERMINAL_CLOSE_LIMIT}). '
                        f'{chances_left} chance(s) remaining before permanent termination.'
                    )
                else:
                    detail = (
                        f'Secure Agent terminal closed ({close_count}/{TERMINAL_CLOSE_LIMIT}). '
                        'Exam terminated.'
                    )
                log_entry = {
                    'timestamp': timezone.now().isoformat(),
                    'action': 'Terminal Closed',
                    'details': detail,
                    'category': 'security',
                    'termination_reason': 'terminal_close',
                }
                logs = list(invitation.activity_logs) if isinstance(invitation.activity_logs, list) else []
                logs.append(log_entry)
                invitation.activity_logs = logs
                invitation.save(update_fields=['terminal_close_count', 'activity_logs', 'updated_at'])
                print(f"[CANDIDATE_ACTIVITY] {invitation.email} | Terminal Closed: {detail}")
            else:
                invitation.save(update_fields=['updated_at'])

        should_terminate = close_count >= TERMINAL_CLOSE_LIMIT
        return Response({
            'close_count': close_count,
            'chances_left': chances_left,
            'limit': TERMINAL_CLOSE_LIMIT,
            'should_terminate': should_terminate,
        })
    except CandidateInvitation.DoesNotExist:
        return Response({'error': 'Invitation not found.'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def exam_tab_heartbeat_view(request, token):
    """
    Called every ~15 seconds by the active exam tab to keep the session lock alive.

    Body (optional):
        { "session_id": "<uuid>" }

    - If the session_id matches the current claimed_session_id, update the
      heartbeat timestamp so the lock is not considered stale.
    - If no session is currently locked (claimed_session_id is None), claim it.
    - If a *different* session_id is already locked AND still fresh, return 409.
    - If the existing lock is stale (> 30 s), hand it to the caller.
    """
    SESSION_LOCK_TIMEOUT_SECONDS = 30

    session_id = (
        request.data.get('session_id')
        or request.headers.get('X-Session-ID')
        or ''
    ).strip()

    try:
        with transaction.atomic():
            invitation = CandidateInvitation.objects.select_for_update().get(
                token=token,
                is_deleted=False,
            )

            now = timezone.now()

            # Helper: is the existing lock stale?
            def _stale():
                last_seen = getattr(invitation, 'claimed_session_last_seen', None)
                if not last_seen:
                    return True
                return (now - last_seen).total_seconds() > SESSION_LOCK_TIMEOUT_SECONDS

            if not session_id:
                # Heartbeat without a session_id — just acknowledge
                return Response({'ok': True, 'locked': False})

            if invitation.claimed_session_id and invitation.claimed_session_id != session_id:
                if not _stale():
                    # Another fresh tab owns the lock
                    return Response(
                        {'error': 'This assessment is already in use in another tab.'},
                        status=status.HTTP_409_CONFLICT,
                    )
                # Stale lock — take it over
                invitation.claimed_session_id = session_id

            elif not invitation.claimed_session_id:
                invitation.claimed_session_id = session_id

            # Update heartbeat timestamp
            invitation.claimed_session_last_seen = now
            invitation.save(update_fields=['claimed_session_id', 'claimed_session_last_seen'])

        return Response({'ok': True, 'locked': True})

    except CandidateInvitation.DoesNotExist:
        return Response({'error': 'Invitation not found.'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def log_candidate_activity_view(request, token):
    try:
        invitation = CandidateInvitation.objects.get(token=token, is_deleted=False)
        action = request.data.get('action')
        details = request.data.get('details', '')
        
        if action:
            _append_invitation_activity_log(
                invitation,
                action,
                details,
                category=request.data.get('category'),
                termination_reason=request.data.get('termination_reason'),
                termination_label=request.data.get('termination_label'),
            )
        return Response({'status': 'logged'})
    except CandidateInvitation.DoesNotExist:
        return Response({'error': 'Invalid token'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=500)


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def terminate_invitation_exam_view(request, token):
    """
    Policy termination: save partial answers, mark submission as terminated, enable PDF in results.
    """
    try:
        try:
            inv = CandidateInvitation.objects.select_related('assessment').get(token=token, is_deleted=False)
        except CandidateInvitation.DoesNotExist:
            return Response({'error': 'Invitation not found.'}, status=status.HTTP_404_NOT_FOUND)

        data = request.data or {}
        termination_reason = (data.get('termination_reason') or 'policy_violation').strip()
        termination_detail = (data.get('termination_detail') or '').strip()
        answers_in = data.get('answers') if isinstance(data.get('answers'), dict) else {}
        code_map = data.get('code_map') if isinstance(data.get('code_map'), dict) else {}

        submission = getattr(inv, 'submission', None)
        if inv.status == 'submitted' and submission and submission.result == 'terminated':
            return Response({
                'ok': True,
                'submission_id': submission.id,
                'already_terminated': True,
            }, status=status.HTTP_200_OK)

        assessment = inv.assessment
        valid_aq_ids = set(
            AssessmentQuestion.objects.filter(assessment=assessment).values_list('id', flat=True)
        )

        cleaned = {}
        for k, v in (answers_in or {}).items():
            try:
                aqid = int(k)
            except Exception:
                continue
            if aqid in valid_aq_ids:
                cleaned[str(aqid)] = v

        submission, _created = CandidateSubmission.objects.get_or_create(
            invitation=inv,
            defaults={
                'is_qualified': False,
                'result': 'pending',
            },
        )

        merged_answers = dict(submission.answers or {})
        merged_answers.update(cleaned)

        if code_map:
            for acq_id_str, info in code_map.items():
                if not isinstance(info, dict):
                    continue
                ans_key = f'acq_{acq_id_str}'
                merged_answers[ans_key] = {
                    'submitted_code': info.get('code') or '',
                    'language': info.get('language') or 'python3',
                    'terminated_partial': True,
                }

        merged_answers['_termination'] = {
            'reason': termination_reason,
            'detail': termination_detail,
            'at': timezone.now().isoformat(),
        }

        submission.answers = merged_answers
        _update_submission_scoring_logic(submission, finalize=True)
        submission.result = 'terminated'
        submission.is_qualified = False
        submission.submitted_at = timezone.now()
        submission.save()

        inv.status = 'submitted'
        inv.save(update_fields=['status', 'updated_at'])

        label_map = {
            'terminal_close': 'Secure Agent terminal closed (3 times)',
            'remote_access': 'Remote access application detected',
            'grace_expired': 'Remote access app not closed within grace period',
            'remote_app_after_precheck': 'Remote app detected after precheck',
        }
        termination_label = label_map.get(
            termination_reason,
            termination_reason.replace('_', ' ').title(),
        )
        _append_invitation_activity_log(
            inv,
            'Session Terminated',
            termination_detail or termination_label,
            category='termination',
            termination_reason=termination_reason,
            termination_label=termination_label,
        )

        return Response({
            'ok': True,
            'submission_id': submission.id,
            'result': 'terminated',
            'termination_reason': termination_reason,
            'activity_logs': list(inv.activity_logs) if isinstance(inv.activity_logs, list) else [],
        }, status=status.HTTP_200_OK)
    except Exception as e:
        import traceback
        print(f"terminate_invitation_exam_view error: {e}")
        print(traceback.format_exc())
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_submission_result_view(request, submission_id):
    """
    Manually updates the result of a submission.

    - Company Admin / App Admin: direct update (immediate effect).
    - HR Manager / HR: creates a QualificationRequest pending admin approval.
      The submission result stays unchanged until the admin approves.
      A 'reason' field is REQUIRED for non-admin users.
    """
    try:
        new_result = request.data.get('result')
        if new_result not in ['selected', 'rejected', 'hold']:
            return Response({'error': 'Invalid result status.'}, status=status.HTTP_400_BAD_REQUEST)

        user_profile = getattr(request.user, 'profile', None)
        company_id = user_profile.company_id if user_profile and user_profile.company else None

        try:
            if not company_id:
                submission = CandidateSubmission.objects.select_related('invitation').get(id=submission_id)
            else:
                submission = CandidateSubmission.objects.select_related('invitation').get(
                    id=submission_id,
                    invitation__assessment__user_profile__company_id=company_id
                )
        except CandidateSubmission.DoesNotExist:
            return Response({'error': 'Submission not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Block manual status override if there is an unresolved identity mismatch
        details = CandidateDetails.objects.filter(invitation=submission.invitation).order_by('id').last()
        if details and (getattr(details, 'identity_mismatch_detected', False) or getattr(details, 'identity_mismatch', False)):
            if not getattr(details, 'photo_update_approved', False) and details.photo_update_status != 'approved':
                return Response({'error': 'This candidate has an unresolved identity mismatch. Please action the request in the Settings & Workflows page.'}, status=status.HTTP_400_BAD_REQUEST)

        is_admin = (
            user_profile
            and (
                user_profile.role == UserProfile.ROLE_COMPANY_ADMIN
                or _is_application_admin_email(user_profile.email)
            )
        )

        # ── Non-admin path: create a qualification request ──────────────────
        if not is_admin:
            # 'hold' cannot be requested via approval workflow
            if new_result == 'hold':
                return Response({'error': 'Only admins can set a result to Hold directly.'}, status=status.HTTP_403_FORBIDDEN)

            reason = (request.data.get('reason') or '').strip()
            if not reason:
                return Response({'error': 'A reason is required when requesting a qualification change.'}, status=status.HTTP_400_BAD_REQUEST)

            # Check for existing pending request to prevent duplicates
            existing = QualificationRequest.objects.filter(
                submission=submission,
                status=QualificationRequest.STATUS_PENDING,
            ).first()
            if existing:
                return Response({
                    'message': 'A qualification request for this candidate is already pending admin approval.',
                    'pending': True,
                }, status=status.HTTP_200_OK)

            inv = submission.invitation
            qual_req = QualificationRequest.objects.create(
                requester=user_profile,
                submission=submission,
                content_type=QualificationRequest.CONTENT_STANDARD,
                requested_result=new_result,
                reason=reason,
                candidate_name=inv.name if inv else '',
                candidate_email=inv.email if inv else '',
            )
            from api.tasks import send_qualification_request_email_task
            send_qualification_request_email_task.apply_async(args=[qual_req.id])
            return Response({
                'message': 'Your qualification request has been submitted and is pending admin approval.',
                'pending': True,
            }, status=status.HTTP_201_CREATED)

        # ── Admin path: direct update ────────────────────────────────────────
        old_result = submission.result
        if old_result == new_result:
            return Response({'message': f'Result is already {new_result}.'}, status=status.HTTP_200_OK)

        submission.result = new_result
        # Keep is_qualified in sync so the auto-schedule Celery task
        # (which gates on submission.is_qualified) works correctly when
        # an admin manually promotes a Hold candidate to Selected.
        if new_result == 'selected':
            submission.is_qualified = True
        elif new_result in ('rejected', 'hold'):
            submission.is_qualified = False
        submission.save(update_fields=['result', 'is_qualified'])

        inv = submission.invitation
        from api.tasks import send_custom_assessment_result_task, send_regret_email_task

        if new_result == 'selected':
            send_custom_assessment_result_task.apply_async(args=[inv.id], countdown=300)
        elif new_result == 'rejected':
            send_regret_email_task.apply_async(args=[inv.id], countdown=300)

        return Response({
            'message': f'Submission result updated from {old_result} to {new_result}.',
            'new_result': new_result
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def _render_decision_page(req, error=None, success=None, decision_result=None):
    from django.utils import timezone
    
    # Format dates
    requested_at_str = timezone.localtime(req.requested_at).strftime('%d %b %Y, %I:%M %p') if req.requested_at else '-'
    decided_at_str = timezone.localtime(req.decided_at).strftime('%d %b %Y, %I:%M %p') if req.decided_at else '-'
    
    details = req.candidate_details
    candidate_name = f"{details.first_name} {details.last_name}" if details else "-"
    candidate_email = details.email if details else "-"
    candidate_pan = details.pan_number if details else "-"
    
    hr_profile = req.hr_user
    hr_name = f"{hr_profile.first_name} {hr_profile.last_name or ''}" if hr_profile else "HR Recruiter"
    hr_email = hr_profile.email if hr_profile else "-"
    
    original_url = ""
    is_backup_valid = False
    if req.original_face_backup:
        try:
            if req.original_face_backup.storage.exists(req.original_face_backup.name) and req.original_face_backup.size > 1000:
                original_url = req.original_face_backup.url
                is_backup_valid = True
        except Exception:
            pass

    if not is_backup_valid and details:
        first_details = CandidateDetails.objects.filter(email=details.email).order_by('id').first()
        if first_details and first_details.snapshot:
            original_url = first_details.snapshot

    captured_url = ""
    is_captured_valid = False
    if req.captured_face_backup:
        try:
            if req.captured_face_backup.storage.exists(req.captured_face_backup.name) and req.captured_face_backup.size > 1000:
                captured_url = req.captured_face_backup.url
                is_captured_valid = True
        except Exception:
            pass

    if not is_captured_valid and details:
        captured_url = details.snapshot

    # Build the card HTML based on status
    status_card = ""
    form_html = ""
    
    if req.status == 'approved' or decision_result == 'approved':
        status_card = f"""
        <div class="glass-card rounded-2xl p-8 max-w-lg w-full text-center shadow-2xl border border-emerald-500/20">
            <div class="w-16 h-16 bg-emerald-500/10 text-emerald-400 rounded-full flex items-center justify-center mx-auto mb-6">
                <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7"></path></svg>
            </div>
            <h1 class="text-2xl font-extrabold text-white mb-2">Request Approved</h1>
            <p class="text-slate-400 text-sm mb-6">The baseline registered face for this candidate has been successfully updated in the database and DeepFace index.</p>
            
            <div class="bg-slate-900/40 rounded-xl p-4 text-left border border-slate-800 text-xs mb-6 space-y-2">
                <div><span class="text-slate-500 font-semibold">Candidate:</span> <span class="text-slate-300">{candidate_name}</span></div>
                <div><span class="text-slate-500 font-semibold">PAN Number:</span> <span class="text-slate-300">{candidate_pan}</span></div>
                <div><span class="text-slate-500 font-semibold">HR Recruiter:</span> <span class="text-slate-300">{hr_name}</span></div>
                <div><span class="text-slate-500 font-semibold">Decision Date:</span> <span class="text-slate-300">{decided_at_str}</span></div>
                {f'<div><span class="text-slate-500 font-semibold">Admin Note:</span> <span class="text-slate-300 italic">"{req.admin_note}"</span></div>' if req.admin_note else ''}
            </div>
            
            <div class="text-xs text-slate-500">You may close this window. The recruiter's dashboard has been updated.</div>
        </div>
        """
    elif req.status == 'rejected' or decision_result == 'rejected':
        status_card = f"""
        <div class="glass-card rounded-2xl p-8 max-w-lg w-full text-center shadow-2xl border border-rose-500/20">
            <div class="w-16 h-16 bg-rose-500/10 text-rose-400 rounded-full flex items-center justify-center mx-auto mb-6">
                <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M6 18L18 6M6 6l12 12"></path></svg>
            </div>
            <h1 class="text-2xl font-extrabold text-white mb-2">Request Rejected</h1>
            <p class="text-slate-400 text-sm mb-6">The identity mismatch approval request was rejected. The candidate's registered face baseline remains unchanged.</p>
            
            <div class="bg-slate-900/40 rounded-xl p-4 text-left border border-slate-800 text-xs mb-6 space-y-2">
                <div><span class="text-slate-500 font-semibold">Candidate:</span> <span class="text-slate-300">{candidate_name}</span></div>
                <div><span class="text-slate-500 font-semibold">HR Recruiter:</span> <span class="text-slate-300">{hr_name}</span></div>
                <div><span class="text-slate-500 font-semibold">Decision Date:</span> <span class="text-slate-300">{decided_at_str}</span></div>
                {f'<div><span class="text-slate-500 font-semibold">Rejection Note:</span> <span class="text-slate-300 italic">"{req.admin_note}"</span></div>' if req.admin_note else ''}
            </div>
            
            <div class="text-xs text-slate-500">You may close this window. The recruiter's dashboard has been updated.</div>
        </div>
        """
    else:
        form_html = f"""
        <form method="POST" class="mt-6 space-y-6">
            <div>
                <label for="admin_note" class="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Admin Review Notes / Audit Notes (Optional)</label>
                <textarea id="admin_note" name="admin_note" rows="3" placeholder="Add any details, verification checks or justification for this decision..." class="w-full bg-slate-950/60 border border-slate-800 rounded-xl p-3 text-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition resize-none"></textarea>
            </div>
            
            <div class="flex flex-col sm:flex-row gap-4 pt-2">
                <button type="submit" name="action" value="approve" class="flex-1 bg-gradient-to-r from-emerald-600 to-teal-500 hover:from-emerald-500 hover:to-teal-400 text-white font-bold py-3.5 px-6 rounded-xl transition duration-200 shadow-lg shadow-emerald-500/10 hover:shadow-emerald-500/20 flex items-center justify-center gap-2 text-sm">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                    Approve & Update Face
                </button>
                <button type="submit" name="action" value="reject" class="flex-1 bg-gradient-to-r from-rose-600 to-pink-600 hover:from-rose-500 hover:to-pink-500 text-white font-bold py-3.5 px-6 rounded-xl transition duration-200 shadow-lg shadow-rose-500/10 hover:shadow-rose-500/20 flex items-center justify-center gap-2 text-sm">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                    Reject Request
                </button>
            </div>
        </form>
        """
        
        status_card = f"""
        <div class="glass-card rounded-2xl p-6 md:p-8 max-w-4xl w-full shadow-2xl border border-slate-800">
            <div class="flex flex-col md:flex-row justify-between items-start md:items-center border-b border-slate-800 pb-6 mb-6 gap-4">
                <div>
                    <h1 class="text-xl md:text-2xl font-black text-white tracking-tight flex items-center gap-2.5">
                        <span class="w-2.5 h-2.5 bg-yellow-500 rounded-full animate-pulse"></span>
                        Identity Mismatch Review
                    </h1>
                    <p class="text-slate-400 text-xs mt-1">Manual verification and baseline registration update request.</p>
                </div>
                <div class="bg-yellow-500/10 text-yellow-500 border border-yellow-500/20 text-[10px] font-black uppercase tracking-wider px-3 py-1.5 rounded-md">
                    Pending Admin Approval
                </div>
            </div>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6 bg-slate-950/40 rounded-xl p-5 border border-slate-900/60 mb-8">
                <div class="space-y-3">
                    <h3 class="text-xs font-bold text-slate-500 uppercase tracking-wider border-b border-slate-900 pb-1.5">Candidate Details</h3>
                    <div class="text-sm"><span class="text-slate-400 font-medium">Name:</span> <span class="text-slate-200 font-semibold">{candidate_name}</span></div>
                    <div class="text-sm"><span class="text-slate-400 font-medium">Email:</span> <span class="text-slate-200 font-semibold">{candidate_email}</span></div>
                    <div class="text-sm"><span class="text-slate-400 font-medium">PAN Number:</span> <span class="text-slate-200 font-semibold">{candidate_pan}</span></div>
                </div>
                <div class="space-y-3">
                    <h3 class="text-xs font-bold text-slate-500 uppercase tracking-wider border-b border-slate-900 pb-1.5">HR Request Metadata</h3>
                    <div class="text-sm"><span class="text-slate-400 font-medium">Requested By:</span> <span class="text-slate-200 font-semibold">{hr_name} ({hr_email})</span></div>
                    <div class="text-sm"><span class="text-slate-400 font-medium">Requested At:</span> <span class="text-slate-200 font-semibold">{requested_at_str}</span></div>
                    <div class="text-sm"><span class="text-slate-400 font-medium">HR Recruiter Reason:</span> <span class="text-slate-200 font-semibold italic">"{req.hr_reason}"</span></div>
                </div>
            </div>
            
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-6 mb-6">
                <div class="flex flex-col items-center">
                    <span class="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-3">Original Registered Face</span>
                    <div class="w-full aspect-[4/3] rounded-xl overflow-hidden border-2 border-slate-800 bg-slate-950 flex items-center justify-center shadow-inner">
                        {f'<img src="{original_url}" class="w-full h-full object-cover" alt="Original Registered Face"/>' if original_url else '<span class="text-slate-600 text-xs font-semibold">No Image Available</span>'}
                    </div>
                </div>
                <div class="flex flex-col items-center">
                    <span class="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-3">Captured Mismatch Face</span>
                    <div class="w-full aspect-[4/3] rounded-xl overflow-hidden border-2 border-rose-500/30 bg-slate-950 flex items-center justify-center shadow-inner">
                        {f'<img src="{captured_url}" class="w-full h-full object-cover" alt="Captured Mismatch Face"/>' if captured_url else '<span class="text-slate-600 text-xs font-semibold">No Image Available</span>'}
                    </div>
                </div>
            </div>
            
            <div class="bg-rose-500/10 border border-rose-500/20 text-rose-400 rounded-xl p-4 text-xs leading-relaxed font-medium mb-6">
                <strong>CRITICAL SECURITY ACTION:</strong> Approving this request will overwrite the baseline registration image for this candidate (under PAN <strong>{candidate_pan}</strong>) with the current mismatch capture image. Mismatch warning flags and history will remain fully intact for compliance logs.
            </div>
            
            {form_html}
        </div>
        """

    # Assemble full page
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>VerifiHire - Candidate Identity Review</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
        <style>
            body {{
                font-family: 'Plus Jakarta Sans', sans-serif;
                background: radial-gradient(circle at top left, #0f172a, #020617);
            }}
            .glass-card {{
                background: rgba(15, 23, 42, 0.45);
                backdrop-filter: blur(12px);
                -webkit-backdrop-filter: blur(12px);
                border: 1px solid rgba(255, 255, 255, 0.08);
            }}
        </style>
    </head>
    <body class="min-h-screen text-slate-100 flex items-center justify-center p-4 sm:p-6 md:p-8">
        {status_card}
    </body>
    </html>
    """
    return html


@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def request_photo_update_view(request, submission_id):
    """
    Recruiter requests photo update / manual review.
    Creates a pending FaceUpdateRequest and emails the company admins.
    """
    try:
        import uuid
        from PIL import Image
        import io
        from django.core.mail import send_mail
        from django.conf import settings

        user_profile = getattr(request.user, 'profile', None)
        company_id = user_profile.company_id if user_profile and user_profile.company else None
        
        # 1. Fetch submission
        try:
            if not company_id:
                submission = CandidateSubmission.objects.select_related('invitation').get(id=submission_id)
            else:
                submission = CandidateSubmission.objects.select_related('invitation').get(
                    id=submission_id,
                    invitation__assessment__user_profile__company_id=company_id
                )
        except CandidateSubmission.DoesNotExist:
            return Response({'error': 'Submission not found.'}, status=status.HTTP_404_NOT_FOUND)

        inv = submission.invitation
        
        # 2. Get latest details
        details = CandidateDetails.objects.filter(invitation=inv).order_by('id').last()
        if not details:
            return Response({'error': 'Candidate details not found.'}, status=status.HTTP_404_NOT_FOUND)

        # 3. Check status
        if details.photo_update_status == 'pending':
            return Response({'error': 'An approval request is already pending with the admin.'}, status=status.HTTP_400_BAD_REQUEST)
        if details.photo_update_status == 'approved':
            return Response({'error': 'This identity mismatch has already been approved.'}, status=status.HTTP_400_BAD_REQUEST)

        # 4. Validate snapshot exists
        snapshot = details.snapshot
        if not snapshot:
            return Response({'error': 'No captured snapshot found to approve.'}, status=status.HTTP_400_BAD_REQUEST)

        reason = (request.data.get('reason') or '').strip()
        if not reason:
            return Response({'error': 'Reason is required for manual review approval request.'}, status=status.HTTP_400_BAD_REQUEST)

        # Retrieve proctoring integrity details
        integrity_flagged = False
        integrity_score = 100.0
        integrity_details_str = ""
        integrity_details_html = ""
        tab_switches = 0
        phone_detections = 0
        multiface_detections = 0
        no_face_detections = 0
        suspicion_score = 0
        suspicion_reasons = []

        try:
            if hasattr(inv, 'integrity') and inv.integrity:
                integrity_score = float(inv.integrity.integrity_score)
                tab_switches = inv.integrity.tab_switches
                phone_detections = inv.integrity.phone_detections
                multiface_detections = inv.integrity.multiface_detections
                no_face_detections = inv.integrity.no_face_detections
                suspicion_score = inv.integrity.suspicion_score
                suspicion_reasons = inv.integrity.suspicion_reasons or []
                
                if integrity_score < 70.0:
                    integrity_flagged = True
        except Exception as e:
            print(f"[Integrity] Error reading integrity during request creation: {e}")

        if integrity_flagged:
            reasons_text = ", ".join(suspicion_reasons) if suspicion_reasons else "None"
            integrity_details_str = (
                f"\n--- PROCTORING INTEGRITY DETAILS ---\n"
                f"Integrity Score: {integrity_score}%\n"
                f"Tab Switches: {tab_switches}\n"
                f"Phone Detections: {phone_detections}\n"
                f"Multi-face Detections: {multiface_detections}\n"
                f"No-face Detections: {no_face_detections}\n"
                f"Suspicion Score: {suspicion_score}\n"
                f"Suspicion Reasons: {reasons_text}\n"
            )
            
            reasons_html_list = "".join([f"<li style='margin-bottom: 4px;'>{r}</li>" for r in suspicion_reasons]) if suspicion_reasons else "<li>None</li>"
            
            integrity_details_html = f"""
            <div style="margin-top: 24px; padding: 20px; background-color: #fffbeb; border: 1px solid #fef3c7; border-radius: 8px; border-left: 4px solid #f59e0b;">
              <h3 style="color: #b45309; margin-top: 0; margin-bottom: 12px; font-size: 15px; font-weight: 700; display: flex; align-items: center; gap: 6px;">
                ⚠️ Proctoring Integrity Flags Detected
              </h3>
              <p style="font-size: 13px; color: #78350f; margin-bottom: 12px; line-height: 1.4;">
                This candidate also has a low integrity score (<strong>{integrity_score}%</strong>) indicating potential proctoring violations during the assessment.
              </p>
              <table style="width: 100%; border-collapse: collapse; font-size: 13px; color: #78350f;">
                <tr>
                  <td style="padding: 6px 0; font-weight: 700; width: 45%;">Integrity Score:</td>
                  <td style="padding: 6px 0; font-weight: 700;">{integrity_score}%</td>
                </tr>
                <tr>
                  <td style="padding: 6px 0;">Tab Switches:</td>
                  <td style="padding: 6px 0;">{tab_switches}</td>
                </tr>
                <tr>
                  <td style="padding: 6px 0;">Phone Detections:</td>
                  <td style="padding: 6px 0;">{phone_detections}</td>
                </tr>
                <tr>
                  <td style="padding: 6px 0;">Multi-face Detections:</td>
                  <td style="padding: 6px 0;">{multiface_detections}</td>
                </tr>
                <tr>
                  <td style="padding: 6px 0;">No-face Detections:</td>
                  <td style="padding: 6px 0;">{no_face_detections}</td>
                </tr>
                <tr>
                  <td style="padding: 6px 0;">Suspicion Score:</td>
                  <td style="padding: 6px 0;">{suspicion_score}</td>
                </tr>
                <tr style="vertical-align: top;">
                  <td style="padding: 6px 0;">Suspicion Reasons:</td>
                  <td style="padding: 6px 0;">
                    <ul style="margin: 0; padding-left: 20px;">
                      {reasons_html_list}
                    </ul>
                  </td>
                </tr>
              </table>
            </div>
            """

        # 5. Extract snapshot data
        try:
            if ',' in snapshot:
                header, snapshot_b64 = snapshot.split(',', 1)
            else:
                snapshot_b64 = snapshot
            snapshot_data = base64.b64decode(snapshot_b64)
            
            img = Image.open(io.BytesIO(snapshot_data))
            img.verify()
        except Exception as e:
            return Response({'error': f'Captured snapshot is not a valid or usable image: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

        # 6. Setup backups for request
        norm_email = details.email.lower().strip()
        norm_pan = re.sub(r'[^A-Z0-9]', '', details.pan_number.strip().upper())
        person_id = norm_pan

        # Retrieve current baseline identity link
        link = IdentityLink.objects.filter(pan_number=norm_pan).first()
        if not link:
            link = IdentityLink.objects.filter(email=norm_email).first()

        original_face_data = None
        if link and link.snapshot_image:
            try:
                link.snapshot_image.seek(0)
                original_face_data = link.snapshot_image.read()
            except Exception as e:
                print(f"[Backup] Failed to read IdentityLink face image: {e}")

        if not original_face_data:
            # Fallback: Backup from first CandidateDetails snapshot (which would have been the first registered face)
            first_details = CandidateDetails.objects.filter(email=norm_email).order_by('id').first()
            if first_details and first_details.snapshot and first_details.id != details.id:
                try:
                    f_b64 = first_details.snapshot.split(',', 1)[1] if ',' in first_details.snapshot else first_details.snapshot
                    original_face_data = base64.b64decode(f_b64)
                except Exception as e:
                    print(f"[Backup] Failed to read first details snapshot: {e}")

        # 7. Create FaceUpdateRequest inside a transaction block
        with transaction.atomic():
            req = FaceUpdateRequest.objects.create(
                submission=submission,
                candidate_details=details,
                company=user_profile.company,
                hr_user=user_profile,
                hr_reason=reason,
                status='pending',
                integrity_flagged=integrity_flagged
            )

            # Save copies to request backup fields
            if snapshot_data:
                req.captured_face_backup.save(
                    name=f"req_captured_{submission_id}_{uuid.uuid4().hex[:8]}.jpg",
                    content=ContentFile(snapshot_data),
                    save=False
                )
            if original_face_data:
                req.original_face_backup.save(
                    name=f"req_original_{submission_id}_{uuid.uuid4().hex[:8]}.jpg",
                    content=ContentFile(original_face_data),
                    save=False
                )
            req.save()

            # Update status on details
            details.photo_update_status = 'pending'
            details.save(update_fields=['photo_update_status'])

            # Log HR manual review approval request submission
            _append_invitation_activity_log(
                inv,
                action='Identity Mismatch Approval Requested by HR',
                details=f"HR Recruiter {user_profile.first_name} {user_profile.last_name or ''} ({user_profile.email}) submitted a review approval request. Reason: {reason}",
                category='security'
            )

        # 8. Send Email notification to Admins
        admins = UserProfile.objects.filter(company=user_profile.company, role=UserProfile.ROLE_COMPANY_ADMIN)
        admin_emails = [a.email for a in admins if a.email]
        
        if not admin_emails:
            if user_profile.manager and user_profile.manager.email:
                admin_emails = [user_profile.manager.email]
            else:
                fallback_admin = UserProfile.objects.filter(company=user_profile.company).exclude(email=None).first()
                if fallback_admin:
                    admin_emails = [fallback_admin.email]
                else:
                    admin_emails = [settings.DEFAULT_FROM_EMAIL]

        if integrity_flagged:
            subject = f"VerifiHire - Identity Mismatch & Proctoring Integrity Review Request for {details.first_name} {details.last_name}"
        else:
            subject = f"VerifiHire - Identity Mismatch Approval Request for {details.first_name} {details.last_name}"
        
        message = (
            f"Hello Admin,\n\n"
            f"An approval request has been submitted for manual review:\n\n"
            f"Candidate: {details.first_name} {details.last_name}\n"
            f"Email: {details.email}\n"
            f"PAN Number: {details.pan_number}\n"
            f"Recruiter: {user_profile.first_name} {user_profile.last_name or ''} ({user_profile.email})\n"
            f"Reason: {reason}\n"
            f"{integrity_details_str}\n"
            f"Please log in to your VerifiHire dashboard and navigate to the 'Settings & Workflows' page to review and action this request.\n\n"
            f"Thank you,\n"
            f"VerifiHire Support"
        )

        html_message = f"""
        <html>
        <body style="font-family: 'Inter', Arial, sans-serif; background-color: #f8fafc; padding: 20px; color: #0f172a; margin: 0;">
          <div style="max-width: 600px; margin: 20px auto; background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 32px; box-shadow: 0 4px 12px rgba(0,0,0,0.05);">
            <h2 style="color: #0f172a; border-bottom: 2px solid #3b82f6; padding-bottom: 12px; margin-top: 0; font-size: 20px; font-weight: 700;">
              {"Identity Mismatch & Proctoring Integrity Review Request" if integrity_flagged else "Identity Mismatch Approval Request"}
            </h2>
            <p style="font-size: 15px; line-height: 1.5; color: #334155;">
              Recruiter <strong>{user_profile.first_name} {user_profile.last_name or ''}</strong> has requested manual review approval for a candidate.
            </p>
            <table style="width: 100%; margin: 24px 0; border-collapse: collapse; font-size: 14px;">
              <tr>
                <td style="padding: 10px 0; font-weight: 700; color: #64748b; width: 35%;">Candidate Name:</td>
                <td style="padding: 10px 0; color: #0f172a;">{details.first_name} {details.last_name}</td>
              </tr>
              <tr>
                <td style="padding: 10px 0; font-weight: 700; color: #64748b;">Candidate Email:</td>
                <td style="padding: 10px 0; color: #0f172a;">{details.email}</td>
              </tr>
              <tr>
                <td style="padding: 10px 0; font-weight: 700; color: #64748b;">PAN Number:</td>
                <td style="padding: 10px 0; color: #0f172a;">{details.pan_number}</td>
              </tr>
              <tr>
                <td style="padding: 10px 0; font-weight: 700; color: #64748b; vertical-align: top;">HR Reason:</td>
                <td style="padding: 10px 0; color: #0f172a; font-style: italic; background-color: #f8fafc; padding: 12px; border-radius: 6px; border-left: 3px solid #cbd5e1;">"{reason}"</td>
              </tr>
            </table>
            {integrity_details_html}
            <p style="font-size: 14px; line-height: 1.5; color: #334155; margin-top: 24px;">
              Please log in to your VerifiHire portal and navigate to the <strong>Settings & Workflows</strong> page to review the comparison and decide on the request.
            </p>
            <p style="font-size: 11px; color: #94a3b8; margin-top: 40px; border-top: 1px solid #e2e8f0; padding-top: 16px; text-align: center;">
              This is an automated security notification from VerifiHire. Please do not reply directly to this email.
            </p>
          </div>
        </body>
        </html>
        """

        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=admin_emails,
                fail_silently=False,
                html_message=html_message
            )
            email_sent = True
        except Exception as mail_err:
            print(f"[Email] Failed to send admin photo update request email: {mail_err}")
            email_sent = False

        return Response({
            'message': 'Identity manual review request submitted to Admin successfully.',
            'email_sent': email_sent,
            'photo_update_status': 'pending'
        }, status=status.HTTP_200_OK)

    except Exception as e:
        import traceback
        print(f"Error in request_photo_update_view: {str(e)}")
        print(traceback.format_exc())
        return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def decide_photo_update_view(request, token):
    """
    Renders the decision page for the admin to approve or reject a face update request.
    Handles the action when submitted.
    """
    try:
        from PIL import Image
        import io
        import re
        import uuid
        from django.core.files.base import ContentFile
        from django.http import HttpResponse

        try:
            req = FaceUpdateRequest.objects.select_related('submission', 'candidate_details', 'hr_user', 'company').get(token=token)
        except FaceUpdateRequest.DoesNotExist:
            return HttpResponse("<h1>404 Not Found</h1><p>Invalid or expired request token.</p>", status=404)

        if request.method == 'GET':
            html_content = _render_decision_page(req)
            return HttpResponse(html_content, content_type='text/html')

        elif request.method == 'POST':
            if req.status != 'pending':
                html_content = _render_decision_page(req)
                return HttpResponse(html_content, content_type='text/html')

            action = request.POST.get('action')
            admin_note = (request.POST.get('admin_note') or '').strip()

            if action not in ['approve', 'reject']:
                html_content = _render_decision_page(req, error="Invalid action specified.")
                return HttpResponse(html_content, content_type='text/html')

            details = req.candidate_details
            if not details:
                return HttpResponse("<h1>Error</h1><p>Candidate details not found.</p>", status=400)

            if action == 'approve':
                with transaction.atomic():
                    # Refresh details under transaction lock
                    details = CandidateDetails.objects.select_for_update().get(id=details.id)
                    if details.photo_update_approved:
                        req.status = 'approved'
                        req.save()
                        html_content = _render_decision_page(req)
                        return HttpResponse(html_content, content_type='text/html')

                    norm_email = details.email.lower().strip()
                    norm_pan = re.sub(r'[^A-Z0-9]', '', details.pan_number.strip().upper())
                    person_id = norm_pan

                    # Retrieve baseline identity link
                    link = IdentityLink.objects.filter(pan_number=norm_pan).first()
                    if not link:
                        link = IdentityLink.objects.filter(email=norm_email).first()

                    # Backup old registered face from IdentityLink
                    old_face_file = None
                    if link and link.snapshot_image:
                        old_face_file = link.snapshot_image

                    if old_face_file:
                        try:
                            old_face_file.seek(0)
                            old_file_data = old_face_file.read()
                            details.previous_registered_face_backup.save(
                                name=f"backup_{person_id}_{os.path.basename(old_face_file.name)}",
                                content=ContentFile(old_file_data),
                                save=False
                            )
                        except Exception as e:
                            print(f"[Backup] Failed to backup old registered face: {e}")
                    else:
                        if req.original_face_backup:
                            try:
                                req.original_face_backup.seek(0)
                                orig_data = req.original_face_backup.read()
                                details.previous_registered_face_backup.save(
                                    name=f"backup_first_details_{person_id}.jpg",
                                    content=ContentFile(orig_data),
                                    save=False
                                )
                            except Exception as e:
                                print(f"[Backup] Failed to copy backup from request: {e}")

                    # Overwrite/Create IdentityLink
                    if not link:
                        link = IdentityLink(email=norm_email, pan_number=norm_pan)

                    if req.captured_face_backup:
                        try:
                            req.captured_face_backup.seek(0)
                            cap_data = req.captured_face_backup.read()
                            snapshot_file = ContentFile(cap_data, name=f"snapshot_{person_id}.jpg")
                            link.snapshot_image = snapshot_file
                        except Exception as e:
                            print(f"[IdentityLink] Error copying captured snapshot to link: {e}")
                    link.save()

                    # Overwrite DeepFace canonical image file
                    reg_result = register_face_with_deepface(person_id, details.snapshot)
                    if not reg_result.get('success'):
                        print(f"[DeepFace] Registration failed: {reg_result.get('message')}")

                    # Save approval metadata
                    details.photo_update_approved = True
                    details.photo_update_approved_by = "Company Admin"
                    details.photo_update_approved_at = timezone.now()
                    details.photo_update_reason = req.hr_reason
                    details.photo_update_status = 'approved'
                    details.save()

                    # Save FaceUpdateRequest
                    req.status = 'approved'
                    req.admin_note = admin_note
                    req.decided_at = timezone.now()
                    req.save()

                    # Create activity log entry
                    log_entry = {
                        'timestamp': timezone.now().isoformat(),
                        'action': 'Identity Mismatch Approved by Admin',
                        'details': f"Admin approved identity mismatch. HR Reason: {req.hr_reason}. Admin Note: {admin_note}",
                        'category': 'security'
                    }
                    inv_obj = CandidateInvitation.objects.get(id=details.invitation_id)
                    logs = list(inv_obj.activity_logs) if isinstance(inv_obj.activity_logs, list) else []
                    logs.append(log_entry)
                    inv_obj.activity_logs = logs
                    inv_obj.save(update_fields=['activity_logs', 'updated_at'])

            elif action == 'reject':
                with transaction.atomic():
                    details = CandidateDetails.objects.select_for_update().get(id=details.id)
                    details.photo_update_status = 'rejected'
                    details.photo_update_approved = False
                    details.photo_update_admin_note = admin_note
                    details.save(update_fields=['photo_update_status', 'photo_update_approved', 'photo_update_admin_note'])

                    # Save FaceUpdateRequest
                    req.status = 'rejected'
                    req.admin_note = admin_note
                    req.decided_at = timezone.now()
                    req.save()

                    # Create activity log entry
                    log_entry = {
                        'timestamp': timezone.now().isoformat(),
                        'action': 'Identity Mismatch Rejected by Admin',
                        'details': f"Admin rejected identity mismatch request. Admin Note: {admin_note}",
                        'category': 'security'
                    }
                    inv_obj = CandidateInvitation.objects.get(id=details.invitation_id)
                    logs = list(inv_obj.activity_logs) if isinstance(inv_obj.activity_logs, list) else []
                    logs.append(log_entry)
                    inv_obj.activity_logs = logs
                    inv_obj.save(update_fields=['activity_logs', 'updated_at'])

            html_content = _render_decision_page(req, decision_result=action)
            return HttpResponse(html_content, content_type='text/html')

    except Exception as e:
        import traceback
        print(f"Error in decide_photo_update_view: {str(e)}")
        print(traceback.format_exc())
        from django.http import HttpResponseServerError
        return HttpResponseServerError(f"An internal error occurred: {str(e)}")

