from .._imports import *
from .._imports import _is_application_admin_email
from ai_assessments.results_helpers import get_ai_assessment_results, get_ai_candidate_results
from api.utils.batch_utils import generate_batch_id, generate_batch_name
from ..models import CandidateSubmission, QualificationRequest
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

        frontend_base = getattr(settings, 'FRONTEND_BASE_URL', None) or os.environ.get('FRONTEND_BASE_URL') or 'https://verifihireai.com'

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

        if not check_only and session_id:
            with transaction.atomic():
                try:
                    inv = CandidateInvitation.objects.select_for_update().select_related('assessment').get(token=token)
                except CandidateInvitation.DoesNotExist:
                    return Response({'error': 'Invitation not found.'}, status=status.HTTP_404_NOT_FOUND)
                
                if inv.claimed_session_id and inv.claimed_session_id != session_id:
                    return Response({'error': 'This assessment is already in use. If this is not you, please contact our support team.'}, status=status.HTTP_409_CONFLICT)
                
                if not inv.claimed_session_id:
                    inv.claimed_session_id = session_id
                    inv.save(update_fields=['claimed_session_id'])
        else:
            try:
                inv = CandidateInvitation.objects.select_related('assessment').get(token=token)
            except CandidateInvitation.DoesNotExist:
                return Response({'error': 'Invitation not found.'}, status=status.HTTP_404_NOT_FOUND)
                
            if inv.claimed_session_id and session_id and inv.claimed_session_id != session_id:
                return Response({'error': 'This assessment is already in use. If this is not you, please contact our support team.'}, status=status.HTTP_409_CONFLICT)

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

        # 8. Check Section Pass/Fail
        # Candidate must pass BOTH the overall threshold AND section-specific minimums
        
        # 9. Determine Result (Status)
        is_malpractice = (integrity_score < 70)
        
        # 10. Check Qualification
        passed_overall = final_percentage_rounded >= min_pass
        passed_mcq = submission.objective_percentage >= MIN_MCQ_THRESHOLD
        passed_coding = submission.coding_percentage >= MIN_CODING_THRESHOLD
        passed_integrity = (integrity_score >= MIN_INTEGRITY_THRESHOLD)

        has_mcq = (submission.objective_total > 0)
        has_coding = (submission.coding_total > 0)
        
        is_zero_score = (final_percentage_rounded <= 0) or (submission.score == 0 and (has_mcq or has_coding))

        if is_zero_score:
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
                },
                'integrity': {
                    'integrity_score': getattr(inv.integrity, 'integrity_score', 100.0) if hasattr(inv, 'integrity') else 100.0,
                    'warning_logs': _get_filtered_warning_logs(getattr(inv.integrity, 'warning_logs', [])) if hasattr(inv, 'integrity') else []
                }
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
        if inv_ids:
            # Fetch most recent details for each invitation in one query
            details_qs = CandidateDetails.objects.filter(invitation_id__in=inv_ids).order_by('id')
            for d in details_qs:
                details_map[d.invitation_id] = d

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
                # Logic: if current time > end_time -> not_attempted, else sent
                inv_status = 'sent'
                if inv.end_time and now > inv.end_time:
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
        if existing_email_link and existing_email_link.pan_number != norm_pan:
            _save_identity_violation_screenshot(invitation, snapshot, "Email-PAN Mismatch")
            return Response({
                'error': 'Identity Violation: This email address is already linked to a different candidate identity. To ensure assessment integrity, you must use your original registered credentials.'
            }, status=status.HTTP_403_FORBIDDEN)

        # 3. Biometric Verification (Lookup by PAN)
        identity_link = IdentityLink.objects.filter(pan_number=norm_pan).first()
        
        verify_status = False
        match_score = 0.0
        
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
                return Response({
                    'error': 'Identity Mismatch Detected: The captured face does not match the registered candidate. Assessment has been stopped.'
                }, status=status.HTTP_403_FORBIDDEN)
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
                return Response({
                    'error': f"Identity Verification System Error: {error_msg}"
                }, status=status.HTTP_400_BAD_REQUEST)

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
                'identity_mismatch_detected': not verify_status if identity_link else False,
                'face_match_score': match_score,
                'identity_mismatch': not verify_status if identity_link else False,
                'mismatch_score': match_score,
            }
        )

        return Response({
            'success': True,
            'message': 'Candidate details saved successfully',
            'id': candidate_details.id,
            'created': created,
            'created_at': candidate_details.created_at.isoformat(),
        }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

    except Exception as e:
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
        submission.save(update_fields=['result'])

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

