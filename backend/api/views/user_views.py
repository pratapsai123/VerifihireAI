from ._imports import *


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def invite_user_view(request):
    """
    Create an invitation for internal company roles (HR Manager / HR).

    Expected request body:
    {
      "inviter_email": "companyadmin@acme.com",
      "email": "hrmanager@acme.com",
      "role": "hr_manager" | "hr"
    }

    NOTE: This repo currently doesn't have JWT/session auth wired in.
    For now we authorize by checking inviter_email's role in UserProfile.
    """
    try:
        inviter_email = _normalize_email(request.data.get('inviter_email', ''))
        invitee_email = _normalize_email(request.data.get('email', ''))
        role = (request.data.get('role') or '').strip().lower()

        if not inviter_email:
            return Response({'error': 'inviter_email is required.'}, status=status.HTTP_400_BAD_REQUEST)

        # Application Admin can view all data but cannot send invites (per requirement)
        if _is_application_admin_email(inviter_email):
            return Response({'error': 'Application Admin is not allowed to send invitations.'}, status=status.HTTP_403_FORBIDDEN)

        if not invitee_email:
            return Response({'error': 'email is required.'}, status=status.HTTP_400_BAD_REQUEST)
        if role not in {UserProfile.ROLE_HR_MANAGER, UserProfile.ROLE_HR}:
            return Response({'error': 'role must be hr_manager or hr.'}, status=status.HTTP_400_BAD_REQUEST)

        inviter = UserProfile.objects.filter(email=inviter_email).select_related('company').first()
        if not inviter or not inviter.company:
            return Response({'error': 'Invalid inviter.'}, status=status.HTTP_403_FORBIDDEN)

        if inviter.role not in {UserProfile.ROLE_COMPANY_ADMIN, UserProfile.ROLE_HR_MANAGER}:
            return Response({'error': 'You are not allowed to invite users.'}, status=status.HTTP_403_FORBIDDEN)

        if inviter.role == UserProfile.ROLE_HR_MANAGER and role != UserProfile.ROLE_HR:
            return Response({'error': 'HR Manager can only invite HR users.'}, status=status.HTTP_403_FORBIDDEN)

        company = inviter.company
        company_domain = (company.domain or '').strip().lower()
        if not company_domain:
            return Response({'error': 'Company domain is not configured.'}, status=status.HTTP_400_BAD_REQUEST)

        invitee_domain = _email_domain(invitee_email)
        if not invitee_domain:
            return Response({'error': 'Invalid email address.'}, status=status.HTTP_400_BAD_REQUEST)
        if invitee_domain != company_domain:
            return Response({'error': 'Invitee email domain must match company domain.'}, status=status.HTTP_400_BAD_REQUEST)
        if invitee_domain in _free_email_domains():
            return Response({'error': 'Free email domains are not allowed for internal roles.'}, status=status.HTTP_400_BAD_REQUEST)

        # Already registered?
        if UserProfile.objects.filter(email=invitee_email).exists():
            return Response({'error': 'A user with this email already exists.'}, status=status.HTTP_400_BAD_REQUEST)

        # Enforce max 5 HR_MANAGER per company
        if role == UserProfile.ROLE_HR_MANAGER and UserProfile.objects.filter(company=company, role=UserProfile.ROLE_HR_MANAGER).count() >= 5:
            return Response({'error': 'Maximum of 5 HR Managers allowed per company.'}, status=status.HTTP_409_CONFLICT)

        # Prevent multiple pending invites
        existing_pending = UserInvitation.objects.filter(company=company, email=invitee_email, status=UserInvitation.STATUS_PENDING).first()
        if existing_pending and not existing_pending.is_expired():
            return Response({'error': 'A pending invitation already exists for this email.'}, status=status.HTTP_409_CONFLICT)

        temp_password = _generate_temp_password(12)
        expires_at = timezone.now() + timedelta(hours=48)

        invitation = UserInvitation.objects.create(
            company=company,
            email=invitee_email,
            role=role,
            invited_by=inviter,
            temp_password_hash=make_password(temp_password),
            status=UserInvitation.STATUS_PENDING,
            expires_at=expires_at,
        )

        # Prefer explicit env, otherwise best-effort derive from incoming request host.
        frontend_base = (
            getattr(settings, 'FRONTEND_BASE_URL', None)
            or os.environ.get('FRONTEND_BASE_URL')
        )
        if not frontend_base:
            # request.build_absolute_uri('/') gives http(s)://host/; trim trailing slash
            frontend_base = request.build_absolute_uri('/').rstrip('/')
        if not frontend_base:
            frontend_base = 'https://verifyhire.duckdns.org'
        activation_link = f"{frontend_base.rstrip('/')}/accept-invite?token={invitation.token}"

        subject = f"{company.name} - Account Invitation"
        message = (
            f"You have been invited to VeriFiHire.\n\n"
            f"Company: {company.name}\n"
            f"Role: {role}\n\n"
            f"Activation link (one-time): {activation_link}\n"
            f"Temporary password: {temp_password}\n\n"
            f"This link expires in 48 hours."
        )

        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[invitee_email],
                fail_silently=False,
            )
            email_sent = True
        except Exception as mail_err:
            invitation.status = UserInvitation.STATUS_PENDING
            invitation.save(update_fields=['status'])
            email_sent = False

        payload = {
            'message': 'Invitation created.',
            'email_sent': email_sent,
            'invitation': {
                'id': invitation.id,
                'email': invitation.email,
                'role': invitation.role,
                'company': company.name,
                'token': str(invitation.token),
                'expires_at': invitation.expires_at.isoformat() if invitation.expires_at else None,
            },
        }
        if not email_sent:
            # Dev fallback: return temp password if email fails (consistent with OTP endpoints)
            payload['temp_password'] = temp_password
            payload['activation_link'] = activation_link
        return Response(payload, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def cancel_invite_view(request, token):
    """
    Cancel a pending invitation.

    Body:
      { "requester_email": "..." }
    """
    try:
        requester_email = _normalize_email(request.data.get('requester_email', ''))
        if not requester_email:
            return Response({'error': 'requester_email is required.'}, status=status.HTTP_400_BAD_REQUEST)
        if _is_application_admin_email(requester_email):
            return Response({'error': 'Application Admin cannot cancel invitations.'}, status=status.HTTP_403_FORBIDDEN)

        requester = UserProfile.objects.filter(email=requester_email).select_related('company').first()
        if not requester or not requester.company:
            return Response({'error': 'Invalid requester.'}, status=status.HTTP_403_FORBIDDEN)
        if requester.role not in {UserProfile.ROLE_COMPANY_ADMIN, UserProfile.ROLE_HR_MANAGER}:
            return Response({'error': 'Forbidden.'}, status=status.HTTP_403_FORBIDDEN)

        inv = UserInvitation.objects.select_related('company').filter(token=token).first()
        if not inv:
            return Response({'error': 'Invitation not found.'}, status=status.HTTP_404_NOT_FOUND)
        if inv.company_id != requester.company_id:
            return Response({'error': 'Forbidden.'}, status=status.HTTP_403_FORBIDDEN)

        if inv.status != UserInvitation.STATUS_PENDING:
            return Response({'error': f'Invitation is {inv.status}.'}, status=status.HTTP_409_CONFLICT)

        inv.status = UserInvitation.STATUS_CANCELLED
        inv.save(update_fields=['status'])
        return Response({'message': 'Invitation cancelled.'}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def resend_invite_view(request, token):
    """
    Resend a pending invitation. Regenerates the temporary password.

    Body:
      { "requester_email": "..." }
    """
    try:
        requester_email = _normalize_email(request.data.get('requester_email', ''))
        if not requester_email:
            return Response({'error': 'requester_email is required.'}, status=status.HTTP_400_BAD_REQUEST)
        if _is_application_admin_email(requester_email):
            return Response({'error': 'Application Admin cannot resend invitations.'}, status=status.HTTP_403_FORBIDDEN)

        requester = UserProfile.objects.filter(email=requester_email).select_related('company').first()
        if not requester or not requester.company:
            return Response({'error': 'Invalid requester.'}, status=status.HTTP_403_FORBIDDEN)
        if requester.role not in {UserProfile.ROLE_COMPANY_ADMIN, UserProfile.ROLE_HR_MANAGER}:
            return Response({'error': 'Forbidden.'}, status=status.HTTP_403_FORBIDDEN)

        inv = UserInvitation.objects.select_related('company').filter(token=token).first()
        if not inv:
            return Response({'error': 'Invitation not found.'}, status=status.HTTP_404_NOT_FOUND)
        if inv.company_id != requester.company_id:
            return Response({'error': 'Forbidden.'}, status=status.HTTP_403_FORBIDDEN)

        if inv.status != UserInvitation.STATUS_PENDING:
            return Response({'error': f'Invitation is {inv.status}.'}, status=status.HTTP_409_CONFLICT)

        # HR Manager can only manage HR invites
        if requester.role == UserProfile.ROLE_HR_MANAGER and inv.role != UserProfile.ROLE_HR:
            return Response({'error': 'HR Manager can only manage HR invitations.'}, status=status.HTTP_403_FORBIDDEN)

        # Refresh temp password + expiry window
        temp_password = _generate_temp_password(12)
        inv.temp_password_hash = make_password(temp_password)
        inv.expires_at = timezone.now() + timedelta(hours=48)
        inv.save(update_fields=['temp_password_hash', 'expires_at'])

        frontend_base = getattr(settings, 'FRONTEND_BASE_URL', None) or os.environ.get('FRONTEND_BASE_URL') or 'https://verifyhire.duckdns.org'
        activation_link = f"{frontend_base.rstrip('/')}/accept-invite?token={inv.token}"

        subject = f"{inv.company.name} - Account Invitation (Resent)"
        message = (
            f"Your VeriFiHire invitation has been resent.\n\n"
            f"Company: {inv.company.name}\n"
            f"Role: {inv.role}\n\n"
            f"Activation link (one-time): {activation_link}\n"
            f"Temporary password: {temp_password}\n\n"
            f"This link expires in 48 hours."
        )

        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[inv.email],
                fail_silently=False,
            )
            email_sent = True
        except Exception:
            email_sent = False

        payload = {
            'message': 'Invitation resent.',
            'email_sent': email_sent,
            'activation_link': activation_link if not email_sent else None,
            'temp_password': temp_password if not email_sent else None,
            'expires_at': inv.expires_at.isoformat() if inv.expires_at else None,
        }
        return Response(payload, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['GET'])
@permission_classes([AllowAny])
def get_invite_view(request, token):
    """
    Public: fetch invitation metadata for the accept-invite UI.
    """
    try:
        inv = UserInvitation.objects.select_related('company').filter(token=token).first()
        if not inv:
            return Response({'error': 'Invitation not found.'}, status=status.HTTP_404_NOT_FOUND)

        if inv.status != UserInvitation.STATUS_PENDING:
            return Response({'error': f'Invitation is {inv.status}.'}, status=status.HTTP_409_CONFLICT)

        if inv.is_expired():
            inv.status = UserInvitation.STATUS_EXPIRED
            inv.save(update_fields=['status'])
            return Response({'error': 'Invitation has expired.'}, status=status.HTTP_410_GONE)

        return Response(
            {
                'email': inv.email,
                'role': inv.role,
                'company': inv.company.name,
                'expires_at': inv.expires_at.isoformat() if inv.expires_at else None,
            },
            status=status.HTTP_200_OK,
        )
    except Exception as e:
        return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def accept_invite_view(request):
    """
    Accept a user invitation and set password.

    Expected request body:
    {
      "token": "<uuid>",
      "full_name": "First Last",
      "temp_password": "....",
      "new_password": "....",
      "confirm_password": "...."
    }
    """
    try:
        token = (request.data.get('token') or '').strip()
        full_name = (request.data.get('full_name') or '').strip()
        temp_password = request.data.get('temp_password') or ''
        new_password = request.data.get('new_password') or ''
        confirm_password = request.data.get('confirm_password') or ''

        if not token:
            return Response({'error': 'token is required.'}, status=status.HTTP_400_BAD_REQUEST)
        if not full_name:
            return Response({'error': 'full_name is required.'}, status=status.HTTP_400_BAD_REQUEST)
        if not temp_password:
            return Response({'error': 'temp_password is required.'}, status=status.HTTP_400_BAD_REQUEST)
        if not new_password or not confirm_password:
            return Response({'error': 'new_password and confirm_password are required.'}, status=status.HTTP_400_BAD_REQUEST)
        if new_password != confirm_password:
            return Response({'error': 'Passwords do not match.'}, status=status.HTTP_400_BAD_REQUEST)
        if len(new_password) < 6:
            return Response({'error': 'Password must be at least 6 characters long.'}, status=status.HTTP_400_BAD_REQUEST)

        inv = UserInvitation.objects.select_related('company').filter(token=token).first()
        if not inv:
            return Response({'error': 'Invitation not found.'}, status=status.HTTP_404_NOT_FOUND)
        if inv.status != UserInvitation.STATUS_PENDING:
            return Response({'error': f'Invitation is {inv.status}.'}, status=status.HTTP_409_CONFLICT)
        if inv.is_expired():
            inv.status = UserInvitation.STATUS_EXPIRED
            inv.save(update_fields=['status'])
            return Response({'error': 'Invitation has expired.'}, status=status.HTTP_410_GONE)

        if not check_password(temp_password, inv.temp_password_hash):
            return Response({'error': 'Invalid temporary password.'}, status=status.HTTP_400_BAD_REQUEST)

        email = _normalize_email(inv.email)
        if UserProfile.objects.filter(email=email).exists():
            return Response({'error': 'A user with this email already exists.'}, status=status.HTTP_409_CONFLICT)

        # Enforce max 5 HR_MANAGER per company
        if inv.role == UserProfile.ROLE_HR_MANAGER and UserProfile.objects.filter(company=inv.company, role=UserProfile.ROLE_HR_MANAGER).count() >= 5:
            return Response({'error': 'Maximum of 5 HR Managers allowed per company.'}, status=status.HTTP_409_CONFLICT)

        name_parts = full_name.split(' ', 1)
        first_name = name_parts[0].strip()
        last_name = name_parts[1].strip() if len(name_parts) > 1 else ''

        user = User.objects.create_user(
            username=email,
            email=email,
            password=new_password,
            first_name=first_name,
            last_name=last_name,
        )

        profile = UserProfile.objects.create(
            first_name=first_name,
            last_name=last_name if last_name else None,
            email=email,
            password=None,  # deprecated
            role=inv.role,
            organization_name=inv.company.name,
            company=inv.company,
            user=user,
        )

        inv.status = UserInvitation.STATUS_ACCEPTED
        inv.accepted_at = timezone.now()
        inv.temp_password_hash = ''
        inv.save(update_fields=['status', 'accepted_at', 'temp_password_hash'])

        return Response(
            {
                'message': 'Invitation accepted. Account created successfully.',
                'user': {
                    'id': profile.id,
                    'email': profile.email,
                    'role': profile.role,
                    'organization_name': profile.organization_name,
                },
            },
            status=status.HTTP_201_CREATED,
        )

    except Exception as e:
        return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['GET'])
