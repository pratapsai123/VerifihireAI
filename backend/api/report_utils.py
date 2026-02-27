"""
Utility to generate a comprehensive PDF report for a candidate submission.
Sections: Personal Info (with passport-size snapshot at top-right),
PAN Card, Exam Answers (with test case stdout), Results, Feedback.
Max 20 pages.
"""

import io
import base64
import os
import traceback
import requests

from PIL import Image as PILImage

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    Image, PageBreak, HRFlowable, Preformatted,
)
from reportlab.lib.utils import ImageReader

from django.http import HttpResponse

from .models import (
    CandidateSubmission, CandidateInvitation, CandidateDetails,
    AssessmentQuestion, AssessmentCodingQuestion, CodingTestCase,
)

MAX_PAGES = 20
EXECUTOR_BASE_URL = os.environ.get("EXECUTOR_BASE_URL", "http://localhost:4000").rstrip("/")


# ─── Styles ──────────────────────────────────────────────────────────────────

def _build_styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        'ReportTitle', parent=styles['Title'],
        fontSize=22, textColor=colors.HexColor('#1e293b'), spaceAfter=6,
    ))
    styles.add(ParagraphStyle(
        'SectionHeader', parent=styles['Heading2'],
        fontSize=14, textColor=colors.HexColor('#0f172a'),
        spaceBefore=18, spaceAfter=8, borderWidth=0,
    ))
    styles.add(ParagraphStyle(
        'InfoLabel', parent=styles['Normal'],
        fontSize=10, textColor=colors.HexColor('#64748b'),
    ))
    styles.add(ParagraphStyle(
        'InfoValue', parent=styles['Normal'],
        fontSize=11, textColor=colors.HexColor('#1e293b'), fontName='Helvetica-Bold',
    ))
    styles.add(ParagraphStyle(
        'CodeBlock', parent=styles['Code'],
        fontSize=8, leading=10, textColor=colors.HexColor('#1e293b'),
        backColor=colors.HexColor('#f1f5f9'),
        borderWidth=1, borderColor=colors.HexColor('#e2e8f0'), borderPadding=6,
    ))
    styles.add(ParagraphStyle(
        'QualifiedBadge', parent=styles['Normal'],
        fontSize=12, fontName='Helvetica-Bold', textColor=colors.HexColor('#16a34a'),
    ))
    styles.add(ParagraphStyle(
        'NotQualifiedBadge', parent=styles['Normal'],
        fontSize=12, fontName='Helvetica-Bold', textColor=colors.HexColor('#dc2626'),
    ))
    return styles


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _info_row(label, value, styles):
    return [
        Paragraph(label, styles['InfoLabel']),
        Paragraph(str(value) if value else '-', styles['InfoValue']),
    ]


def _safe(text):
    if text is None:
        return '-'
    return str(text).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def _safe_para(text, style):
    return Paragraph(_safe(text), style)


def _is_file_path(s):
    """Safely check if a string is a valid file path (not base64)."""
    if not isinstance(s, str) or len(s) > 500:
        return False  # base64 strings are much longer than file paths
    try:
        return os.path.isfile(s)
    except (OSError, ValueError):
        return False


def _convert_image_to_png_bytesio(source):
    """
    Convert an image source (base64 string OR file path) to a BytesIO
    containing PNG data.  Returns None on failure.
    """
    pil_img = None

    if _is_file_path(source):
        # File path
        try:
            pil_img = PILImage.open(source)
            print(f"[report] Opened image file: {source}")
        except Exception as e:
            print(f"[report] Cannot open image file {source}: {e}")
            return None
    elif isinstance(source, str) and len(source) > 50:
        # base64 string (data URI or raw)
        s = source.strip()
        if ',' in s and s.startswith('data:'):
            s = s.split(',', 1)[1]
        s = s.replace('\n', '').replace('\r', '').replace(' ', '')
        padding = 4 - len(s) % 4
        if padding != 4:
            s += '=' * padding
        try:
            raw = base64.b64decode(s)
            print(f"[report] base64 decoded: {len(raw)} bytes")
        except Exception as e:
            print(f"[report] base64 decode failed: {e}")
            return None
        try:
            pil_img = PILImage.open(io.BytesIO(raw))
            print(f"[report] PIL opened: mode={pil_img.mode}, size={pil_img.size}, format={pil_img.format}")
        except Exception as e:
            print(f"[report] PIL open failed: {e}")
            return None
    else:
        print(f"[report] Invalid image source: type={type(source)}, len={len(source) if isinstance(source, str) else 'N/A'}")
        return None

    try:
        if pil_img.mode not in ('RGB', 'L'):
            pil_img = pil_img.convert('RGB')
        buf = io.BytesIO()
        pil_img.save(buf, format='PNG')
        buf.seek(0)
        print(f"[report] PNG conversion OK: {buf.getbuffer().nbytes} bytes")
        return buf
    except Exception as e:
        print(f"[report] PNG conversion failed: {e}")
        traceback.print_exc()
        return None


