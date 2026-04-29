from .._imports import *
import uuid


HEARTBEAT_TIMEOUT_SECONDS = 15


def _mark_timed_out(session):
    if not session or session.action == 'STOP':
        return session
    if not session.last_heartbeat:
        return session
    age = (timezone.now() - session.last_heartbeat).total_seconds()
    if age > HEARTBEAT_TIMEOUT_SECONDS:
        session.action = 'STOP'
        session.status = 'VIOLATION'
        session.reason = 'Heartbeat timeout'
        session.is_active = False
        session.save(update_fields=['action', 'status', 'reason', 'is_active', 'updated_at'])
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

    session = SecuritySession.objects.create(
        token=token,
        session_type=session_type,
        user_id=user_id or token,
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
        session.status = 'VIOLATION'
        session.action = 'STOP'
        session.blocked_app = app
        session.blocked_process_name = process_name
        session.blocked_app_path = app_path
        session.reason = f'Policy violation: {app or process_name or "remote tool detected"}'
        session.is_active = False
        session.save(update_fields=[
            'status', 'action', 'blocked_app', 'blocked_process_name', 'blocked_app_path',
            'reason', 'is_active', 'updated_at'
        ])
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
    session.save(update_fields=['status', 'updated_at'])
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
    return Response({
        'session_id': str(session.session_id),
        'action': session.action,
        'status': session.status,
        'reason': session.reason,
        'blocked_app': session.blocked_app,
        'blocked_process_name': session.blocked_process_name,
        'blocked_app_path': session.blocked_app_path,
        'blocked_hardware': session.blocked_hardware,
        'last_heartbeat': session.last_heartbeat.isoformat() if session.last_heartbeat else None,
    })


@api_view(['GET'])
@permission_classes([AllowAny])
@csrf_exempt
def security_signatures_view(request):
    rules = getattr(settings, 'SECURITY_SIGNATURE_RULES', [])
    return Response({'version': '1', 'rules': rules})
