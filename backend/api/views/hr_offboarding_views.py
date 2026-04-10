"""
HR Offboarding Views
"""

from .._imports import *


def _can_manage(actor, target):
    if not actor or not target:
        return False
    if actor.company_id != target.company_id:
        return False

    if actor.role == UserProfile.ROLE_COMPANY_ADMIN:
        return target.role in {
            UserProfile.ROLE_HR_MANAGER,
            UserProfile.ROLE_HR,
            UserProfile.ROLE_INTERVIEWER,
        }

    if actor.role == UserProfile.ROLE_HR_MANAGER:
        if target.role not in {UserProfile.ROLE_HR, UserProfile.ROLE_INTERVIEWER}:
            return False
        return (
            target.manager_id == actor.id
            or target.invited_by_profile_id == actor.id
        )

    return False


def _preview_counts(from_user):
    from ..models import Assessment, CustomAssessment, CandidateInvitation

    data = {
        "assessments": Assessment.objects.filter(user_profile=from_user, is_deleted=False).count(),
        "custom_assessments": CustomAssessment.objects.filter(user_profile=from_user).count(),
        "candidate_invitations": CandidateInvitation.objects.filter(user_profile=from_user).count(),
        "ai_assessments": 0,
        "ai_candidates": 0,
        "subordinates": UserProfile.objects.filter(manager=from_user).count(),
    }

    try:
        from ai_assessments.models import Assessment as AIAssessment
        data["ai_assessments"] = AIAssessment.objects.filter(user_profile=from_user, is_deleted=False).count()
    except Exception:
        pass

    try:
        from ai_candidates.models import Candidate as AICandidate
        data["ai_candidates"] = AICandidate.objects.filter(user_profile=from_user, is_deleted=False).count()
    except Exception:
        pass

    return data


