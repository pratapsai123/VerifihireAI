from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from ..models import (
    CandidateInvitation, 
    CandidateIntegrity,
    KeystrokeLog, 
    BehaviorLog,
)


import json

@api_view(['POST'])
@permission_classes([AllowAny])
def track_events_view(request):
    """
    API endpoint to accept batched keystroke and behavior data.
    """
    data = request.data
    token = data.get('token')
    if not token:
        return Response({'error': 'Token is required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        invitation = CandidateInvitation.objects.get(token=token)
        print(f"[MALPRACTICE] Found invitation: {token}")
    except CandidateInvitation.DoesNotExist:
        return Response({'error': 'Invalid token'}, status=status.HTTP_404_NOT_FOUND)

    # Get or create integrity record
    integrity, created = CandidateIntegrity.objects.get_or_create(
        invitation=invitation
    )

    keystrokes_data = data.get('keystrokes', [])
    behavior_data = data.get('behavior', [])
    print(f"[MALPRACTICE] Received {len(keystrokes_data)} keystrokes and {len(behavior_data)} behavior events")



    # 1. Save Keystrokes in a single record (batch)
    if keystrokes_data:
        # Optional: Calculate a simple rhythm profile (e.g. average timing)
        avg_time = sum([k.get('time_diff', 0) for k in keystrokes_data]) / len(keystrokes_data)
        
        KeystrokeLog.objects.create(
            invitation=invitation,
            events=keystrokes_data,
            rhythm={'avg_time_diff': avg_time, 'sample_count': len(keystrokes_data)}
        )


    # 2. Save Behavior Flags
    for bh in behavior_data:
        BehaviorLog.objects.create(
            invitation=invitation,
            type=bh.get('type'),
            value=str(bh.get('value')),
            created_at=bh.get('timestamp', timezone.now())
        )


    # 3. Analysis Logic & Suspicion Scoring
    reasons = set(integrity.suspicion_reasons)
    current_score = integrity.suspicion_score


    # Analysis: Typing Gaps
    # Detect long pauses (> 20s)
    for ks in keystrokes_data:
        if ks.get('time_diff', 0) > 20000: # 20 seconds in ms
            reasons.add("Long typing pause detected")
            current_score = min(100, current_score + 10)
            
            # Sub-check: High-speed typing after pause
            # (In a batch, we can check the next few entries if they are within 5s)
            # This is complex to do perfectly in batch but we can approximate.
            pass

    # Analysis: Burst Typing
    # > 80 chars in 5 sec
    # We can check the batch total if the batch window is small (5s)
    if len(keystrokes_data) > 80:
        reasons.add("Burst typing detected (>80 chars/5s)")
        current_score = min(100, current_score + 25)

    # Analysis: Backspace Behavior
    # We now check within the JSON events of all logs for this invitation
    all_logs = KeystrokeLog.objects.filter(invitation=invitation)
    total_chars = 0
    backspaces = 0
    for log in all_logs:
        evs = log.events
        total_chars += len(evs)
        backspaces += len([e for e in evs if e.get('key') == 'Backspace'])



    if total_chars > 200:
        ratio = backspaces / total_chars
        if ratio < 0.01: # Less than 1% backspace usage
            reasons.add("Anomaly: Extremely low backspace usage")
            current_score = min(100, current_score + 15)

    # Analysis: Tab Switching
    # Use the official tab switches count tracked in CandidateIntegrity
    tab_switches = integrity.tab_switches
    if tab_switches > 3:
        # Remove any existing/stale tab switching reasons first
        reasons = {r for r in reasons if not r.startswith("Frequent tab switching (")}
        reasons.add(f"Frequent tab switching ({tab_switches} times)")
        current_score = min(100, current_score + 20)
    else:
        # If <= 3, also ensure old/stale reasons are removed
        reasons = {r for r in reasons if not r.startswith("Frequent tab switching (")}


    # Analysis: Code Evolution
    snapshots = BehaviorLog.objects.filter(invitation=invitation, type='code_snapshot').order_by('-created_at')[:2]
    if len(snapshots) == 2:
        curr_code = snapshots[0].value
        prev_code = snapshots[1].value
        if len(curr_code) - len(prev_code) > 500: # Large jump
            reasons.add("Sudden large code block detected (possible paste)")
            current_score = min(100, current_score + 30)

    integrity.suspicion_score = current_score
    integrity.suspicion_reasons = list(reasons)
    integrity.save()
    print(f"[MALPRACTICE] Updated score for invitation {invitation.id}: {current_score}. Reasons: {list(reasons)}")


    return Response({

        'status': 'success',
        'suspicion_score': current_score,
        'reasons': list(reasons)
    }, status=status.HTTP_200_OK)