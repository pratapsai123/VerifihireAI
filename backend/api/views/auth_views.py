from .._imports import *
from .._imports import _otp_expiry_seconds, _email_domain, _free_email_domains


@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request):
    """Root endpoint that displays available API endpoints."""
    return Response({
        'message': 'FaceD Interview Backend API',
        'version': '1.0',
        'endpoints': {'register': '/api/register/', 'login': '/api/login/', 'admin': '/admin/'},
        'documentation': 'Use POST requests to /api/register/ and /api/login/'
    })


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def send_otp_view(request):
    """
    Send OTP to email for verification.
    Expected request body:
    {
        "email": "user@company.com"
    }
    """
    try:
        email = request.data.get('email', '').strip().lower()
        context = request.data.get('context', '').strip().lower()
        
        if not email:
            return Response(
                {'error': 'Email is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate email format
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, email):
            return Response(
                {'error': 'Invalid email format.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if user already exists (only for registration flow)
        if context == 'register':
            if UserProfile.objects.filter(email=email).exists():
                return Response(
                    {'email': ['Account with this email already exists. Please login.']},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Enforce business-domain signup for company registration
            domain = _email_domain(email)
            if not domain:
                return Response({'error': 'Invalid email address.'}, status=status.HTTP_400_BAD_REQUEST)
            if domain in _free_email_domains():
                return Response(
                    {
                        'businessEmail': ['Please use your company email (free email domains like Gmail/Yahoo are not allowed for company registration).'],
                        'email': ['Please use your company email.']
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Check company admin count for this domain
            domain = _email_domain(email)
            if domain:
                company = Company.objects.filter(domain=domain).first()
                if company and UserProfile.objects.filter(company=company, role=UserProfile.ROLE_COMPANY_ADMIN).count() >= 10:
                    return Response(
                        {
                            'businessEmail': ['This organization already has 10 registered admins. Please request an invitation from your Company Admin.'],
                            'organizationName': ['This organization has reached its admin limit.']
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )
        else:
            # For non-registration flows (forgot password, etc.), verify email exists
            user_exists = UserProfile.objects.filter(email=email).exists() or \
                          User.objects.filter(email=email).exists() or \
                          User.objects.filter(username=email).exists()
            
            if not user_exists:
                return Response(
                    {'error': 'Incorrect email or account does not exist.'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Enforce business-domain policy for forgot password (except for platform admins)
            domain = _email_domain(email)
            if domain in _free_email_domains() and not _is_application_admin_email(email):
                return Response(
                    {'error': 'Password reset is only allowed for business email accounts. Platform admins, please contact support if you are using a personal email.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # --- Global OTP Brute Force Check ---
        otp_max_attempts = getattr(settings, 'OTP_MAX_ATTEMPTS', 5)
        otp_lockout_minutes = getattr(settings, 'OTP_LOCKOUT_MINUTES', 15)
        
        recent_failures = list(OtpAttemptLog.objects.filter(
            email=email, succeeded=False
        ).order_by('-attempted_at')[:otp_max_attempts])

        if len(recent_failures) == otp_max_attempts:
            latest_failure = recent_failures[0]
            nth_failure = recent_failures[-1]
            if (latest_failure.attempted_at - nth_failure.attempted_at) <= timedelta(minutes=otp_lockout_minutes):
                lock_expires_at = latest_failure.attempted_at + timedelta(minutes=otp_lockout_minutes)
                if timezone.now() < lock_expires_at:
                    remaining_time = lock_expires_at - timezone.now()
                    remaining_seconds = max(1, int(remaining_time.total_seconds()))
                    return Response(
                        {'error': f'Too many failed OTP attempts. Please wait {remaining_seconds} seconds.'},
                        status=status.HTTP_429_TOO_MANY_REQUESTS
                    )

        # --- OTP Cooldown Check ---
        otp_cooldown_seconds = getattr(settings, 'OTP_RESEND_COOLDOWN_SECONDS', 120)
        cooldown_threshold = timezone.now() - timedelta(seconds=otp_cooldown_seconds)
        
        recent_otp = EmailOTP.objects.filter(
            email=email,
            created_at__gte=cooldown_threshold
        ).order_by('-created_at').first()
        
        if recent_otp:
            cooldown_expires_at = recent_otp.created_at + timedelta(seconds=otp_cooldown_seconds)
            remaining_time = cooldown_expires_at - timezone.now()
            remaining_seconds = max(1, int(remaining_time.total_seconds()))
            return Response(
                {'error': f'Please wait {remaining_seconds} seconds before requesting a new OTP.'},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )

        # Generate OTP
        otp = EmailOTP.generate_otp()
        expires_in = _otp_expiry_seconds()
        expires_minutes = max(1, int(round(expires_in / 60)))
        
        # Invalidate previous OTPs for this email
        EmailOTP.objects.filter(email=email, is_verified=False).update(is_verified=True)
        
        # Create new OTP
        email_otp = EmailOTP.objects.create(email=email, otp=otp)
        
        # Send email with OTP
        try:
            send_mail(
                subject='VeriFiHire - Email Verification OTP',
                message=f'Your OTP for email verification is: {otp}\n\nThis OTP is valid for {expires_minutes} minutes.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
        except Exception as e:
            # Issue 2 fix: NEVER return the OTP in the response body.
            # Fail closed — if email delivery fails, the user must retry.
            print(f"Email sending failed: {str(e)}")
            return Response(
                {'error': 'Email delivery failed. Please try again or contact support.'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        return Response(
            {
                'message': 'OTP sent to your email. Please check your inbox.',
                'email': email,
                'expires_in': expires_in
            },
            status=status.HTTP_200_OK
        )
        
    except Exception as e:
        import traceback
        error_message = str(e)
        # Check if it's a database error (table doesn't exist)
        if 'no such table' in error_message.lower() or 'relation' in error_message.lower() or 'does not exist' in error_message.lower():
            error_message = 'Database table not found. Please run migrations: python manage.py makemigrations && python manage.py migrate'
        print(f"Error in send_otp_view: {error_message}")
        print(traceback.format_exc())
        return Response(
            {'error': f'An error occurred: {error_message}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def verify_otp_view(request):
    """
    Verify OTP for email.
    Expected request body:
    {
        "email": "user@company.com",
        "otp": "123456"
    }
    """
    try:
        email = request.data.get('email', '').strip().lower()
        otp = request.data.get('otp', '').strip()
        
        if not email:
            return Response(
                {'error': 'Email is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not otp:
            return Response(
                {'error': 'OTP is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Find the most recent unverified OTP for this email
        try:
            email_otp = EmailOTP.objects.filter(
                email=email,
                is_verified=False
            ).order_by('-created_at').first()
            
            if not email_otp:
                return Response(
                    {'error': 'No OTP found for this email. Please request a new OTP.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if email_otp.is_expired():
                return Response(
                    {'error': 'OTP has expired. Please request a new OTP.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Global OTP Brute Force Check
            otp_max_attempts = getattr(settings, 'OTP_MAX_ATTEMPTS', 5)
            otp_lockout_minutes = getattr(settings, 'OTP_LOCKOUT_MINUTES', 15)
            
            recent_failures = list(OtpAttemptLog.objects.filter(
                email=email, succeeded=False
            ).order_by('-attempted_at')[:otp_max_attempts])

            if len(recent_failures) == otp_max_attempts:
                latest_failure = recent_failures[0]
                nth_failure = recent_failures[-1]
                if (latest_failure.attempted_at - nth_failure.attempted_at) <= timedelta(minutes=otp_lockout_minutes):
                    lock_expires_at = latest_failure.attempted_at + timedelta(minutes=otp_lockout_minutes)
                    if timezone.now() < lock_expires_at:
                        remaining_time = lock_expires_at - timezone.now()
                        remaining_seconds = max(1, int(remaining_time.total_seconds()))
                        return Response(
                            {'error': f'Too many failed OTP attempts. Please wait {remaining_seconds} seconds.'},
                            status=status.HTTP_429_TOO_MANY_REQUESTS
                        )
            
            if email_otp.otp != otp:
                OtpAttemptLog.objects.create(email=email, succeeded=False)
                failures = list(OtpAttemptLog.objects.filter(email=email, succeeded=False).order_by('-attempted_at')[:otp_max_attempts])
                f_count = sum(1 for f in failures if (failures[0].attempted_at - f.attempted_at) <= timedelta(minutes=otp_lockout_minutes))
                remaining = max(0, otp_max_attempts - f_count)
                
                return Response(
                    {'error': f'Invalid OTP. {remaining} attempt(s) remaining.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Mark OTP as verified and clear global failures
            email_otp.is_verified = True
            email_otp.save()
            OtpAttemptLog.objects.filter(email=email, succeeded=False).delete()
            
            return Response(
                {
                    'message': 'Email verified successfully!',
                    'verified': True
                },
                status=status.HTTP_200_OK
            )
            
        except EmailOTP.DoesNotExist:
            return Response(
                {'error': 'Invalid OTP or email.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
    except Exception as e:
        return Response(
            {'error': f'An error occurred: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password_view(request):
    """
    Reset password after email OTP verification.
    Expected request body:
    {
        "email": "user@company.com",
        "otp": "123456",
        "new_password": "password123",
        "confirm_password": "password123"
    }
    """
    try:
        email = request.data.get('email', '').strip().lower()
        otp = request.data.get('otp', '').strip()
        new_password = request.data.get('new_password', '')
        confirm_password = request.data.get('confirm_password', '')

        if not email:
            return Response({'email': ['Email is required.']}, status=status.HTTP_400_BAD_REQUEST)
        if not otp:
            return Response({'otp': ['OTP is required.']}, status=status.HTTP_400_BAD_REQUEST)
        if not new_password:
            return Response({'new_password': ['New password is required.']}, status=status.HTTP_400_BAD_REQUEST)
        if not confirm_password:
            return Response({'confirm_password': ['Confirm password is required.']}, status=status.HTTP_400_BAD_REQUEST)
        
        if new_password != confirm_password:
            return Response({'confirm_password': ['Passwords do not match.']}, status=status.HTTP_400_BAD_REQUEST)
        if len(new_password) < 6:
            return Response({'new_password': ['Password must be at least 6 characters long.']}, status=status.HTTP_400_BAD_REQUEST)

        # Find the most recent verified OTP for this email
        email_otp = EmailOTP.objects.filter(email=email, is_verified=True).order_by('-created_at').first()
        if not email_otp:
            return Response({'error': 'Please verify OTP first.'}, status=status.HTTP_400_BAD_REQUEST)
        if email_otp.is_expired():
            return Response({'error': 'OTP has expired. Please request a new OTP.'}, status=status.HTTP_400_BAD_REQUEST)
        if email_otp.otp != otp:
            return Response({'error': 'Invalid OTP. Please try again.'}, status=status.HTTP_400_BAD_REQUEST)

        # Update user password (prefer Django auth user hashing)
        user_profile = UserProfile.objects.filter(email=email).first()

        if user_profile and user_profile.user:
            # Security check: Prevent password reuse (check current hashed password and legacy plaintext)
            if user_profile.user.check_password(new_password) or user_profile.password == new_password or user_profile.old_password == new_password:
                return Response({'error': 'This password has already been used. Please choose a new password.'}, status=status.HTTP_400_BAD_REQUEST)
            
            user_profile.user.set_password(new_password)
            user_profile.user.save()
            # Capture current password to old_password before clearing it
            if user_profile.password:
                user_profile.old_password = user_profile.password
                user_profile.password = None
            user_profile.save(update_fields=['old_password', 'password', 'updated_at'])
        elif user_profile:
            # Legacy profile update
            if user_profile.password == new_password or user_profile.old_password == new_password:
                 return Response({'error': 'This password has already been used. Please choose a new password.'}, status=status.HTTP_400_BAD_REQUEST)
            
            user_profile.old_password = user_profile.password
            user_profile.password = new_password
            user_profile.save(update_fields=['old_password', 'password', 'updated_at'])
        else:
            # Allow password reset for application admin accounts (no UserProfile)
            auth_user = User.objects.filter(username=email).first() or User.objects.filter(email=email).first()
            if not auth_user:
                return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
            
            # Security check: Prevent password reuse
            if auth_user.check_password(new_password):
                return Response({'error': 'This password has already been used. Please choose a new password.'}, status=status.HTTP_400_BAD_REQUEST)
            
            auth_user.set_password(new_password)
            auth_user.save()

        return Response({'message': 'Password reset successful.'}, status=status.HTTP_200_OK)

    except Exception as e:
        import traceback
        print(f"Error in reset_password_view: {str(e)}")
        print(traceback.format_exc())
        return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])  # Issue 3 fix: was AllowAny (credential stuffing oracle)
def verify_current_password_view(request):
    """
    Verify current password for the authenticated user.
    Email is taken from the JWT token (request.user), NOT the request body.
    """
    try:
        # Issue 3 fix: use authenticated user's email from token, not from request body
        email = request.user.email or request.user.username
        password = request.data.get('password', '')

        if not password:
            return Response({'error': 'Password is required.'}, status=status.HTTP_400_BAD_REQUEST)

        # Find user
        user_profile = UserProfile.objects.filter(email=email).first()
        auth_user = request.user

        # Verify password
        if not auth_user.check_password(password):
            # Check legacy profile password if it exists
            if user_profile and user_profile.password == password:
                pass # Proceed
            else:
                return Response({'error': 'Incorrect current password.'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'message': 'Password verified successfully!'}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])  # Issue 3 fix: was AllowAny
def change_password_view(request):
    """
    Change password for an authenticated user.
    Expected request body:
    {
        "email": "user@company.com",
        "current_password": "oldpassword123",
        "new_password": "password123",
        "confirm_password": "password123"
    }
    """
    try:
        # Issue 3 fix: get email from the authenticated JWT token, not the request body
        email = request.user.email or request.user.username
        current_password = request.data.get('current_password', '')
        new_password = request.data.get('new_password', '')
        confirm_password = request.data.get('confirm_password', '')
        if not current_password:
            return Response({'error': 'Current password is required.'}, status=status.HTTP_400_BAD_REQUEST)
        if not new_password:
            return Response({'error': 'New password is required.'}, status=status.HTTP_400_BAD_REQUEST)
        if not confirm_password:
            return Response({'error': 'Confirm password is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if new_password != confirm_password:
            return Response({'error': 'Passwords do not match.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if len(new_password) < 6:
            return Response({'error': 'Password must be at least 6 characters long.'}, status=status.HTTP_400_BAD_REQUEST)

        # Find user
        user_profile = UserProfile.objects.filter(email=email).first()
        auth_user = None

        if user_profile and user_profile.user:
            auth_user = user_profile.user
        else:
            auth_user = User.objects.filter(username=email).first() or User.objects.filter(email=email).first()

        if not auth_user:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Verify current password
        if not auth_user.check_password(current_password):
            # Check legacy profile password if it exists
            if user_profile and user_profile.password == current_password:
                pass # Proceed
            else:
                return Response({'error': 'Incorrect current password.'}, status=status.HTTP_400_BAD_REQUEST)

        # Security check: Prevent password reuse
        if auth_user.check_password(new_password):
            return Response({'error': 'New password cannot be the same as the current password.'}, status=status.HTTP_400_BAD_REQUEST)

        # Update password
        auth_user.set_password(new_password)
        auth_user.save()

        # Sync with UserProfile if needed
        if user_profile:
            user_profile.old_password = current_password
            user_profile.password = None
            user_profile.updated_at = timezone.now()
            user_profile.save(update_fields=['old_password', 'password', 'updated_at'])

        return Response({'message': 'Password updated successfully!'}, status=status.HTTP_200_OK)

    except Exception as e:
        import traceback
        print(f"Error in change_password_view: {str(e)}")
        print(traceback.format_exc())
        return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    """
    Register a new user with ALL signup form fields.
    Expected request body:
    {
        "first_name": "John",
        "last_name": "Doe",
        "email": "user@company.com",
        "business_email": "user@company.com",
        "role": "recruiter",
        "organization_name": "ABC Company",
        "password": "password123"
    }
    """
    try:
        # Get all fields from request
        full_name = request.data.get('full_name', '').strip()
        email = request.data.get('email', '').strip().lower() or request.data.get('business_email', '').strip().lower()
        organization_name = request.data.get('organization_name', '').strip()
        password = request.data.get('password', '')
        
        # Support legacy fields for backward compatibility
        if not full_name:
            first_name = request.data.get('first_name', '').strip()
            last_name = request.data.get('last_name', '').strip()
            if first_name:
                full_name = f"{first_name} {last_name}".strip()
        
        if not full_name and request.data.get('name'):
            full_name = request.data.get('name', '').strip()
        
        # Split full_name into first_name and last_name
        name_parts = full_name.split(' ', 1) if full_name else []
        first_name = name_parts[0] if name_parts else ''
        last_name = name_parts[1] if len(name_parts) > 1 else ''

        # Validation
        if not full_name or not first_name:
            return Response(
                {'error': 'Full name is required.', 'full_name': ['This field is required.']},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not email:
            return Response(
                {'error': 'Business email is required.', 'email': ['This field is required.']},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not organization_name:
            return Response(
                {'error': 'Organization name is required.', 'organization_name': ['This field is required.']},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not password:
            return Response(
                {'error': 'Password is required.', 'password': ['This field is required.']},
                status=status.HTTP_400_BAD_REQUEST
            )

        if len(password) < 6:
            return Response(
                {'error': 'Password must be at least 6 characters long.', 'password': ['Password must be at least 6 characters.']},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Enforce business-domain signup for company registration (platform admin can be gmail, but is created separately)
        domain = _email_domain(email)
        if not domain:
            return Response({'error': 'Invalid email address.'}, status=status.HTTP_400_BAD_REQUEST)
        if domain in _free_email_domains():
            return Response(
                {'error': 'Please use your company email (free email domains are not allowed for company registration).', 'email': ['Please use your company email.']},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if email already exists in UserProfile
        if UserProfile.objects.filter(email=email).exists():
            return Response(
                {'error': 'A user with this email already exists.', 'email': ['A user with this email already exists.']},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verify that email has been verified via OTP
        verified_otp = EmailOTP.objects.filter(
            email=email,
            is_verified=True
        ).order_by('-created_at').first()
        
        if not verified_otp:
            return Response(
                {'error': 'Please verify your email first by entering the OTP.', 'email': ['Email verification required.']},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if OTP verification is recent (within 30 minutes)
        if timezone.now() > verified_otp.created_at + timedelta(minutes=30):
            return Response(
                {'error': 'Email verification has expired. Please verify your email again.', 'email': ['Email verification expired.']},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create/get company tenant (registration is ONLY allowed for the very first user of a company)
        # Check if this domain is already registered to a different organization name
        existing_company_with_domain = Company.objects.filter(domain=domain).first()
        
        if existing_company_with_domain:
            # If domain exists, we must use this company
            if existing_company_with_domain.name.lower() != organization_name.lower():
                return Response(
                    {'organizationName': [f"The email domain '{domain}' is already registered to organization '{existing_company_with_domain.name}'. Please enter the organization name correctly."]},
                    status=status.HTTP_400_BAD_REQUEST
                )
            company = existing_company_with_domain
        else:
            # Domain not registered yet, find or create company by name (case-insensitive)
            company = Company.objects.filter(name__iexact=organization_name).first()
        if not company:
                company = Company.objects.create(
                    name=organization_name,
                    approval_status=Company.APPROVAL_PENDING
                )
        
        # Ensure company domain is set if not already
        if not company.domain:
            company.domain = domain
            company.save(update_fields=['domain'])
        elif company.domain != domain:
             return Response(
                {'organization_name': [f"Organization '{company.name}' is already registered with a different domain. Please contact your admin."]},
                status=status.HTTP_400_BAD_REQUEST
            )

        if UserProfile.objects.filter(company=company, role=UserProfile.ROLE_COMPANY_ADMIN).count() >= 10:
            return Response(
                {
                    'businessEmail': ['This organization already has 10 registered admins. Please request an invitation from your Company Admin.'],
                    'organizationName': ['This organization has reached its admin limit.']
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Always create Django User for authentication (hashed password)
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )

        # Create user profile (role is assigned automatically per PDF: first user is COMPANY_ADMIN)
        user_profile = UserProfile.objects.create(
            first_name=first_name,
            last_name=last_name if last_name else None,
            email=email,
            password=None,  # deprecated field
            role=UserProfile.ROLE_COMPANY_ADMIN,
            organization_name=organization_name,
            company=company,
            user=user,
            is_approved=False,
        )

        # Notify platform admin about the new company registration
        try:
            admin_email_list = list(
                User.objects.filter(application_admin_profile__isnull=False).values_list('email', flat=True)
            )
            if admin_email_list:
                send_mail(
                    subject='VeriFiHire - New Company Registration Pending Approval',
                    message=(
                        f'A new company has registered and is pending your approval.\n\n'
                        f'Company: {organization_name}\n'
                        f'Admin: {first_name} {last_name}\n'
                        f'Email: {email}\n\n'
                        f'Please log in to the platform admin dashboard to review and approve or reject this registration.'
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=admin_email_list,
                    fail_silently=True,
                )
        except Exception as notify_err:
            print(f'Admin notification email failed: {notify_err}')

        return Response(
            {
                'message': 'Registration successful! Your account is pending superadmin approval.',
                'pending_approval': True,
                'user': {
                    'id': user_profile.id,
                    'first_name': user_profile.first_name,
                    'last_name': user_profile.last_name,
                    'email': user_profile.email,
                    'role': user_profile.role,
                    'organization_name': user_profile.organization_name,
                    'registration_timestamp': user_profile.registration_timestamp.isoformat(),
                }
            },
            status=status.HTTP_201_CREATED
        )

    except Exception as e:
        return Response(
            {'error': f'An error occurred: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """
    Login a user - Step 1: Verify email and password, then send OTP.
    Expected request body:
    {
        "email": "user@example.com",
        "password": "password123"
    }
    """
    try:
        email = request.data.get('email', '').strip().lower()
        password = request.data.get('password', '')

        # Validation
        if not email:
            return Response(
                {'email': ['Email is required.']},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not password:
            return Response(
                {'password': ['Password is required.']},
                status=status.HTTP_400_BAD_REQUEST
            )

        # --- Brute Force Check ---
        login_max_attempts = getattr(settings, 'LOGIN_MAX_ATTEMPTS', 5)
        login_lockout_minutes = getattr(settings, 'LOGIN_LOCKOUT_MINUTES', 15)
        
        recent_failures = list(LoginAttemptLog.objects.filter(
            email=email, succeeded=False
        ).order_by('-attempted_at')[:login_max_attempts])

        if len(recent_failures) == login_max_attempts:
            latest_failure = recent_failures[0]
            nth_failure = recent_failures[-1]
            
            # If the cluster of 5 failures happened within the lockout window
            if (latest_failure.attempted_at - nth_failure.attempted_at) <= timedelta(minutes=login_lockout_minutes):
                lock_expires_at = latest_failure.attempted_at + timedelta(minutes=login_lockout_minutes)
                if timezone.now() < lock_expires_at:
                    remaining_time = lock_expires_at - timezone.now()
                    remaining_seconds = max(1, int(remaining_time.total_seconds()))
                    return Response(
                        {'error': f'Too many failed login attempts. Please wait {remaining_seconds} seconds.'},
                        status=status.HTTP_429_TOO_MANY_REQUESTS
                    )

        user_profile = UserProfile.objects.filter(email=email).select_related('company').first()

        # Company users (UserProfile)
        if user_profile:
            if user_profile.user:
                if not user_profile.user.check_password(password):
                    LoginAttemptLog.objects.create(email=email, succeeded=False)
                    failures = list(LoginAttemptLog.objects.filter(email=email, succeeded=False).order_by('-attempted_at')[:login_max_attempts])
                    f_count = sum(1 for f in failures if (failures[0].attempted_at - f.attempted_at) <= timedelta(minutes=login_lockout_minutes))
                    remaining = max(0, login_max_attempts - f_count)
                    return Response({'error': f'Invalid email or password. {remaining} attempt(s) left.'}, status=status.HTTP_401_UNAUTHORIZED)
            else:
                # Backward compatibility: plaintext profile password (legacy)
                if user_profile.password != password:
                    LoginAttemptLog.objects.create(email=email, succeeded=False)
                    failures = list(LoginAttemptLog.objects.filter(email=email, succeeded=False).order_by('-attempted_at')[:login_max_attempts])
                    f_count = sum(1 for f in failures if (failures[0].attempted_at - f.attempted_at) <= timedelta(minutes=login_lockout_minutes))
                    remaining = max(0, login_max_attempts - f_count)
                    return Response({'error': f'Invalid email or password. {remaining} attempt(s) left.'}, status=status.HTTP_401_UNAUTHORIZED)
                # Best-effort migrate to hashed auth user on successful legacy login
                try:
                    user = User.objects.create_user(
                        username=email,
                        email=email,
                        password=password,
                        first_name=user_profile.first_name or '',
                        last_name=user_profile.last_name or '',
                    )
                    user_profile.user = user
                    user_profile.old_password = user_profile.password
                    user_profile.password = None
                    user_profile.save(update_fields=['user', 'old_password', 'password', 'updated_at'])
                except Exception as migrate_err:
                    print(f"Migration error: {migrate_err}")
                    pass

            # Check if user has been deactivated
            if not getattr(user_profile, 'is_active', True):
                return Response(
                    {'error': 'Your account has been deactivated. Please contact your company administrator.'},
                    status=status.HTTP_403_FORBIDDEN,
                )

            # Check if user and company are approved
            if not user_profile.is_approved:
                return Response({'error': 'Your account is pending superadmin approval.'}, status=status.HTTP_403_FORBIDDEN)
            
            if user_profile.company and user_profile.company.approval_status != Company.APPROVAL_APPROVED:
                if user_profile.company.approval_status == Company.APPROVAL_REJECTED:
                    return Response({
                        'error': f'Your company registration was rejected. Reason: {user_profile.company.rejected_reason or "No reason provided."}'
                    }, status=status.HTTP_403_FORBIDDEN)
                return Response({'error': 'Your company registration is pending superadmin approval.'}, status=status.HTTP_403_FORBIDDEN)
        else:
            # Application Admin users (no UserProfile): must exist in ApplicationAdmin table
            auth_user = User.objects.filter(username=email).first() or User.objects.filter(email=email).first()
            if not auth_user:
                return Response(
                    {'error': 'Your account is not registered with us.'},
                    status=status.HTTP_404_NOT_FOUND
                )
            if not auth_user.check_password(password):
                LoginAttemptLog.objects.create(email=email, succeeded=False)
                failures = list(LoginAttemptLog.objects.filter(email=email, succeeded=False).order_by('-attempted_at')[:login_max_attempts])
                f_count = sum(1 for f in failures if (failures[0].attempted_at - f.attempted_at) <= timedelta(minutes=login_lockout_minutes))
                remaining = max(0, login_max_attempts - f_count)
                return Response(
                    {'error': f'Incorrect password. {remaining} attempt(s) left.'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            if not ApplicationAdmin.objects.filter(user=auth_user).exists():
                return Response(
                    {'error': 'Your account is not registered with us.'},
                    status=status.HTTP_404_NOT_FOUND
                )
                
        # Clear old failures on successful login
        LoginAttemptLog.objects.filter(email=email, succeeded=False).delete()
        
        # --- Global OTP Brute Force Check ---
        otp_max_attempts = getattr(settings, 'OTP_MAX_ATTEMPTS', 5)
        otp_lockout_minutes = getattr(settings, 'OTP_LOCKOUT_MINUTES', 15)
        
        recent_failures = list(OtpAttemptLog.objects.filter(
            email=email, succeeded=False
        ).order_by('-attempted_at')[:otp_max_attempts])

        if len(recent_failures) == otp_max_attempts:
            latest_failure = recent_failures[0]
            nth_failure = recent_failures[-1]
            if (latest_failure.attempted_at - nth_failure.attempted_at) <= timedelta(minutes=otp_lockout_minutes):
                lock_expires_at = latest_failure.attempted_at + timedelta(minutes=otp_lockout_minutes)
                if timezone.now() < lock_expires_at:
                    remaining_time = lock_expires_at - timezone.now()
                    remaining_seconds = max(1, int(remaining_time.total_seconds()))
                    return Response(
                        {'error': f'Too many failed OTP attempts. Please wait {remaining_seconds} seconds.'},
                        status=status.HTTP_429_TOO_MANY_REQUESTS
                    )

        # --- OTP Cooldown Check ---
        # Only consider UNVERIFIED OTPs for the cooldown.
        # A verified OTP means the previous session completed successfully —
        # the user should NOT be blocked from logging in again within 2 minutes
        # (e.g. just signed up and approved, or logged out and back in quickly).
        otp_cooldown_seconds = getattr(settings, 'OTP_RESEND_COOLDOWN_SECONDS', 120)
        cooldown_threshold = timezone.now() - timedelta(seconds=otp_cooldown_seconds)
        
        recent_otp = EmailOTP.objects.filter(
            email=email,
            is_verified=False,
            created_at__gte=cooldown_threshold
        ).order_by('-created_at').first()
        
        if recent_otp:
            cooldown_expires_at = recent_otp.created_at + timedelta(seconds=otp_cooldown_seconds)
            remaining_time = cooldown_expires_at - timezone.now()
            remaining_seconds = max(1, int(remaining_time.total_seconds()))
            return Response(
                {'error': f'Please wait {remaining_seconds} seconds before requesting a new OTP.'},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )

        # Generate and send OTP for 2-step verification
        otp = EmailOTP.generate_otp()
        expires_in = _otp_expiry_seconds()
        expires_minutes = max(1, int(round(expires_in / 60)))
        
        # Invalidate previous OTPs for this email
        EmailOTP.objects.filter(email=email, is_verified=False).update(is_verified=True)
        
        # Create new OTP for login
        email_otp = EmailOTP.objects.create(email=email, otp=otp)
        
        # Send email with OTP
        try:
            send_mail(
                subject='VeriFiHire - Login Verification OTP',
                message=f'Your OTP for login verification is: {otp}\n\nThis OTP is valid for {expires_minutes} minutes.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
        except Exception as e:
            print(f"Email sending failed: {str(e)}")
            # Issue 2 fix: NEVER return the OTP in the response body on email failure.
            # Fail closed — the user must retry; they do not get the OTP as a bypass.
            return Response(
                {'error': 'Email delivery failed. Please try again or contact support.'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        # Return response indicating OTP is required
        return Response(
            {
                'message': 'Credentials verified. OTP sent to your email. Please verify to complete login.',
                'otp_required': True,
                'email': email,
                'expires_in': expires_in
            },
            status=status.HTTP_200_OK
        )

    except Exception as e:
        import traceback
        print(f"Error in login_view: {str(e)}")
        print(traceback.format_exc())
        return Response(
            {'error': f'An error occurred: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def verify_login_otp_view(request):
    """
    Login a user - Step 2: Verify OTP and complete login.
    Expected request body:
    {
        "email": "user@example.com",
        "otp": "123456"
    }
    """
    try:
        email = request.data.get('email', '').strip().lower()
        otp = request.data.get('otp', '').strip()
        
        if not email:
            return Response(
                {'error': 'Email is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not otp:
            return Response(
                {'error': 'OTP is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Find the most recent unverified OTP for this email
        try:
            email_otp = EmailOTP.objects.filter(
                email=email,
                is_verified=False
            ).order_by('-created_at').first()
            
            if not email_otp:
                return Response(
                    {'error': 'No OTP found for this email. Please login again.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if email_otp.is_expired():
                return Response(
                    {'error': 'OTP has expired. Please login again.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Global OTP Brute Force Check
            otp_max_attempts = getattr(settings, 'OTP_MAX_ATTEMPTS', 5)
            otp_lockout_minutes = getattr(settings, 'OTP_LOCKOUT_MINUTES', 15)
            
            recent_failures = list(OtpAttemptLog.objects.filter(
                email=email, succeeded=False
            ).order_by('-attempted_at')[:otp_max_attempts])

            if len(recent_failures) == otp_max_attempts:
                latest_failure = recent_failures[0]
                nth_failure = recent_failures[-1]
                if (latest_failure.attempted_at - nth_failure.attempted_at) <= timedelta(minutes=otp_lockout_minutes):
                    lock_expires_at = latest_failure.attempted_at + timedelta(minutes=otp_lockout_minutes)
                    if timezone.now() < lock_expires_at:
                        remaining_time = lock_expires_at - timezone.now()
                        remaining_seconds = max(1, int(remaining_time.total_seconds()))
                        return Response(
                            {'error': f'Too many failed OTP attempts. Please wait {remaining_seconds} seconds.'},
                            status=status.HTTP_429_TOO_MANY_REQUESTS
                        )
            
            if email_otp.otp != otp:
                OtpAttemptLog.objects.create(email=email, succeeded=False)
                failures = list(OtpAttemptLog.objects.filter(email=email, succeeded=False).order_by('-attempted_at')[:otp_max_attempts])
                f_count = sum(1 for f in failures if (failures[0].attempted_at - f.attempted_at) <= timedelta(minutes=otp_lockout_minutes))
                remaining = max(0, otp_max_attempts - f_count)
                
                return Response(
                    {'error': f'Invalid OTP. {remaining} attempt(s) remaining.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Mark OTP as verified and clear global failures
            email_otp.is_verified = True
            email_otp.save()
            OtpAttemptLog.objects.filter(email=email, succeeded=False).delete()
            
            # Prefer user profile; fallback to application admin
            user_profile = UserProfile.objects.filter(email=email).first()
            app_admin = None
            auth_user = None
            if not user_profile:
                auth_user = User.objects.filter(username=email).first() or User.objects.filter(email=email).first()
                if auth_user:
                    app_admin = ApplicationAdmin.objects.filter(user=auth_user).first()
                if not app_admin:
                    return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
            else:
                if user_profile.user:
                    auth_user = user_profile.user
                else:
                    auth_user = User.objects.filter(username=email).first() or User.objects.filter(email=email).first()
                
                # Double check approval in step 2
                if not user_profile.is_approved:
                    return Response({'error': 'Your account is pending superadmin approval.'}, status=status.HTTP_403_FORBIDDEN)
                
                if user_profile.company and user_profile.company.approval_status != Company.APPROVAL_APPROVED:
                    return Response({'error': 'Your company registration is pending superadmin approval.'}, status=status.HTTP_403_FORBIDDEN)
            
            if not auth_user:
                return Response({'error': 'Authentication user not found. Please contact support.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            refresh = RefreshToken.for_user(auth_user)
            # Add database identifier to token to force logout if DB context changes
            db_conf = settings.DATABASES['default']
            db_id = f"{db_conf.get('HOST', '127.0.0.1')}:{db_conf.get('PORT', '5432')}/{db_conf.get('NAME', 'postgres')}"
            refresh['db_name'] = db_id



            if user_profile:
                user_profile.last_login_at = timezone.now()
                user_profile.save(update_fields=['last_login_at'])
            
            # Return success response with user data and token
            response = Response(
                {
                    'message': 'Login successful!',
                    'token': str(refresh.access_token),
                    'user': {
                        'id': (user_profile.id if user_profile else app_admin.user_id),
                        'first_name': (user_profile.first_name if user_profile else (auth_user.first_name or '')),
                        'last_name': (user_profile.last_name if user_profile else (auth_user.last_name or '')),
                        'email': (user_profile.email if user_profile else (auth_user.email or auth_user.username)),
                        'role': (user_profile.role if user_profile else UserProfile.ROLE_APPLICATION_ADMIN),
                        'organization_name': (user_profile.organization_name if user_profile else None),
                        'registration_timestamp': (user_profile.registration_timestamp.isoformat() if user_profile else app_admin.created_at.isoformat()),
                    }
                },
                status=status.HTTP_200_OK
            )
            
            response.set_cookie(
                key='refresh_token',
                value=str(refresh),
                httponly=True,
                secure=settings.SESSION_COOKIE_SECURE,
                samesite='Lax',
                # Issue 7 fix: sync max_age with SIMPLE_JWT setting (was hardcoded timedelta(hours=12))
                max_age=int(settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds())
            )
            return response
            
        except Exception as e:
            return Response(
                {'error': f'An error occurred: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
    except Exception as e:
        import traceback
        print(f"Error in verify_login_otp_view: {str(e)}")
        print(traceback.format_exc())
        return Response(
            {'error': f'An error occurred: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def heartbeat_view(request):
    """
    Lightweight endpoint for proactive session validation.
    The custom DBContextJWTAuthentication already checks the DB context.
    Returns 200 if the token is valid for the current database context.
    Returns 401 via middleware/auth-class if context has changed.
    """
    return Response({'status': 'ok', 'db_name': settings.DATABASES['default']['NAME']}, status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def refresh_token_view(request):
    """
    Refresh the access token using the HTTP-only refresh_token cookie.
    """
    try:
        from rest_framework_simplejwt.exceptions import TokenError
        refresh_token = request.COOKIES.get('refresh_token')
        
        if not refresh_token:
            return Response({'error': 'Refresh token missing.'}, status=status.HTTP_401_UNAUTHORIZED)
            
        try:
            refresh = RefreshToken(refresh_token)
            
            # 🛡️ SECURITY: Validate database context for the refresh token
            db_conf = settings.DATABASES['default']
            current_db_id = f"{db_conf.get('HOST', '127.0.0.1')}:{db_conf.get('PORT', '5432')}/{db_conf.get('NAME', 'postgres')}"
            token_db_id = refresh.payload.get('db_name')

            if token_db_id != current_db_id:
                return Response({
                    "detail": "Database context mismatch. Please login again.",
                    "code": "db_mismatch"
                }, status=status.HTTP_401_UNAUTHORIZED)

            # Ensure custom claims like db_name are copied to the new access token
            
            access_token = refresh.access_token
            
            access_token['db_name'] = current_db_id
            
            response = Response(
                {
                    'token': str(access_token)
                },
                status=status.HTTP_200_OK
            )
            return response
            
        except TokenError as e:
            return Response({'error': 'Invalid or expired refresh token.'}, status=status.HTTP_401_UNAUTHORIZED)
            
    except Exception as e:
        import traceback
        print(f"Error in refresh_token_view: {str(e)}")
        print(traceback.format_exc())
        return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



