import os
import time
from datetime import timedelta
from typing import Any

import requests
from django.db import transaction
from django.utils import timezone
from requests.exceptions import RequestException
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import CodingInvite, CodingInviteQuestion, CodingQuestion, CodingTestCase, CodingSubmission


EXECUTOR_BASE_URL = os.environ.get("EXECUTOR_BASE_URL", "http://localhost:4000").rstrip("/")

DEFAULT_LANGS = [
    "cpp",
    "java",
    "python3",
    "python",
    "javascript",
    "typescript",
    "csharp",
    "c",
    "go",
    "kotlin",
    "swift",
    "rust",
    "ruby",
    "php",
    "dart",
    "scala",
    "sql",
]

INVITE_DEFAULT_TIME_LIMIT_SECONDS = 2700  # 45 minutes default


def _languages_or_primary(q: CodingQuestion):
    # Return exactly what is stored; no defaults
    # Ensure it's always a list
    if q.languages is None:
        return []
    if isinstance(q.languages, list):
        return q.languages
    # Handle case where it might be stored as a string or other type
    try:
        if isinstance(q.languages, str):
            import json
            parsed = json.loads(q.languages)
            return parsed if isinstance(parsed, list) else []
        return []
    except Exception:
        return []


def _normalize_output(text: Any) -> str:
    """
    Normalize stdout for deterministic comparison:
    - normalize newlines
    - strip trailing whitespace per line
    - strip leading/trailing empty lines
    """
    s = "" if text is None else str(text)
    s = s.replace("\r\n", "\n")
    lines = [ln.rstrip() for ln in s.split("\n")]
    s2 = "\n".join(lines).strip()
    return s2


def _validate_sql_safety(code: str) -> str | None:
    """
    Reject code containing forbidden SQL keywords.
    Returns error message if unsafe, None if safe.
    """
    # Keywords forbidden by the USER
    forbidden = [
        "DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "CREATE", 
        "TRUNCATE", "ATTACH", "PRAGMA"
    ]
    
    # We use a simple upper-case check. 
    # This is extremely strict as per "Reject immediately if query contains"
    code_upper = code.upper()
    
    # To avoid matching harmless words (e.g. "update_date"), we can use regex 
    # or just check split words. But requirements say "contains". 
    # I will assume whole-word matching is preferred to avoid false positives 
    # like 'create_at' or 'update_time', but still safe.
    import re
    for kw in forbidden:
        # Match whole word, case insensitive
        if re.search(r'\b' + re.escape(kw) + r'\b', code_upper):
            return f"Query contains forbidden keyword: {kw}"
    return None





def _merge_code(question: CodingQuestion, user_code: str, language: str = "") -> str:
    """Return user code as-is for full program mode."""
    return "" if user_code is None else str(user_code)


def _call_executor(*, language: str, source_code: str, stdin: str | None, time_limit_ms: int, memory_mb: int, testcases: list | None = None, schema_sql: str | None = None, database_engine: str | None = None) -> dict:
    clean_stdin = stdin or ""
    if clean_stdin.strip() == "None":
        clean_stdin = ""

    payload = {
        "language": language,
        "source_code": source_code,
        "stdin": clean_stdin,
        "time_limit_ms": time_limit_ms,
        "memory_mb": memory_mb,
    }
    if testcases:
        for tc in testcases:
            if tc.get("stdin") and str(tc["stdin"]).strip() == "None":
                tc["stdin"] = ""
        payload["testcases"] = testcases
    if schema_sql:
        payload["schema_sql"] = schema_sql
    if database_engine:
        payload["database_engine"] = database_engine

    try:
        # Increase timeout buffer and ensure min 120s
        timeout_val = max(120, int(time_limit_ms / 1000) * (len(testcases) if testcases else 1) + 60)
        resp = requests.post(f"{EXECUTOR_BASE_URL}/execute", json=payload, timeout=timeout_val)
        
        if resp.status_code >= 400:
             return {"ok": False, "error": f"Executor returned status {resp.status_code}"}
        
        data = resp.json()
        if not data.get("ok"):
             return {"ok": False, "error": data.get("error") or "Executor Error"}
        return data

    except RequestException as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Executor Timeout/Request Error: {str(e)}")
        return {"ok": False, "error": f"Execution Service Unavailable or Timed Out (Port 4000). Error: {str(e)}"}
    except Exception as e:
        return {"ok": False, "error": f"Unexpected Executor Call Failure: {str(e)}"}


def _map_to_valid_language(lang: str) -> str:
    """
    Map frontend language codes to valid backend CodingQuestion.LANGUAGE_CHOICES.
    Returns the primary language that the executor can handle.
    """
    lang = lang.lower().strip()
    # Map common variations to valid choices
    mapping = {
        'python3': 'python',
        'python': 'python',
        'typescript': 'typescript',
        'ts': 'typescript',
        'javascript': 'javascript',
        'js': 'javascript',
        'java': 'java',
        'c': 'c',
        'cpp': 'cpp',
        'c++': 'cpp',
        'csharp': 'csharp',
        'c#': 'csharp',
        'go': 'go',
        'golang': 'go',
        'rust': 'rust',
        'rs': 'rust',
        'php': 'php',
        # Natively supported now
        'kotlin': 'kotlin',
        'kt': 'kotlin',
        'swift': 'swift',
        'ruby': 'ruby',
        'rb': 'ruby',
        'dart': 'dart',
        'scala': 'scala',
        'sql': 'sql',
    }
    return mapping.get(lang.lower(), 'python')  # Default to python if unknown


