from ._imports import *


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

        # Get or create a default interview (or create one per batch)
        # For simplicity, we'll create one interview per batch of invites
        interview = Interview.objects.create(
            name=interview_name,
            description=f'Interview created on {timezone.now().strftime("%Y-%m-%d %H:%M:%S")}',
        )

        frontend_base = getattr(settings, 'FRONTEND_BASE_URL', None) or os.environ.get('FRONTEND_BASE_URL') or 'https://verifyhire.duckdns.org'

        results = []
        sent_count = 0
        fail_count = 0

        drafts = InterviewInvitation.objects.filter(id__in=draft_ids, status='draft')

        for invitation in drafts:
            # Associate the draft with this new interview
            invitation.interview = interview
            name = invitation.name
            email = invitation.email
            interviewer_name = invitation.interviewer_name
            interviewer_email = invitation.interviewer_email
            
            start_time = invitation.start_time
            end_time = invitation.end_time
            time_zone = invitation.time_zone
            
            # Read validity mode (assuming it was passed if needed, or default to exact_window for now)
            validity_mode = 'exact_window'

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
                    schedule_text += "Available: 12:00 AM to 11:59 PM\n"
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
        interview_id = request.GET.get('interview_id', None)
        qs = InterviewInvitation.objects.select_related('interview').order_by('-created_at')
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
@permission_classes([IsAuthenticated])
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
        from .models import LiveInterviewFeedback
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
        if request.method == 'GET':
            qs = InterviewInvitation.objects.filter(status='draft').order_by('-created_at')
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
                
            draft = InterviewInvitation.objects.filter(id=draft_id, status='draft').first()
            if not draft:
                return Response({'error': 'Draft not found'}, status=status.HTTP_404_NOT_FOUND)
                
            draft.delete()
            return Response({'message': 'Draft deleted successfully'}, status=status.HTTP_204_NO_CONTENT)

    except Exception as e:
        import traceback
        print(f"Error in draft_interview_invitations_view: {str(e)}")
        print(traceback.format_exc())
        return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



