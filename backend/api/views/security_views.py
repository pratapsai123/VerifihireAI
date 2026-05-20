from .._imports import *
import uuid


HEARTBEAT_TIMEOUT_SECONDS = 600


def _agent_expired_response(message=None):
    return Response({
        'error': message or (
            'To maintain assessment integrity, this session requires a new instance of the '
            'Secure Agent. Please download and run the latest agent, then retry.'
        ),
        'agent_expired': True,
        'action': 'STOP',
    }, status=status.HTTP_403_FORBIDDEN)


def _consume_agent_instance(agent_id, session=None):
    """Mark agent as single-use consumed and deactivate related security sessions."""
    if not agent_id:
        return
    now = timezone.now()
    SecureAgentInstance.objects.filter(instance_id=agent_id, consumed=False).update(
        consumed=True,
        consumed_at=now,
    )
    qs = SecuritySession.objects.filter(agent_instance_id=agent_id, is_active=True)
    if session:
        qs = qs.filter(session_id=session.session_id)
    qs.update(is_active=False, updated_at=now)


def _validate_agent_instance(agent_id, token):
    """
    Enforce one agent install per assessment/interview attempt.
    Returns a DRF Response on failure, or None when the agent may proceed.
    """
    if not agent_id:
        return Response({
            'error': 'Secure Agent instance ID is required. Please download and run VerifiHire Secure Agent.',
            'agent_expired': True,
        }, status=status.HTTP_400_BAD_REQUEST)

    reg = SecureAgentInstance.objects.filter(instance_id=agent_id).first()
    if reg:
        if reg.consumed:
            return _agent_expired_response()
        if reg.first_token != token:
            return _agent_expired_response()
        return None

    SecureAgentInstance.objects.create(instance_id=agent_id, first_token=token)
    return None


def _get_reusable_session(token, agent_id):
    """Allow page refresh / reconnect without consuming a new agent install."""
    if not agent_id:
        return None
    return SecuritySession.objects.filter(
        token=token,
        agent_instance_id=agent_id,
        is_active=True,
        action__in=['CONTINUE', 'WARN', 'PAUSE'],
    ).order_by('-created_at').first()


