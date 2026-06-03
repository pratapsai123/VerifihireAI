from .._imports import *
from .._imports import _email_domain, _free_email_domains, _generate_temp_password, _normalize_email, _is_application_admin_email


@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
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
            return Response({'email': ['Email is required.']}, status=status.HTTP_400_BAD_REQUEST)
        if role not in {UserProfile.ROLE_HR_MANAGER, UserProfile.ROLE_HR, UserProfile.ROLE_INTERVIEWER}:
            return Response({'role': ['Role must be hr_manager, hr or interviewer.']}, status=status.HTTP_400_BAD_REQUEST)

        inviter = UserProfile.objects.filter(email=inviter_email).select_related('company').first()
        if not inviter or not inviter.company:
            return Response({'error': 'Invalid inviter.'}, status=status.HTTP_403_FORBIDDEN)

        if inviter.role not in {UserProfile.ROLE_COMPANY_ADMIN, UserProfile.ROLE_HR_MANAGER, UserProfile.ROLE_HR}:
            return Response({'error': 'You are not allowed to invite users.'}, status=status.HTTP_403_FORBIDDEN)

        if inviter.role == UserProfile.ROLE_HR_MANAGER and role not in {UserProfile.ROLE_HR, UserProfile.ROLE_INTERVIEWER}:
            return Response({'error': 'HR Manager can only invite HR or Interviewer users.'}, status=status.HTTP_403_FORBIDDEN)

        if inviter.role == UserProfile.ROLE_HR and role != UserProfile.ROLE_INTERVIEWER:
            return Response({'error': 'HR can only invite Interviewer users.'}, status=status.HTTP_403_FORBIDDEN)

        company = inviter.company
        company_domain = (company.domain or '').strip().lower()
        if not company_domain:
            return Response({'error': 'Company domain is not configured.'}, status=status.HTTP_400_BAD_REQUEST)

        invitee_domain = _email_domain(invitee_email)
        if not invitee_domain:
            return Response({'email': ['Invalid email address.']}, status=status.HTTP_400_BAD_REQUEST)
        if invitee_domain != company_domain:
            return Response({'email': [f'Invitee email domain must match company domain ({company_domain}).']}, status=status.HTTP_400_BAD_REQUEST)
        if invitee_domain in _free_email_domains():
            return Response({'email': ['Free email domains are not allowed for internal roles.']}, status=status.HTTP_400_BAD_REQUEST)

        # Already registered?
        if UserProfile.objects.filter(email=invitee_email).exists():
            return Response({'email': ['A user with this email already exists.']}, status=status.HTTP_400_BAD_REQUEST)



        # Prevent multiple pending invites
        existing_pending = UserInvitation.objects.filter(company=company, email=invitee_email, status=UserInvitation.STATUS_PENDING).first()
        if existing_pending and not existing_pending.is_expired():
            return Response({'email': ['A pending invitation already exists for this email.']}, status=status.HTTP_409_CONFLICT)

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
            frontend_base = 'http://localhost:3000'
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
@permission_classes([IsAuthenticated])
def cancel_invite_view(request, token):
    """
    Cancel a pending invitation.
    Uses authenticated user from request.user.
    """
    try:
        requester = getattr(request.user, 'profile', None)
        if not requester or not requester.role:
            return Response({'error': 'User profile not found.'}, status=status.HTTP_403_FORBIDDEN)

        if _is_application_admin_email(requester.email):
            return Response({'error': 'Application Admin cannot cancel invitations.'}, status=status.HTTP_403_FORBIDDEN)

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
@permission_classes([IsAuthenticated])
def resend_invite_view(request, token):
    """
    Resend a pending invitation. Regenerates the temporary password.
    Uses authenticated user from request.user.
    """
    try:
        requester = getattr(request.user, 'profile', None)
        if not requester or not requester.role:
            return Response({'error': 'User profile not found.'}, status=status.HTTP_403_FORBIDDEN)

        if _is_application_admin_email(requester.email):
            return Response({'error': 'Application Admin cannot resend invitations.'}, status=status.HTTP_403_FORBIDDEN)

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

        frontend_base = getattr(settings, 'FRONTEND_BASE_URL', None) or os.environ.get('FRONTEND_BASE_URL') or 'http://localhost:3000'
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



        name_parts = full_name.split(' ', 1)
        first_name = name_parts[0].strip()
        last_name = name_parts[1].strip() if len(name_parts) > 1 else ''

        # Use get_or_create to handle the case where an auth_user already exists
        # (e.g., the person was previously added as an interview panel member,
        # which creates an auth_user row without a UserProfile).
        user, auth_created = User.objects.get_or_create(
            username=email,
            defaults={
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
            }
        )
        # Always set the real password (panel-member accounts have a random temp password)
        user.set_password(new_password)
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.save()

        profile = UserProfile.objects.create(
            first_name=first_name,
            last_name=last_name if last_name else None,
            email=email,
            password=None,  # deprecated
            role=inv.role,
            organization_name=inv.company.name,
            company=inv.company,
            user=user,
            # Hierarchy: link to the Admin or HR Manager who invited this user.
            # inv.invited_by acts as both the creator (static) and initial manager (dynamic).
            invited_by_profile=inv.invited_by,
            manager=inv.invited_by,
            is_approved=True, # Auto-approve users invited by an approved admin/manager
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
@permission_classes([IsAuthenticated])
def team_members_view(request):
    """
    List team members and invitation details.

    Identity is taken from the verified JWT Bearer token (request.user).
    No query params needed for authentication.

    Access rules:
    - application_admin : can view all companies' users + invites
    - company_admin     : can view their own hierarchy (HRMs + HRs they invited)
    - hr_manager        : can view only themselves + HRs they directly invited
    - hr / others       : forbidden (403)
    """
    try:
        # SECURITY FIX: Identity comes from the verified JWT token (request.user),
        # NOT from an easily-spoofed ?requester_email= query parameter.
        # @permission_classes([IsAuthenticated]) already validated the JWT above.
        jwt_user = request.user

        # Check if this is the Platform Application Admin (Django superuser or specific email)
        is_app_admin = _is_application_admin_email(getattr(jwt_user, 'email', ''))

        requester_profile = None
        if not is_app_admin:
            requester_profile = (
                UserProfile.objects
                .filter(user=jwt_user)
                .select_related('company')
                .first()
            )
            if not requester_profile or not requester_profile.company:
                return Response({'error': 'Your account has no company assigned.'}, status=status.HTTP_403_FORBIDDEN)
            if requester_profile.role not in {UserProfile.ROLE_COMPANY_ADMIN, UserProfile.ROLE_HR_MANAGER, UserProfile.ROLE_HR, UserProfile.ROLE_INTERVIEWER}:
                return Response({'error': 'Forbidden. Only Company Admins, HR Managers, HRs, and Interviewers can view team members.'}, status=status.HTTP_403_FORBIDDEN)

        if is_app_admin:
            members_qs = UserProfile.objects.select_related('company').order_by('company__name', 'email')
            invites_qs = UserInvitation.objects.select_related('company', 'invited_by').order_by('-created_at')
        else:
            company = requester_profile.company
            role = (requester_profile.role or '').strip().lower()

            if role == UserProfile.ROLE_HR_MANAGER:
                # HR Manager: sees only members they directly invited
                # + invitations they personally sent
                scoped_ids = get_scoped_user_ids(requester_profile)  # [self + their HRs]
                
                # NEW: Add all interviewers from the same Admin's tree
                from .._imports import get_admin_tree_interviewer_ids
                interviewer_ids = get_admin_tree_interviewer_ids(requester_profile)
                all_member_ids = list(set(scoped_ids + interviewer_ids))

                members_qs = (
                    UserProfile.objects.filter(
                        id__in=all_member_ids,
                        company=company,
                    )
                    .exclude(role=UserProfile.ROLE_APPLICATION_ADMIN)
                    .select_related('company')
                    .order_by('email')
                )
                invites_qs = (
                    UserInvitation.objects.filter(
                        company=company,
                        invited_by=requester_profile,
                    )
                    .select_related('company', 'invited_by')
                    .order_by('-created_at')
                )
            elif role in {UserProfile.ROLE_HR, UserProfile.ROLE_INTERVIEWER}:
                # HR/Interviewer: sees themselves + all interviewers in the same admin tree
                scoped_ids = get_scoped_user_ids(requester_profile)
                from .._imports import get_admin_tree_interviewer_ids
                interviewer_ids = get_admin_tree_interviewer_ids(requester_profile)
                all_member_ids = list(set(scoped_ids + interviewer_ids))

                members_qs = (
                    UserProfile.objects.filter(
                        id__in=all_member_ids,
                        company=company,
                    )
                    .exclude(role=UserProfile.ROLE_APPLICATION_ADMIN)
                    .select_related('company')
                    .order_by('email')
                )
                invites_qs = UserInvitation.objects.none()
            else:
                # Company Admin: sees their own HR Managers + those HRMs' HRs
                # (not other Company Admins' sub-trees)
                scoped_ids = get_scoped_user_ids(requester_profile)  # [self + HRMs + HRs]
                members_qs = (
                    UserProfile.objects.filter(
                        id__in=scoped_ids,
                        company=company,
                    )
                    .exclude(role=UserProfile.ROLE_APPLICATION_ADMIN)
                    .select_related('company')
                    .order_by('email')
                )
                # Invitations sent by this Admin OR by any HRM under this Admin
                # Use a single query to find HRM IDs (no per-item loop)
                hrm_ids = list(
                    UserProfile.objects.filter(
                        id__in=scoped_ids,
                        role=UserProfile.ROLE_HR_MANAGER,
                        company=company,
                    ).values_list('id', flat=True)
                )
                invites_qs = (
                    UserInvitation.objects.filter(
                        company=company,
                        invited_by_id__in=[requester_profile.id] + hrm_ids,
                    )
                    .select_related('company', 'invited_by')
                    .order_by('-created_at')
                )

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
                'is_active': getattr(u, 'is_active', True),
                'deactivated_at': u.deactivated_at.isoformat() if getattr(u, 'deactivated_at', None) else None,
                'deactivation_reason': getattr(u, 'deactivation_reason', None),
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
                'requester_email': getattr(jwt_user, 'email', None),
                'members': members,
                'invitations': invitations,
            },
            status=status.HTTP_200_OK,
        )
    except Exception as e:
        return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['GET', 'POST', 'PUT'])