def _clean_languages(value) -> list[str]:
    """
    Clean and validate language list. Returns list of valid language codes
    that can be stored in the languages JSONField (for display/selection).
    """
    allowed = set(DEFAULT_LANGS)
    if isinstance(value, str):
        raw_list = [v.strip() for v in value.split(",")]
    elif isinstance(value, (list, tuple)):
        raw_list = [str(v).strip() for v in value if str(v).strip()]
    else:
        raw_list = []
    seen = set()
    cleaned = []
    for v in raw_list:
        lv = v.lower()
        if lv in allowed and lv not in seen:
            cleaned.append(lv)
            seen.add(lv)
    return cleaned


def _invite_remaining_seconds(invite: CodingInvite) -> int:
    if invite.expires_at:
        remaining = int((invite.expires_at - timezone.now()).total_seconds())
        return max(0, remaining)
    return max(0, int(invite.time_limit_seconds or INVITE_DEFAULT_TIME_LIMIT_SECONDS))


def _ensure_invite_started(invite: CodingInvite):
    if invite.started_at:
        return
    now = timezone.now()
    invite.started_at = now
    invite.expires_at = now + timedelta(seconds=int(invite.time_limit_seconds or INVITE_DEFAULT_TIME_LIMIT_SECONDS))
    invite.status = CodingInvite.STATUS_STARTED
    invite.save(update_fields=["started_at", "expires_at", "status", "updated_at"])


def _allowed_languages_for_invite(invite: CodingInvite, question: CodingQuestion | None = None) -> list[str]:
    langs = []
    if isinstance(invite.allowed_languages, list):
        langs = [str(v).lower() for v in invite.allowed_languages if str(v).strip()]
    if langs:
        return langs
    if question:
        qlangs = [str(v).lower() for v in (_languages_or_primary(question) or []) if v]
        if qlangs:
            return qlangs
        if question.language:
            return [str(question.language).lower()]
    return []


def _normalize_language_for_invite(invite: CodingInvite, requested_lang: str | None, question: CodingQuestion | None = None) -> str | None:
    requested = (requested_lang or "").lower().strip()
    allowed = _allowed_languages_for_invite(invite, question)
    if allowed:
        if requested and requested in allowed:
            return requested
        return allowed[0]
    return requested or (question.language if question else None)


def _serialize_invite_question(iq: CodingInviteQuestion) -> dict:
    q = iq.question
    langs = _languages_or_primary(q)
    return {
        "invite_question_id": iq.id,
        "question_id": q.id,
        "title": q.title,
        "description": q.description,
        "languages": langs,
        "mode": q.mode,
        "starter_code": q.starter_code,
        "time_limit_ms": q.time_limit_ms,
        "memory_limit_mb": q.memory_limit_mb,
        "order": iq.display_order,
        "last_code": iq.last_code,
        "last_language": iq.last_language,
        "last_run_result": iq.last_run_result,
        "run_count": iq.run_count,
    }


def _perform_invite_submission(invite: CodingInvite, *, code_map: dict | None, auto: bool, reason: str | None = None, selected_language: str | None = None) -> dict:
    if invite.status in (CodingInvite.STATUS_SUBMITTED, CodingInvite.STATUS_EXPIRED):
        return {
            "status": invite.status,
            "remaining_seconds": _invite_remaining_seconds(invite),
            "auto_submitted": bool(invite.auto_submitted),
            "final_results": invite.final_results or {},
        }

    effective_language = _normalize_language_for_invite(invite, selected_language or invite.selected_language, None)
    if effective_language and effective_language != invite.selected_language:
        invite.selected_language = effective_language

    results = []
    now = timezone.now()

    with transaction.atomic():
        for iq in invite.invite_questions.select_related("question").order_by("display_order"):
            q = iq.question
            # resolve code and language for this question
            entry = None
            if code_map:
                entry = code_map.get(str(q.id)) or code_map.get(q.id)
            code = ""
            lang_override = None
            if isinstance(entry, dict):
                code = entry.get("code") or entry.get("submitted_code") or ""
                lang_override = entry.get("language")
            elif isinstance(entry, str):
                code = entry

            if not code:
                code = iq.last_code or q.starter_code or ""

            lang_for_q = _normalize_language_for_invite(invite, lang_override or effective_language or iq.last_language, q)

            evaluation = _evaluate_question(q=q, user_code=code, include_hidden=True, exec_language=lang_for_q)
            sub = CodingSubmission.objects.create(
                question_id=q.id,
                user_email=invite.candidate_email,
                candidate_name=invite.candidate_name,
                language=lang_for_q or q.language,
                mode=q.mode,
                submitted_code=code,
                passed_count=evaluation["passed_count"],
                total_tests=evaluation["total_tests"],
                status=evaluation["status"],
                execution_time_ms=evaluation["execution_time_ms"],
                results={"tests": evaluation["results"]},
            )

            iq.final_submission = sub
            iq.last_language = lang_for_q or iq.last_language
            iq.last_code = code
            iq.last_run_result = evaluation
            iq.save(update_fields=["final_submission", "last_language", "last_code", "last_run_result", "updated_at"])

            results.append(
                {
                    "question_id": q.id,
                    "invite_question_id": iq.id,
                    "submission_id": sub.id,
                    "status": evaluation["status"],
                    "passed_count": evaluation["passed_count"],
                    "total_tests": evaluation["total_tests"],
                    "execution_time_ms": evaluation["execution_time_ms"],
                }
            )

        invite.status = CodingInvite.STATUS_EXPIRED if auto else CodingInvite.STATUS_SUBMITTED
        invite.submitted_at = now
        invite.auto_submitted = auto
        invite.final_results = {
            "reason": reason or ("auto_submit" if auto else "manual_submit"),
            "questions": results,
        }
        invite.save(update_fields=["status", "submitted_at", "auto_submitted", "final_results", "selected_language", "updated_at"])

    return {
        "status": invite.status,
        "submitted_at": invite.submitted_at.isoformat() if invite.submitted_at else None,
        "auto_submitted": auto,
        "remaining_seconds": 0,
        "results": results,
    }


