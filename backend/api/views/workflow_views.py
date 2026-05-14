from .._imports import *
from .._imports import _is_application_admin_email

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def company_deletion_settings_view(request):
    """
    GET: View company deletion permission setting.
    POST: Update company deletion permission setting (Company Admins only).
    """
    user_profile = getattr(request.user, 'profile', None)
    if not user_profile or not user_profile.company:
        return Response({'error': 'Company profile not found.'}, status=status.HTTP_404_NOT_FOUND)
    
    company = user_profile.company
    
    if request.method == 'GET':
        return Response({
            'require_delete_permission': company.require_delete_permission
        })
    
    if request.method == 'POST':
        if user_profile.role != UserProfile.ROLE_COMPANY_ADMIN and not _is_application_admin_email(user_profile.email):
            return Response({'error': 'Only Company Admins can change settings.'}, status=status.HTTP_403_FORBIDDEN)
        
        val = request.data.get('require_delete_permission')
        if val is not None:
            company.require_delete_permission = bool(val)
            company.save()
            return Response({'message': 'Settings updated successfully.', 'require_delete_permission': company.require_delete_permission})
        return Response({'error': 'Invalid data.'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_deletion_requests_view(request):
    """
    Lists deletion requests for the current user.
    - HR/HRM: List their own requests + Approved ones for the Recycle Bin.
    - HRM: Also list requests pending their approval (from their HRs).
    - Admin: List all requests for their company.
    """
    user_profile = getattr(request.user, 'profile', None)
    if not user_profile or not user_profile.company:
        return Response({'error': 'Company profile not found.'}, status=status.HTTP_404_NOT_FOUND)
    
    role = user_profile.role
    company = user_profile.company
    status_filter = request.query_params.get('status')
    
    from api._imports import get_scoped_user_ids
    scoped_ids = get_scoped_user_ids(user_profile)

    if scoped_ids is None:
        # App Admin / Company Admin see all requests in the company
        qs = DeletionRequest.objects.filter(requester__company=company)
    else:
        # Scoped: HR Managers and HR see requests they made, requests made by their team, 
        # plus any request they are assigned to approve.
        qs = DeletionRequest.objects.filter(
            models.Q(requester_id__in=scoped_ids) | models.Q(approver=user_profile)
        )
    
    if status_filter:
        qs = qs.filter(status=status_filter)
        
    data = []
    for r in qs.select_related('requester', 'approver').order_by('-created_at'):
        data.append({
            'id': r.id,
            'requester_email': r.requester.email,
            'requester_name': f"{r.requester.first_name} {r.requester.last_name}",
            'requester_role': r.requester.role.replace('_', ' ').title(),
            'approver_email': r.approver.email if r.approver else None,
            'approver_name': f"{r.approver.first_name} {r.approver.last_name}" if r.approver else "N/A",
            'approver_role': r.approver.role.replace('_', ' ').title() if r.approver else "N/A",
            'content_type': r.content_type,
            'object_id': r.object_id,
            'object_repr': r.object_repr,
            'reason': r.reason,
            'status': r.status,
            'created_at': r.created_at.isoformat(),
            'actioned_at': r.actioned_at.isoformat() if r.actioned_at else None,
            'rejection_reason': r.rejection_reason,
            'company_name': company.name
        })
        
    return Response(data)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def action_deletion_request_view(request, request_id):
    """
    Approve or Reject a deletion request.
    Only the assigned approver (or Company Admin) can take action.
    """
    user_profile = getattr(request.user, 'profile', None)
    try:
        del_request = DeletionRequest.objects.get(id=request_id)
    except DeletionRequest.DoesNotExist:
        return Response({'error': 'Request not found.'}, status=status.HTTP_404_NOT_FOUND)
    
    # Permission check
    is_approver = (del_request.approver == user_profile)
    is_admin = (user_profile.role == UserProfile.ROLE_COMPANY_ADMIN and del_request.requester.company == user_profile.company)
    
    if not (is_approver or is_admin or _is_application_admin_email(user_profile.email)):
        return Response({'error': 'Not authorized to action this request.'}, status=status.HTTP_403_FORBIDDEN)
    
    if del_request.status != DeletionRequest.STATUS_PENDING:
        return Response({'error': 'This request has already been actioned.'}, status=status.HTTP_400_BAD_REQUEST)
    
    action = request.data.get('action') # 'approve' or 'reject'
    if action == 'approve':
        # Perform the actual deletion based on content_type
        success = _perform_actual_deletion(del_request)
        if success:
            del_request.status = DeletionRequest.STATUS_APPROVED
            del_request.actioned_at = timezone.now()
            del_request.save()
            return Response({'message': 'Request approved and item deleted.'})
        else:
            return Response({'error': 'Failed to delete the item (it may have been deleted already).'}, status=status.HTTP_400_BAD_REQUEST)
            
    elif action == 'reject':
        del_request.status = DeletionRequest.STATUS_REJECTED
        del_request.actioned_at = timezone.now()
        del_request.rejection_reason = request.data.get('reason', 'Rejected by manager.')
        del_request.save()
        return Response({'message': 'Request rejected.'})
    
    return Response({'error': 'Invalid action.'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def pending_deletion_requests_count_view(request):
    """
    Returns the count of deletion requests pending approval for the current user.
    """
    user_profile = getattr(request.user, 'profile', None)
    if not user_profile or not user_profile.company:
        return Response({'count': 0})
    
    role = user_profile.role
    company = user_profile.company
    
    # We only care about PENDING requests that this user can action
    if role == UserProfile.ROLE_COMPANY_ADMIN or _is_application_admin_email(user_profile.email):
        # Admin can action all pending requests in company
        count = DeletionRequest.objects.filter(requester__company=company, status=DeletionRequest.STATUS_PENDING).count()
    elif role == UserProfile.ROLE_HR_MANAGER:
        # HRM can action requests where they are the assigned approver
        count = DeletionRequest.objects.filter(approver=user_profile, status=DeletionRequest.STATUS_PENDING).count()
    else:
        # HR normally can't approve, so count is 0
        count = 0
        
    return Response({'count': count})


def _perform_actual_deletion(req):

    """
    Helper to delete the object referred to in the DeletionRequest.
    Supports standard assessments, AI assessments, job roles, and candidate profiles.
    """
    try:
        if req.content_type == 'CandidateSubmission':
            obj = CandidateSubmission.objects.get(id=req.object_id)
        elif req.content_type == 'Assessment':
            obj = Assessment.objects.get(id=req.object_id)
        elif req.content_type == 'CandidateInvitation':
            obj = CandidateInvitation.objects.get(id=req.object_id)
        elif req.content_type == 'JobRole':
            obj = JobRole.objects.get(id=req.object_id)
        elif req.content_type == 'Candidate':
            obj = Candidate.objects.get(id=req.object_id)
        elif req.content_type == 'AIAssessmentSubmission':
            from ai_assessments.models import AIAssessmentSubmission
            obj = AIAssessmentSubmission.objects.get(id=req.object_id)
        elif req.content_type == 'InterviewInvitation':
            obj = InterviewInvitation.objects.get(id=req.object_id)
        elif req.content_type == 'UserProfile':
            obj = UserProfile.objects.get(id=req.object_id)
            # Hierarchical Reassignment: If this user is a manager, 
            # reassign their subordinates to their own manager.
            subordinates = UserProfile.objects.filter(manager=obj)
            new_manager = obj.manager
            if subordinates.exists():
                subordinates.update(manager=new_manager)
        else:
            return False
            
        if not obj:
            return False
            
        obj.is_deleted = True
        obj.save()
        return True
    except Exception:
        return False


def _perform_restore(req):
    """
    Reverses a soft-delete by setting is_deleted=False on the object.
    """
    try:
        obj = None
        if req.content_type == 'CandidateSubmission':
            obj = CandidateSubmission.objects.get(id=req.object_id)
        elif req.content_type == 'Assessment':
            obj = Assessment.objects.get(id=req.object_id)
        elif req.content_type == 'CandidateInvitation':
            obj = CandidateInvitation.objects.get(id=req.object_id)
        elif req.content_type == 'JobRole':
            obj = JobRole.objects.get(id=req.object_id)
        elif req.content_type == 'Candidate':
            from ai_candidates.models import Candidate as AICandidate
            obj = AICandidate.objects.get(id=req.object_id)
        elif req.content_type == 'AIAssessmentSubmission':
            from ai_assessments.models import AIAssessmentSubmission as AISubmission
            obj = AISubmission.objects.get(id=req.object_id)
        elif req.content_type == 'InterviewInvitation':
            obj = InterviewInvitation.objects.get(id=req.object_id)
        else:
            return False, 'Unknown content type'

        if not obj:
            return False, 'Object not found.'

        obj.is_deleted = False
        obj.save()
        return True, ''
    except Exception as e:
        import traceback
        traceback.print_exc()
        return False, str(e)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def restore_deletion_request_view(request, request_id):
    """
    Restore a soft-deleted item from the Recycle Bin.
    Only Company Admins and App Admins can restore.
    """
    user_profile = getattr(request.user, 'profile', None)
    if not user_profile:
        return Response({'error': 'Unauthorized.'}, status=status.HTTP_403_FORBIDDEN)

    is_admin = (user_profile.role == UserProfile.ROLE_COMPANY_ADMIN)
    is_app_admin = _is_application_admin_email(user_profile.email)

    if not (is_admin or is_app_admin):
        return Response({'error': 'Only Company Admins can restore deleted items.'}, status=status.HTTP_403_FORBIDDEN)

    try:
        del_request = DeletionRequest.objects.get(id=request_id)
    except DeletionRequest.DoesNotExist:
        return Response({'error': 'Request not found.'}, status=status.HTTP_404_NOT_FOUND)

    if del_request.status != DeletionRequest.STATUS_APPROVED:
        return Response({'error': 'Only approved (deleted) items can be restored.'}, status=status.HTTP_400_BAD_REQUEST)

    success, error_msg = _perform_restore(del_request)
    if success:
        del_request.status = getattr(DeletionRequest, 'STATUS_RESTORED', 'restored')
        del_request.reason = f"[RESTORED on {timezone.localtime().strftime('%Y-%m-%dT%H:%M:%S')}] Admin Restored | {del_request.reason or ''}"
        del_request.save()
        return Response({'message': f'"{del_request.object_repr}" has been successfully restored.'})
    else:
        return Response({'error': f'Failed to restore item. {error_msg}'}, status=status.HTTP_400_BAD_REQUEST)


# ---------------------------------------------------------------------------
# Qualification Approval Workflow
# ---------------------------------------------------------------------------

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_qualification_requests_view(request):
    """
    Lists qualification requests visible to the current user.
    - Company Admin / App Admin: all requests in their company.
    - HR Manager / HR: only their own requests.
    """
    user_profile = getattr(request.user, 'profile', None)
    if not user_profile or not user_profile.company:
        return Response({'error': 'Company profile not found.'}, status=status.HTTP_404_NOT_FOUND)

    company = user_profile.company
    role = user_profile.role
    is_admin = (
        role == UserProfile.ROLE_COMPANY_ADMIN
        or _is_application_admin_email(user_profile.email)
    )

    if is_admin:
        qs = QualificationRequest.objects.filter(requester__company=company)
    else:
        qs = QualificationRequest.objects.filter(requester=user_profile)

    status_filter = request.query_params.get('status')
    if status_filter:
        qs = qs.filter(status=status_filter)

    data = []
    for req in qs.select_related('requester', 'actioned_by', 'submission__invitation').order_by('-created_at'):
        # Build a download URL if there's a standard submission
        report_url = None
        if req.content_type == QualificationRequest.CONTENT_STANDARD and req.submission_id:
            report_url = f"/results/{req.submission_id}/report/"

        data.append({
            'id': req.id,
            'content_type': req.content_type,
            'submission_id': req.submission_id,
            'ai_submission_id': req.ai_submission_id,
            'candidate_name': req.candidate_name,
            'candidate_email': req.candidate_email,
            'requested_result': req.requested_result,
            'reason': req.reason,
            'status': req.status,
            'rejection_reason': req.rejection_reason,
            'requester_name': f"{req.requester.first_name} {req.requester.last_name}".strip(),
            'requester_email': req.requester.email,
            'requester_role': req.requester.role.replace('_', ' ').title(),
            'actioned_by_name': (
                f"{req.actioned_by.first_name} {req.actioned_by.last_name}".strip()
                if req.actioned_by else None
            ),
            'actioned_at': req.actioned_at.isoformat() if req.actioned_at else None,
            'created_at': req.created_at.isoformat(),
            'report_url': report_url,
        })

    return Response(data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def action_qualification_request_view(request, request_id):
    """
    Approve or Reject a qualification request.
    Only Company Admin / App Admin can take action.
    On approval, the underlying submission result is updated.
    """
    user_profile = getattr(request.user, 'profile', None)
    if not user_profile:
        return Response({'error': 'Unauthorized.'}, status=status.HTTP_403_FORBIDDEN)

    is_admin = (
        user_profile.role == UserProfile.ROLE_COMPANY_ADMIN
        or _is_application_admin_email(user_profile.email)
    )
    if not is_admin:
        return Response({'error': 'Only Company Admins can approve or reject qualification requests.'}, status=status.HTTP_403_FORBIDDEN)

    try:
        qual_req = QualificationRequest.objects.get(id=request_id)
    except QualificationRequest.DoesNotExist:
        return Response({'error': 'Request not found.'}, status=status.HTTP_404_NOT_FOUND)

    # Make sure admin belongs to same company as the requester
    if qual_req.requester.company != user_profile.company and not _is_application_admin_email(user_profile.email):
        return Response({'error': 'Not authorized to action this request.'}, status=status.HTTP_403_FORBIDDEN)

    if qual_req.status != QualificationRequest.STATUS_PENDING:
        return Response({'error': 'This request has already been actioned.'}, status=status.HTTP_400_BAD_REQUEST)

    action = request.data.get('action')  # 'approve' or 'reject'

    if action == 'approve':
        # Apply the result change to the actual submission
        try:
            if qual_req.content_type == QualificationRequest.CONTENT_STANDARD:
                sub = CandidateSubmission.objects.get(id=qual_req.submission_id)
                old_result = sub.result
                sub.result = qual_req.requested_result
                sub.save(update_fields=['result'])

                # Trigger email based on new status (5-min delay)
                from api.tasks import send_custom_assessment_result_task, send_regret_email_task
                inv = sub.invitation
                if qual_req.requested_result == 'selected':
                    send_custom_assessment_result_task.apply_async(args=[inv.id], countdown=300)
                elif qual_req.requested_result == 'rejected':
                    send_regret_email_task.apply_async(args=[inv.id], countdown=300)

            elif qual_req.content_type == QualificationRequest.CONTENT_AI:
                from ai_assessments.models import AIAssessmentSubmission
                ai_sub = AIAssessmentSubmission.objects.get(id=qual_req.ai_submission_id)
                ai_sub.status = qual_req.requested_result
                ai_sub.save(update_fields=['status'])

        except Exception as e:
            return Response({'error': f'Failed to update submission: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

        qual_req.status = QualificationRequest.STATUS_APPROVED
        qual_req.actioned_by = user_profile
        qual_req.actioned_at = timezone.now()
        qual_req.save()
        
        from api.tasks import send_qualification_action_email_task
        send_qualification_action_email_task.apply_async(args=[qual_req.id, 'approved'])
        
        return Response({'message': 'Qualification request approved. Candidate status updated.'})

    elif action == 'reject':
        rejection_reason = (request.data.get('reason') or '').strip()
        if not rejection_reason:
            return Response({'error': 'A rejection reason is required.'}, status=status.HTTP_400_BAD_REQUEST)

        qual_req.status = QualificationRequest.STATUS_REJECTED
        qual_req.actioned_by = user_profile
        qual_req.actioned_at = timezone.now()
        qual_req.rejection_reason = rejection_reason
        qual_req.save()
        
        from api.tasks import send_qualification_action_email_task
        send_qualification_action_email_task.apply_async(args=[qual_req.id, 'rejected', rejection_reason])
        
        return Response({'message': 'Qualification request rejected.'})

    return Response({'error': 'Invalid action. Use "approve" or "reject".'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def pending_qualification_requests_count_view(request):
    """
    Returns count of pending qualification requests that the admin can action.
    """
    user_profile = getattr(request.user, 'profile', None)
    if not user_profile or not user_profile.company:
        return Response({'count': 0})

    is_admin = (
        user_profile.role == UserProfile.ROLE_COMPANY_ADMIN
        or _is_application_admin_email(user_profile.email)
    )
    if not is_admin:
        return Response({'count': 0})

    count = QualificationRequest.objects.filter(
        requester__company=user_profile.company,
        status=QualificationRequest.STATUS_PENDING
    ).count()
    return Response({'count': count})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_ai_qualification_request_view(request):
    """
    HR / HR Manager submits a qualification change request for an AI assessment candidate.
    Body: { ai_submission_id, requested_result ('selected'|'rejected'), reason, candidate_name, candidate_email }
    """
    user_profile = getattr(request.user, 'profile', None)
    if not user_profile:
        return Response({'error': 'Unauthorized.'}, status=status.HTTP_403_FORBIDDEN)

    is_admin = (
        user_profile.role == UserProfile.ROLE_COMPANY_ADMIN
        or _is_application_admin_email(user_profile.email)
    )
    ai_submission_id = request.data.get('ai_submission_id')
    requested_result = request.data.get('requested_result', '').strip()
    reason = (request.data.get('reason') or '').strip()
    candidate_name = (request.data.get('candidate_name') or '').strip()
    candidate_email = (request.data.get('candidate_email') or '').strip()

    if not ai_submission_id:
        return Response({'error': 'ai_submission_id is required.'}, status=status.HTTP_400_BAD_REQUEST)
    if requested_result not in ('selected', 'rejected'):
        return Response({'error': 'requested_result must be "selected" or "rejected".'}, status=status.HTTP_400_BAD_REQUEST)

    if is_admin:
        from ai_assessments.models import AIAssessmentSubmission
        try:
            ai_sub = AIAssessmentSubmission.objects.get(id=ai_submission_id)
            ai_sub.status = requested_result
            ai_sub.save(update_fields=['status'])
            return Response({'message': f'Candidate marked as {requested_result}.', 'pending': False}, status=status.HTTP_200_OK)
        except AIAssessmentSubmission.DoesNotExist:
            return Response({'error': 'AI Submission not found.'}, status=status.HTTP_404_NOT_FOUND)

    if not reason:
        return Response({'error': 'A reason is required.'}, status=status.HTTP_400_BAD_REQUEST)

    # Prevent duplicate pending request for the same AI submission
    existing = QualificationRequest.objects.filter(
        content_type=QualificationRequest.CONTENT_AI,
        ai_submission_id=str(ai_submission_id),
        status=QualificationRequest.STATUS_PENDING,
    ).first()
    if existing:
        return Response({'error': 'A pending qualification request already exists for this candidate.'}, status=status.HTTP_400_BAD_REQUEST)

    qual_req = QualificationRequest.objects.create(
        requester=user_profile,
        content_type=QualificationRequest.CONTENT_AI,
        ai_submission_id=str(ai_submission_id),
        requested_result=requested_result,
        reason=reason,
        candidate_name=candidate_name,
        candidate_email=candidate_email,
        status=QualificationRequest.STATUS_PENDING,
    )

    from api.tasks import send_qualification_request_email_task
    send_qualification_request_email_task.apply_async(args=[qual_req.id])

    return Response({
        'message': 'Qualification request submitted. It will be reviewed by an admin.',
        'request_id': qual_req.id,
        'pending': True,
    }, status=status.HTTP_201_CREATED)