def _mark_timed_out(session):
    if not session or session.action == 'STOP':
        return session

    timeout = HEARTBEAT_TIMEOUT_SECONDS
    if session.last_heartbeat:
        elapsed = (timezone.now() - session.last_heartbeat).total_seconds()
        if elapsed > timeout:
            session.action = 'STOP'
            session.reason = (
                'Security session timed out: Secure Agent connection lost for more than 10 minutes. '
                'Please ensure a stable internet connection.'
            )
            session.is_active = False
            session.save(update_fields=['action', 'reason', 'is_active', 'updated_at'])
            _consume_agent_instance(session.agent_instance_id, session=session)
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
    agent_id = (data.get('agent_instance_id') or '').strip()

    if not token:
        return Response({'error': 'token is required'}, status=status.HTTP_400_BAD_REQUEST)

    if SecuritySession.token_has_permanent_revocation(token):
        return Response({
            'error': 'Access permanently revoked due to policy violation.',
            'is_violated': True,
        }, status=status.HTTP_403_FORBIDDEN)

    agent_error = _validate_agent_instance(agent_id, token)
    if agent_error:
        return agent_error

    existing = _get_reusable_session(token, agent_id)
    if existing:
        existing.last_heartbeat = timezone.now()
        existing.save(update_fields=['last_heartbeat', 'updated_at'])
        return Response({
            'session_id': str(existing.session_id),
            'action': existing.action,
            'status': existing.status,
            'reused': True,
        }, status=status.HTTP_200_OK)

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
def consume_agent_instance_view(request):
    """Called when an exam/interview ends so the agent cannot be reused."""
    data = request.data or {}
    agent_id = (data.get('agent_instance_id') or '').strip()
    session_id = data.get('session_id')
    token = (data.get('token') or '').strip()

    session = None
    if session_id:
        session = SecuritySession.objects.filter(session_id=session_id).order_by('-created_at').first()
    elif token:
        session = SecuritySession.objects.filter(token=token, is_active=True).order_by('-created_at').first()

    if agent_id:
        _consume_agent_instance(agent_id, session=session)
    elif session and session.agent_instance_id:
        _consume_agent_instance(session.agent_instance_id, session=session)
    elif token:
        SecuritySession.objects.filter(token=token, is_active=True).update(is_active=False)

    return Response({'consumed': True}, status=status.HTTP_200_OK)


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
        if session.violation_count == 0:
            session.violation_count = 1
            session.violation_start_time = timezone.now()
            session.status = 'VIOLATION'
            session.action = 'WARN'
            session.blocked_app = app
            session.blocked_process_name = process_name
            session.blocked_app_path = app_path
            session.reason = (
                f'Warning: Remote access tool detected ({app}). '
                'Close it within 3 minutes or access will be revoked.'
            )
            session.save()
            return Response({
                'action': 'WARN',
                'violation_start_time': session.violation_start_time.isoformat(),
                'blocked_app': app,
            })

        if session.action == 'WARN':
            grace_seconds = (timezone.now() - session.violation_start_time).total_seconds()
            if grace_seconds <= 180:
                return Response({
                    'action': 'WARN',
                    'violation_start_time': session.violation_start_time.isoformat(),
                    'blocked_app': app,
                })
            session.reason = (
                f'Policy violation: Remote access tool ({app}) not closed within grace period.'
            )
        else:
            session.violation_count += 1
            session.reason = (
                f'Policy violation: Second detection of remote access tool ({app}). '
                'Access revoked immediately.'
            )

        session.status = 'VIOLATION'
        session.action = 'STOP'
        session.blocked_app = app
        session.blocked_process_name = process_name
        session.blocked_app_path = app_path
        session.is_active = False
        session.save()
        _consume_agent_instance(session.agent_instance_id, session=session)
        print(f"[SECURITY_CHECK] STOP triggered for {session_id} - App: {app}")
        return Response({'action': 'STOP'})

    if status_value == 'HARDWARE_VIOLATION':
        session.status = 'HARDWARE_VIOLATION'
        session.action = 'PAUSE'
        session.blocked_hardware = app
        session.reason = f'Hardware violation: {app or "external device connected"}'
        session.save(update_fields=['status', 'action', 'blocked_hardware', 'reason', 'updated_at'])
        return Response({'action': 'PAUSE', 'blocked_hardware': app})

    if status_value == 'HARDWARE_SAFE':
        if session.action == 'PAUSE':
            session.status = 'SAFE'
            session.action = 'CONTINUE'
            session.blocked_hardware = None
            session.reason = 'Hardware cleared — exam resumed'
            session.save(update_fields=['status', 'action', 'blocked_hardware', 'reason', 'updated_at'])
        return Response({'action': session.action})

    session.status = 'SAFE'
    session.action = 'CONTINUE'
    session.violation_count = 0
    session.violation_start_time = None
    session.blocked_app = None
    session.blocked_process_name = None
    session.blocked_app_path = None
    session.save(update_fields=[
        'status', 'action', 'violation_count', 'violation_start_time',
        'blocked_app', 'blocked_process_name', 'blocked_app_path', 'updated_at',
    ])
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
    from api.views.candidate_assessment_views import (
        TERMINAL_CLOSE_LIMIT,
        _invitation_terminal_close_chances_left,
    )

    is_violated = SecuritySession.token_has_permanent_revocation(token)
    terminal_close_count = 0
    chances_left = TERMINAL_CLOSE_LIMIT

    try:
        invitation = CandidateInvitation.objects.get(token=token, is_deleted=False)
        terminal_close_count = int(invitation.terminal_close_count or 0)
        chances_left = _invitation_terminal_close_chances_left(invitation)
        submission = getattr(invitation, 'submission', None)
        if submission and getattr(submission, 'result', None) == 'terminated':
            is_violated = True
        elif terminal_close_count >= TERMINAL_CLOSE_LIMIT:
            is_violated = True
    except CandidateInvitation.DoesNotExist:
        pass

    return Response({
        'is_violated': is_violated,
        'terminal_close_count': terminal_close_count,
        'terminal_close_limit': TERMINAL_CLOSE_LIMIT,
        'chances_left': chances_left,
    })


@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def terminate_terminal_close_view(request):
    """Final strike: candidate closed the Secure Agent terminal 3 times during the exam."""
    data = request.data or {}
    session_id = data.get('session_id')
    user_id = data.get('user_id')
    token = (data.get('token') or '').strip()

    session = _resolve_security_session(session_id=session_id, user_id=user_id)
    if not session and token:
        session = SecuritySession.objects.filter(
            token=token, is_active=True
        ).order_by('-created_at').first()

    if session:
        session.status = 'VIOLATION'
        session.action = 'STOP'
        session.reason = (
            'Exam terminated: Secure Agent terminal was closed 3 times during the exam.'
        )
        session.is_active = False
        session.save(update_fields=['status', 'action', 'reason', 'is_active', 'updated_at'])
        _consume_agent_instance(session.agent_instance_id, session=session)
        print(f"[SECURITY_TERMINAL] Session {session.session_id} stopped after 3 terminal closes.")

    if token:
        try:
            from api.views.candidate_assessment_views import TERMINAL_CLOSE_LIMIT

            CandidateInvitation.objects.filter(token=token, is_deleted=False).update(
                terminal_close_count=TERMINAL_CLOSE_LIMIT,
            )
        except Exception:
            pass

    return Response({'terminated': True}, status=status.HTTP_200_OK)
