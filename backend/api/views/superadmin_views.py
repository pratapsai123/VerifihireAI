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
    
    users_qs = UserProfile.objects.all().order_by('-registration_timestamp')
    if status_filter == 'pending':
        users_qs = users_qs.filter(is_approved=False)
    elif status_filter == 'approved':
        users_qs = users_qs.filter(is_approved=True)

    result = []
    for profile in users_qs:
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
