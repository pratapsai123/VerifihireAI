from .._imports import *
from .._imports import _is_application_admin_email
import logging
logger = logging.getLogger(__name__)

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

                # CROSS-UPDATE: Synchronize with the Candidate record
                try:
                    from ai_candidates.models import Candidate
                    email = ai_sub.candidate_email
                    batch_id = ai_sub.batch_id
                    candidates = Candidate.objects.filter(email__iexact=email).order_by('-id')
                    candidate = candidates.filter(batch_id=batch_id).first() if batch_id else candidates.first()
                    if candidate:
                        if qual_req.requested_result == 'selected':
                            candidate.status = 'Assessment Passed'
                        else:
                            candidate.status = 'Assessment Failed'
                        candidate.save(update_fields=['status'])
                except Exception as sync_err:
                    logger.warning(f"Failed to cross-update candidate after qualification approval: {sync_err}")

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
        
        # Try AI Assessment Submission first
        ai_sub = None
        candidate_obj = None
        try:
            ai_sub = AIAssessmentSubmission.objects.get(id=ai_submission_id)
        except (AIAssessmentSubmission.DoesNotExist, ValueError):
            pass
        
        # If not found as AI Assessment, try as AI Interview Candidate
        if not ai_sub:
            try:
                from ai_candidates.models import Candidate
                candidate_obj = Candidate.objects.get(id=ai_submission_id)
            except (Candidate.DoesNotExist, ValueError):
                return Response({'error': 'Submission/Candidate not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        if ai_sub:
            # AI Assessment flow (existing)
            ai_sub.status = requested_result
            ai_sub.save(update_fields=['status'])

            # CROSS-UPDATE: Synchronize with the Candidate record
            try:
                from ai_candidates.models import Candidate
                email = ai_sub.candidate_email
                batch_id = ai_sub.batch_id
                candidates = Candidate.objects.filter(email__iexact=email).order_by('-id')
                candidate = candidates.filter(batch_id=batch_id).first() if batch_id else candidates.first()
                if candidate:
                    if requested_result == 'selected':
                        candidate.status = 'Assessment Passed'
                    else:
                        candidate.status = 'Assessment Failed'
                    candidate.save(update_fields=['status'])
                    logger.info(f"Admin Override: Candidate {email} status updated to '{candidate.status}'")
            except Exception as sync_err:
                logger.warning(f"Failed to cross-update candidate after admin override: {sync_err}")

            # If approved, trigger the interview pipeline for automatic assessments
            if requested_result == 'selected':
                is_automatic = getattr(ai_sub.assessment, 'creation_type', 'manual') == 'automatic'
                if is_automatic:
                    try:
                        from api.pipeline import process_assessment_passed
                        process_assessment_passed(ai_sub.id)
                        logger.info(f"Admin Override: Pipeline triggered for AI submission {ai_sub.id}")
                    except Exception as pipe_err:
                        logger.error(f"Admin Override: Pipeline trigger failed for {ai_sub.id}: {pipe_err}")

        elif candidate_obj:
            # AI Interview Candidate flow (new)
            if requested_result == 'selected':
                candidate_obj.status = 'Hired'
            else:
                candidate_obj.status = 'Rejected'
            candidate_obj.save(update_fields=['status'])
            logger.info(f"Admin Override: AI Interview Candidate {candidate_obj.email} status updated to '{candidate_obj.status}'")

        return Response({'message': f'Candidate marked as {requested_result}.', 'pending': False}, status=status.HTTP_200_OK)

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


# ---------------------------------------------------------------------------
# Face Approval Workflow
# ---------------------------------------------------------------------------

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_face_requests_view(request):
    """
    Lists face update / manual review requests for the current user's company.
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
        qs = FaceUpdateRequest.objects.filter(company=company)
    else:
        qs = FaceUpdateRequest.objects.filter(hr_user=user_profile)
        
    status_filter = request.query_params.get('status')
    if status_filter:
        qs = qs.filter(status=status_filter)
        
    data = []
    for r in qs.select_related('candidate_details', 'hr_user', 'admin_user').order_by('-requested_at'):
        candidate_name = f"{r.candidate_details.first_name} {r.candidate_details.last_name}" if r.candidate_details else "N/A"
        candidate_email = r.candidate_details.email if r.candidate_details else "N/A"
        candidate_pan = r.candidate_details.pan_number if r.candidate_details else "N/A"
        
        hr_name = f"{r.hr_user.first_name} {r.hr_user.last_name}" if r.hr_user else "N/A"
        hr_email = r.hr_user.email if r.hr_user else "N/A"
        hr_role = r.hr_user.role.replace('_', ' ').title() if r.hr_user else "N/A"
        
        admin_name = f"{r.admin_user.first_name} {r.admin_user.last_name}" if r.admin_user else "N/A"
        admin_email = r.admin_user.email if r.admin_user else "N/A"
        
        # Helper to check if image is valid (not truncated or corrupted)
        def _is_valid_img(src):
            if not src:
                return False
            if hasattr(src, 'storage') and hasattr(src, 'name'):
                try:
                    if not src.storage.exists(src.name) or src.size < 1000:
                        return False
                    from PIL import Image as PILImage
                    import io
                    src.seek(0)
                    img = PILImage.open(io.BytesIO(src.read()))
                    img.load()
                    return True
                except Exception:
                    return False
            elif isinstance(src, str):
                if len(src) < 500:
                    try:
                        if os.path.exists(src) and os.path.getsize(src) > 1000:
                            from PIL import Image as PILImage
                            img = PILImage.open(src)
                            img.load()
                            return True
                    except Exception:
                        return False
                else:
                    try:
                        import base64
                        import io
                        from PIL import Image as PILImage
                        s = src.strip()
                        if ',' in s and s.startswith('data:'):
                            s = s.split(',', 1)[1]
                        s = s.replace('\n', '').replace('\r', '').replace(' ', '')
                        padding = 4 - len(s) % 4
                        if padding != 4:
                            s += '=' * padding
                        raw = base64.b64decode(s)
                        img = PILImage.open(io.BytesIO(raw))
                        img.load()
                        return True
                    except Exception:
                        return False
            return False

        email = r.candidate_details.email if r.candidate_details else ""
        pan = r.candidate_details.pan_number if r.candidate_details else ""

        # 1. Original Registered Face URL fallbacks
        original_face_url = None
        
        # Priority 1: request backup
        if r.original_face_backup and _is_valid_img(r.original_face_backup):
            original_face_url = r.original_face_backup.url
            
        # Priority 2: details previous backup
        if not original_face_url and r.candidate_details and r.candidate_details.previous_registered_face_backup:
            if _is_valid_img(r.candidate_details.previous_registered_face_backup):
                original_face_url = r.candidate_details.previous_registered_face_backup.url
                
        # Priority 3: original face backup from other requests for the same candidate
        if not original_face_url:
            other_reqs = []
            if pan:
                other_reqs.extend(list(FaceUpdateRequest.objects.filter(candidate_details__pan_number=pan).order_by('-id')))
            if email:
                other_reqs.extend(list(FaceUpdateRequest.objects.filter(candidate_details__email__iexact=email.strip()).order_by('-id')))
            for req_obj in other_reqs:
                if req_obj.original_face_backup and _is_valid_img(req_obj.original_face_backup):
                    original_face_url = req_obj.original_face_backup.url
                    break
                    
        # Priority 4: details snapshot (check all details records for the same candidate)
        if not original_face_url:
            details_qs = []
            if email:
                details_qs.extend(list(CandidateDetails.objects.filter(email__iexact=email.strip()).order_by('id')))
            if pan:
                details_qs.extend(list(CandidateDetails.objects.filter(pan_number=pan).order_by('id')))
            for details_obj in details_qs:
                if details_obj.snapshot and _is_valid_img(details_obj.snapshot):
                    original_face_url = details_obj.snapshot
                    break

        # Priority 5: oldest IdentityLink snapshot_image
        if not original_face_url:
            links = []
            if email:
                links.extend(list(IdentityLink.objects.filter(email__iexact=email.strip()).order_by('id')))
            if pan:
                links.extend(list(IdentityLink.objects.filter(pan_number=pan).order_by('id')))
            for link in links:
                if link.snapshot_image and _is_valid_img(link.snapshot_image):
                    original_face_url = link.snapshot_image.url
                    break

        # 2. Captured Mismatch Face URL fallbacks
        captured_face_url = None
        
        # Priority 1: request backup
        if r.captured_face_backup and _is_valid_img(r.captured_face_backup):
            captured_face_url = r.captured_face_backup.url
            
        # Priority 2: candidate_details snapshot
        if not captured_face_url and r.candidate_details and r.candidate_details.snapshot and _is_valid_img(r.candidate_details.snapshot):
            captured_face_url = r.candidate_details.snapshot
            
        # Priority 3: captured face backup from other requests for the same candidate
        if not captured_face_url:
            other_reqs = []
            if pan:
                other_reqs.extend(list(FaceUpdateRequest.objects.filter(candidate_details__pan_number=pan).order_by('-id')))
            if email:
                other_reqs.extend(list(FaceUpdateRequest.objects.filter(candidate_details__email__iexact=email.strip()).order_by('-id')))
            for req_obj in other_reqs:
                if req_obj.captured_face_backup and _is_valid_img(req_obj.captured_face_backup):
                    captured_face_url = req_obj.captured_face_backup.url
                    break
                    
        # Priority 4: snapshots from other details records (check all details records for the same candidate)
        if not captured_face_url:
            details_qs = []
            if email:
                details_qs.extend(list(CandidateDetails.objects.filter(email__iexact=email.strip()).order_by('-id')))
            if pan:
                details_qs.extend(list(CandidateDetails.objects.filter(pan_number=pan).order_by('-id')))
            for details_obj in details_qs:
                if details_obj.snapshot and _is_valid_img(details_obj.snapshot):
                    captured_face_url = details_obj.snapshot
                    break
        
        integrity_details = None
        integrity_screenshots = []
        
        if r.integrity_flagged:
            try:
                inv_obj = r.submission.invitation
                if hasattr(inv_obj, 'integrity') and inv_obj.integrity:
                    # Clean/deduplicate and correct tab switching reasons dynamically
                    raw_reasons = list(inv_obj.integrity.suspicion_reasons or [])
                    filtered_reasons = [reason for reason in raw_reasons if not reason.startswith("Frequent tab switching (")]
                    if inv_obj.integrity.tab_switches > 3:
                        filtered_reasons.append(f"Frequent tab switching ({inv_obj.integrity.tab_switches} times)")

                    integrity_details = {
                        'integrity_score': inv_obj.integrity.integrity_score,
                        'tab_switches': inv_obj.integrity.tab_switches,
                        'phone_detections': inv_obj.integrity.phone_detections,
                        'multiface_detections': inv_obj.integrity.multiface_detections,
                        # Apply the first 3 grace warning filters for no face detections
                        'no_face_detections': max(0, inv_obj.integrity.no_face_detections - 3),
                        'suspicion_score': inv_obj.integrity.suspicion_score,
                        'suspicion_reasons': filtered_reasons,
                    }
                
                # Fetch proctoring screenshots ordered by timestamp (oldest first) to apply chronological grace filter
                snaps = inv_obj.integrity_screenshots.all().order_by('timestamp')
                filtered_snaps = []
                no_face_skip_count = 0
                for snap in snaps:
                    evt = snap.event_type.lower() if snap.event_type else ""
                    if evt in ['no_face_detection', 'face_detection_lost', 'face_detection_lost_rechecked', 'no_face']:
                        no_face_skip_count += 1
                        if no_face_skip_count <= 3:
                            continue  # Hide first 3 face warnings
                    filtered_snaps.append(snap)
                
                # Restore newest-first order
                filtered_snaps.reverse()
                
                for snap in filtered_snaps:
                    integrity_screenshots.append({
                        'event_type': snap.event_type,
                        'timestamp': snap.timestamp.isoformat(),
                        'screenshot_url': snap.screenshot.url if snap.screenshot else None,
                        'webcam_screenshot_url': snap.webcam_screenshot.url if snap.webcam_screenshot else None,
                    })
            except Exception as e:
                print(f"[List] Error loading integrity info for request {r.id}: {e}")

        data.append({
            'id': r.id,
            'token': str(r.token),
            'candidate_name': candidate_name,
            'candidate_email': candidate_email,
            'candidate_pan': candidate_pan,
            'hr_name': hr_name,
            'hr_email': hr_email,
            'hr_role': hr_role,
            'hr_reason': r.hr_reason,
            'requested_at': r.requested_at.isoformat(),
            'status': r.status,
            'admin_name': admin_name,
            'admin_email': admin_email,
            'admin_note': r.admin_note,
            'decided_at': r.decided_at.isoformat() if r.decided_at else None,
            'original_face_url': original_face_url,
            'captured_face_url': captured_face_url,
            'integrity_flagged': r.integrity_flagged,
            'face_approved': r.face_approved,
            'integrity_approved': r.integrity_approved,
            'integrity_details': integrity_details,
            'integrity_screenshots': integrity_screenshots,
        })
        
    return Response(data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def pending_face_requests_count_view(request):
    """
    Returns the count of face update requests pending approval.
    """
    user_profile = getattr(request.user, 'profile', None)
    if not user_profile or not user_profile.company:
        return Response({'count': 0})
        
    role = user_profile.role
    company = user_profile.company
    
    is_admin = (
        role == UserProfile.ROLE_COMPANY_ADMIN
        or _is_application_admin_email(user_profile.email)
    )
    
    if is_admin:
        count = FaceUpdateRequest.objects.filter(company=company, status='pending').count()
    else:
        count = FaceUpdateRequest.objects.filter(hr_user=user_profile, status='pending').count()
        
    return Response({'count': count})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def action_face_request_view(request, request_id):
    """
    Approve or Reject a face update request and proctoring integrity flags.
    Only Company Admin / App Admin can take action.
    """
    import os
    import re
    from django.core.files.base import ContentFile
    
    user_profile = getattr(request.user, 'profile', None)
    if not user_profile:
        return Response({'error': 'Unauthorized.'}, status=status.HTTP_403_FORBIDDEN)
        
    is_admin = (
        user_profile.role == UserProfile.ROLE_COMPANY_ADMIN
        or _is_application_admin_email(user_profile.email)
    )
    if not is_admin:
        return Response({'error': 'Only Company Admins can approve or reject face update requests.'}, status=status.HTTP_403_FORBIDDEN)
        
    try:
        req = FaceUpdateRequest.objects.select_related('submission', 'candidate_details', 'hr_user', 'company').get(id=request_id)
    except FaceUpdateRequest.DoesNotExist:
        return Response({'error': 'Request not found.'}, status=status.HTTP_404_NOT_FOUND)
        
    if req.company != user_profile.company and not _is_application_admin_email(user_profile.email):
        return Response({'error': 'Not authorized to action this request.'}, status=status.HTTP_403_FORBIDDEN)
        
    if req.status != 'pending':
        return Response({'error': 'This request has already been actioned.'}, status=status.HTTP_400_BAD_REQUEST)
        
    action = request.data.get('action')
    admin_note = (request.data.get('admin_note') or '').strip()
    
    # Combined inputs
    face_approved = request.data.get('face_approved')
    integrity_approved = request.data.get('integrity_approved')
    
    # Handle fallback/legacy action
    if face_approved is None and integrity_approved is None:
        if action == 'approve':
            face_approved = True
            integrity_approved = True if req.integrity_flagged else None
        elif action == 'reject':
            face_approved = False
            integrity_approved = False if req.integrity_flagged else None
        else:
            return Response({'error': 'Invalid action or approval parameters.'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        # Convert to boolean/None
        face_approved = bool(face_approved)
        if req.integrity_flagged:
            integrity_approved = bool(integrity_approved)
        else:
            integrity_approved = None

    details = req.candidate_details
    if not details:
        return Response({'error': 'Candidate details not found.'}, status=status.HTTP_400_BAD_REQUEST)

    # Determine overall request approval status
    # If integrity was flagged, both must be approved. Otherwise, just face mismatch.
    is_overall_approved = face_approved and (integrity_approved if req.integrity_flagged else True)

    with transaction.atomic():
        # Refresh details under transaction lock
        details = CandidateDetails.objects.select_for_update().get(id=details.id)
        
        if face_approved:
            norm_email = details.email.lower().strip()
            norm_pan = re.sub(r'[^A-Z0-9]', '', details.pan_number.strip().upper())
            person_id = norm_pan
            
            # Retrieve baseline identity link
            link = IdentityLink.objects.filter(pan_number=norm_pan).first()
            if not link:
                link = IdentityLink.objects.filter(email=norm_email).first()
                
            # Backup old registered face from IdentityLink
            old_face_file = None
            if link and link.snapshot_image:
                old_face_file = link.snapshot_image
                
            if old_face_file:
                try:
                    old_face_file.seek(0)
                    old_file_data = old_face_file.read()
                    details.previous_registered_face_backup.save(
                        name=f"backup_{person_id}_{os.path.basename(old_face_file.name)}",
                        content=ContentFile(old_file_data),
                        save=False
                    )
                except Exception as e:
                    print(f"[Backup] Failed to backup old registered face: {e}")
            else:
                if req.original_face_backup:
                    try:
                        req.original_face_backup.seek(0)
                        orig_data = req.original_face_backup.read()
                        details.previous_registered_face_backup.save(
                            name=f"backup_first_details_{person_id}.jpg",
                            content=ContentFile(orig_data),
                            save=False
                        )
                    except Exception as e:
                        print(f"[Backup] Failed to copy backup from request: {e}")
                        
            # Overwrite/Create IdentityLink
            if not link:
                link = IdentityLink(email=norm_email, pan_number=norm_pan)
                
            if req.captured_face_backup:
                try:
                    req.captured_face_backup.seek(0)
                    cap_data = req.captured_face_backup.read()
                    snapshot_file = ContentFile(cap_data, name=f"snapshot_{person_id}.jpg")
                    link.snapshot_image = snapshot_file
                except Exception as e:
                    print(f"[IdentityLink] Error copying captured snapshot to link: {e}")
            link.save()
            
            # Overwrite DeepFace canonical image file
            from api.ocr_utils import register_face_with_deepface
            
            deepface_snapshot = details.snapshot
            if req.captured_face_backup:
                try:
                    req.captured_face_backup.seek(0)
                    import base64
                    cap_data = req.captured_face_backup.read()
                    cap_b64 = base64.b64encode(cap_data).decode('utf-8')
                    deepface_snapshot = f"data:image/jpeg;base64,{cap_b64}"
                except Exception as e:
                    print(f"[DeepFace] Failed to read captured_face_backup: {e}")
                    
            reg_result = register_face_with_deepface(person_id, deepface_snapshot)
            if not reg_result.get('success'):
                print(f"[DeepFace] Registration failed: {reg_result.get('message')}")
                
            # Save approval metadata on details
            details.photo_update_approved = True
            details.photo_update_approved_by = "Company Admin"
            details.photo_update_approved_at = timezone.now()
            details.photo_update_reason = req.hr_reason
            details.photo_update_status = 'approved'
            details.save()
        else:
            details.photo_update_status = 'rejected'
            details.photo_update_approved = False
            details.photo_update_admin_note = admin_note
            details.save(update_fields=['photo_update_status', 'photo_update_approved', 'photo_update_admin_note'])

        # Save FaceUpdateRequest
        req.status = 'approved' if is_overall_approved else 'rejected'
        req.face_approved = face_approved
        req.integrity_approved = integrity_approved
        req.admin_note = admin_note
        req.decided_at = timezone.now()
        req.admin_user = user_profile
        req.save()
        
        # Create activity log entries
        inv_obj = CandidateInvitation.objects.get(id=details.invitation_id)
        logs = list(inv_obj.activity_logs) if isinstance(inv_obj.activity_logs, list) else []
        
        face_decision_str = "Approved" if face_approved else "Rejected"
        log_entry_face = {
            'timestamp': timezone.now().isoformat(),
            'action': f"Identity Mismatch {face_decision_str} by Admin",
            'details': f"Admin {face_decision_str.lower()} identity mismatch request. HR Reason: {req.hr_reason}. Admin Note: {admin_note}",
            'category': 'security'
        }
        logs.append(log_entry_face)
        
        if req.integrity_flagged:
            integrity_decision_str = "Approved" if integrity_approved else "Rejected"
            log_entry_integrity = {
                'timestamp': timezone.now().isoformat(),
                'action': f"Proctoring Integrity {integrity_decision_str} by Admin",
                'details': f"Admin {integrity_decision_str.lower()} proctoring integrity violations request. Admin Note: {admin_note}",
                'category': 'security'
            }
            logs.append(log_entry_integrity)
            
        inv_obj.activity_logs = logs
        inv_obj.save(update_fields=['activity_logs', 'updated_at'])
        
        # Recalculate submission scoring and result status immediately!
        from api.views.candidate_assessment_views import _update_submission_scoring_logic
        _update_submission_scoring_logic(req.submission, finalize=True)
        req.submission.save()
        
    return Response({'message': f'Request actioned successfully. Status is {"approved" if is_overall_approved else "rejected"}.'})