@permission_classes([AllowAny])
def team_members_view(request):
    """
    List team members and invitation details.

    Since this repo doesn't have JWT/session auth wired in, the caller supplies:
      ?requester_email=...

    Access rules:
    - application_admin: can view all companies' users + invites
    - company_admin/hr_manager: can view only their company users + invites
    - hr/candidate/etc: forbidden
    """
    try:
        requester_email = _normalize_email(request.query_params.get('requester_email', ''))
        if not requester_email:
            return Response({'error': 'requester_email is required.'}, status=status.HTTP_400_BAD_REQUEST)

        is_app_admin = _is_application_admin_email(requester_email)
        requester_profile = None
        if not is_app_admin:
            requester_profile = UserProfile.objects.filter(email=requester_email).select_related('company').first()
            if not requester_profile or not requester_profile.company:
                return Response({'error': 'Invalid requester.'}, status=status.HTTP_403_FORBIDDEN)
            if requester_profile.role not in {UserProfile.ROLE_COMPANY_ADMIN, UserProfile.ROLE_HR_MANAGER}:
                return Response({'error': 'Forbidden.'}, status=status.HTTP_403_FORBIDDEN)

        if is_app_admin:
            members_qs = UserProfile.objects.select_related('company').order_by('company__name', 'email')
            invites_qs = UserInvitation.objects.select_related('company', 'invited_by').order_by('-created_at')
        else:
            company = requester_profile.company
            # Never include application admin in company-scoped member lists
            members_qs = (
                UserProfile.objects.filter(company=company)
                .exclude(role=UserProfile.ROLE_APPLICATION_ADMIN)
                .select_related('company')
                .order_by('email')
            )
            invites_qs = UserInvitation.objects.filter(company=company).select_related('company', 'invited_by').order_by('-created_at')

        members = []
        for u in members_qs:
            members.append({
                'id': u.id,
                'first_name': u.first_name,
                'last_name': u.last_name,
                'email': u.email,
                'role': u.role,
                'organization_name': u.organization_name,
                'company': (u.company.name if u.company else None),
                'registration_timestamp': u.registration_timestamp.isoformat() if u.registration_timestamp else None,
            })

        invitations = []
        now = timezone.now()
        for inv in invites_qs:
            status_value = inv.status
            if status_value == UserInvitation.STATUS_PENDING and inv.expires_at and now > inv.expires_at:
                status_value = UserInvitation.STATUS_EXPIRED
            invitations.append({
                'id': inv.id,
                'email': inv.email,
                'role': inv.role,
                'company': inv.company.name,
                'status': status_value,
                'token': str(inv.token),
                'invited_by': inv.invited_by.email if inv.invited_by else None,
                'created_at': inv.created_at.isoformat() if inv.created_at else None,
                'expires_at': inv.expires_at.isoformat() if inv.expires_at else None,
                'accepted_at': inv.accepted_at.isoformat() if inv.accepted_at else None,
            })

        return Response(
            {
                'scope': 'all' if is_app_admin else 'company',
                'requester_email': requester_email,
                'members': members,
                'invitations': invitations,
            },
            status=status.HTTP_200_OK,
        )
    except Exception as e:
        return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['GET'])
@permission_classes([AllowAny])
def profile_view(request):
    """Return logged-in user profile. Query param: ?email=user@company.com"""
    try:
        email = _normalize_email(request.query_params.get('email', ''))
        if not email:
            return Response({'error': 'email is required.'}, status=status.HTTP_400_BAD_REQUEST)
        profile = UserProfile.objects.select_related('company').filter(email=email).first()
        if not profile:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
        return Response({
            'id': profile.id,
            'email': profile.email,
            'first_name': profile.first_name,
            'last_name': profile.last_name,
            'role': profile.role,
            'organization_name': profile.organization_name,
            'company': {
                'id': profile.company.id,
                'name': profile.company.name,
                'domain': profile.company.domain,
            } if profile.company else None,
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