@permission_classes([IsAuthenticated])
def profile_view(request):
    """
    Return or update the profile of the authenticated user.
    """
    try:
        # SECURITY FIX: Use the authenticated user from the JWT token.
        # This prevents "Hijacking" by searching for other users' emails.
        profile = getattr(request.user, 'profile', None)
        if not profile:
            return Response({'error': 'User profile not found.'}, status=status.HTTP_404_NOT_FOUND)

        if request.method == 'GET':
            return Response({
                'id': profile.id,
                'email': profile.email,
                'first_name': profile.first_name,
                'last_name': profile.last_name,
                'role': profile.role,
                'organization_name': profile.organization_name,
                'avatar': profile.avatar.url if profile.avatar else None,
                'updated_at': profile.updated_at.isoformat() if profile.updated_at else None,
                'company': {
                    'id': profile.company.id,
                    'name': profile.company.name,
                    'domain': profile.company.domain,
                } if profile.company else None,
            }, status=status.HTTP_200_OK)

        # For POST/PUT
        else:
            # Note: We ignore any 'email' passed in the body for security.
            # Only the authenticated user's profile found above is modified.

            # Extract fields
            full_name = request.data.get('full_name')
            avatar = request.FILES.get('avatar')

            # SECURITY: We no longer allow the user to change their own 'role' 
            # or 'organization_name' here to prevent self-promotion.
            
            if full_name:
                name_parts = full_name.strip().split(' ')
                profile.first_name = name_parts[0]
                profile.last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''
            
            if avatar:
                profile.avatar = avatar
            elif request.data.get('delete_avatar') == 'true':
                profile.avatar = None
            
            profile.save()

            return Response({
                'message': 'Profile updated successfully!',
                'id': profile.id,
                'email': profile.email,
                'full_name': f"{profile.first_name} {profile.last_name}".strip(),
                'avatar': profile.avatar.url if profile.avatar else None,
            }, status=status.HTTP_200_OK)
    except Exception as e:
        import traceback
        print(f"Error in profile_view: {str(e)}")
        print(traceback.format_exc())
        return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_team_member_view(request):
    """
    Quickly add an interviewer (team member) to the company.
    Expected body: { "name": "...", "email": "..." }
    """
    try:
        requester_profile = getattr(request.user, 'profile', None)
        if not requester_profile or not requester_profile.company:
            return Response({'error': 'Your account has no company assigned.'}, status=status.HTTP_403_FORBIDDEN)
        
        if requester_profile.role not in {UserProfile.ROLE_COMPANY_ADMIN, UserProfile.ROLE_HR_MANAGER}:
            return Response({'error': 'Only Company Admins and HR Managers can add team members.'}, status=status.HTTP_403_FORBIDDEN)

        name = (request.data.get('name') or '').strip()
        email = _normalize_email(request.data.get('email', ''))

        if not name or not email:
            return Response({'error': 'Name and Email are required.'}, status=status.HTTP_400_BAD_REQUEST)

        # Domain Validation Logic
        company = requester_profile.company
        company_domain = (company.domain or '').strip().lower()
        
        if not company_domain:
            return Response({'error': 'Your company domain is not configured. Please contact support.'}, status=status.HTTP_400_BAD_REQUEST)

        invitee_domain = _email_domain(email)
        if not invitee_domain:
            return Response({'error': 'Please provide a valid email address.'}, status=status.HTTP_400_BAD_REQUEST)

        # 1. Block free email domains
        if invitee_domain in _free_email_domains():
            return Response({
                'error': f'Generic email accounts (like {invitee_domain}) are not allowed for interviewers. Please use an official "{company_domain}" email.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # 2. Enforce strict company domain match
        if invitee_domain != company_domain:
            return Response({
                'error': f'You can only add team members with an official "{company_domain}" email address. "{invitee_domain}" belongs to another organization.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Check if already exists
        existing = UserProfile.objects.filter(email=email).first()
        if existing:
            if existing.company_id != requester_profile.company_id:
                return Response({'error': 'A user with this email already exists in another company.'}, status=status.HTTP_409_CONFLICT)
            
            return Response({
                'message': 'User already exists in your team.',
                'member': {
                    'id': existing.id,
                    'first_name': existing.first_name,
                    'last_name': existing.last_name,
                    'email': existing.email,
                    'role': existing.role,
                }
            }, status=status.HTTP_200_OK)

        # Create new user
        name_parts = name.split(' ', 1)
        first_name = name_parts[0].strip()
        last_name = name_parts[1].strip() if len(name_parts) > 1 else ''

        # Use get_or_create to handle the case where an auth_user already exists
        # (e.g., the person was previously added as an interview panel member,
        # which creates an auth_user row without a UserProfile).
        temp_password = _generate_temp_password(12)
        user, auth_created = User.objects.get_or_create(
            username=email,
            defaults={
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
            }
        )
        if auth_created:
            user.set_password(temp_password)
            user.save()
        else:
            # Reuse the existing auth_user; update display fields if needed
            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            user.save(update_fields=['first_name', 'last_name', 'email'])

        new_profile = UserProfile.objects.create(
            user=user,
            email=email,
            first_name=first_name,
            last_name=last_name or None,
            role=UserProfile.ROLE_INTERVIEWER,
            company=requester_profile.company,
            organization_name=requester_profile.company.name,
            manager=requester_profile,
            invited_by_profile=requester_profile,
            is_approved=True, # Auto-approve team members added by admin
        )

        return Response({
            'message': 'Team member added successfully.',
            'member': {
                'id': new_profile.id,
                'first_name': new_profile.first_name,
                'last_name': new_profile.last_name,
                'email': new_profile.email,
                'role': new_profile.role,
            }
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        import traceback
        print(f"Error in add_team_member_view: {str(e)}")
        print(traceback.format_exc())
        return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
