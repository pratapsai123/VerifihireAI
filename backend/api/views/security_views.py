from .._imports import *
import uuid


HEARTBEAT_TIMEOUT_SECONDS = 600


def _mark_timed_out(session):
    if not session or session.action == 'STOP':
        return session
    
    timeout = HEARTBEAT_TIMEOUT_SECONDS
    if session.last_heartbeat:
        elapsed = (timezone.now() - session.last_heartbeat).total_seconds()
        if elapsed > timeout:
            session.action = 'STOP'
            session.reason = 'Security session timed out: Secure Agent connection lost for more than 10 minutes. Please ensure a stable internet connection.'
            session.is_active = False
            session.save(update_fields=['action', 'reason', 'is_active', 'updated_at'])
            print(f"[SECURITY_TIMEOUT] Session {session.session_id} stopped due to persistent Agent silence (10min+).")
    return session



def _resolve_security_session(session_id=None, user_id=None):
    session = None
    if session_id and user_id:
        session = SecuritySession.objects.filter(session_id=session_id, user_id=user_id).order_by('-created_at').first()
    if not session and session_id:
        session = SecuritySession.objects.filter(session_id=session_id).order_by('-created_at').first()
    if not session and user_id:
        session = SecuritySession.objects.filter(user_id=user_id).order_by('-created_at').first()
    return _mark_timed_out(session)