def _make_rl_image(source, width, height):
    """
    Turn an image source (base64 or path) into a ReportLab Image flowable.
    """
    png_buf = _convert_image_to_png_bytesio(source)
    if png_buf is None:
        return None
    try:
        img = Image(png_buf, width=width, height=height)
        img.hAlign = 'LEFT'
        return img
    except Exception as e:
        print(f"[report] ReportLab Image creation failed: {e}")
        return None


def _kv_table(rows, styles):
    tbl = Table(rows, colWidths=[120, 380])
    tbl.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LINEBELOW', (0, 0), (-1, -2), 0.5, colors.HexColor('#f1f5f9')),
    ]))
    return tbl


def _run_code_against_testcases(code, language, testcases, schema_sql=None, database_engine=None):
    """
    Re-execute submitted code against test cases via the executor service.
    Returns a list of dicts: [{stdin, expected, stdout, passed}, ...]
    """
    if not code or not testcases:
        return []

    tc_payload = []
    for tc in testcases:
        tc_payload.append({
            "id": tc.id,
            "stdin": tc.stdin or "",
            "expected_stdout": tc.expected_stdout or "",
        })

    payload = {
        "language": language,
        "source_code": code,
        "stdin": "",
        "time_limit_ms": 5000,
        "memory_mb": 256,
        "testcases": tc_payload,
        "schema_sql": schema_sql,
        "database_engine": database_engine,
    }

    try:
        print(f"[report] Calling executor at {EXECUTOR_BASE_URL}/execute for lang={language} with {len(tc_payload)} testcases")
        resp = requests.post(
            f"{EXECUTOR_BASE_URL}/execute",
            json=payload,
            timeout=30,
        )
        print(f"[report] Executor response status: {resp.status_code}")
        if resp.status_code < 400:
            data = resp.json()
            results = data.get("results", [])
            print(f"[report] Executor results count: {len(results)}")
            if results:
                print(f"[report] First result sample: {str(results[0])[:200]}")
            if data.get("ok"):
                return results
            else:
                print(f"[report] Executor returned ok=False: {data.get('error')}")
        else:
             print(f"[report] Executor failed: {resp.text}")
    except Exception as e:
        print(f"[report] Executor call failed: {e}")
        traceback.print_exc()

    return []


class PageCounter:
    def __init__(self):
        self.page_count = 0

    def on_page(self, canvas, doc):
        self.page_count += 1


# ─── Main ────────────────────────────────────────────────────────────────────

