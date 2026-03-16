from ._imports import *


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

        data = request.data or {}
        candidates = data.get('candidates', [])
        if not isinstance(candidates, list) or len(candidates) == 0:
            return Response({'error': 'candidates must be a non-empty array.'}, status=status.HTTP_400_BAD_REQUEST)

        frontend_base = getattr(settings, 'FRONTEND_BASE_URL', None) or os.environ.get('FRONTEND_BASE_URL') or 'https://verifyhire.duckdns.org'

        results = []
        sent_count = 0
        fail_count = 0

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

            invitation = CandidateInvitation.objects.create(
                assessment=assessment,
                name=name,
                email=email,
                pan_number=pan_number,
                phone=phone,
                start_time=start_time,
                end_time=end_time,
                time_zone=time_zone,
                start_grace_minutes=start_grace_minutes,
                status='draft',
            )

            start_link = f"{frontend_base.rstrip('/')}/take-assessment/{invitation.token}"
            subject = f"{assessment.display_name or assessment.name or 'Assessment'} - Invitation"

            # Read validity mode from payload
            validity_mode = (payload.get('validity_mode') or '').strip() or 'exact_window'

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
                    schedule_text += "  Available: 12:00 AM to 11:59 PM\n"
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
                    schedule_html += (
                        '<tr>'
                        '<td style="padding:6px 16px 6px 0;color:#475569;font-weight:600;">🕐 Available</td>'
                        '<td style="padding:6px 0;">12:00 AM to 11:59 PM</td>'
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
        try:
            inv = CandidateInvitation.objects.select_related('assessment').get(token=token)
        except CandidateInvitation.DoesNotExist:
            return Response({'error': 'Invitation not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Single-use: if already submitted, block further access
        if inv.status == 'submitted':
            return Response({'error': 'Your exam has been completed.'}, status=status.HTTP_409_CONFLICT)

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

        # Start-time window enforcement:
        # - If NOT started yet: candidate can open only between [start_time, start_time + grace]
        # - If already started: do NOT block on grace (allows reconnect/refresh)
        now = timezone.now()
        if inv.started_at is None:
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

            # Compute the extended deadline: end_time + grace_minutes.
            # last_valid_start = extended_deadline - assessment_duration.
            # Only candidates who arrive before last_valid_start can get the full duration.
            # Anyone arriving after last_valid_start is blocked entirely.
            extended_deadline = (end_time + timedelta(minutes=grace_minutes)) if end_time and grace_minutes > 0 else end_time

            # Compute the assessment duration for the cutoff check
            _entry_duration = _hhmmss_to_seconds(getattr(assessment, 'total_time', '') or '')
            if extended_deadline and _entry_duration > 0:
                # Last moment a candidate can start and still get the full duration
                last_valid_start = extended_deadline - timedelta(seconds=_entry_duration)
            else:
                last_valid_start = extended_deadline

            if start_time and now < start_time:
                return Response({'error': 'This exam has not started yet.', 'schedule': _schedule_info}, status=status.HTTP_403_FORBIDDEN)
            # Block if they can no longer get the full assessment duration
            if last_valid_start and now > last_valid_start:
                return Response({'error': 'The start window for this exam has expired.', 'schedule': _schedule_info}, status=status.HTTP_410_GONE)
            # Also block if there is no grace and we are past end_time
            if end_time and not grace_minutes and now >= end_time:
                return Response({'error': 'This assessment link has expired.', 'schedule': _schedule_info}, status=status.HTTP_410_GONE)

        # Compute the extended deadline (end_time + grace) used to cap expires_at.
        # This allows late starters (within grace window) to still use full assessment
        # duration, but hard-stops anyone at the extended deadline.
        _raw_end_time = getattr(inv, 'end_time', None)
        _raw_end_time = _make_aware_if_needed(_raw_end_time)
        _grace = max(0, int(getattr(inv, 'start_grace_minutes', 0) or 0))
        extended_deadline = (_raw_end_time + timedelta(minutes=_grace)) if _raw_end_time and _grace > 0 else _raw_end_time

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
                if extended_deadline:
                    expires_at = min(expires_at, extended_deadline) if expires_at else extended_deadline
                inv.expires_at = expires_at
            else:
                # Ensure existing expires_at is capped by extended deadline (in case schedule changed after start)
                if extended_deadline:
                    if inv.expires_at and inv.expires_at > extended_deadline:
                        inv.expires_at = extended_deadline
                    elif inv.expires_at is None:
                        inv.expires_at = extended_deadline

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
        if not isinstance(answers, dict) or len(answers.keys()) == 0:
            return Response({'error': 'answers must be a non-empty object.'}, status=status.HTTP_400_BAD_REQUEST)

        assessment = inv.assessment
        valid_aq_ids = set(
            AssessmentQuestion.objects.filter(assessment=assessment).values_list('id', flat=True)
        )
        # Filter to only valid question ids
        cleaned = {}
        for k, v in (answers or {}).items():
            try:
                aqid = int(k)
            except Exception:
                continue
            if aqid not in valid_aq_ids:
                continue
            cleaned[str(aqid)] = v

        if not cleaned:
            return Response({'error': 'No valid answers provided.'}, status=status.HTTP_400_BAD_REQUEST)

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
        )
        
        # Store Objective Scores
        submission.objective_score = score
        submission.objective_total = total
        submission.objective_percentage = percentage
        submission.answers = cleaned

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
        
        final_percent = (obj_term + cod_term) / 100.0
            
        submission.score = submission.objective_score + submission.coding_score
        submission.total = submission.objective_total + submission.coding_total
        submission.percentage = round(final_percent)
        submission.final_percentage = final_percent
        
        min_pass = (inv.assessment.min_pass_percentage or 60.0)
        submission.is_qualified = submission.percentage >= min_pass
        submission.result = 'selected' if submission.is_qualified else 'rejected'
        
        submission.save(update_fields=[
            'answers', 
            'objective_score', 'objective_total', 'objective_percentage',
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
            penalty = 10
        elif event_type == 'phone_detection':
            integrity.phone_detections += 1
            penalty = 30
        elif event_type == 'multiface_detection':
            integrity.multiface_detections += 1
            penalty = 15
        elif event_type in ['no_face_detection', 'face_detection_lost']:
            integrity.no_face_detections += 1
            penalty = 5
        else:
            return Response({'error': 'Unknown event type'}, status=status.HTTP_400_BAD_REQUEST)

        # Grace system: first 3 warnings are logged but forgiven
        logs = integrity.warning_logs if isinstance(integrity.warning_logs, list) else []
        logs.append({
            'event_type': event_type,
            'timestamp': timestamp,
            'penalty_applied': penalty
        })
        integrity.warning_logs = logs

        if len(logs) <= 3:
            # Forgive penalty for first three violations
            penalty = 0

        if penalty > 0:
            integrity.integrity_score = max(0.0, integrity.integrity_score - penalty)
        
        # Handle Screenshot if provided
        screenshot_b64 = data.get('screenshot')
        webcam_b64 = data.get('webcam_screenshot')
        
        if screenshot_b64 or webcam_b64:
            try:
                integrity_snap = IntegrityScreenshot(
                    invitation=inv,
                    event_type=event_type,
                    timestamp=timezone.now()
                )
                
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
            'warnings_used': len(logs)
        }, status=status.HTTP_200_OK)

    except CandidateInvitation.DoesNotExist:
        return Response({'error': 'Invitation not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        import traceback
        print("Integrity Error:", traceback.format_exc())
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def _update_submission_scoring_logic(submission):
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
    
    # 4. Update coding fields
    submission.coding_score = int(candidate_total_points)
    submission.coding_total = int(total_possible_points)
    submission.coding_percentage = coding_percentage

    # 5. Combine with Objective (if any)
    # Objective score is already stored in fields (or 0 if none)
    assessment = inv.assessment
    
    # Weighted Scoring Logic
    w_obj = assessment.weightage_objective if assessment.weightage_objective is not None else 50
    w_cod = assessment.weightage_coding if assessment.weightage_coding is not None else 50
    
    if w_obj + w_cod == 0:
        w_obj = 50
        w_cod = 50

    # Calculate final percentage using weights
    obj_term = (submission.objective_percentage * w_obj)
    cod_term = (submission.coding_percentage * w_cod)
    
    final_percentage = (obj_term + cod_term) / 100.0

    final_percentage_rounded = round(final_percentage)
    
    # 6. Update aggregate fields
    submission.score = submission.objective_score + submission.coding_score
    submission.total = submission.objective_total + submission.coding_total
    submission.percentage = final_percentage_rounded
    submission.final_percentage = final_percentage
    
    min_pass = getattr(inv.assessment, 'min_pass_percentage', 60.0) or 60.0
    submission.is_qualified = final_percentage_rounded >= min_pass
    submission.result = 'selected' if submission.is_qualified else 'rejected'


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

        # Check if this specific question was already submitted
        submission = getattr(inv, 'submission', None)
        if submission and submission.answers and f"acq_{acq.id}" in submission.answers:
             return Response({'error': 'This question has already been submitted.'}, status=status.HTTP_400_BAD_REQUEST)

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
                    "result": "selected",
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
                    assessment.shortlisted = int(getattr(assessment, 'shortlisted', 0) or 0) + 1
                    assessment.save(update_fields=['submitted', 'evaluated', 'shortlisted'])
            except Exception:
                pass
            result["submission_id"] = submission.id

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
                "result": "selected",
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

        # Use helper for scoring
        _update_submission_scoring_logic(submission)
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
                    'warning_logs': getattr(inv.integrity, 'warning_logs', []) if hasattr(inv, 'integrity') else []
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

        if company_id:
            scoped_ids = get_scoped_user_ids(user_profile)
            if scoped_ids is None:
                # Application Admin: all results across the company
                qs = CandidateSubmission.objects.filter(
                    invitation__assessment__user_profile__company_id=company_id,
                    is_deleted=False
                ).select_related('invitation', 'invitation__assessment').order_by('-submitted_at')
            else:
                # Role-scoped: only results for assessments in this user's hierarchy
                qs = CandidateSubmission.objects.filter(
                    invitation__assessment__user_profile_id__in=scoped_ids,
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
        
        # Similar logic for AI assessments — exclude ONGOING (not yet submitted)
        ai_qs = AIAssessmentSubmission.objects.select_related('assessment').exclude(status='ONGOING').order_by('-submitted_at')
        
        if start_date:
            ai_qs = ai_qs.filter(submitted_at__date__gte=start_date)
        if end_date:
            ai_qs = ai_qs.filter(submitted_at__date__lte=end_date)

        # Combine and limit
        results = []
        for s in qs[:400]:
            inv = s.invitation
            a = inv.assessment
            results.append(
                {
                    'submission_id': s.id,
                    'submitted_at': s.submitted_at.isoformat() if s.submitted_at else None,
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

                    'status': s.result,
                    'integrity': {
                        'integrity_score': getattr(inv.integrity, 'integrity_score', 100.0) if hasattr(inv, 'integrity') else 100.0,
                        'warning_logs': getattr(inv.integrity, 'warning_logs', []) if hasattr(inv, 'integrity') else []
                    }
                }
            )

        # Re-sort combined results by submitted_at
        results.sort(key=lambda x: str(x['submitted_at'] or ''), reverse=True)

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
        
        # Use centralized helper to handle policy and workflow
        response, handled = handle_deletion_request(
            user_profile=user_profile,
            company=user_profile.company,
            content_type='CandidateSubmission',
            object_id=instance.id,
            object_repr=f"Submission for {instance.invitation.email}",
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
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def candidates_overview_view(request):
    """
    Recruiter overview: list invited candidates and their status.
    Query params:
      - assessment_id: optional
    """
    try:
        user_profile = getattr(request.user, 'profile', None)
        company_id = user_profile.company_id if user_profile and user_profile.company else None

        assessment_id = request.GET.get('assessment_id', None)

        if company_id:
            scoped_ids = get_scoped_user_ids(user_profile)
            if scoped_ids is None:
                # Application Admin: all candidates across the company
                qs = CandidateInvitation.objects.filter(
                    assessment__user_profile__company_id=company_id
                ).select_related('assessment').order_by('-created_at')
            else:
                # Role-scoped: only candidates for assessments in this user's hierarchy
                qs = CandidateInvitation.objects.filter(
                    assessment__user_profile_id__in=scoped_ids
                ).select_related('assessment').order_by('-created_at')
        else:
            qs = CandidateInvitation.objects.none()

        # Date filtering
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')

        if start_date:
            qs = qs.filter(created_at__date__gte=start_date)
        if end_date:
            qs = qs.filter(created_at__date__lte=end_date)

        if assessment_id:
            try:
                qs = qs.filter(assessment_id=int(assessment_id))
            except Exception:
                return Response({'error': 'assessment_id must be an integer.'}, status=status.HTTP_400_BAD_REQUEST)

        qs = qs[:500]
        results = []
        for inv in qs:
            sub = getattr(inv, 'submission', None)
            results.append(
                {
                    'id': inv.id,
                    'name': inv.name,
                    'email': inv.email,
                    'pan_number': inv.pan_number,
                    'phone': inv.phone,
                    'status': inv.status,
                    'token': str(inv.token),
                    'created_at': inv.created_at.isoformat() if inv.created_at else None,
                    'started_at': inv.started_at.isoformat() if getattr(inv, 'started_at', None) else None,
                    'expires_at': inv.expires_at.isoformat() if getattr(inv, 'expires_at', None) else None,
                    'submitted_at': sub.submitted_at.isoformat() if sub and sub.submitted_at else None,
                    'submission_id': sub.id if sub else None,
                    'rating': getattr(sub, 'rating', None) if sub else None,
                    'score': sub.score if sub else 0,
                    'total_score': sub.total if sub else 0,
                    'final_percentage': sub.final_percentage if sub else 0,
                    'result': sub.result if sub else None,
                    'is_qualified': sub.is_qualified if sub else False,
                    'assessment': {
                        'id': inv.assessment_id,
                        'display_name': inv.assessment.display_name,
                        'name': inv.assessment.name,
                    } if inv.assessment_id else None,
                }
            )

        # Merge results from Resume Matcher (ai_candidates) if no assessment filter is applied
        if not assessment_id:
            try:
                # SECURITY FIX: Scope AI candidates to the requester's company only
                # The `company` FK already exists on Candidate model (migration 0020)
                if company_id:
                    ai_qs = Candidate.objects.filter(
                        company_id=company_id
                    ).order_by('-submission_date')
                else:
                    ai_qs = Candidate.objects.none()
                if start_date:
                    ai_qs = ai_qs.filter(submission_date__date__gte=start_date)
                if end_date:
                    ai_qs = ai_qs.filter(submission_date__date__lte=end_date)
                
                ai_cands = ai_qs[:50]

                for cand in ai_cands:
                    results.append({
                        'id': cand.id,
                        'name': cand.full_name,
                        'email': cand.email,
                        'pan_number': None,
                        'phone': None,
                        'status': cand.status,
                        'token': None,
                        'created_at': cand.submission_date.isoformat() if cand.submission_date else None,
                        'started_at': cand.submission_date.isoformat() if cand.submission_date else None,
                        'expires_at': None,
                        'submitted_at': None,
                        'submission_id': None,
                        'rating': None,
                        'score': 0,
                        'total_score': 0,
                        'final_percentage': 0,
                        'result': None,
                        'is_qualified': False,
                        'assessment': {
                            'id': 0,
                            'display_name': cand.job_title,
                            'name': cand.job_title,
                        }
                    })
                
                # Re-sort combined results by created_at date
                def get_date(item):
                    return item.get('created_at') or ''
                results.sort(key=get_date, reverse=True)
            except Exception as e:
                print(f"Error merging ai_candidates: {e}")

        return Response({'count': len(results), 'results': results}, status=status.HTTP_200_OK)
    except Exception as e:
        import traceback
        print(f"Error in candidates_overview_view: {str(e)}")
        print(traceback.format_exc())
        return Response({'error': f'An error occurred while fetching candidates: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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

        if inv.status == 'submitted':
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
        submission, created = CandidateSubmission.objects.get_or_create(invitation=inv)
        submission.objective_score = score
        submission.objective_total = total_obj_questions
        submission.objective_percentage = round(percentage, 2)
        submission.answers = answers # Store current state
        submission.save()
        
        from api.models import AssessmentCodingQuestion
        has_coding = AssessmentCodingQuestion.objects.filter(assessment=assessment).exists()

        # Check Cutoff
        passed = True
        next_stage = 'coding' if has_coding else 'finish'
        message = "Objective section completed."
        
        if assessment.has_objective_cutoff:
            cutoff = assessment.min_objective_pass_percentage
            if percentage < cutoff:
                passed = False
                message = "You did not meet the minimum requirement for the objective section."
                next_stage = 'finish'
                # Mark as submitted/failed immediately
                inv.status = 'submitted'
                inv.save()
                
                # Update final result
                submission.result = 'rejected'
                submission.is_qualified = False
                
                # Recalculate final percentage using existing logic
                _update_submission_scoring_logic(submission)
                submission.save()
            else:
                passed = True
                if has_coding:
                    message = "Objective cutoff passed. Proceeding to coding section."
                    next_stage = 'coding'
                else:
                    message = "Objective section completed."
                    next_stage = 'finish'
                    # Mark as submitted immediately
                    inv.status = 'submitted'
                    inv.save()

                # Even if passed, update scoring so partial results are correct
                _update_submission_scoring_logic(submission)
                submission.save()
        else:
            # If no cutoff, still update scoring for partial results
            if not has_coding:
                next_stage = 'finish'
                message = "Objective section completed."
                # Mark as submitted immediately
                inv.status = 'submitted'
                inv.save()
            else:
                next_stage = 'coding'
                message = "Objective section completed. Proceeding to coding section."

            _update_submission_scoring_logic(submission)
            submission.save()
        
        # Reload to get updated fields from _update_submission_scoring_logic
        submission.refresh_from_db()

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
def save_candidate_details_view(request):
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
        if not token:
            return Response(
                {'error': 'Token is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate token exists in CandidateInvitation
        try:
            invitation = CandidateInvitation.objects.get(token=token)
        except CandidateInvitation.DoesNotExist:
            return Response(
                {'error': 'Invalid token'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Extract data
        first_name = request.data.get('first_name', '').strip()
        last_name = request.data.get('last_name', '').strip()
        email = request.data.get('email', '').strip()
        phone = request.data.get('phone', '').strip()
        pan_number = request.data.get('pan_number', '').strip().upper()
        snapshot = request.data.get('snapshot', '').strip()
        pan_file = request.FILES.get('pan_file')

        # Validation
        if not all([first_name, last_name, email, phone, pan_number, snapshot]):
            return Response(
                {'error': 'All fields are required: first_name, last_name, email, phone, pan_number, snapshot'},
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

