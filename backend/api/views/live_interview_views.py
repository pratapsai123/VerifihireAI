from .._imports import *
import datetime

@api_view(['POST'])
@permission_classes([AllowAny])
def create_interview_invitations_and_send_email_view(request):
    """
    Send emails for existing draft interview invitations.
    
    Body:
    {
      "draft_ids": [1, 2, 3],
      "interview_name": "Optional interview name" (defaults to "Interview")
    }
    """
    try:
        data = request.data or {}
        draft_ids = data.get('draft_ids', [])
        interview_name = data.get('interview_name', 'Interview').strip() or 'Interview'
        
        if not isinstance(draft_ids, list) or len(draft_ids) == 0:
            return Response({'error': 'draft_ids must be a non-empty array of IDs.'}, status=status.HTTP_400_BAD_REQUEST)

        # Retrieve global schedule settings if provided
        global_start_time_raw = data.get('start_time')
        global_end_time_raw = data.get('end_time')
        global_time_zone = data.get('time_zone')
        global_start_grace_minutes = data.get('start_grace_minutes', 0)
        
        from django.utils.dateparse import parse_datetime

        # Get or create a default interview (or create one per batch)
        # For simplicity, we'll create one interview per batch of invites
        req_user_profile = getattr(request.user, 'profile', None) if hasattr(request, 'user') and request.user.is_authenticated else None
        interview = Interview.objects.create(
            name=interview_name,
            description=f'Interview created on {timezone.now().strftime("%Y-%m-%d %H:%M:%S")}',
            company=req_user_profile.company if req_user_profile else None,
            created_by=req_user_profile,
        )

        frontend_base = getattr(settings, 'FRONTEND_BASE_URL', None) or os.environ.get('FRONTEND_BASE_URL') or 'https://verifihireai.com'

        results = []
        sent_count = 0
        fail_count = 0

        drafts = InterviewInvitation.objects.filter(id__in=draft_ids, status='draft')

        for invitation in drafts:
            # Associate the draft with this new interview
            invitation.interview = interview
            
            if global_start_time_raw:
                invitation.start_time = parse_datetime(global_start_time_raw)
            if global_end_time_raw:
                invitation.end_time = parse_datetime(global_end_time_raw)
            if global_time_zone:
                invitation.time_zone = global_time_zone
            invitation.start_grace_minutes = int(global_start_grace_minutes)

            invitation.status = 'sent'
            invitation.save()

            name = invitation.name
            email = invitation.email
            interviewer_name = invitation.interviewer_name
            interviewer_email = invitation.interviewer_email
            
            start_time = invitation.start_time
            end_time = invitation.end_time
            time_zone = invitation.time_zone
            
            # Read validity mode from payload
            validity_mode = (data.get('validity_mode') or '').strip() or 'exact_window'
            
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

            interview_link = f"{frontend_base.rstrip('/')}/live-interview?token={invitation.token}"
            interviewer_link = f"{frontend_base.rstrip('/')}/live-interview-interviewer?token={invitation.token}"
            subject = f"Interview Invitation - {interview_name}"

            # Build schedule blocks based on validity mode
            if validity_mode == 'exact_window':
                display_date = local_start.strftime('%B %d, %Y') if local_start else ''
                display_start_time = local_start.strftime('%I:%M %p') if local_start else ''
                display_end_time = local_end.strftime('%I:%M %p') if local_end else ''

                schedule_text = ''
                if display_date:
                    schedule_text = (
                        f"Date: {display_date}\n"
                        f"Start Time: {display_start_time}\n"
                    )
                    if display_end_time:
                        schedule_text += f"End Time: {display_end_time}\n"
                    if display_tz:
                        schedule_text += f"Time Zone: {display_tz}\n"

                schedule_html = ''
                if display_date:
                    schedule_html = '<table style="border-collapse:collapse;width:100%;">'
                    schedule_html += (
                        '<tr>'
                        '<td style="padding:6px 16px 6px 0;color:#475569;font-weight:600;">📅 Date</td>'
                        f'<td style="padding:6px 0;">{display_date}</td>'
                        '</tr>'
                        '<tr>'
                        '<td style="padding:6px 16px 6px 0;color:#475569;font-weight:600;">🕐 Start Time</td>'
                        f'<td style="padding:6px 0;">{display_start_time}</td>'
                        '</tr>'
                    )
                    if display_end_time:
                        schedule_html += (
                            '<tr>'
                            '<td style="padding:6px 16px 6px 0;color:#475569;font-weight:600;">🕐 End Time</td>'
                            f'<td style="padding:6px 0;">{display_end_time}</td>'
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
                display_start_date = local_start.strftime('%B %d, %Y') if local_start else ''
                display_end_date = local_end.strftime('%B %d, %Y') if local_end else ''

                schedule_text = ''
                if display_start_date:
                    schedule_text = f"Start Date: {display_start_date}\n"
                    if display_end_date and display_end_date != display_start_date:
                        schedule_text += f"End Date: {display_end_date}\n"
                    if display_tz:
                        schedule_text += f"Time Zone: {display_tz}\n"

                schedule_html = ''
                if display_start_date:
                    schedule_html = '<table style="border-collapse:collapse;width:100%;">'
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
                f"You have been invited to participate in a live interview.\n\n"
                f"Interview: {interview_name}\n"
            )
            if schedule_text:
                text_body += f"\n{schedule_text}"
            text_body += (
                f"\nJoin Interview Link: {interview_link}\n\n"
                "Please join the interview at the scheduled time.\n\n"
                "Best regards,\n"
                "VerifiHireAI Team"
            )

            html_body = f"""
                <div style="font-family: Arial, sans-serif; line-height: 1.6; color: #111; max-width: 600px;">
                  <h2 style="color: #2563eb;">Interview Invitation</h2>
                  <p>Hi <strong>{name}</strong>,</p>
                  <p>You have been invited to participate in a live interview.</p>
                  
                  <div style="background: #f8fafc; padding: 16px; border-radius: 8px; margin: 20px 0;">
                    <p style="margin: 8px 0;"><strong>Interview:</strong> {interview_name}</p>
                    {schedule_html}
                  </div>
                  
                  <p style="margin: 24px 0;">
                    <a href="{interview_link}" target="_blank"
                       style="background:#2563eb;color:#fff;padding:14px 24px;border-radius:10px;text-decoration:none;font-weight:700;display:inline-block;">
                      Join Interview
                    </a>
                  </p>
                  
                  <p style="font-size:12px;color:#475569;margin-top:24px;">
                    If the button doesn't work, copy this link:<br/>
                    <a href="{interview_link}" style="color:#2563eb;word-break:break-all;">{interview_link}</a>
                  </p>
                  
                  <p style="margin-top:24px;color:#64748b;font-size:14px;">
                    Best regards,<br/>
                    <strong>VerifiHireAI Team</strong>
                  </p>
                </div>
            """

            try:
                # 1. Send Email to Candidate
                msg = EmailMultiAlternatives(
                    subject=subject,
                    body=text_body,
                    from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', None),
                    to=[email],
                )
                msg.attach_alternative(html_body, "text/html")
                msg.send(fail_silently=False)
                
                # 2. Send Email to Interviewer
                if interviewer_email:
                    int_subject = f"Live Interview Assignment - {interview_name}"
                    int_text = (
                        f"Hi {interviewer_name or 'Interviewer'},\n\n"
                        f"You have been assigned to conduct a live interview with {name} ({email}).\n\n"
                        f"Interview: {interview_name}\n"
                    )
                    if schedule_text:
                        int_text += f"\n{schedule_text}"
                    int_text += (
                        f"\nInterviewer Link: {interviewer_link}\n\n"
                        "Please join the room at the scheduled time.\n\n"
                        "Best regards,\nVerifiHireAI"
                    )
                    
                    int_html = f"""
                    <div style="font-family: Arial, sans-serif; line-height: 1.6; color: #111; max-width: 600px;">
                        <h2 style="color: #2563eb;">Live Interview Assignment</h2>
                        <p>Hi <strong>{interviewer_name or 'Interviewer'}</strong>,</p>
                        <p>You have been assigned to conduct a live interview with <strong>{name}</strong> ({email}).</p>
                        <div style="background: #f8fafc; padding: 16px; border-radius: 8px; margin: 20px 0;">
                            <p style="margin: 8px 0;"><strong>Interview:</strong> {interview_name}</p>
                            {schedule_html}
                        </div>
                        <p style="margin: 24px 0;">
                            <a href="{interviewer_link}" target="_blank"
                               style="background:#059669;color:#fff;padding:14px 24px;border-radius:10px;text-decoration:none;font-weight:700;display:inline-block;">
                            Join as Interviewer
                            </a>
                        </p>
                    </div>
                    """
                    msg_int = EmailMultiAlternatives(
                        subject=int_subject,
                        body=int_text,
                        from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', None),
                        to=[interviewer_email],
                    )
                    msg_int.attach_alternative(int_html, "text/html")
                    msg_int.send(fail_silently=False)

                invitation.status = 'sent'
                invitation.last_error = None
                invitation.save(update_fields=['status', 'last_error', 'updated_at', 'interview'])
                sent_count += 1
            except Exception as mail_err:
                invitation.status = 'failed'
                invitation.last_error = str(mail_err)
                invitation.save(update_fields=['status', 'last_error', 'updated_at', 'interview'])
                fail_count += 1

            results.append(
                {
                    'id': invitation.id,
                    'name': invitation.name,
                    'email': invitation.email,
                    'interviewer_name': invitation.interviewer_name,
                    'interviewer_email': invitation.interviewer_email,
                    'pan_number': invitation.pan_number,
                    'phone': invitation.phone,
                    'token': str(invitation.token),
                    'status': invitation.status,
                    'interview_link': interview_link,
                    'interviewer_link': f"{frontend_base.rstrip('/')}/live-interview-interviewer?token={invitation.token}",
                    'error': invitation.last_error,
                }
            )

        return Response(
            {
                'message': 'Interview invitations processed.',
                'sent': sent_count,
                'failed': fail_count,
                'results': results,
            },
            status=status.HTTP_200_OK if fail_count == 0 else status.HTTP_207_MULTI_STATUS
        )
    except Exception as e:
        import traceback
        print(f"Error in create_interview_invitations_and_send_email_view: {str(e)}")
        print(traceback.format_exc())
        return Response({'error': f'An error occurred while sending invitations: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def interview_invitations_overview_view(request):
    """
    Overview: list interview invitations and their status.
    Query params:
      - interview_id: optional filter by interview
    """
    try:
        user_profile = getattr(request.user, 'profile', None)
        company_id = user_profile.company_id if user_profile and user_profile.company else None

        interview_id = request.GET.get('interview_id', None)
        if company_id:
            scoped_ids = get_scoped_user_ids(user_profile)
            if scoped_ids is None:
                # Application Admin: all interviews for the company
                qs = InterviewInvitation.objects.filter(
                    (models.Q(interview__company_id=company_id) |
                     models.Q(interview__created_by__company_id=company_id) |
                     models.Q(interviewer_email=user_profile.email)),
                    is_deleted=False
                ).select_related('interview').order_by('-created_at').distinct()
            else:
                # Role-scoped: interviews created by users in hierarchy OR where user is the interviewer
                qs = InterviewInvitation.objects.filter(
                    (models.Q(interview__created_by_id__in=scoped_ids) |
                     models.Q(interviewer_email=user_profile.email)),
                    is_deleted=False
                ).select_related('interview').order_by('-created_at').distinct()
        else:
            qs = InterviewInvitation.objects.none()
        if interview_id:
            try:
                qs = qs.filter(interview_id=int(interview_id))
            except Exception:
                return Response({'error': 'interview_id must be an integer.'}, status=status.HTTP_400_BAD_REQUEST)

        qs = qs[:500]
        results = []
        for inv in qs:
            feedback = getattr(inv, 'feedback', None)
            results.append(
                {
                    'id': inv.id,
                    'name': inv.name,
                    'email': inv.email,
                    'interviewer_name': inv.interviewer_name,
                    'interviewer_email': inv.interviewer_email,
                    'pan_number': inv.pan_number,
                    'phone': inv.phone,
                    'status': inv.status,
                    'token': str(inv.token),
                    'start_time': inv.start_time.isoformat() if inv.start_time else None,
                    'end_time': inv.end_time.isoformat() if inv.end_time else None,
                    'time_zone': inv.time_zone,
                    'start_grace_minutes': inv.start_grace_minutes,
                    'created_at': inv.created_at.isoformat() if inv.created_at else None,
                    'updated_at': inv.updated_at.isoformat() if inv.updated_at else None,
                    'interview': {
                        'id': inv.interview_id,
                        'name': inv.interview.name if inv.interview else None,
                        'description': inv.interview.description if inv.interview else None,
                    } if inv.interview_id else None,
                    'feedback': {
                        'interviewer_feedback': feedback.interviewer_feedback,
                        'interviewer_rating': feedback.interviewer_rating,
                        'interviewer_technical_rating': feedback.interviewer_technical_rating,
                        'interviewer_communication_rating': feedback.interviewer_communication_rating,
                        'interviewer_team_fit_rating': feedback.interviewer_team_fit_rating,
                        'interviewer_average_rating': feedback.interviewer_average_rating,
                        'candidate_feedback': feedback.candidate_feedback,
                        'candidate_rating': feedback.candidate_rating,
                        'updated_at': feedback.updated_at.isoformat() if feedback.updated_at else None,
                    } if feedback else None
                }
            )

        return Response({'count': len(results), 'results': results}, status=status.HTTP_200_OK)
    except Exception as e:
        import traceback
        print(f"Error in interview_invitations_overview_view: {str(e)}")
        print(traceback.format_exc())
        return Response({'error': f'An error occurred while fetching interview invitations: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['GET'])
@permission_classes([AllowAny])
def get_interview_invitation_by_token_view(request, token):
    """
    Get interview invitation details by token.
    """
    try:
        try:
            invitation = InterviewInvitation.objects.select_related('interview').get(token=token)
        except InterviewInvitation.DoesNotExist:
            return Response({'error': 'Interview invitation not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        return Response({
            'id': invitation.id,
            'name': invitation.name,
            'email': invitation.email,
            'interviewer_name': invitation.interviewer_name,
            'interviewer_email': invitation.interviewer_email,
            'pan_number': invitation.pan_number,
            'phone': invitation.phone,
            'status': invitation.status,
            'token': str(invitation.token),
            'start_time': invitation.start_time.isoformat() if invitation.start_time else None,
            'end_time': invitation.end_time.isoformat() if invitation.end_time else None,
            'time_zone': invitation.time_zone,
            'start_grace_minutes': invitation.start_grace_minutes,
            'created_at': invitation.created_at.isoformat() if invitation.created_at else None,
            'interview': {
                'id': invitation.interview_id,
                'name': invitation.interview.name if invitation.interview else None,
                'description': invitation.interview.description if invitation.interview else None,
            } if invitation.interview_id else None,
        }, status=status.HTTP_200_OK)
    except Exception as e:
        import traceback
        print(f"Error in get_interview_invitation_by_token_view: {str(e)}")
        print(traceback.format_exc())
        return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




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


@api_view(['GET'])
@permission_classes([AllowAny])
@csrf_exempt
def get_candidate_details_view(request, token):
    """
    Get candidate details for a given token.
    """
    try:
        candidate_details = CandidateDetails.objects.get(token=token)
        
        return Response({
            'success': True,
            'data': {
                'id': candidate_details.id,
                'first_name': candidate_details.first_name,
                'last_name': candidate_details.last_name,
                'email': candidate_details.email,
                'phone': candidate_details.phone,
                'pan_number': candidate_details.pan_number,
                'pan_file': candidate_details.pan_file.url if candidate_details.pan_file else None,
                'snapshot': candidate_details.snapshot,
                'created_at': candidate_details.created_at.isoformat(),
                'updated_at': candidate_details.updated_at.isoformat(),
            }
        }, status=status.HTTP_200_OK)

    except CandidateDetails.DoesNotExist:
        return Response(
            {'error': 'Candidate details not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': f'Failed to retrieve candidate details: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def verify_pan_backend_view(request):
    """
    Verify PAN number against uploaded image using backend OCR (pytesseract).
    Expected request body:
    - pan_number: string
    - pan_file: file (image)
    """
    try:
        data = request.data
        pan_number = data.get('pan_number', '').strip().upper()
        # Handle file upload properly
        pan_file = request.FILES.get('pan_file')

        if not pan_number:
            return Response({'error': 'PAN number is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not pan_file:
            return Response({'error': 'PAN file is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Basic validation of PAN format
        if not re.match(r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$', pan_number):
             return Response({'error': 'Invalid PAN number format'}, status=status.HTTP_400_BAD_REQUEST)

        # Check file type
        if not pan_file.content_type.startswith('image/'):
            return Response({'error': 'File must be an image for OCR verification'}, status=status.HTTP_400_BAD_REQUEST)

        # Perform OCR
        extracted_text, success = extract_text_from_image(pan_file)

        # Clean extracted text for comparison
        clean_extracted = re.sub(r'[^A-Z0-9]', '', extracted_text.upper())

        if success:
             # Strict check: Extracted PAN must match Input PAN
             extracted_clean = extracted_text.replace(" ", "").upper()
             if pan_number == extracted_clean:
                 return Response({
                    'success': True, 
                    'verified': True, 
                    'message': 'PAN verification successful',
                    'extracted_pan': extracted_text
                }, status=status.HTTP_200_OK)

        # Fallback: Check if input PAN exists anywhere in the full extracted text (fuzzy match)
        if pan_number in clean_extracted:
             return Response({
                'success': True, 
                'verified': True, 
                'message': 'PAN verified (fuzzy match)',
                'extracted_pan': pan_number
            }, status=status.HTTP_200_OK)

        return Response({
            'success': True, 
            'verified': False, 
            'message': 'PAN verification failed. Extracted text did not match.',
            'debug_info': clean_extracted[:100]
        }, status=status.HTTP_200_OK)

    except Exception as e:
        print(f"Backend PAN Verification Error: {e}")
        return Response({
            'error': f'Verification processing failed: {str(e)}',
            'success': False
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_candidate_report_view(request, submission_id: int):
    """
    Download a comprehensive PDF report for a candidate submission.
    Includes: personal info, results, PAN card, objective answers, coding answers.
    """
    try:
        response = generate_candidate_report(submission_id)
        if response is None:
            return Response(
                {'error': 'Submission not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        return response
    except Exception as e:
        import traceback
        print(f"Error in download_candidate_report_view: {str(e)}")
        print(traceback.format_exc())
        return Response(
            {'error': f'Failed to generate report: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def submit_interview_feedback(request):
    """
    Submit feedback after a live interview.
    Handles both candidate and interviewer feedback.
    payload: {
        "token": "uuid",
        "feedback": "text",
        "rating": int (1-5),
        "role": "interviewer" | "candidate" (optional, default candidate)
    }
    """
    import uuid
    print(f"DEBUG: submit_interview_feedback called. Data: {request.data}")
    
    token = request.data.get('token')
    feedback_text = request.data.get('feedback')
    rating = request.data.get('rating')  # Legacy/Overall
    tech_rating = request.data.get('technical_rating')
    comm_rating = request.data.get('communication_rating')
    fit_rating = request.data.get('team_fit_rating')
    role = request.data.get('role', 'candidate')

    if not token or not feedback_text:
        return Response({'error': 'Token and feedback are required.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Validate UUID
        try:
            uuid_token = uuid.UUID(str(token))
        except ValueError:
             print(f"DEBUG: Invalid token format: {token}")
             return Response({'error': 'Invalid token format.'}, status=status.HTTP_400_BAD_REQUEST)

        # Try finding invitation by token
        invitation = InterviewInvitation.objects.filter(token=uuid_token).first()
        
        if not invitation:
            print(f"DEBUG: No invitation found for token: {token}")
            return Response({'error': 'Invalid token.'}, status=status.HTTP_404_NOT_FOUND)

        # Check if feedback object exists
        from api.models import LiveInterviewFeedback
        feedback_obj, created = LiveInterviewFeedback.objects.get_or_create(invitation=invitation)
        print(f"DEBUG: Feedback object {'created' if created else 'found'}: {feedback_obj}")

        if role == 'interviewer':
            feedback_obj.interviewer_feedback = feedback_text
            
            # Save individual ratings
            try:
                if rating: feedback_obj.interviewer_rating = int(rating)
                if tech_rating: feedback_obj.interviewer_technical_rating = int(tech_rating)
                if comm_rating: feedback_obj.interviewer_communication_rating = int(comm_rating)
                if fit_rating: feedback_obj.interviewer_team_fit_rating = int(fit_rating)
                
                # Calculate average if all three are present
                ratings_list = []
                if tech_rating: ratings_list.append(int(tech_rating))
                if comm_rating: ratings_list.append(int(comm_rating))
                if fit_rating: ratings_list.append(int(fit_rating))
                
                if ratings_list:
                    feedback_obj.interviewer_average_rating = sum(ratings_list) / len(ratings_list)
            except (ValueError, TypeError):
                pass
        else:
            # Default to candidate
            feedback_obj.candidate_feedback = feedback_text
            if rating:
                try:
                    feedback_obj.candidate_rating = int(rating)
                except ValueError:
                    pass
        
        feedback_obj.save()
        print(f"DEBUG: Feedback saved successfully for role: {role}")

        # Mark the invitation as completed when the interviewer submits feedback
        if role == 'interviewer':
            invitation.status = 'completed'
            invitation.save(update_fields=['status', 'updated_at'])
            print(f"DEBUG: Invitation {invitation.id} status updated to 'completed'")

        return Response({'success': True, 'message': 'Feedback submitted successfully.'}, status=status.HTTP_200_OK)

    except Exception as e:
        import traceback
        print(f"Error submitting feedback: {e}")
        print(traceback.format_exc())
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
@csrf_exempt
@api_view(['GET', 'POST', 'DELETE'])
@permission_classes([AllowAny])
def draft_interview_invitations_view(request, draft_id=None):
    """
    CRUD endpoint for Draft Candidate Invitations.
    """
    try:
        user_profile = getattr(request.user, 'profile', None)
        company_id = user_profile.company_id if user_profile and user_profile.company else None

        if request.method == 'GET':
            if company_id:
                # InterviewInvitation has no company field; isolate via the Interview's company.
                # Also cover legacy data where interview.created_by is in this company.
                qs = InterviewInvitation.objects.filter(
                    models.Q(status='draft') &
                    (
                        models.Q(interview__company_id=company_id) |
                        models.Q(interview__created_by__company_id=company_id) |
                        models.Q(interview__isnull=True)  # truly orphan drafts
                    )
                ).order_by('-created_at')
            else:
                qs = InterviewInvitation.objects.none()
            results = []
            for inv in qs:
                results.append(
                    {
                        'id': inv.id,
                        'name': inv.name,
                        'email': inv.email,
                        'interviewer_name': inv.interviewer_name,
                        'interviewer_email': inv.interviewer_email,
                        'pan_number': inv.pan_number,
                        'phone': inv.phone,
                        'status': inv.status,
                        'token': str(inv.token),
                    }
                )
            return Response({'count': len(results), 'results': results}, status=status.HTTP_200_OK)
            
        elif request.method == 'POST':
            data = request.data or {}
            
            # Allow bulk insert or single insert
            candidates = data.get('candidates', [data]) if 'candidates' in data else [data]
            
            created_drafts = []
            for payload in candidates:
                name = (payload.get('name') or '').strip()
                email = (payload.get('email') or '').strip().lower()
                interviewer_name = (payload.get('interviewer_name') or '').strip()
                interviewer_email = (payload.get('interviewer_email') or '').strip().lower()
                pan_number = (payload.get('pan_number') or payload.get('pan') or '').strip().upper() or None
                phone = (payload.get('phone') or '').strip() or None
                
                # Time handling
                start_time_raw = (payload.get('start_time') or '').strip() or None
                end_time_raw = (payload.get('end_time') or '').strip() or None
                time_zone = (payload.get('time_zone') or '').strip() or None
                try:
                    start_grace_minutes = int(payload.get('start_grace_minutes', 0))
                except Exception:
                    start_grace_minutes = 0

                start_time = parse_datetime(start_time_raw) if start_time_raw else None
                end_time = parse_datetime(end_time_raw) if end_time_raw else None

                if not name or not email:
                    continue  # Skip invalid

                invitation = InterviewInvitation.objects.create(
                    name=name,
                    email=email,
                    interviewer_name=interviewer_name,
                    interviewer_email=interviewer_email,
                    pan_number=pan_number,
                    phone=phone,
                    start_time=start_time,
                    end_time=end_time,
                    time_zone=time_zone,
                    start_grace_minutes=max(0, start_grace_minutes),
                    status='draft',
                    # Note: InterviewInvitation has no company field directly;
                    # company isolation is via interview__company_id
                )
                
                created_drafts.append({
                    'id': invitation.id,
                    'name': invitation.name,
                    'email': invitation.email,
                    'interviewer_name': invitation.interviewer_name,
                    'interviewer_email': invitation.interviewer_email,
                    'pan_number': invitation.pan_number,
                    'phone': invitation.phone,
                    'token': str(invitation.token),
                    'status': invitation.status
                })

            return Response({'message': 'Draft(s) saved', 'results': created_drafts}, status=status.HTTP_201_CREATED)
            
        elif request.method == 'DELETE':
            if draft_id is None:
                return Response({'error': 'Draft ID is required for deletion'}, status=status.HTTP_400_BAD_REQUEST)
                
            draft = InterviewInvitation.objects.filter(id=draft_id, status='draft', interview__company_id=company_id).first()
            if not draft:
                return Response({'error': 'Draft not found'}, status=status.HTTP_404_NOT_FOUND)
                
            # Use centralized helper to handle policy and workflow
            response, handled = handle_deletion_request(
                user_profile=user_profile,
                company=user_profile.company,
                content_type='InterviewInvitation',
                object_id=draft.id,
                object_repr=f"Interview Draft for {draft.name} ({draft.email})",
                reason=request.data.get('reason')
            )
            
            if handled:
                return response

            draft.delete()
            return Response({'message': 'Draft deleted successfully'}, status=status.HTTP_204_NO_CONTENT)


    except Exception as e:
        import traceback
        print(f"Error in draft_interview_invitations_view: {str(e)}")
        print(traceback.format_exc())
        return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_all_interviewer_slots_view(request):
    """
    Admin/HR utility to generate slots for all assigned interviewers of an assessment.
    Query params/Body: { "assessment_id": 12, "days": 7 }
    """
    from api.utils.slot_utils import generate_slots_for_interviewer
    
    assessment_id = request.data.get('assessment_id')
    interviewer_ids = request.data.get('interviewer_ids', [])
    days = int(request.data.get('days', 5))
    
    try:
        assessment = Assessment.objects.get(id=assessment_id)
    except Assessment.DoesNotExist:
        return Response({'error': 'Assessment not found'}, status=404)
        
    # Update assignments if provided
    if interviewer_ids:
        assessment.assigned_interviewers.set(interviewer_ids)
        
    interviewers = assessment.assigned_interviewers.all()
    if not interviewers.exists():
        # Fallback: maybe the HR who created it?
        interviewers = [assessment.user_profile] if assessment.user_profile else []
        
    total_slots = 0
    start_date = timezone.now().date()
    
    for interviewer in interviewers:
        count = generate_slots_for_interviewer(interviewer, start_date, days)
        total_slots += count
        
    return Response({
        'success': True,
        'message': f'Generated {total_slots} slots for {len(interviewers)} interviewers.',
    })

@api_view(['GET'])
@permission_classes([AllowAny])
def get_available_slots_view(request, token):
    """
    Dynamically generates 45-minute slots based on interviewer availability windows.
    Subtracts existing booked/reserved slots to show real-time "Effective Availability".
    """
    try:
        inv = CandidateInvitation.objects.get(token=token)
        assessment = inv.assessment
        
        # 1. Assigned Pool
        interviewer_ids = assessment.assigned_interviewers.values_list('id', flat=True)
        now = timezone.now()
        
        # Check if this invitation already has a confirmed booking
        booked_slot = InterviewSlot.objects.filter(invitation=inv, status=InterviewSlot.STATUS_BOOKED).first()
        if booked_slot:
            return Response({
                'success': True,
                'already_booked': True,
                'booking_details': {
                    'date': booked_slot.slot_date.isoformat(),
                    'time': f"{booked_slot.start_time.strftime('%I:%M %p')} - {booked_slot.end_time.strftime('%I:%M %p')}",
                    'interviewer': booked_slot.interviewer.first_name or booked_slot.interviewer.email
                }
            })
        
        # Enforce 3-day lead time (72 hours prep buffer)
        today = now.date()
        min_booking_date = (now + datetime.timedelta(days=3)).date()

        # 2. Reservation Cleanup
        InterviewSlot.objects.filter(
            status=InterviewSlot.STATUS_RESERVED,
            reservation_expiry_time__lt=now
        ).update(
            status=InterviewSlot.STATUS_AVAILABLE,
            reserved_by_token=None,
            reservation_expiry_time=None
        )

        # 3. Get Windows & Existing Slots
        windows = InterviewerAvailability.objects.filter(
            interviewer_id__in=interviewer_ids,
            date__gte=min_booking_date
        ).select_related('interviewer')

        all_real_slots = InterviewSlot.objects.filter(
            interviewer_id__in=interviewer_ids,
            slot_date__gte=min_booking_date
        )

        # 4. Generate Combined Map
        # Key: (date_str, start_time_str) -> one slot object
        slots_map = {}

        for win in windows:
            curr_dt = datetime.datetime.combine(win.date, win.start_time)
            end_dt = datetime.datetime.combine(win.date, win.end_time)
            
            slot_duration = 50
            break_duration = 10
            step = slot_duration + break_duration

            while curr_dt + datetime.timedelta(minutes=slot_duration) <= end_dt:
                slot_date = curr_dt.date()
                slot_start = curr_dt.time()
                slot_end = (curr_dt + datetime.timedelta(minutes=slot_duration)).time()
                
                # Check overlapping slots that ARE booked or reserved (by others)
                is_busy = all_real_slots.filter(
                    interviewer=win.interviewer,
                    slot_date=slot_date,
                    start_time__lt=slot_end,
                    end_time__gt=slot_start,
                    status__in=[InterviewSlot.STATUS_BOOKED, InterviewSlot.STATUS_RESERVED]
                ).exclude(
                    status=InterviewSlot.STATUS_RESERVED,
                    reserved_by_token=str(token)
                ).exists()

                if not is_busy:
                    key = (slot_date.isoformat(), slot_start.strftime('%H:%M'))
                    if key not in slots_map:
                        # Check if a REAL slot already exists for THIS specific start time
                        # to reuse its ID (helps with frontend consistency)
                        existing = all_real_slots.filter(
                            interviewer=win.interviewer,
                            slot_date=slot_date,
                            start_time=slot_start,
                            status=InterviewSlot.STATUS_AVAILABLE
                        ).first()

                        slots_map[key] = {
                            'id': str(existing.id) if existing else f"dynamic_{slot_date.isoformat()}_{slot_start.strftime('%H%M')}",
                            'date': slot_date.isoformat(),
                            'start_time': slot_start.strftime('%I:%M %p'),
                            'end_time': slot_end.strftime('%I:%M %p'),
                            'status': 'available',
                            'is_mine': False
                        }
                
                curr_dt += datetime.timedelta(minutes=step)

        # 5. Overlay "My" reservations (so they show up even if busy or different time)
        for rs in all_real_slots:
            is_mine = rs.reserved_by_token == str(token)
            if is_mine:
                key = (rs.slot_date.isoformat(), rs.start_time.strftime('%H:%M'))
                slots_map[key] = {
                    'id': str(rs.id), 
                    'date': rs.slot_date.isoformat(),
                    'start_time': rs.start_time.strftime('%I:%M %p'),
                    'end_time': rs.end_time.strftime('%I:%M %p'),
                    'status': rs.status,
                    'is_mine': True
                }

        # 6. Sort by date and time correctly using the keys (which are in 24h format)
        sorted_keys = sorted(slots_map.keys())
        sorted_slots = [slots_map[k] for k in sorted_keys]

        return Response({
            'success': True,
            'slots': sorted_slots
        })
        
    except CandidateInvitation.DoesNotExist:
        return Response({'error': 'Invalid invitation'}, status=404)
    except Exception as e:
        print(f"Error in dynamic slots: {e}")
        return Response({'error': str(e)}, status=500)

@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def reserve_interview_slot_view(request, token):
    """
    Temporarily reserves a slot for 5 minutes.
    Handles both virtual (dynamic) slot IDs and real (existing) slot IDs.
    """
    slot_id = request.data.get('slot_id')
    if not slot_id:
        return Response({'error': 'slot_id required'}, status=400)
        
    try:
        inv = CandidateInvitation.objects.get(token=token)
        assessment = inv.assessment
        now = timezone.now()

        # CASE A: Virtual Slot (dynamic_YYYY-MM-DD_HHMM)
        if str(slot_id).startswith('dynamic_'):
            try:
                parts = str(slot_id).split('_')
                if len(parts) < 3:
                    return Response({'error': f'Invalid slot ID format: {slot_id}'}, status=400)
                    
                date_str = parts[1]
                time_code = parts[2]
                
                target_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
                target_time = datetime.datetime.strptime(time_code, '%H%M').time()
                
                # Combine into datetime for duration calculation
                base_dt = datetime.datetime.combine(target_date, target_time)
                target_end = (base_dt + timedelta(minutes=50)).time()

                # Robust Lead Time check: must be at least 3 full days away from 'now.date()'
                # If today is Mar 16, earliest allowed target_date is Mar 19.
                min_booking_date = now.date() + timedelta(days=3)
                
                if target_date < min_booking_date:
                    return Response({
                        'error': f'Booking too soon. Earliest available date is {min_booking_date.strftime("%B %d, %Y")}.',
                        'code': 'LEAD_TIME_VIOLATION'
                    }, status=400)

            except Exception as e:
                import traceback
                print(traceback.format_exc())
                return Response({'error': f'Failed to process slot selection: {str(e)}'}, status=400)

            with transaction.atomic():
                interviewer_ids = assessment.assigned_interviewers.values_list('id', flat=True)
                
                # Find interviwers who HAVE a window covering this time
                has_window = InterviewerAvailability.objects.filter(
                    interviewer_id__in=interviewer_ids,
                    date=target_date,
                    start_time__lte=target_time,
                    end_time__gte=target_end
                ).values_list('interviewer_id', flat=True)

                # Subtract those who are already BUSY (Booked or Reserved by someone else)
                busy = InterviewSlot.objects.filter(
                    interviewer_id__in=has_window,
                    slot_date=target_date,
                    start_time=target_time,
                    status__in=[InterviewSlot.STATUS_BOOKED, InterviewSlot.STATUS_RESERVED]
                ).exclude(
                    status=InterviewSlot.STATUS_RESERVED,
                    reserved_by_token=str(token)
                ).values_list('interviewer_id', flat=True)

                available_ids = [idx for idx in has_window if idx not in busy]

                if not available_ids:
                    return Response({'error': 'No interviewer available at this time anymore.'}, status=409)

                # Pick the one with the least interviews this week (simple load balancing)
                # For now, just pick the first available
                selected_interviewer_id = available_ids[0]

                # Clear old reservations for this token
                InterviewSlot.objects.filter(
                    reserved_by_token=str(token),
                    status=InterviewSlot.STATUS_RESERVED
                ).update(
                    status=InterviewSlot.STATUS_AVAILABLE,
                    reserved_by_token=None,
                    reservation_expiry_time=None
                )

                # Create the new RESERVED slot
                # Create or Update the RESERVED slot
                slot, created = InterviewSlot.objects.update_or_create(
                    interviewer_id=selected_interviewer_id,
                    slot_date=target_date,
                    start_time=target_time,
                    defaults={
                        'end_time': target_end,
                        'status': InterviewSlot.STATUS_RESERVED,
                        'reserved_by_token': str(token),
                        'reservation_expiry_time': now + datetime.timedelta(minutes=5),
                        'invitation': inv
                    }
                )
                
                return Response({
                    'success': True,
                    'message': 'Slot reserved for 5 minutes.',
                    'slot_id': slot.id,
                    'expiry': slot.reservation_expiry_time.isoformat()
                })

        # CASE B: Real Slot Record
        try:
            slot = InterviewSlot.objects.get(id=slot_id)
        except (InterviewSlot.DoesNotExist, ValueError):
            return Response({'error': 'Slot not found'}, status=404)

        with transaction.atomic():
            # Check if this slot belongs to the assigned pool for security
            if not assessment.assigned_interviewers.filter(id=slot.interviewer_id).exists():
                return Response({'error': 'Unauthorized slot'}, status=403)

            # Validate 3-day lead time for static slots
            min_booking_date = now.date() + timedelta(days=3)
            if slot.slot_date < min_booking_date:
                return Response({
                    'error': f'This slot is no longer available. (3-day lead time required). Earliest allowed: {min_booking_date.isoformat()}',
                    'code': 'LEAD_TIME_VIOLATION'
                }, status=400)

            # Check availability
            if slot.status == InterviewSlot.STATUS_BOOKED:
                return Response({'error': 'Slot already booked'}, status=409)
                
            if slot.status == InterviewSlot.STATUS_RESERVED:
                if slot.reserved_by_token != str(token) and slot.reservation_expiry_time > now:
                    return Response({'error': 'Slot is temporarily reserved by another candidate'}, status=409)
            
            # Clear old reservations
            InterviewSlot.objects.filter(
                reserved_by_token=str(token),
                status=InterviewSlot.STATUS_RESERVED
            ).exclude(id=slot.id).update(
                status=InterviewSlot.STATUS_AVAILABLE,
                reserved_by_token=None,
                reservation_expiry_time=None
            )

            # Refresh reservation
            slot.status = InterviewSlot.STATUS_RESERVED
            slot.reserved_by_token = str(token)
            slot.reservation_expiry_time = now + datetime.timedelta(minutes=5)
            slot.save()
            
            return Response({
                'success': True,
                'message': 'Slot reserved for 5 minutes.',
                'slot_id': slot.id,
                'expiry': slot.reservation_expiry_time.isoformat()
            })
            
    except InterviewSlot.DoesNotExist:
        return Response({'error': 'Slot not found'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def confirm_interview_booking_view(request, token):
    """
    Finalizes the booking. Green status.
    """
    slot_id = request.data.get('slot_id')
    try:
        inv = CandidateInvitation.objects.get(token=token)
        now = timezone.now()
        
        with transaction.atomic():
            slot = InterviewSlot.objects.select_for_update().get(id=slot_id)
            
            # Verification: 3-day lead time
            min_booking_date = now.date() + timedelta(days=3)
            if slot.slot_date < min_booking_date:
                return Response({
                    'error': f'Booking failed: 3-day lead time required. Earliest allowed: {min_booking_date.isoformat()}',
                    'code': 'LEAD_TIME_VIOLATION'
                }, status=400)
            if slot.status == InterviewSlot.STATUS_RESERVED and slot.reserved_by_token == str(token):
                if slot.reservation_expiry_time < timezone.now():
                    return Response({'error': 'Reservation expired. Please try again.'}, status=409)
            elif slot.status == InterviewSlot.STATUS_AVAILABLE:
                # Allow direct booking if nobody else reserved it
                pass
            else:
                return Response({'error': 'Slot unavailable'}, status=409)
                
            # Finalize
            slot.status = InterviewSlot.STATUS_BOOKED
            
            # Find candidate details. 
            # 1. Direct link to invitation
            candidate_details = inv.candidate_details.first()
            
            # 2. Fallback: Search by email if not directly linked (sometimes details are cached/shared)
            if not candidate_details:
                candidate_details = CandidateDetails.objects.filter(email=inv.email).first()
                
            slot.candidate = candidate_details
            slot.invitation = inv
            slot.save()
            
            # Update Invitation status?
            # User might want invitation status to change to 'interview_scheduled'
            inv.status = 'interview_scheduled'
            inv.save(update_fields=['status'])

            # Create a shadow InterviewInvitation so it appears in standard Interview Lists for the interviewer
            shadow_inv, created = InterviewInvitation.objects.get_or_create(
                token=inv.token, # Use same token for consistency
                defaults={
                    'name': inv.name,
                    'email': inv.email,
                    'interviewer_name': f"{slot.interviewer.first_name or ''} {slot.interviewer.last_name or ''}".strip() or slot.interviewer.email,
                    'interviewer_email': slot.interviewer.email,
                    'start_time': timezone.make_aware(datetime.datetime.combine(slot.slot_date, slot.start_time)),
                    'end_time': timezone.make_aware(datetime.datetime.combine(slot.slot_date, slot.end_time)),
                    'status': 'accepted', # Mark as accepted for listing
                }
            )
            if not created:
                shadow_inv.status = 'accepted'
                shadow_inv.start_time = timezone.make_aware(datetime.datetime.combine(slot.slot_date, slot.start_time))
                shadow_inv.end_time = timezone.make_aware(datetime.datetime.combine(slot.slot_date, slot.end_time))
                shadow_inv.interviewer_email = slot.interviewer.email
                shadow_inv.save()

            # Send confirmation emails
            try:
                from ..tasks import send_interview_confirmation_task
                send_interview_confirmation_task.delay(slot.id)
            except Exception as e:
                pass
            
            return Response({
                'success': True,
                'message': 'Interview booked successfully!',
                'booking_details': {
                    'date': slot.slot_date.isoformat(),
                    'time': f"{slot.start_time.strftime('%I:%M %p')} - {slot.end_time.strftime('%I:%M %p')}",
                    'interviewer': slot.interviewer.first_name or slot.interviewer.email
                }
            })
            
    except Exception as e:
        return Response({'error': str(e)}, status=500)

def _broadcast_slot_change(slot_id, status_str, reserved_by):
    # Helper for real-time updates via Channels
    try:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            'interview_slots_global',
            {
                'type': 'slot_status_update',
                'slot_id': slot_id,
                'status': status_str,
                'token': reserved_by
            }
        )
    except:
        pass


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_interviewer_availability_view(request):
    try:
        profile = UserProfile.objects.get(user=request.user)
        windows = InterviewerAvailability.objects.filter(
            interviewer=profile,
            date__gte=timezone.now().date()
        )
        
        # Pre-fetch booked slots for this interviewer to avoid N+1 queries
        booked_slots = InterviewSlot.objects.filter(
            interviewer=profile,
            status=InterviewSlot.STATUS_BOOKED,
            slot_date__gte=timezone.now().date()
        )
        
        # Map booked slots for easy lookup
        # Key format: "YYYY-MM-DD_HH:MM"
        booked_map = {
            f"{s.slot_date.isoformat()}_{s.start_time.strftime('%H:%M')}": True
            for s in booked_slots
        }

        data = [{
            'id': w.id,
            'date': w.date.isoformat(),
            'start_time': w.start_time.strftime('%H:%M'),
            'end_time': w.end_time.strftime('%H:%M'),
            'is_booked': booked_map.get(f"{w.date.isoformat()}_{w.start_time.strftime('%H:%M')}", False)
        } for w in windows]
        return Response({'success': True, 'windows': data})
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['POST', 'DELETE'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def manage_interviewer_availability_view(request):
    try:
        profile = UserProfile.objects.get(user=request.user)
        if request.method == 'POST':
            date_str = request.data.get('date')
            start_str = request.data.get('start_time')
            end_str = request.data.get('end_time')
            InterviewerAvailability.objects.create(
                interviewer=profile,
                date=date_str,
                start_time=start_str,
                end_time=end_str
            )
            return Response({'success': True, 'message': 'Availability saved.'})
        elif request.method == 'DELETE':
            window_id = request.data.get('id')
            window = InterviewerAvailability.objects.filter(id=window_id, interviewer=profile).first()
            if not window:
                return Response({'error': 'Availability window not found.'}, status=404)
            
            # Check if this specific slot is already booked
            is_booked = InterviewSlot.objects.filter(
                interviewer=profile,
                slot_date=window.date,
                start_time=window.start_time,
                status=InterviewSlot.STATUS_BOOKED
            ).exists()
            
            # Use same logic as confirmation check: if it's reserved and not expired
            active_reservation = InterviewSlot.objects.filter(
                interviewer=profile,
                slot_date=window.date,
                start_time=window.start_time,
                status=InterviewSlot.STATUS_RESERVED,
                reservation_expiry_time__gt=timezone.now()
            ).exists()
            
            if is_booked or active_reservation:
                error_msg = 'Cannot remove a slot that has already been booked by a candidate.' if is_booked else 'This slot is temporarily locked by a candidate who is currently booking it.'
                return Response({
                    'error': error_msg,
                    'code': 'SLOT_BOOKED' if is_booked else 'SLOT_RESERVED'
                }, status=status.HTTP_400_BAD_REQUEST)

            window.delete()
            return Response({'success': True, 'message': 'Availability removed.'})
    except Exception as e:
        return Response({'error': str(e)}, status=500)