def generate_candidate_report(submission_id):
    """
    Generate a comprehensive PDF report for a candidate submission.
    Returns a Django HttpResponse with the PDF, or None if not found.
    """
    try:
        submission = CandidateSubmission.objects.select_related(
            'invitation', 'invitation__assessment'
        ).get(id=submission_id)
    except CandidateSubmission.DoesNotExist:
        return None

    inv = submission.invitation
    assessment = inv.assessment

    # Find candidate details - try token first, then email
    candidate_detail = None
    try:
        candidate_detail = CandidateDetails.objects.filter(token=inv.token).first()
        if not candidate_detail:
            candidate_detail = CandidateDetails.objects.filter(email=inv.email).first()
    except Exception as e:
        print(f"[report] Error fetching CandidateDetails: {e}")

    if candidate_detail:
        full_name = f"{candidate_detail.first_name} {candidate_detail.last_name}"
        email = candidate_detail.email
        phone = candidate_detail.phone
        pan_number = candidate_detail.pan_number
    else:
        full_name = inv.name or '-'
        email = inv.email or '-'
        phone = inv.phone or '-'
        pan_number = '-'

    print(f"[report] Generating report for submission {submission_id}, "
          f"candidate_detail={'found (id=' + str(candidate_detail.id) + ')' if candidate_detail else 'NOT FOUND'}")

    # ── Build PDF ──
    buffer = io.BytesIO()
    page_counter = PageCounter()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40,
    )

    styles = _build_styles()
    story = []

    # ════════════════════════════════════════════════════════════════════════
    # HEADER: Title + Passport-size Photo (top-right)
    # ════════════════════════════════════════════════════════════════════════
    PASSPORT_W = 1.2 * inch
    PASSPORT_H = 1.5 * inch
    snap_img = None
    if candidate_detail and candidate_detail.snapshot:
        print(f"[report] Snapshot data length: {len(candidate_detail.snapshot)}")
        snap_img = _make_rl_image(candidate_detail.snapshot, PASSPORT_W, PASSPORT_H)
        if snap_img:
            print("[report] Snapshot image created successfully")
        else:
            print("[report] Snapshot image creation FAILED")

    title_para = Paragraph('Candidate Report', styles['ReportTitle'])
    subtitle_para = Paragraph(
        _safe(assessment.display_name or assessment.name or 'Assessment'),
        styles['Normal'],
    )

    if snap_img:
        # Simple single-row layout: [title + subtitle | photo]
        left_content = Paragraph(
            'Candidate Report<br/><font size="11">' +
            _safe(assessment.display_name or assessment.name or 'Assessment') +
            '</font>',
            styles['ReportTitle'],
        )

        header_table = Table(
            [[left_content, snap_img]],
            colWidths=[doc.width - PASSPORT_W - 20, PASSPORT_W + 10],
            rowHeights=[PASSPORT_H + 8],
        )
        header_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (0, 0), 'MIDDLE'),
            ('VALIGN', (1, 0), (1, 0), 'TOP'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ('BOX', (1, 0), (1, 0), 1, colors.HexColor('#cbd5e1')),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ('LEFTPADDING', (0, 0), (0, 0), 0),
            ('RIGHTPADDING', (1, 0), (1, 0), 0),
        ]))
        story.append(header_table)
        print("[report] Header table with snapshot added to story")
    else:
        story.append(title_para)
        story.append(subtitle_para)
        print("[report] Header WITHOUT snapshot added to story")

    story.append(Spacer(1, 12))
    story.append(HRFlowable(width='100%', thickness=1, color=colors.HexColor('#e2e8f0'), spaceAfter=12))

    # ════════════════════════════════════════════════════════════════════════
    # 1. PERSONAL INFORMATION
    # ════════════════════════════════════════════════════════════════════════
    story.append(Paragraph('Personal Information', styles['SectionHeader']))
    info_data = [
        _info_row('Full Name', full_name, styles),
        _info_row('Email', email, styles),
        _info_row('Phone', phone, styles),
        _info_row('PAN Number', pan_number, styles),
        _info_row('Assessment', assessment.display_name or assessment.name, styles),
        _info_row(
            'Submitted At',
            submission.submitted_at.strftime('%d %b %Y, %I:%M %p') if submission.submitted_at else '-',
            styles,
        ),
    ]
    story.append(_kv_table(info_data, styles))
    story.append(Spacer(1, 12))

    # ════════════════════════════════════════════════════════════════════════
    # 2. PAN CARD
    # ════════════════════════════════════════════════════════════════════════
    story.append(Paragraph('PAN Card', styles['SectionHeader']))
    pan_added = False
    if candidate_detail and candidate_detail.pan_file:
        try:
            pan_path = candidate_detail.pan_file.path
            print(f"[report] PAN file path: {pan_path}, exists: {os.path.exists(pan_path)}")
            if os.path.exists(pan_path):
                pan_img = _make_rl_image(pan_path, 4 * inch, 2.5 * inch)
                if pan_img:
                    story.append(pan_img)
                    pan_added = True
                    print("[report] PAN image added successfully")
                else:
                    print("[report] PAN image creation failed")
        except Exception as e:
            print(f"[report] PAN image error: {e}")
            traceback.print_exc()

    if not pan_added:
        story.append(Paragraph('PAN card image not available.', styles['Normal']))
    story.append(Spacer(1, 12))

    # ════════════════════════════════════════════════════════════════════════
    # 3. EXAM ANSWERS
    # ════════════════════════════════════════════════════════════════════════
    answers = submission.answers or {}
    objective_keys = [k for k in answers.keys() if not k.startswith('acq_')]
    coding_keys = [k for k in answers.keys() if k.startswith('acq_')]

    # ── 3a. Objective Exam ──
    if objective_keys:
        count = len(objective_keys)
        story.append(Paragraph(f'Objective Exam Answers ({count} Questions)', styles['SectionHeader']))

        aq_map = {}
        try:
            aqs = AssessmentQuestion.objects.filter(
                assessment=assessment
            ).select_related('question').order_by('order')
            for aq in aqs:
                aq_map[str(aq.id)] = aq
        except Exception:
            pass

        obj_data = [[
            Paragraph('<b>Q#</b>', styles['Normal']),
            Paragraph('<b>Question</b>', styles['Normal']),
            Paragraph('<b>Your Answer</b>', styles['Normal']),
            Paragraph('<b>Correct</b>', styles['Normal']),
            Paragraph('<b>Result</b>', styles['Normal']),
        ]]

        # Add mapping extraction
        option_map = inv.option_map or {}

        for idx, key in enumerate(objective_keys, 1):
            candidate_answer = answers[key]
            aq = aq_map.get(key)
            
            # Map submitted labels back to original labels if options were shuffled
            mapping = option_map.get(key, None)

            def _norm_choice(v):
                if v is None:
                    return ''
                return str(v).strip().upper()
                
            def _get_option_text(q_obj, choice_label):
                if not choice_label or not q_obj:
                    return choice_label
                cl = choice_label.strip().upper()
                if cl == 'A' and getattr(q_obj, 'option_a', None):
                    return f"A: {q_obj.option_a}"
                if cl == 'B' and getattr(q_obj, 'option_b', None):
                    return f"B: {q_obj.option_b}"
                if cl == 'C' and getattr(q_obj, 'option_c', None):
                    return f"C: {q_obj.option_c}"
                if cl == 'D' and getattr(q_obj, 'option_d', None):
                    return f"D: {q_obj.option_d}"
                return choice_label

            if aq:
                q_text = aq.question.question if aq.question else 'N/A'
                q_type = (aq.question_type or '').strip().upper()
                if q_type == 'MSQ':
                    correct_raw = sorted(aq.correct_answers or [])
                    correct_formatted = [_get_option_text(aq.question, c) for c in correct_raw]
                    correct = ', '.join(correct_formatted)
                    
                    submitted_list = candidate_answer if isinstance(candidate_answer, list) else []
                    raw = [_norm_choice(x) for x in submitted_list if _norm_choice(x)]
                    if mapping and isinstance(mapping, dict):
                        raw = [mapping.get(x, x) for x in raw]  # newLabel -> origLabel
                    
                    raw_sorted = sorted(raw)
                    ans_formatted = [_get_option_text(aq.question, c) for c in raw_sorted]
                    ans_display = ', '.join(ans_formatted) if ans_formatted else str(candidate_answer)
                    
                    sub_set = raw_sorted
                    cor_set = sorted([_norm_choice(x) for x in (aq.correct_answers or [])])
                    is_correct = sub_set == cor_set and len(sub_set) > 0
                else:
                    correct_raw = aq.correct_answer or '-'
                    correct = _get_option_text(aq.question, correct_raw) if correct_raw != '-' else '-'
                    
                    submitted_choice = _norm_choice(candidate_answer)
                    if mapping and isinstance(mapping, dict):
                        submitted_choice = mapping.get(submitted_choice, submitted_choice)
                        
                    ans_display = _get_option_text(aq.question, submitted_choice) if submitted_choice else '-'
                    is_correct = submitted_choice == _norm_choice(aq.correct_answer) and len(submitted_choice) > 0
            else:
                q_text = f'Question {key}'
                correct = '-'
                ans_display = str(candidate_answer) if candidate_answer else '-'
                is_correct = False

            icon = '\u2713' if is_correct else '\u2717'
            clr = colors.HexColor('#16a34a') if is_correct else colors.HexColor('#dc2626')

            obj_data.append([
                Paragraph(str(idx), styles['Normal']),
                _safe_para(q_text[:120] + ('...' if len(str(q_text)) > 120 else ''), styles['Normal']),
                _safe_para(ans_display, styles['Normal']),
                _safe_para(correct, styles['Normal']),
                Paragraph(f'<font color="{clr}">{icon}</font>', styles['Normal']),
            ])

        obj_table = Table(obj_data, colWidths=[30, 220, 80, 80, 40])
        obj_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f1f5f9')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#0f172a')),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#fafafa')]),
        ]))
        story.append(obj_table)
        story.append(Spacer(1, 12))

    # ── 3b. Coding Exam ──
    if coding_keys:
        story.append(PageBreak())
        count = len(coding_keys)
        story.append(Paragraph(f'Coding Exam Answers ({count} Questions)', styles['SectionHeader']))

        # Build ACQ map for titles and coding_question reference
        acq_map = {}
        try:
            acq_ids = []
            for k in coding_keys:
                cdata = answers[k]
                if isinstance(cdata, dict) and cdata.get('acq_id'):
                    acq_ids.append(int(cdata['acq_id']))
            if acq_ids:
                for acq in AssessmentCodingQuestion.objects.filter(
                    id__in=acq_ids
                ).select_related('coding_question'):
                    acq_map[acq.id] = acq
        except Exception as e:
            print(f"[report] Error fetching ACQs: {e}")

        # Pre-fetch test cases for all coding questions
        testcase_map = {}
        try:
            q_ids = []
            for k in coding_keys:
                cdata = answers[k]
                if isinstance(cdata, dict) and cdata.get('question_id'):
                    q_ids.append(int(cdata['question_id']))
            if q_ids:
                for tc in CodingTestCase.objects.filter(question_id__in=q_ids).order_by('id'):
                    testcase_map.setdefault(tc.question_id, []).append(tc)
        except Exception as e:
            print(f"[report] Error fetching test cases: {e}")

        for idx, key in enumerate(coding_keys, 1):
            cdata = answers[key]
            if not isinstance(cdata, dict):
                continue

            acq_id = cdata.get('acq_id')
            acq = acq_map.get(acq_id)
            title = acq.title if acq and acq.title else f'Coding Question {idx}'
            language = cdata.get('language', 'N/A')
            passed = cdata.get('passed_count', 0)
            total_tests = cdata.get('total_tests', 0)
            submitted_code = cdata.get('submitted_code', '')
            question_id = cdata.get('question_id')

            # Question header
            story.append(Paragraph(
                f'<b>{idx}. {_safe(title)}</b>  |  Language: {_safe(language)}  |  Tests Passed: {passed}/{total_tests}',
                styles['Normal'],
            ))
            story.append(Spacer(1, 4))

            # Code block
            if submitted_code:
                code_display = submitted_code[:3000]
                if len(submitted_code) > 3000:
                    code_display += '\n\n... (code truncated) ...'
                story.append(Preformatted(code_display, styles['CodeBlock']))
            else:
                story.append(Paragraph('<i>No code submitted</i>', styles['Normal']))

            story.append(Spacer(1, 8))

            # Re-execute code against test cases to get actual stdout
            tcs = testcase_map.get(question_id, [])
            if tcs and submitted_code:
                # Merge code using ACQ helper if available
                exec_code = submitted_code
                if acq and acq.coding_question:
                    try:
                        from .views import _acq_merge_code
                        exec_code = _acq_merge_code(acq, submitted_code)
                    except Exception:
                        pass

                # Prepare SQL capabilities if needed
                schema_sql = None
                database_engine = None
                
                # Check for SQL and fetch schema
                is_sql = str(language).strip().lower() == 'sql'
                if is_sql and acq and acq.coding_question:
                     schema_sql = acq.coding_question.schema_sql
                     database_engine = acq.coding_question.database_engine

                exec_results = _run_code_against_testcases(
                    exec_code, language, tcs, 
                    schema_sql=schema_sql, database_engine=database_engine
                )

                if is_sql:
                    # ── SQL formatted layout (Vertical) ──
                    story.append(Paragraph('<b>Test Case Results (SQL):</b>', styles['Normal']))
                    story.append(Spacer(1, 6))

                    for t_idx, tc in enumerate(tcs, 1):
                        stdin_str = str(tc.stdin or '-')
                        expected_str = str(tc.expected_stdout or '-')

                        # Find matching execution result
                        actual_str = '-'
                        status_str = '-'
                        if exec_results and t_idx <= len(exec_results):
                            r = exec_results[t_idx - 1]
                            actual_str = str(r.get('stdout', r.get('output', '-')) or '-')
                            p = r.get('passed', r.get('status', None))
                            if isinstance(p, bool):
                                status_str = 'Passed' if p else 'Failed'
                            elif str(p).lower() in ('true', 'pass', 'passed', 'accepted'):
                                status_str = 'Passed'
                            else:
                                status_str = 'Failed'

                        status_clr = colors.HexColor('#16a34a') if status_str == 'Passed' else colors.HexColor('#dc2626')

                        # 1. Test Case Header
                        story.append(Paragraph(f'<b>Test Case {t_idx}</b>', styles['Normal']))
                        story.append(Spacer(1, 4))

                        # 2. Expected Output
                        story.append(Paragraph('<b>Expected Output:</b>', styles['InfoLabel']))
                        if len(expected_str) > 2000:
                            expected_str = expected_str[:2000] + '\n... (truncated)'
                        story.append(Preformatted(expected_str, styles['CodeBlock']))
                        story.append(Spacer(1, 6))

                        # 3. Actual Output
                        story.append(Paragraph('<b>Actual Output:</b>', styles['InfoLabel']))
                        print(f"[report] Test {t_idx} actual output len: {len(actual_str)}")
                        if len(actual_str) > 2000:
                            actual_str = actual_str[:2000] + '\n... (truncated)'
                        story.append(Preformatted(actual_str, styles['CodeBlock']))
                        story.append(Spacer(1, 6))

                        # 4. Status
                        story.append(Paragraph(f'<b>Status:</b> <font color="{status_clr}">{status_str}</font>', styles['Normal']))
                        
                        story.append(Spacer(1, 12))
                        story.append(HRFlowable(width='100%', thickness=0.5, color=colors.HexColor('#e2e8f0'), spaceAfter=12))

                else:
                    # ── Standard table layout for other languages ──
                    story.append(Paragraph('<b>Test Case Results:</b>', styles['Normal']))
                    story.append(Spacer(1, 4))

                    test_header = [
                        Paragraph('<b>Test#</b>', styles['Normal']),
                        Paragraph('<b>Input</b>', styles['Normal']),
                        Paragraph('<b>Expected Output</b>', styles['Normal']),
                        Paragraph('<b>Actual Output</b>', styles['Normal']),
                        Paragraph('<b>Status</b>', styles['Normal']),
                    ]
                    test_data = [test_header]

                    for t_idx, tc in enumerate(tcs, 1):
                        stdin_str = str(tc.stdin or '-')[:150]
                        expected_str = str(tc.expected_stdout or '-')[:150]

                        # Find matching execution result
                        actual_str = '-'
                        status_str = '-'
                        if exec_results and t_idx <= len(exec_results):
                            r = exec_results[t_idx - 1]
                            actual_str = str(r.get('stdout', r.get('output', '-')) or '-')[:150]
                            p = r.get('passed', r.get('status', None))
                            if isinstance(p, bool):
                                status_str = 'Passed' if p else 'Failed'
                            elif str(p).lower() in ('true', 'pass', 'passed', 'accepted'):
                                status_str = 'Passed'
                            else:
                                status_str = 'Failed'

                        status_clr = colors.HexColor('#16a34a') if status_str == 'Passed' else colors.HexColor('#dc2626')

                        test_data.append([
                            Paragraph(str(t_idx), styles['Normal']),
                            _safe_para(stdin_str, styles['Normal']),
                            _safe_para(expected_str, styles['Normal']),
                            _safe_para(actual_str, styles['Normal']),
                            Paragraph(f'<font color="{status_clr}">{_safe(status_str)}</font>', styles['Normal']),
                        ])

                    test_table = Table(test_data, colWidths=[35, 115, 130, 130, 50])
                    test_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f1f5f9')),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, -1), 8),
                        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
                        ('TOPPADDING', (0, 0), (-1, -1), 3),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
                        ('LEFTPADDING', (0, 0), (-1, -1), 4),
                        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
                    ]))
                    story.append(test_table)



            elif tcs:
                # No code but test cases exist, just show expected
                story.append(Paragraph('<b>Test Cases (Expected):</b>', styles['Normal']))
                story.append(Spacer(1, 4))
                test_header = [
                    Paragraph('<b>Test#</b>', styles['Normal']),
                    Paragraph('<b>Input</b>', styles['Normal']),
                    Paragraph('<b>Expected Output</b>', styles['Normal']),
                ]
                test_data = [test_header]
                for t_idx, tc in enumerate(tcs, 1):
                    test_data.append([
                        Paragraph(str(t_idx), styles['Normal']),
                        _safe_para(str(tc.stdin or '-')[:200], styles['Normal']),
                        _safe_para(str(tc.expected_stdout or '-')[:200], styles['Normal']),
                    ])
                test_table = Table(test_data, colWidths=[40, 220, 240])
                test_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f1f5f9')),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 8),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
                    ('TOPPADDING', (0, 0), (-1, -1), 3),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
                    ('LEFTPADDING', (0, 0), (-1, -1), 4),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 4),
                ]))
                story.append(test_table)

            story.append(Spacer(1, 12))
            story.append(HRFlowable(width='100%', thickness=0.5, color=colors.HexColor('#e2e8f0'), spaceAfter=8))

    # ════════════════════════════════════════════════════════════════════════
    # 4. RESULTS SUMMARY
    # ════════════════════════════════════════════════════════════════════════
    story.append(Paragraph('Results Summary', styles['SectionHeader']))

    status_style = styles['QualifiedBadge'] if submission.is_qualified else styles['NotQualifiedBadge']
    status_text = 'Qualified' if submission.is_qualified else 'Not Qualified'

    pct = submission.final_percentage if submission.final_percentage is not None else submission.percentage
    
    # Custom score display: show split scores if both are available
    if submission.objective_total > 0 and submission.coding_total > 0:
        score_display = f"Objective: {submission.objective_score}/{submission.objective_total}, Coding: {submission.coding_score}/{submission.coding_total}"
    elif submission.objective_total > 0:
        score_display = f"{submission.objective_score} / {submission.objective_total}"
    elif submission.coding_total > 0:
        score_display = f"{submission.coding_score} / {submission.coding_total}"
    else:
        score_display = f"{submission.score} / {submission.total}"

    results_data = [
        _info_row('Score', score_display, styles),
        _info_row('Percentage', f"{pct:.1f}%", styles),
        [Paragraph('Status', styles['InfoLabel']), Paragraph(status_text, status_style)],
        _info_row('Result', submission.result or '-', styles),
    ]
    story.append(_kv_table(results_data, styles))
    story.append(Spacer(1, 12))

    # ════════════════════════════════════════════════════════════════════════
    # 5. CANDIDATE FEEDBACK
    # ════════════════════════════════════════════════════════════════════════
    rating = submission.rating
    feedback = submission.feedback
    if rating or feedback:
        story.append(Paragraph('Candidate Feedback', styles['SectionHeader']))
        fb_data = []
        if rating is not None:
            stars = '\u2605' * rating + '\u2606' * (5 - rating)
            fb_data.append(_info_row('Rating', f"{stars}  ({rating}/5)", styles))
        if feedback:
            fb_data.append([
                Paragraph('Feedback', styles['InfoLabel']),
                _safe_para(feedback, styles['InfoValue']),
            ])
        story.append(_kv_table(fb_data, styles))
        story.append(Spacer(1, 12))

    # ── Build PDF with page limit ──
    doc.build(story, onFirstPage=page_counter.on_page, onLaterPages=page_counter.on_page)
    buffer.seek(0)

    if page_counter.page_count > MAX_PAGES:
        buffer2 = io.BytesIO()
        doc2 = SimpleDocTemplate(
            buffer2, pagesize=A4,
            rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40,
        )
        story.append(Paragraph(
            f'<i>Note: Report truncated to {MAX_PAGES} pages.</i>',
            styles['Normal'],
        ))
        doc2.build(story, onFirstPage=PageCounter().on_page, onLaterPages=PageCounter().on_page)
        buffer2.seek(0)
        pdf_data = buffer2.getvalue()
    else:
        pdf_data = buffer.getvalue()

    safe_name = (full_name or 'candidate').replace(' ', '_')
    filename = f"Report_{safe_name}.pdf"

    response = HttpResponse(pdf_data, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response