@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def start_security_session_view(request):
    data = request.data or {}
    token = (data.get('token') or '').strip()
    session_type = (data.get('type') or 'assessment').strip().lower()
    user_id = (data.get('user_id') or token or '').strip()

    if not token:
        return Response({'error': 'token is required'}, status=status.HTTP_400_BAD_REQUEST)

    if SecuritySession.objects.filter(token=token, status='VIOLATION').exists():
        return Response({
            'error': 'Access permanently revoked due to policy violation.',
            'is_violated': True
        }, status=status.HTTP_403_FORBIDDEN)

    agent_id = (data.get('agent_instance_id') or '').strip()
    if agent_id:
        # Check if this agent ID was already used for a different token
        # This prevents using the same .exe download for multiple distinct assessments.
        if SecuritySession.objects.filter(agent_instance_id=agent_id).exclude(token=token).exists():
            return Response({
                'error': 'To maintain assessment integrity, this session requires a new instance of the Secure Agent.',
                'agent_expired': True,
                'action': 'STOP'
            }, status=status.HTTP_403_FORBIDDEN)

    session = SecuritySession.objects.create(
        token=token,
        session_type=session_type,
        user_id=user_id or token,
        agent_instance_id=agent_id,
        status='SAFE',
        action='CONTINUE',
        last_heartbeat=timezone.now(),
    )
    return Response({
        'session_id': str(session.session_id),
        'action': session.action,
        'status': session.status,
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def security_check_view(request):
    data = request.data or {}
    session_id = data.get('session_id')
    user_id = data.get('user_id')
    status_value = (data.get('status') or 'SAFE').upper()
    app = (data.get('app') or '').strip()
    process_name = (data.get('process_name') or '').strip()
    app_path = (data.get('app_path') or '').strip()

    session = _resolve_security_session(session_id=session_id, user_id=user_id)
    if not session:
        return Response({'action': 'STOP', 'error': 'security session not found'}, status=status.HTTP_404_NOT_FOUND)

    if session.action == 'STOP':
        return Response({'action': 'STOP'})

    if status_value == 'VIOLATION':
        # First time violation: Start 3-minute grace period
        if session.violation_count == 0:
            session.violation_count = 1
            session.violation_start_time = timezone.now()
            session.status = 'VIOLATION'
            session.action = 'WARN'
            session.blocked_app = app
            session.blocked_process_name = process_name
            session.blocked_app_path = app_path
            session.reason = f'Warning: Remote access tool detected ({app}). Close it within 3 minutes or access will be revoked.'
            session.save()
            return Response({
                'action': 'WARN', 
                'violation_start_time': session.violation_start_time.isoformat(),
                'blocked_app': app
            })
        
        # If they already had a warning or are in grace period
        # If they are currently in 'WARN' state, check if 3 minutes have passed
        if session.action == 'WARN':
            grace_seconds = (timezone.now() - session.violation_start_time).total_seconds()
            if grace_seconds <= 180:
                # Still in grace period
                return Response({
                    'action': 'WARN',
                    'violation_start_time': session.violation_start_time.isoformat(),
                    'blocked_app': app
                })
            else:
                # Grace period EXPIRED -> Permanent STOP
                session.reason = f'Policy violation: Remote access tool ({app}) not closed within grace period.'
        else:
            # They already closed it once (action was CONTINUE but violation_count is 1)
            # This is the SECOND time -> Immediate STOP
            session.violation_count += 1
            session.reason = f'Policy violation: Second detection of remote access tool ({app}). Access revoked immediately.'

        # Permanent STOP logic
        session.status = 'VIOLATION'
        session.action = 'STOP'
        session.blocked_app = app
        session.blocked_process_name = process_name
        session.blocked_app_path = app_path
        session.is_active = False
        session.save()
        print(f"[SECURITY_CHECK] STOP triggered for {session_id} - App: {app}")
        return Response({'action': 'STOP'})

    if status_value == 'HARDWARE_VIOLATION':
        # Pause the exam — do NOT stop it permanently; device can be removed to resume
        session.status = 'HARDWARE_VIOLATION'
        session.action = 'PAUSE'
        session.blocked_hardware = app  # app field contains the device name(s)
        session.reason = f'Hardware violation: {app or "external device connected"}'
        session.save(update_fields=['status', 'action', 'blocked_hardware', 'reason', 'updated_at'])
        return Response({'action': 'PAUSE', 'blocked_hardware': app})

    if status_value == 'HARDWARE_SAFE':
        # Device was removed — un-pause if we were paused due to hardware
        if session.action == 'PAUSE':
            session.status = 'SAFE'
            session.action = 'CONTINUE'
            session.blocked_hardware = None
            session.reason = 'Hardware cleared — exam resumed'
            session.save(update_fields=['status', 'action', 'blocked_hardware', 'reason', 'updated_at'])
        return Response({'action': session.action})

    session.status = 'SAFE'
    session.action = 'CONTINUE'
    session.save(update_fields=['status', 'action', 'updated_at'])
    return Response({'action': 'CONTINUE'})


@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def security_heartbeat_view(request):
    data = request.data or {}
    session_id = data.get('session_id')
    user_id = data.get('user_id')
    session = _resolve_security_session(session_id=session_id, user_id=user_id)
    if not session:
        return Response({'action': 'STOP', 'error': 'security session not found'}, status=status.HTTP_404_NOT_FOUND)
    if session.action == 'STOP':
        return Response({'action': 'STOP'})
    session.last_heartbeat = timezone.now()
    session.save(update_fields=['last_heartbeat', 'updated_at'])
    return Response({'action': 'CONTINUE'})


@api_view(['GET'])
@permission_classes([AllowAny])
@csrf_exempt
def security_session_status_view(request, session_id):
    session = SecuritySession.objects.filter(session_id=session_id).order_by('-created_at').first()
    if not session:
        return Response({'error': 'security session not found'}, status=status.HTTP_404_NOT_FOUND)
    _mark_timed_out(session)
    print(f"[SECURITY_STATUS] Session {session_id} is {session.action}")
    return Response({
        'session_id': str(session.session_id),
        'action': session.action,
        'status': session.status,
        'reason': session.reason,
        'blocked_app': session.blocked_app,
        'blocked_process_name': session.blocked_process_name,
        'blocked_app_path': session.blocked_app_path,
        'blocked_hardware': session.blocked_hardware,
        'violation_count': session.violation_count,
        'violation_start_time': session.violation_start_time.isoformat() if session.violation_start_time else None,
        'last_heartbeat': session.last_heartbeat.isoformat() if session.last_heartbeat else None,
    })


@api_view(['GET'])
@permission_classes([AllowAny])
@csrf_exempt
def security_signatures_view(request):
    rules = getattr(settings, 'SECURITY_SIGNATURE_RULES', [])
    return Response({'version': '1', 'rules': rules})


@api_view(['GET'])
@permission_classes([AllowAny])
@csrf_exempt
def check_violation_status_view(request, token):
    is_violated = SecuritySession.objects.filter(token=token, status='VIOLATION').exists()
    return Response({'is_violated': is_violated})