def _auto_submit_if_expired(invite: CodingInvite) -> dict | None:
    remaining = _invite_remaining_seconds(invite)
    if remaining > 0:
        return None
    if invite.status in (CodingInvite.STATUS_SUBMITTED, CodingInvite.STATUS_EXPIRED):
        return {
            "status": invite.status,
            "remaining_seconds": 0,
            "auto_submitted": bool(invite.auto_submitted),
            "final_results": invite.final_results or {},
        }
    return _perform_invite_submission(invite, code_map=None, auto=True, reason="timer_expired")


def _get_org_from_request(request) -> str | None:
    """
    Infer organization/company name from request data, query params, headers, or authenticated user.
    This is used to scope coding questions per tenant/company.
    """
    # 1) POST/PUT payload
    data = getattr(request, "data", None) or {}
    org = (
        data.get("organization_name_snapshot")
        or data.get("organization_name")
        or data.get("company_name")
        or data.get("company")
    )

    # 2) Query params (GET list/detail)
    if not org and hasattr(request, "GET"):
        org = (
            request.GET.get("organization_name")
            or request.GET.get("company_name")
            or request.GET.get("company")
        )

    # 3) Header override
    if not org:
        org = request.headers.get("X-Organization-Name") or request.headers.get("X-Company-Name")

    # 4) Authenticated user profile (if any)
    if not org and getattr(request, "user", None) and getattr(request.user, "is_authenticated", False):
        profile = getattr(request.user, "profile", None)
        if profile:
            org = getattr(profile, "organization_name", None)
            if not org and getattr(profile, "company", None):
                org = getattr(profile.company, "name", None)

    if org is None:
        return None

    org_str = str(org).strip()
    return org_str if org_str else None