@csrf_exempt
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def transfer_preview_view(request, user_id):
    try:
        actor = getattr(request.user, "profile", None)
        if not actor:
            return Response({"error": "Actor profile not found."}, status=status.HTTP_403_FORBIDDEN)

        from_user = UserProfile.objects.select_related("company").filter(id=user_id).first()
        if not from_user:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        if not _can_manage(actor, from_user):
            return Response({"error": "You are not permitted to manage this user."}, status=status.HTTP_403_FORBIDDEN)

        counts = _preview_counts(from_user)
        replacements_qs = UserProfile.objects.filter(
            company=from_user.company,
            is_active=True,
            is_approved=True,
            role=from_user.role,
        ).exclude(id=from_user.id).order_by("first_name", "last_name")

        replacements = [{
            "id": u.id,
            "name": f"{u.first_name or ''} {u.last_name or ''}".strip() or u.email,
            "email": u.email,
            "role": u.role,
        } for u in replacements_qs]

        return Response({
            "user": {
                "id": from_user.id,
                "name": f"{from_user.first_name or ''} {from_user.last_name or ''}".strip() or from_user.email,
                "email": from_user.email,
                "role": from_user.role,
                "is_active": from_user.is_active,
            },
            "ownership_counts": counts,
            "eligible_replacements": replacements,
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def transfer_ownership_view(request, user_id):
    try:
        actor = getattr(request.user, "profile", None)
        if not actor:
            return Response({"error": "Actor profile not found."}, status=status.HTTP_403_FORBIDDEN)

        from_user = UserProfile.objects.select_related("company").filter(id=user_id).first()
        if not from_user:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        if not _can_manage(actor, from_user):
            return Response({"error": "You are not permitted to manage this user."}, status=status.HTTP_403_FORBIDDEN)

        to_user_id = request.data.get("to_user_id")
        transfer_reason = (request.data.get("transfer_reason") or "").strip()
        deactivate_after = bool(request.data.get("deactivate_after", True))
        if not to_user_id:
            return Response({"error": "to_user_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        to_user = UserProfile.objects.select_related("company").filter(id=to_user_id).first()
        if not to_user:
            return Response({"error": "Replacement user not found."}, status=status.HTTP_404_NOT_FOUND)
        if to_user.company_id != from_user.company_id:
            return Response({"error": "Replacement user must belong to the same company."}, status=status.HTTP_400_BAD_REQUEST)
        if not to_user.is_active:
            return Response({"error": "Replacement user is deactivated."}, status=status.HTTP_400_BAD_REQUEST)
        if to_user.id == from_user.id:
            return Response({"error": "Cannot transfer ownership to same user."}, status=status.HTTP_400_BAD_REQUEST)

        from ..models import Assessment, CustomAssessment, CandidateInvitation, OwnershipTransferLog

        counts = {
            "assessments": 0,
            "custom_assessments": 0,
            "candidate_invitations": 0,
            "ai_assessments": 0,
            "ai_candidates": 0,
            "subordinates": 0,
        }

        with transaction.atomic():
            counts["assessments"] = Assessment.objects.filter(user_profile=from_user).update(user_profile=to_user)
            counts["custom_assessments"] = CustomAssessment.objects.filter(user_profile=from_user).update(user_profile=to_user)
            counts["candidate_invitations"] = CandidateInvitation.objects.filter(user_profile=from_user).update(user_profile=to_user)

            try:
                from ai_assessments.models import Assessment as AIAssessment
                counts["ai_assessments"] = AIAssessment.objects.filter(user_profile=from_user).update(user_profile=to_user)
            except Exception:
                pass

            try:
                from ai_candidates.models import Candidate as AICandidate
                counts["ai_candidates"] = AICandidate.objects.filter(user_profile=from_user).update(user_profile=to_user)
            except Exception:
                pass

            counts["subordinates"] = UserProfile.objects.filter(manager=from_user).update(manager=to_user)

            OwnershipTransferLog.objects.create(
                transferred_by=actor,
                transferred_from=from_user,
                transferred_to=to_user,
                transfer_reason=transfer_reason,
                assessments_transferred=counts["assessments"],
                custom_assessments_transferred=counts["custom_assessments"],
                candidate_invitations_transferred=counts["candidate_invitations"],
                ai_assessments_transferred=counts["ai_assessments"],
                ai_candidates_transferred=counts["ai_candidates"],
                subordinates_reassigned=counts["subordinates"],
                from_name=f"{from_user.first_name or ''} {from_user.last_name or ''}".strip(),
                from_email=from_user.email,
                to_name=f"{to_user.first_name or ''} {to_user.last_name or ''}".strip(),
                to_email=to_user.email,
                by_name=f"{actor.first_name or ''} {actor.last_name or ''}".strip(),
                by_email=actor.email,
                also_deactivated=deactivate_after,
            )

            if deactivate_after:
                from_user.is_active = False
                from_user.deactivated_at = timezone.now()
                from_user.deactivated_by = actor
                from_user.deactivation_reason = transfer_reason or "Replaced by another user."
                from_user.save(update_fields=["is_active", "deactivated_at", "deactivated_by", "deactivation_reason", "updated_at"])
                if from_user.user:
                    from_user.user.is_active = False
                    from_user.user.save(update_fields=["is_active"])

        return Response({
            "message": "Ownership transfer completed successfully.",
            "transferred_from": {"id": from_user.id, "email": from_user.email},
            "transferred_to": {"id": to_user.id, "email": to_user.email},
            "transferred_by": {"id": actor.id, "email": actor.email},
            "transfer_reason": transfer_reason,
            "deactivated": deactivate_after,
            "counts": counts,
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def deactivate_user_view(request, user_id):
    try:
        actor = getattr(request.user, "profile", None)
        if not actor:
            return Response({"error": "Actor profile not found."}, status=status.HTTP_403_FORBIDDEN)

        target = UserProfile.objects.select_related("company", "user").filter(id=user_id).first()
        if not target:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        if not _can_manage(actor, target):
            return Response({"error": "You are not permitted to manage this user."}, status=status.HTTP_403_FORBIDDEN)
        if not target.is_active:
            return Response({"error": "User is already deactivated."}, status=status.HTTP_409_CONFLICT)

        reason = (request.data.get("reason") or "").strip()
        target.is_active = False
        target.deactivated_at = timezone.now()
        target.deactivated_by = actor
        target.deactivation_reason = reason or "Deactivated by admin."
        target.save(update_fields=["is_active", "deactivated_at", "deactivated_by", "deactivation_reason", "updated_at"])
        if target.user:
            target.user.is_active = False
            target.user.save(update_fields=["is_active"])

        return Response({
            "message": f"User {target.email} has been deactivated.",
            "user_id": target.id,
            "email": target.email,
            "deactivated_at": target.deactivated_at.isoformat(),
            "reason": target.deactivation_reason,
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def reactivate_user_view(request, user_id):
    try:
        actor = getattr(request.user, "profile", None)
        if not actor:
            return Response({"error": "Actor profile not found."}, status=status.HTTP_403_FORBIDDEN)
        if actor.role != UserProfile.ROLE_COMPANY_ADMIN:
            return Response({"error": "Only Company Admin can reactivate users."}, status=status.HTTP_403_FORBIDDEN)

        target = UserProfile.objects.select_related("company", "user").filter(id=user_id).first()
        if not target:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        if target.company_id != actor.company_id:
            return Response({"error": "User belongs to a different company."}, status=status.HTTP_403_FORBIDDEN)
        if target.is_active:
            return Response({"error": "User is already active."}, status=status.HTTP_409_CONFLICT)

        target.is_active = True
        target.deactivated_at = None
        target.deactivated_by = None
        target.deactivation_reason = None
        target.save(update_fields=["is_active", "deactivated_at", "deactivated_by", "deactivation_reason", "updated_at"])
        if target.user:
            target.user.is_active = True
            target.user.save(update_fields=["is_active"])

        return Response({"message": f"User {target.email} has been reactivated.", "user_id": target.id, "email": target.email}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def transfer_logs_view(request):
    try:
        actor = getattr(request.user, "profile", None)
        if not actor:
            return Response({"error": "Actor profile not found."}, status=status.HTTP_403_FORBIDDEN)

        from ..models import OwnershipTransferLog
        if actor.role == UserProfile.ROLE_COMPANY_ADMIN:
            logs = OwnershipTransferLog.objects.filter(transferred_from__company=actor.company).order_by("-transferred_at")[:100]
        elif actor.role == UserProfile.ROLE_HR_MANAGER:
            logs = OwnershipTransferLog.objects.filter(transferred_by=actor).order_by("-transferred_at")[:50]
        else:
            return Response({"error": "Forbidden."}, status=status.HTTP_403_FORBIDDEN)

        data = []
        for log in logs:
            data.append({
                "id": log.id,
                "transferred_at": log.transferred_at.isoformat(),
                "from_name": log.from_name,
                "from_email": log.from_email,
                "to_name": log.to_name,
                "to_email": log.to_email,
                "by_name": log.by_name,
                "by_email": log.by_email,
                "transfer_reason": log.transfer_reason,
                "also_deactivated": log.also_deactivated,
                "counts": {
                    "assessments": log.assessments_transferred,
                    "custom_assessments": log.custom_assessments_transferred,
                    "candidate_invitations": log.candidate_invitations_transferred,
                    "ai_assessments": log.ai_assessments_transferred,
                    "ai_candidates": log.ai_candidates_transferred,
                    "subordinates": log.subordinates_reassigned,
                },
            })
        return Response({"logs": data}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
