from .._imports import *


def _require_application_admin(request):
    """
    Helper: returns (auth_user, app_admin) if the requester is a valid ApplicationAdmin,
    otherwise returns (None, None).
    """
    auth_user = request.user
    if not auth_user or not auth_user.is_authenticated:
        return None, None
    try:
        app_admin = ApplicationAdmin.objects.get(user=auth_user)
        return auth_user, app_admin
    except ApplicationAdmin.DoesNotExist:
        return None, None


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def superadmin_companies_view(request):
    """
    GET /api/superadmin/companies/?status=pending|approved|rejected
    List all companies with their primary admin info.
    Only accessible by ApplicationAdmin.
    """
    auth_user, app_admin = _require_application_admin(request)
    if not app_admin:
        return Response({'error': 'Forbidden. Platform superadmin access required.'}, status=status.HTTP_403_FORBIDDEN)

    status_filter = request.query_params.get('status', '').strip().lower()

    companies_qs = Company.objects.all().order_by('-created_at')
    if status_filter in ('pending', 'approved', 'rejected'):
        companies_qs = companies_qs.filter(approval_status=status_filter)

    result = []
    for company in companies_qs:
        # Find the first company_admin (or any user) for this company
        primary_user = (
            UserProfile.objects.filter(company=company, role=UserProfile.ROLE_COMPANY_ADMIN)
            .order_by('registration_timestamp')
            .first()
        )
        user_count = UserProfile.objects.filter(company=company).count()

        result.append({
            'id': company.id,
            'name': company.name,
            'domain': company.domain,
            'approval_status': company.approval_status,
            'rejected_reason': company.rejected_reason,
            'created_at': company.created_at.isoformat(),
            'approved_at': company.approved_at.isoformat() if company.approved_at else None,
            'user_count': user_count,
            'primary_admin': {
                'id': primary_user.id if primary_user else None,
                'first_name': primary_user.first_name if primary_user else '',
                'last_name': primary_user.last_name if primary_user else '',
                'email': primary_user.email if primary_user else '',
                'role': primary_user.role if primary_user else '',
                'registered_at': primary_user.registration_timestamp.isoformat() if primary_user else None,
            } if primary_user else None,
        })

    return Response({'companies': result, 'total': len(result)}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def superadmin_approve_company_view(request, company_id):
    """
    POST /api/superadmin/companies/<id>/approve/
    Approve a company registration. Sends email to company admin.
    """
    auth_user, app_admin = _require_application_admin(request)
    if not app_admin:
        return Response({'error': 'Forbidden. Platform superadmin access required.'}, status=status.HTTP_403_FORBIDDEN)

    try:
        company = Company.objects.get(pk=company_id)
    except Company.DoesNotExist:
        return Response({'error': 'Company not found.'}, status=status.HTTP_404_NOT_FOUND)

    company.approval_status = Company.APPROVAL_APPROVED
    company.approved_at = timezone.now()
    company.rejected_reason = None
    company.save(update_fields=['approval_status', 'approved_at', 'rejected_reason'])

    # Notify the company admin
    try:
        admin_profile = (
            UserProfile.objects.filter(company=company, role=UserProfile.ROLE_COMPANY_ADMIN)
            .order_by('registration_timestamp')
            .first()
        )
        if admin_profile:
            admin_profile.is_approved = True
            admin_profile.save(update_fields=['is_approved', 'updated_at'])
            
            send_mail(
                subject='VeriFiHire - Your Company Registration Has Been Approved!',
                message=(
                    f'Dear {admin_profile.first_name or "Admin"},\n\n'
                    f'Great news! Your company "{company.name}" has been approved by the platform administrator.\n\n'
                    f'You can now log in to the VeriFiHire platform and start managing your hiring process.\n\n'
                    f'Thank you for choosing VeriFiHire!'
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[admin_profile.email],
                fail_silently=True,
            )
    except Exception as e:
        print(f'Approval email failed: {e}')

    return Response({
        'message': f'Company "{company.name}" has been approved successfully.',
        'company_id': company.id,
        'approval_status': company.approval_status,
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def superadmin_reject_company_view(request, company_id):
    """
    POST /api/superadmin/companies/<id>/reject/
    Reject a company registration with an optional reason. Sends email to company admin.
    """
    auth_user, app_admin = _require_application_admin(request)
    if not app_admin:
        return Response({'error': 'Forbidden. Platform superadmin access required.'}, status=status.HTTP_403_FORBIDDEN)

    try:
        company = Company.objects.get(pk=company_id)
    except Company.DoesNotExist:
        return Response({'error': 'Company not found.'}, status=status.HTTP_404_NOT_FOUND)

    reason = request.data.get('reason', '').strip()

    company.approval_status = Company.APPROVAL_REJECTED
    company.rejected_reason = reason or None
    company.approved_at = None
    company.save(update_fields=['approval_status', 'rejected_reason', 'approved_at'])

    # Notify the company admin
    try:
        admin_profile = (
            UserProfile.objects.filter(company=company, role=UserProfile.ROLE_COMPANY_ADMIN)
            .order_by('registration_timestamp')
            .first()
        )
        if admin_profile and admin_profile.email:
            msg = (
                f'Dear {admin_profile.first_name or "Admin"},\n\n'
                f'We regret to inform you that your company "{company.name}" registration has been rejected by the platform administrator.\n\n'
            )
            if reason:
                msg += f'Reason: {reason}\n\n'
            msg += 'If you believe this is a mistake, please contact our support team.\n\nThank you.'
            send_mail(
                subject='VeriFiHire - Company Registration Status Update',
                message=msg,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[admin_profile.email],
                fail_silently=True,
            )
    except Exception as e:
        print(f'Rejection email failed: {e}')

    return Response({
        'message': f'Company "{company.name}" has been rejected.',
        'company_id': company.id,
        'approval_status': company.approval_status,
        'rejected_reason': company.rejected_reason,
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def superadmin_users_view(request):
    """
    GET /api/superadmin/users/?status=pending|approved
    List all platform users with approval filter.
    """
    auth_user, app_admin = _require_application_admin(request)
    if not app_admin:
        return Response({'error': 'Forbidden. Platform superadmin access required.'}, status=status.HTTP_403_FORBIDDEN)

    status_filter = request.query_params.get('status', '').strip().lower()
    
    users_qs = UserProfile.objects.all().select_related('manager', 'company').order_by('-registration_timestamp')
    if status_filter == 'pending':
        users_qs = users_qs.filter(is_approved=False)
    elif status_filter == 'approved':
        users_qs = users_qs.filter(is_approved=True)

    result = []
    for profile in users_qs:
        manager_name = None
        if profile.manager:
            m_first = profile.manager.first_name or ''
            m_last = profile.manager.last_name or ''
            manager_name = f"{m_first} {m_last}".strip() or profile.manager.email

        result.append({
            'id': profile.id,
            'first_name': profile.first_name,
            'last_name': profile.last_name,
            'email': profile.email,
            'role': profile.role,
            'organization_name': profile.organization_name,
            'company_id': profile.company.id if profile.company else None,
            'is_approved': profile.is_approved,
            'registered_at': profile.registration_timestamp.isoformat(),
            'manager_id': profile.manager.id if profile.manager else None,
            'manager_name': manager_name,
        })

    return Response({'users': result, 'total': len(result)}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def superadmin_approve_user_view(request, user_id):
    """
    POST /api/superadmin/users/<id>/approve/
    Approve an individual user.
    """
    auth_user, app_admin = _require_application_admin(request)
    if not app_admin:
        return Response({'error': 'Forbidden. Platform superadmin access required.'}, status=status.HTTP_403_FORBIDDEN)

    try:
        profile = UserProfile.objects.get(pk=user_id)
    except UserProfile.DoesNotExist:
        return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

    profile.is_approved = True
    profile.save(update_fields=['is_approved', 'updated_at'])

    return Response({
        'message': f'User "{profile.email}" has been approved.',
        'user_id': profile.id,
        'is_approved': True,
    }, status=status.HTTP_200_OK)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def superadmin_restricted_domains_view(request):
    """
    GET /api/superadmin/restricted-domains/ - List all restricted domains.
    POST /api/superadmin/restricted-domains/ - Add a new restricted domain.
    """
    auth_user, app_admin = _require_application_admin(request)
    if not app_admin:
        return Response({'error': 'Forbidden. Platform superadmin access required.'}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        domains = RestrictedDomain.objects.all().order_by('domain')
        result = [{
            'id': d.id,
            'domain': d.domain,
            'created_at': d.created_at.isoformat(),
            'created_by': d.created_by.email if d.created_by else None
        } for d in domains]
        return Response({'domains': result, 'total': len(result)}, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        domain_name = request.data.get('domain', '').strip().lower()
        if not domain_name:
            return Response({'error': 'Domain name is required.'}, status=status.HTTP_400_BAD_REQUEST)

        # Simple validation: must look like a domain (has a dot, no @)
        if '@' in domain_name or '.' not in domain_name:
            return Response({'error': 'Invalid domain format. Use example.com format.'}, status=status.HTTP_400_BAD_REQUEST)

        if RestrictedDomain.objects.filter(domain=domain_name).exists():
            return Response({'error': f'Domain {domain_name} is already restricted.'}, status=status.HTTP_409_CONFLICT)

        domain_obj = RestrictedDomain.objects.create(
            domain=domain_name,
            created_by=auth_user
        )

        return Response({
            'message': f'Domain {domain_name} added to restriction list.',
            'id': domain_obj.id,
            'domain': domain_obj.domain
        }, status=status.HTTP_201_CREATED)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def superadmin_delete_restricted_domain_view(request, domain_id):
    """
    DELETE /api/superadmin/restricted-domains/<id>/ - Remove a restricted domain.
    """
    auth_user, app_admin = _require_application_admin(request)
    if not app_admin:
        return Response({'error': 'Forbidden. Platform superadmin access required.'}, status=status.HTTP_403_FORBIDDEN)

    try:
        domain_obj = RestrictedDomain.objects.get(pk=domain_id)
        domain_name = domain_obj.domain
        domain_obj.delete()
        return Response({'message': f'Domain {domain_name} removed from restricted list.'}, status=status.HTTP_200_OK)
    except RestrictedDomain.DoesNotExist:
        return Response({'error': 'Restricted domain not found.'}, status=status.HTTP_404_NOT_FOUND)



# --- Student Prep Sessions (Superadmin-Managed) ---

from django.db.models import Q
from django.core.exceptions import ValidationError
from ..models import StudentPrepSession

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def public_practice_schedule_view(request):
    """
    POST /api/practice/schedule/
    Public endpoint for scheduling a mock prep session.
    Extracts text from the uploaded resume, saves a StudentPrepSession, and returns a public token.
    """
    try:
        full_name = request.data.get('name', '').strip() or request.data.get('full_name', '').strip()
        email = request.data.get('email', '').strip().lower()
        phone = request.data.get('phone', '').strip()
        scheduled_time_str = request.data.get('scheduled_time', '').strip()
        target_role = request.data.get('target_role', '').strip()
        experience_level = request.data.get('experience_level', '').strip()

        if not full_name:
            return Response({'error': 'Name is required.'}, status=status.HTTP_400_BAD_REQUEST)
        if not email:
            return Response({'error': 'Email is required.'}, status=status.HTTP_400_BAD_REQUEST)

        scheduled_time = None
        if scheduled_time_str:
            try:
                from django.utils.dateparse import parse_datetime
                scheduled_time = parse_datetime(scheduled_time_str)
            except Exception:
                pass

        # Text extraction from resume
        resume_text = ""
        resume_hash = ""
        uploaded_file = None
        if 'resume' in request.FILES:
            uploaded_file = request.FILES['resume']
            try:
                from .assessment_views import _extract_text_from_uploaded_file
                resume_text, _ = _extract_text_from_uploaded_file(uploaded_file)
                import hashlib
                resume_hash = hashlib.sha256(resume_text.encode('utf-8', errors='ignore')).hexdigest()
            except Exception as e:
                print(f"Error extracting resume: {e}")

        # Parse target role from resume if empty
        if not target_role and resume_text:
            target_role = "Software Engineer"  # Fallback

        # Save session
        session = StudentPrepSession.objects.create(
            full_name=full_name,
            email=email,
            phone=phone,
            resume=uploaded_file,
            resume_text=resume_text,
            resume_hash=resume_hash,
            target_role=target_role or "Software Engineer",
            experience_level=experience_level or "Fresher",
            scheduled_time=scheduled_time or timezone.now(),
            status='Scheduled'
        )

        return Response({
            'message': 'Mock preparation session scheduled successfully!',
            'public_token': str(session.id),
            'session': {
                'id': str(session.id),
                'full_name': session.full_name,
                'email': session.email,
                'phone': session.phone,
                'target_role': session.target_role,
                'experience_level': session.experience_level,
                'scheduled_time': session.scheduled_time.isoformat() if session.scheduled_time else None,
                'status': session.status,
            }
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        import traceback
        print(f"Error scheduling practice session: {e}")
        print(traceback.format_exc())
        return Response({'error': f'Failed to schedule session: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def superadmin_student_prep_sessions_list_view(request):
    """
    GET /api/superadmin/student-prep-sessions/
    Protected: Superadmin only
    List all mock sessions with search/filters (name, email, role, status, score).
    """
    auth_user, app_admin = _require_application_admin(request)
    if not app_admin:
        return Response({'error': 'Forbidden. Platform superadmin access required.'}, status=status.HTTP_403_FORBIDDEN)

    search = request.query_params.get('search', '').strip()
    score_filter = request.query_params.get('score', '').strip()
    status_filter = request.query_params.get('status', '').strip()

    qs = StudentPrepSession.objects.all().order_by('-created_at')

    if search:
        qs = qs.filter(
            Q(full_name__icontains=search) |
            Q(email__icontains=search) |
            Q(target_role__icontains=search)
        )

    if score_filter:
        try:
            qs = qs.filter(score__gte=int(score_filter))
        except ValueError:
            pass

    if status_filter:
        qs = qs.filter(status=status_filter)

    from django.core.paginator import Paginator
    paginator = Paginator(qs, 10)
    page_number = request.query_params.get('page', 1)
    page_obj = paginator.get_page(page_number)

    sessions_data = []
    for s in page_obj:
        sessions_data.append({
            'id': str(s.id),
            'full_name': s.full_name,
            'email': s.email,
            'phone': s.phone,
            'target_role': s.target_role,
            'experience_level': s.experience_level,
            'scheduled_time': s.scheduled_time.isoformat() if s.scheduled_time else None,
            'status': s.status,
            'score': s.score,
            'created_at': s.created_at.isoformat(),
        })

    return Response({
        'sessions': sessions_data,
        'total': paginator.count,
        'pages': paginator.num_pages,
        'current_page': page_obj.number
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def superadmin_student_prep_session_detail_view(request, id):
    """
    GET /api/superadmin/student-prep-sessions/<id>/
    Protected: Superadmin only
    """
    auth_user, app_admin = _require_application_admin(request)
    if not app_admin:
        return Response({'error': 'Forbidden. Platform superadmin access required.'}, status=status.HTTP_403_FORBIDDEN)

    try:
        s = StudentPrepSession.objects.get(pk=id)
    except (StudentPrepSession.DoesNotExist, ValueError, ValidationError):
        return Response({'error': 'Student Prep Session not found.'}, status=status.HTTP_404_NOT_FOUND)

    return Response({
        'id': str(s.id),
        'full_name': s.full_name,
        'email': s.email,
        'phone': s.phone,
        'resume_url': s.resume.url if s.resume else None,
        'resume_text': s.resume_text,
        'resume_hash': s.resume_hash,
        'target_role': s.target_role,
        'experience_level': s.experience_level,
        'scheduled_time': s.scheduled_time.isoformat() if s.scheduled_time else None,
        'status': s.status,
        'interview_questions': s.interview_questions,
        'interview_summary': s.interview_summary,
        'score': s.score,
        'created_at': s.created_at.isoformat(),
    }, status=status.HTTP_200_OK)