def _get_email_from_request(request) -> str | None:
    data = getattr(request, "data", None) or {}
    email = data.get("created_by_email") or data.get("user_email")
    if email:
        return str(email).strip() or None
    user = getattr(request, "user", None)
    if user and getattr(user, "is_authenticated", False):
        return getattr(user, "email", None) or getattr(user, "username", None)
    return None


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def coding_questions_view(request):
    if request.method == "GET":
        try:
            # RBAC: Scope Coding Questions to the requester's invite TREE
            # CodingQuestion stores `created_by_email` instead of a user FK to remain isolated.
            user_profile = getattr(request.user, 'profile', None) if getattr(request.user, 'is_authenticated', False) else None
            
            qs = CodingQuestion.objects.all()
            
            if user_profile:
                from api._imports import get_scoped_user_ids
                scoped_ids = get_scoped_user_ids(user_profile)
                
                if scoped_ids is not None:
                    # Map the scoped profile IDs to their corresponding user emails
                    from api.models import UserProfile
                    scoped_emails = list(
                        UserProfile.objects.filter(id__in=scoped_ids)
                        .select_related('user')
                        .values_list('user__email', flat=True)
                    )
                    # Include the requester's own email just in case the profile link is weird
                    if request.user.email and request.user.email not in scoped_emails:
                        scoped_emails.append(request.user.email)
                    
                    qs = qs.filter(created_by_email__in=scoped_emails)
                else:
                    # Platform Superadmin: Filter by requested org if provided
                    org_name = _get_org_from_request(request)
                    if org_name:
                        qs = qs.filter(organization_name_snapshot__iexact=org_name)
            else:
                # Unauthenticated or no profile: fallback to strict org match if provided, else empty
                org_name = _get_org_from_request(request)
                if org_name:
                    qs = qs.filter(organization_name_snapshot__iexact=org_name)
                else:
                    qs = qs.none() 

            qs = qs.order_by("-created_at")[:500]
            results = []
            for q in qs:
                try:
                    results.append(
                        {
                            "id": q.id,
                            "title": q.title or "",
                            "description": q.description or "",
                            "language": q.language or "",
                            "languages": _languages_or_primary(q),
                            "mode": q.mode or "",
                            "starter_code": q.starter_code or "",
                            "schema_sql": q.schema_sql or "",
                            "database_engine": q.database_engine or "",
                            "difficulty": q.difficulty,
                            "time_limit_ms": q.time_limit_ms,
                            "memory_limit_mb": q.memory_limit_mb,
                            "created_by_email": q.created_by_email or "",
                            "organization_name_snapshot": q.organization_name_snapshot or "",
                            "custom_assessment_id": q.custom_assessment_id,
                            "is_active": q.is_active if q.is_active is not None else True,
                            "created_at": q.created_at.isoformat() if q.created_at else None,
                            "updated_at": q.updated_at.isoformat() if q.updated_at else None,
                        }
                    )
                except Exception as e:
                    # Log error for this specific question but continue with others
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f"Error serializing coding question {q.id}: {str(e)}")
                    continue
            return Response({"count": len(results), "results": results}, status=status.HTTP_200_OK)
        except Exception as e:
            import logging
            import traceback
            logger = logging.getLogger(__name__)
            logger.error(f"Error in coding_questions_view GET: {str(e)}\n{traceback.format_exc()}")
            return Response({"error": f"Failed to load coding questions: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # POST
    data = request.data or {}
    raw_langs = data.get("languages")
    if (not raw_langs) and hasattr(request, "data") and hasattr(request.data, "getlist"):
        raw_langs = request.data.getlist("languages")
    langs = _clean_languages(raw_langs)
    title = (data.get("title") or "").strip()
    if not title:
        return Response({"error": "title is required"}, status=status.HTTP_400_BAD_REQUEST)
    if not langs:
        return Response({"error": "languages is required and must have at least one value"}, status=status.HTTP_400_BAD_REQUEST)
    mode = CodingQuestion.MODE_FULL_PROGRAM
    # Map the first language to a valid backend language choice
    primary_language = _map_to_valid_language(langs[0])

    org_name = _get_org_from_request(request)
    creator_email = _get_email_from_request(request)

    q = CodingQuestion.objects.create(
        title=title,
        description=data.get("description"),
        language=primary_language,
        languages=langs,
        mode=mode,
        starter_code=data.get("starter_code"),
        schema_sql=data.get("schema_sql"),
        database_engine=data.get("database_engine"),
        difficulty=data.get("difficulty", "medium"),
        time_limit_ms=int(data.get("time_limit_ms") or 3000),
        memory_limit_mb=int(data.get("memory_limit_mb") or 256),
        created_by_email=creator_email,
        organization_name_snapshot=org_name,
        custom_assessment_id=data.get("custom_assessment_id"),
        is_active=bool(data.get("is_active", True)),
    )
    return Response({"id": q.id}, status=status.HTTP_201_CREATED)


def _get_coding_question_or_error(request, question_id: int):
    """
    Helper to fetch a CodingQuestion by ID and enforce tree-based RBAC.
    Returns (question_object, None) if successful.
    Returns (None, Response) if not found or unauthorized.
    """
    q = CodingQuestion.objects.filter(id=question_id).first()
    if not q:
        return None, Response({"error": "Coding question not found"}, status=status.HTTP_404_NOT_FOUND)

    # RBAC: Verify ownership via the invite tree.
    user_profile = getattr(request.user, 'profile', None) if getattr(request.user, 'is_authenticated', False) else None
    
    if user_profile:
        from api._imports import get_scoped_user_ids
        scoped_ids = get_scoped_user_ids(user_profile)
        
        if scoped_ids is not None:
            from .models import UserProfile
            scoped_emails = list(
                UserProfile.objects.filter(id__in=scoped_ids)
                .select_related('user')
                .values_list('user__email', flat=True)
            )
            if request.user.email and request.user.email not in scoped_emails:
                scoped_emails.append(request.user.email)
            
            # If the question's creator is not in this user's tree, deny access.
            if q.created_by_email not in scoped_emails:
                return None, Response({"error": "Coding question not found or unauthorized"}, status=status.HTTP_404_NOT_FOUND)
        else:
            # Platform Superadmin: fallback to org match if requested
            requested_org = _get_org_from_request(request)
            if requested_org and q.organization_name_snapshot and q.organization_name_snapshot.lower() != requested_org.lower():
                return None, Response({"error": "Coding question not found"}, status=status.HTTP_404_NOT_FOUND)
    else:
        # Unauthenticated or No Profile context:
        # If the view is IsAuthenticated, this branch generally shouldn't be reached by external users.
        # However, for safety, we MUST have a requested_org to allow access to a question.
        requested_org = _get_org_from_request(request)
        if not requested_org:
            return None, Response({"error": "Unauthorized: No organization context provided"}, status=status.HTTP_401_UNAUTHORIZED)
            
        if q.organization_name_snapshot and q.organization_name_snapshot.lower() != requested_org.lower():
            return None, Response({"error": "Coding question not found"}, status=status.HTTP_404_NOT_FOUND)
            
    return q, None


@api_view(["GET", "PUT", "PATCH", "DELETE"])
@permission_classes([IsAuthenticated])
def coding_question_detail_view(request, question_id: int):
    q, error_response = _get_coding_question_or_error(request, question_id)
    if error_response:
        return error_response

    if request.method == "GET":
        return Response(
            {
                "id": q.id,
                "title": q.title,
                "description": q.description,
                "language": q.language,
                "languages": _languages_or_primary(q),
                "mode": q.mode,
                "starter_code": q.starter_code,
                "schema_sql": q.schema_sql,
                "database_engine": q.database_engine,
                "difficulty": q.difficulty,
                "time_limit_ms": q.time_limit_ms,
                "memory_limit_mb": q.memory_limit_mb,
                "created_by_email": q.created_by_email,
                "organization_name_snapshot": q.organization_name_snapshot,
                "custom_assessment_id": q.custom_assessment_id,
                "is_active": q.is_active,
                "created_at": q.created_at.isoformat() if q.created_at else None,
                "updated_at": q.updated_at.isoformat() if q.updated_at else None,
            },
            status=status.HTTP_200_OK,
        )

    if request.method in ("PUT", "PATCH"):
        data = request.data or {}
        raw_langs = data.get("languages")
        if (not raw_langs) and hasattr(request, "data") and hasattr(request.data, "getlist"):
            raw_langs = request.data.getlist("languages")
        for field in [
            "title",
            "description",
            "starter_code",
            "schema_sql",
            "database_engine",
            "difficulty",
            "created_by_email",
            "organization_name_snapshot",
            "custom_assessment_id",
        ]:
            if field in data:
                setattr(q, field, data.get(field))
        # Always use full_program mode
        q.mode = CodingQuestion.MODE_FULL_PROGRAM
        # Handle language field separately to map to valid choice
        if "language" in data:
            q.language = _map_to_valid_language(data.get("language"))
        if (raw_langs is not None) or ("languages" in data):
            cleaned = _clean_languages(raw_langs)
            if cleaned:
                q.languages = cleaned
                # Map to valid backend language choice
                q.language = _map_to_valid_language(cleaned[0])
            else:
                q.languages = []
                q.language = CodingQuestion.LANGUAGE_PYTHON  # Default fallback
        if "time_limit_ms" in data:
            q.time_limit_ms = int(data.get("time_limit_ms") or 3000)
        if "memory_limit_mb" in data:
            q.memory_limit_mb = int(data.get("memory_limit_mb") or 256)
        if "is_active" in data:
            q.is_active = bool(data.get("is_active"))
        q.save()
        return Response({"ok": True}, status=status.HTTP_200_OK)

    if request.method == "DELETE":
        q.delete()
        return Response({"ok": True}, status=status.HTTP_200_OK)

    return Response({"error": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def coding_testcases_view(request, question_id: int):
    q, error_response = _get_coding_question_or_error(request, question_id)
    if error_response:
        return error_response

    if request.method == "GET":
        tcs = CodingTestCase.objects.filter(question_id=question_id).order_by("id")
        results = []
        for tc in tcs:
            results.append(
                {
                    "id": tc.id,
                    "question_id": tc.question_id,
                    "stdin": tc.stdin,
                    "expected_stdout": tc.expected_stdout,
                    "is_hidden": tc.is_hidden,
                    "created_at": tc.created_at.isoformat() if tc.created_at else None,
                }
            )
        return Response({"count": len(results), "results": results}, status=status.HTTP_200_OK)

    # POST
    data = request.data or {}
    tc = CodingTestCase.objects.create(
        question_id=question_id,
        stdin=data.get("stdin"),
        expected_stdout=data.get("expected_stdout"),
        is_hidden=bool(data.get("is_hidden", False)),
    )
    return Response({"id": tc.id}, status=status.HTTP_201_CREATED)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def coding_testcase_delete_view(request, testcase_id: int):
    tc = CodingTestCase.objects.filter(id=testcase_id).first()
    if not tc:
        return Response({"error": "Testcase not found"}, status=status.HTTP_404_NOT_FOUND)
        
    q, error_response = _get_coding_question_or_error(request, tc.question_id)
    if error_response:
        return error_response
        
    tc.delete()
    return Response({"ok": True}, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def coding_invites_view(request):
    """
    Create a coding invite with one or more questions and an allowed language list.

    Body:
    {
      "candidate_name": "...",
      "candidate_email": "...",
      "question_ids": [1,2,3],
      "allowed_languages": ["python","javascript"],
      "time_limit_seconds": 2700,
      "custom_assessment_id": 123,
      "created_by_email": "...",
      "organization_name_snapshot": "...",
      "invited_by_email": "..."
    }
    """
    data = request.data or {}
    candidate_name = (data.get("candidate_name") or "").strip()
    candidate_email = (data.get("candidate_email") or "").strip()
    if not candidate_name or not candidate_email:
        return Response({"error": "candidate_name and candidate_email are required"}, status=status.HTTP_400_BAD_REQUEST)

    question_ids = data.get("question_ids") or []
    if not isinstance(question_ids, list) or len(question_ids) == 0:
        return Response({"error": "question_ids must be a non-empty array"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        question_ids = [int(qid) for qid in question_ids]
    except Exception:
        return Response({"error": "question_ids must be numeric"}, status=status.HTTP_400_BAD_REQUEST)

    qs = list(CodingQuestion.objects.filter(id__in=question_ids, is_active=True))
    if len(qs) != len(set(question_ids)):
        return Response({"error": "One or more coding questions are invalid or inactive"}, status=status.HTTP_400_BAD_REQUEST)

    allowed_languages = _clean_languages(data.get("allowed_languages") or data.get("languages"))
    if not allowed_languages:
        return Response({"error": "allowed_languages must include at least one language"}, status=status.HTTP_400_BAD_REQUEST)

    time_limit_seconds = int(data.get("time_limit_seconds") or INVITE_DEFAULT_TIME_LIMIT_SECONDS)
    time_limit_seconds = max(60, time_limit_seconds)  # at least 1 minute

    with transaction.atomic():
        invite = CodingInvite.objects.create(
            candidate_name=candidate_name,
            candidate_email=candidate_email,
            allowed_languages=allowed_languages,
            time_limit_seconds=time_limit_seconds,
            organization_name_snapshot=data.get("organization_name_snapshot"),
            created_by_email=data.get("created_by_email"),
            invited_by_email=data.get("invited_by_email"),
            custom_assessment_id=data.get("custom_assessment_id"),
            status=CodingInvite.STATUS_SENT,
        )

        order_map = {qid: idx for idx, qid in enumerate(question_ids)}
        for q in qs:
            CodingInviteQuestion.objects.create(
                invite=invite,
                question=q,
                display_order=order_map.get(q.id, 0) + 1,
            )

    return Response(
        {
            "invite_id": invite.id,
            "token": str(invite.token),
            "allowed_languages": invite.allowed_languages,
            "time_limit_seconds": invite.time_limit_seconds,
            "status": invite.status,
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(["GET"])
@permission_classes([AllowAny])
def coding_invite_detail_view(request, token):
    invite = CodingInvite.objects.filter(token=token).first()
    if not invite:
        return Response({"error": "Invite not found"}, status=status.HTTP_404_NOT_FOUND)

    _ensure_invite_started(invite)
    auto_res = _auto_submit_if_expired(invite)
    remaining = _invite_remaining_seconds(invite)

    questions = [
        _serialize_invite_question(iq)
        for iq in invite.invite_questions.select_related("question").order_by("display_order")
    ]

    response_payload = {
        "invite_id": invite.id,
        "candidate_name": invite.candidate_name,
        "candidate_email": invite.candidate_email,
        "allowed_languages": invite.allowed_languages or [],
        "selected_language": invite.selected_language,
        "status": invite.status,
        "auto_submitted": invite.auto_submitted,
        "remaining_seconds": remaining,
        "time_limit_seconds": invite.time_limit_seconds,
        "questions": questions,
    }
    if invite.submitted_at:
        response_payload["submitted_at"] = invite.submitted_at.isoformat()
    if invite.final_results:
        response_payload["final_results"] = invite.final_results

    if auto_res:
        response_payload.update(auto_res)
    return Response(response_payload, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([AllowAny])
def coding_invite_select_language_view(request, token):
    invite = CodingInvite.objects.filter(token=token).first()
    if not invite:
        return Response({"error": "Invite not found"}, status=status.HTTP_404_NOT_FOUND)

    _ensure_invite_started(invite)
    auto_res = _auto_submit_if_expired(invite)
    if auto_res:
        return Response(auto_res, status=status.HTTP_400_BAD_REQUEST)

    data = request.data or {}
    lang = (data.get("language") or data.get("selected_language") or "").strip().lower()
    allowed = _allowed_languages_for_invite(invite, None)
    if not lang or (allowed and lang not in allowed):
        return Response({"error": "language must be one of the allowed languages"}, status=status.HTTP_400_BAD_REQUEST)

    invite.selected_language = lang
    invite.save(update_fields=["selected_language", "updated_at"])
    return Response({"ok": True, "selected_language": invite.selected_language, "remaining_seconds": _invite_remaining_seconds(invite)}, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([AllowAny])
def coding_invite_run_view(request, token):
    invite = CodingInvite.objects.filter(token=token).first()
    if not invite:
        return Response({"error": "Invite not found"}, status=status.HTTP_404_NOT_FOUND)

    _ensure_invite_started(invite)
    auto_res = _auto_submit_if_expired(invite)
    if auto_res:
        return Response(auto_res, status=status.HTTP_400_BAD_REQUEST)
    if invite.status in (CodingInvite.STATUS_SUBMITTED, CodingInvite.STATUS_EXPIRED):
        return Response({"error": "Invite already submitted or expired"}, status=status.HTTP_400_BAD_REQUEST)

    data = request.data or {}
    question_id = data.get("question_id") or data.get("qid")
    if not question_id:
        return Response({"error": "question_id is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        question_id_int = int(question_id)
    except Exception:
        return Response({"error": "question_id must be numeric"}, status=status.HTTP_400_BAD_REQUEST)

    iq = (
        invite.invite_questions.select_related("question")
        .filter(question_id=question_id_int)
        .first()
    )
    if not iq:
        return Response({"error": "Question is not part of this invite"}, status=status.HTTP_404_NOT_FOUND)

    code = data.get("code")
    if not isinstance(code, str):
        return Response({"error": "code is required"}, status=status.HTTP_400_BAD_REQUEST)

    lang = _normalize_language_for_invite(invite, data.get("language") or invite.selected_language, iq.question)
    if not invite.selected_language and lang:
        invite.selected_language = lang
        invite.save(update_fields=["selected_language", "updated_at"])

    if data.get("use_custom_input") and "stdin" in data:
        exec_lang = lang or iq.question.language
        # Map to valid executor language (e.g. python3 -> python)
        exec_lang = _map_to_valid_language(exec_lang)
        
        if exec_lang == "sql":
            safety_error = _validate_sql_safety(code)
            if safety_error:
                 return Response({"ok": False, "error": safety_error}, status=status.HTTP_200_OK)

        merged_code = _merge_code(iq.question, code, language=exec_lang)
        exec_res = _call_executor(
            language=exec_lang,
            source_code=merged_code,
            stdin=data.get("stdin") or "",
            time_limit_ms=int(iq.question.time_limit_ms or 3000),
            memory_mb=int(iq.question.memory_limit_mb or 256),
            schema_sql=iq.question.schema_sql if exec_lang == 'sql' else None,
            database_engine=iq.question.database_engine if exec_lang == 'sql' else None,
        )
        
        iq.last_code = code
        iq.last_language = exec_lang
        iq.save(update_fields=["last_code", "last_language", "updated_at"])
        return Response(exec_res, status=status.HTTP_200_OK)

    evaluation = _evaluate_question(q=iq.question, user_code=code, include_hidden=False, exec_language=lang or iq.question.language)

    iq.last_code = code
    iq.last_language = lang or iq.last_language
    iq.last_run_result = evaluation
    iq.run_count = (iq.run_count or 0) + 1
    iq.save(update_fields=["last_code", "last_language", "last_run_result", "run_count", "updated_at"])

    return Response(
        {
            "question_id": iq.question_id,
            "invite_question_id": iq.id,
            "remaining_seconds": _invite_remaining_seconds(invite),
            **evaluation,
        },
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def coding_invite_submit_view(request, token):
    invite = CodingInvite.objects.filter(token=token).first()
    if not invite:
        return Response({"error": "Invite not found"}, status=status.HTTP_404_NOT_FOUND)

    _ensure_invite_started(invite)
    auto_res = _auto_submit_if_expired(invite)
    if auto_res:
        return Response(auto_res, status=status.HTTP_400_BAD_REQUEST)
    if invite.status in (CodingInvite.STATUS_SUBMITTED, CodingInvite.STATUS_EXPIRED):
        return Response({"error": "Invite already submitted"}, status=status.HTTP_400_BAD_REQUEST)

    data = request.data or {}
    selected_language = (data.get("language") or data.get("selected_language") or invite.selected_language or "").strip().lower()

    # Build a question_id -> payload map
    code_map = {}
    solutions = data.get("solutions") or data.get("answers") or data.get("questions")
    if isinstance(solutions, list):
        for item in solutions:
            if not isinstance(item, dict):
                continue
            qid = item.get("question_id") or item.get("id") or item.get("qid")
            if qid is None:
                continue
            code_map[str(qid)] = item
    else:
        # Single submission fallback
        qid = data.get("question_id")
        if qid is not None and isinstance(data.get("code"), str):
            code_map[str(qid)] = {"code": data.get("code"), "language": selected_language}

    res = _perform_invite_submission(
        invite,
        code_map=code_map,
        auto=False,
        reason="manual_submit",
        selected_language=selected_language,
    )
    return Response(res, status=status.HTTP_200_OK)


def _evaluate_question(*, q: CodingQuestion, user_code: str, include_hidden: bool, exec_language: str | None = None) -> dict:
    language_to_use = (exec_language or q.language or "").lower()
    valid_langs = {
        CodingQuestion.LANGUAGE_PYTHON,
        CodingQuestion.LANGUAGE_JAVASCRIPT,
        CodingQuestion.LANGUAGE_JAVA,
        CodingQuestion.LANGUAGE_C,
        CodingQuestion.LANGUAGE_CPP,
        CodingQuestion.LANGUAGE_CSHARP,
        CodingQuestion.LANGUAGE_GO,
        CodingQuestion.LANGUAGE_PHP,
        CodingQuestion.LANGUAGE_RUST,
        # Extended set
        "kotlin", "swift", "ruby", "dart", "scala", "typescript", "sql"
    }
    if language_to_use not in valid_langs:
        # Try finding a valid mapping
        language_to_use = _map_to_valid_language(language_to_use)
        if language_to_use not in valid_langs:
            # Fallback to question default or Python
            language_to_use = q.language or CodingQuestion.LANGUAGE_PYTHON

    # Ensure final fallback logic mirrors original intent if mapping fails
    if language_to_use not in valid_langs:
        language_to_use = CodingQuestion.LANGUAGE_PYTHON

    # PART B: SQL SUBMISSION JUDGING - Reject forbidden keywords
    if language_to_use == "sql":
        safety_error = _validate_sql_safety(user_code)
        if safety_error:
            # Construct a failure result consistent with execution failure
            # We calculate 'total_tests' but we can't run them.
            total_tests = CodingTestCase.objects.filter(question_id=q.id).count()
             # If we are strictly "including hidden" or not depends on context, 
             # but validation fail means 0 passing regardless.
            return {
                "question_id": q.id,
                "passed_count": 0,
                "total_tests": total_tests,
                "status": "error",
                "execution_time_ms": 0,
                "results": [{
                    "status": "ERROR",
                    "message": safety_error,
                    "actual": safety_error,
                    "is_hidden": False,  # Visible error
                }]
            }

    tcs_qs = CodingTestCase.objects.filter(question_id=q.id)
    if not include_hidden:
        tcs_qs = tcs_qs.filter(is_hidden=False)
    tcs = list(tcs_qs.order_by("id")[:200])

    merged_code = _merge_code(q, user_code, language=language_to_use)
    
    # Serialize TestCases for Executor
    serialized_tcs = []
    for tc in tcs:
        serialized_tcs.append({
            "id": tc.id,
            "stdin": tc.stdin or "",
            "expected_stdout": tc.expected_stdout or "",
        })

    # Call Executor in Batch
    start_time = time.monotonic()
    exec_res = _call_executor(
        language=language_to_use,
        source_code=merged_code,
        stdin=None,
        time_limit_ms=int(q.time_limit_ms or 3000),
        memory_mb=int(q.memory_limit_mb or 256),
        testcases=serialized_tcs,
        schema_sql=q.schema_sql if language_to_use == 'sql' else None,
        database_engine=q.database_engine if language_to_use == 'sql' else None,
    )
    total_execution_time_ms = int((time.monotonic() - start_time) * 1000)

    if not exec_res.get("ok"):
        # If the batch request itself failed (e.g. timeout or compilation error in some runtimes)
        # We assume all failed or it's a critical error
        return {
            "question_id": q.id,
            "passed_count": 0,
            "total_tests": len(tcs),
            "status": "error",
            "execution_time_ms": total_execution_time_ms,
            "results": [{
                "status": "ERROR",
                "message": exec_res.get("error"),
                "actual": exec_res.get("error"),
            }]
        }

    # Process Results from Executor
    raw_results = exec_res.get("results") or []
    # Map back to full result structure (merge with DB info)
    final_results = []
    passed = exec_res.get("passed_count", 0)
    
    # Create a lookup for raw results by testcase_id
    res_map = {r.get("testcase_id"): r for r in raw_results}

    for tc in tcs:
        r = res_map.get(tc.id)
        if r:
            final_results.append({
                "testcase_id": tc.id,
                "status": r.get("status", "FAIL"),
                "stdin": tc.stdin,
                "expected_stdout": tc.expected_stdout,
                "stdout": r.get("stdout"),
                "stderr": r.get("stderr"),
                "exit_code": r.get("exit_code"),
                "timed_out": r.get("timed_out"),
                "elapsed_ms": r.get("execution_time_ms"),
                "is_hidden": bool(tc.is_hidden),
                "message": r.get("message"),
            })
        else:
            # Should not happen if executor works correctly, but safe fallback
            final_results.append({
                "testcase_id": tc.id,
                "status": "ERROR",
                "message": "Executor did not return result for this testcase",
                "is_hidden": bool(tc.is_hidden),
                "stdout": "",
                "stderr": "",
            })

    status_overall = "passed" if tcs and passed == len(tcs) else "failed"
    if any(r.get("status") == "TIMEOUT" for r in final_results):
        status_overall = "timeout"
    # Prioritize error status if any test errored (compilation etc)
    if any(r.get("status") == "ERROR" for r in final_results):
        status_overall = "error"

    return {
        "question_id": q.id,
        "passed_count": passed,
        "total_tests": len(tcs),
        "status": status_overall,
        "execution_time_ms": total_execution_time_ms,
        "results": final_results,
    }


@api_view(["POST"])
@permission_classes([AllowAny])
def coding_run_view(request, question_id: int):
    q, error_response = _get_coding_question_or_error(request, question_id)
    if error_response:
        return error_response

    data = request.data or {}
    code = data.get("code")
    if not isinstance(code, str):
        return Response({"error": "code is required"}, status=status.HTTP_400_BAD_REQUEST)
    requested_lang = (data.get("language") or q.language).lower()
    allowed_langs = set([l.lower() for l in (q.languages or [])] + [q.language.lower()])
    exec_lang = requested_lang if requested_lang in allowed_langs else q.language

    # If caller provides stdin + use_custom_input, run only one execution (no comparison)
    if data.get("use_custom_input") and "stdin" in data:
        if exec_lang == "sql":
            safety_error = _validate_sql_safety(code)
            if safety_error:
                 return Response({"ok": False, "error": safety_error}, status=status.HTTP_200_OK)

        merged_code = _merge_code(q, code, language=exec_lang)
        exec_res = _call_executor(
            language=exec_lang,
            source_code=merged_code,
            stdin=data.get("stdin") or "",
            time_limit_ms=int(q.time_limit_ms or 3000),
            memory_mb=int(q.memory_limit_mb or 256),
            schema_sql=q.schema_sql if exec_lang == 'sql' else None,
            database_engine=q.database_engine if exec_lang == 'sql' else None,
        )
        return Response(exec_res, status=status.HTTP_200_OK)

    evaluation = _evaluate_question(q=q, user_code=code, include_hidden=False, exec_language=exec_lang)
    return Response(evaluation, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([AllowAny])
def coding_submit_view(request, question_id: int):
    q, error_response = _get_coding_question_or_error(request, question_id)
    if error_response:
        return error_response

    data = request.data or {}
    code = data.get("code")
    if not isinstance(code, str):
        return Response({"error": "code is required"}, status=status.HTTP_400_BAD_REQUEST)
    requested_lang = (data.get("language") or q.language).lower()
    allowed_langs = set([l.lower() for l in (q.languages or [])] + [q.language.lower()])
    exec_lang = requested_lang if requested_lang in allowed_langs else q.language

    evaluation = _evaluate_question(q=q, user_code=code, include_hidden=True, exec_language=exec_lang)

    if data.get("skip_save") is True:
        return Response(evaluation, status=status.HTTP_200_OK)  

    sub = CodingSubmission.objects.create(
        question_id=q.id,
        user_email=data.get("user_email"),
        candidate_name=data.get("candidate_name"),
        language=exec_lang,
        mode=q.mode,
        submitted_code=code,
        passed_count=evaluation["passed_count"],
        total_tests=evaluation["total_tests"],
        status=evaluation["status"],
        execution_time_ms=evaluation["execution_time_ms"],
        results={"tests": evaluation["results"]},
    )

    return Response({"submission_id": sub.id, **evaluation}, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([AllowAny])
def coding_submissions_view(request, question_id: int):
    q, error_response = _get_coding_question_or_error(request, question_id)
    if error_response:
        return error_response

    qs = CodingSubmission.objects.filter(question_id=question_id).order_by("-created_at")[:200]
    results = []
    for s in qs:
        results.append(
            {
                "id": s.id,
                "question_id": s.question_id,
                "user_email": s.user_email,
                "candidate_name": s.candidate_name,
                "language": s.language,
                "mode": s.mode,
                "passed_count": s.passed_count,
                "total_tests": s.total_tests,
                "status": s.status,
                "execution_time_ms": s.execution_time_ms,
                "created_at": s.created_at.isoformat() if s.created_at else None,
            }
        )
    return Response({"count": len(results), "results": results}, status=status.HTTP_200_OK)


