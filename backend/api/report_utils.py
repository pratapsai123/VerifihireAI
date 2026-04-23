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
import difflib
import re
from datetime import datetime

from PIL import Image as PILImage

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    Image, PageBreak, HRFlowable, Preformatted, XPreformatted
)
from reportlab.lib.utils import ImageReader

from pygments import lex
from pygments.lexers import get_lexer_by_name
from pygments.styles import get_style_by_name
import xml.sax.saxutils as saxutils

from django.http import HttpResponse
from django.utils import timezone

from .models import (
    CandidateSubmission, CandidateInvitation, CandidateDetails,
    AssessmentQuestion, AssessmentCodingQuestion, CodingTestCase,
    CandidateIntegrity, IntegrityScreenshot, KeystrokeLog, BehaviorLog,
    CodingSubmission
)
from .ocr_utils import pdf_page_to_png_bytes

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
        'CodeBlockDark', parent=styles['Code'],
        fontSize=8, leading=10, textColor=colors.HexColor('#f8f8f2'),
        backColor=colors.HexColor('#272822'),
        borderWidth=1, borderColor=colors.HexColor('#000000'), borderPadding=6,
    ))
    styles.add(ParagraphStyle(
        'QualifiedBadge', parent=styles['Normal'],
        fontSize=12, fontName='Helvetica-Bold', textColor=colors.HexColor('#16a34a'),
    ))
    styles.add(ParagraphStyle(
        'NotQualifiedBadge', parent=styles['Normal'],
        fontSize=12, fontName='Helvetica-Bold', textColor=colors.HexColor('#dc2626'),
    ))
    styles.add(ParagraphStyle(
        'WarningBadge', parent=styles['Normal'],
        fontSize=12, fontName='Helvetica-Bold', textColor=colors.HexColor('#eab308'),
    ))
    return styles


# ─── Helpers ─────────────────────────────────────────────────────────────────

def highlight_for_reportlab(code, language, style_name='monokai'):
    try:
        lexer = get_lexer_by_name(language, stripall=True)
    except Exception:
        lexer = get_lexer_by_name('text', stripall=True)
        
    try:
        style = get_style_by_name(style_name)
    except Exception:
        style = get_style_by_name('monokai')
    
    html_parts = []
    for token_type, value in lex(code, lexer):
        escaped_value = saxutils.escape(value)
        token_style = style.style_for_token(token_type)
        color = token_style.get('color')
        
        part = escaped_value
        if token_style.get('bold'):
            part = f'<b>{part}</b>'
        if token_style.get('italic'):
            part = f'<i>{part}</i>'
        if color:
            part = f'<font color="#{color}">{part}</font>'

        html_parts.append(part)
            
    return ''.join(html_parts)

def _info_row(label, value, styles):
    return [
        Paragraph(label, styles['InfoLabel']),
        Paragraph(str(value) if value else '-', styles['InfoValue']),
    ]


def _parse_timestamp(ts):
    if not ts or not isinstance(ts, str):
        return None
    try:
        if ts.endswith('Z'):
            ts = ts[:-1] + '+00:00'
        return datetime.fromisoformat(ts)
    except Exception:
        return None


def _is_typing_key(key):
    if not isinstance(key, str):
        return False
    return len(key) == 1 and key.isprintable()


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
            if source.lower().endswith('.pdf'):
                # PDF file path - convert first page to PNG
                print(f"[report] Detected PDF file: {source}")
                with open(source, 'rb') as f:
                    pdf_content = f.read()
                png_bytes = pdf_page_to_png_bytes(pdf_content, page_num=0)
                if png_bytes:
                    pil_img = PILImage.open(io.BytesIO(png_bytes))
                    print(f"[report] PDF page 1 converted to PIL image")
                else:
                    print(f"[report] PDF conversion failed for {source}")
                    return None
            else:
                pil_img = PILImage.open(source)
                print(f"[report] Opened image file: {source}")
        except Exception as e:
            print(f"[report] Cannot open file {source}: {e}")
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
            timeout=120,
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
    except requests.exceptions.Timeout:
        print(f"[report] Executor call TIMED OUT after 120s")
    except Exception as e:
        print(f"[report] Executor call failed: {e}")
        # traceback.print_exc()

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
            timezone.localtime(submission.submitted_at).strftime('%d %b %Y, %I:%M %p') if submission.submitted_at else '-',
            styles,
        ),
    ]
    story.append(_kv_table(info_data, styles))
    story.append(Spacer(1, 12))

    # ════════════════════════════════════════════════════════════════════════
    # 2. PAN CARD
    # ════════════════════════════════════════════════════════════════════════
    story.append(Paragraph('PAN Card', styles['SectionHeader']))
    
    if candidate_detail and candidate_detail.entered_with_consent:
        story.append(Paragraph(
            '<b>Note:</b> Candidate entered with manual confirmation (PAN mismatch / extraction failure)',
            styles['NotQualifiedBadge']
        ))
        story.append(Spacer(1, 10))

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
            Paragraph('<b>Q# / Question</b>', styles['Normal']),
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

            html_parts = []
            
            if aq:
                import xml.sax.saxutils as saxutils
                q_text = aq.question.question if aq.question else 'N/A'
                q_type = (aq.question_type or '').strip().upper()
                
                # Question header
                escaped_q = saxutils.escape(q_text)
                html_parts.append(f'<b>{idx}. {escaped_q}</b><br/><br/>')
                
                # Figure out correct set and selected set
                if q_type == 'MSQ':
                    correct_set = set([_norm_choice(x) for x in (aq.correct_answers or [])])
                    
                    submitted_list = candidate_answer if isinstance(candidate_answer, list) else []
                    raw = [_norm_choice(x) for x in submitted_list if _norm_choice(x)]
                    if mapping and isinstance(mapping, dict):
                        raw = [mapping.get(x, x) for x in raw]  # newLabel -> origLabel
                    selected_set = set(raw)
                    
                    is_correct = sorted(list(selected_set)) == sorted(list(correct_set)) and len(selected_set) > 0
                else:
                    correct_val = _norm_choice(aq.correct_answer)
                    correct_set = {correct_val} if correct_val else set()
                    
                    if q_type == 'TF':
                        # Make sure correct_set maps TF to A/B so it matches the options check
                        if correct_val == 'TRUE': correct_set = {'A'}
                        elif correct_val == 'FALSE': correct_set = {'B'}
                        
                    submitted_choice = _norm_choice(candidate_answer)
                    if mapping and isinstance(mapping, dict):
                        submitted_choice = mapping.get(submitted_choice, submitted_choice)
                    selected_set = {submitted_choice} if submitted_choice else set()
                    
                    is_correct = len(selected_set) > 0 and (list(selected_set)[0] == list(correct_set)[0] if correct_set else False)
                    
                # Build options list
                opts = []
                if q_type == 'TF':
                    opts.append(('A', 'True'))
                    opts.append(('B', 'False'))
                else:
                    q_obj = aq.question
                    if getattr(q_obj, 'option_a', None): opts.append(('A', getattr(q_obj, 'option_a')))
                    if getattr(q_obj, 'option_b', None): opts.append(('B', getattr(q_obj, 'option_b')))
                    if getattr(q_obj, 'option_c', None): opts.append(('C', getattr(q_obj, 'option_c')))
                    if getattr(q_obj, 'option_d', None): opts.append(('D', getattr(q_obj, 'option_d')))
                    
                # Format options text
                for opt_lbl, opt_text in opts:
                    is_opt_correct = opt_lbl in correct_set
                    is_opt_selected = opt_lbl in selected_set
                    color = '#000000'
                    
                    if is_opt_correct: color = '#16a34a' # Green
                    elif is_opt_selected: color = '#dc2626' # Red
                        
                    # Pencil Emoji unicode is U+270E or U+270F
                    pencil = ' <font color="#3b82f6">&#x270E;</font>' if is_opt_selected else ''
                    
                    escaped_opt = saxutils.escape(opt_text)
                    html_parts.append(f'<font color="{color}">{opt_lbl}. {escaped_opt}</font>{pencil}<br/>')
                
            else:
                html_parts.append(f'<b>{idx}. Question {key}</b><br/><br/>')
                is_correct = False

            icon = '\u2713' if is_correct else '\u2717'
            clr = colors.HexColor('#16a34a') if is_correct else colors.HexColor('#dc2626')
            
            cell_html = ''.join(html_parts)

            obj_data.append([
                Paragraph(cell_html, styles['Normal']),
                Paragraph(f'<font color="{clr}"><b>{icon}</b></font>', styles['Normal']),
            ])

        obj_table = Table(obj_data, colWidths=[410, 40])
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
            story.append(Spacer(1, 16))

            # Code block
            if submitted_code:
                code_display = submitted_code[:3000]
                if len(submitted_code) > 3000:
                    code_display += '\n\n... (code truncated) ...'
                formatted_code = highlight_for_reportlab(code_display, language)
                story.append(XPreformatted(formatted_code, styles['CodeBlockDark']))
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

                # Use stored test case results if available, otherwise fallback to re-evaluating
                stored_test_cases = cdata.get('test_cases', [])
                if stored_test_cases:
                    exec_results = stored_test_cases
                else:
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
                            # Check passed status explicitly since executor returns boolean passed or exit_code
                            if 'passed' in r:
                                status_str = 'Passed' if r['passed'] else 'Failed'
                            elif 'status' in r:
                                status = r['status']
                                if isinstance(status, bool):
                                    status_str = 'Passed' if status else 'Failed'
                                elif str(status).lower() in ('true', 'pass', 'passed', 'accepted'):
                                    status_str = 'Passed'
                                else:
                                    status_str = 'Failed'
                            elif 'exit_code' in r:
                                status_str = 'Passed' if r['exit_code'] == 0 else 'Failed'

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
                            # Executor format from JS: r.stdout; or if fallback: r.get('stdout', '-')
                            actual_str = str(r.get('stdout', r.get('output', '-')) or '-')[:150]
                            # Check passed status explicitly since executor returns boolean passed or exit_code
                            if 'passed' in r:
                                status_str = 'Passed' if r['passed'] else 'Failed'
                            elif 'status' in r:
                                status = r['status']
                                if isinstance(status, bool):
                                    status_str = 'Passed' if status else 'Failed'
                                elif str(status).lower() in ('true', 'pass', 'passed', 'accepted'):
                                    status_str = 'Passed'
                                else:
                                    status_str = 'Failed'
                            elif 'exit_code' in r:
                                status_str = 'Passed' if r['exit_code'] == 0 else 'Failed'

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

    pct = submission.final_percentage if submission.final_percentage is not None else submission.percentage
    
    # User Request: If score is 100%, show Qualified status regardless of malpractice hold
    if pct >= 100.0:
        status_style = styles['QualifiedBadge']
        status_text = 'Qualified'
    else:
        status_style = styles['QualifiedBadge'] if submission.is_qualified else styles['NotQualifiedBadge']
        status_text = 'Qualified' if submission.is_qualified else 'Not Qualified'
    
    # Check if coding was actually attempted for score display purposes
    actual_coding_attempts = [
        k for k in coding_keys 
        if isinstance(answers.get(k), dict) and answers[k].get('submitted_code')
    ]

    # Custom score display: show split scores if both are available and coding was reached
    if submission.objective_total > 0 and submission.coding_total > 0 and actual_coding_attempts:
        score_display = f"Objective: {submission.objective_score}/{submission.objective_total}, Coding: {submission.coding_score}/{submission.coding_total}"
    elif submission.objective_total > 0:
        score_display = f"Objective: {submission.objective_score} / {submission.objective_total}"
        if submission.coding_total > 0 and not actual_coding_attempts:
            score_display += " (Coding Gated/Not Reached)"
    elif submission.coding_total > 0:
        score_display = f"Coding: {submission.coding_score} / {submission.coding_total}"
    else:
        score_display = f"{submission.score} / {submission.total}"

    # ── Fetch Integrity Score ──
    integrity_score = 100.0
    violations = 0
    integrity = None
    try:
        integrity = CandidateIntegrity.objects.get(invitation=inv)
        integrity_score = integrity.integrity_score
        
        tab_v = integrity.tab_switches or 0
        phone_v = integrity.phone_detections or 0
        multi_v = integrity.multiface_detections or 0
        no_face_v = integrity.no_face_detections or 0
        
        # First 3 no-face events are warnings (0 penalty)
        no_face_penalty = max(0, no_face_v - 3)
        violations = tab_v + phone_v + multi_v + no_face_penalty
    except CandidateIntegrity.DoesNotExist:
        pass

    # ── Determine Dynamic Result Status ──
    # User Requirement: integrity < 70 => Hold
    final_result_text = submission.result or '-'
    result_style = styles['InfoValue']
    
    if integrity_score < 70:
        final_result_text = 'HOLD'
        result_style = styles['NotQualifiedBadge'] # Reuse red bold style

    results_data = [
        _info_row('Score', score_display, styles),
        _info_row('Percentage', f"{pct:.1f}%", styles),
        [Paragraph('Status', styles['InfoLabel']), Paragraph(status_text, status_style)],
        [Paragraph('Result', styles['InfoLabel']), Paragraph(final_result_text, result_style)],
    ]

    # Add Integrity Score row
    if integrity:
        int_color = colors.HexColor('#16a34a') if integrity_score >= 80 else (colors.HexColor('#eab308') if integrity_score >= 50 else colors.HexColor('#dc2626'))
        results_data.append([
            Paragraph('Integrity Score', styles['InfoLabel']),
            Paragraph(f'<font color="{int_color}">{integrity_score:.1f}%</font> ({violations} Violations)', styles['InfoValue'])
        ])

    story.append(_kv_table(results_data, styles))
    story.append(Spacer(1, 12))

    # ════════════════════════════════════════════════════════════════════════
    # 4. TYPING GAP ANALYSIS
    # ════════════════════════════════════════════════════════════════════════
    # Check if the assessment includes coding questions
    coding_questions = AssessmentCodingQuestion.objects.filter(assessment=assessment)
    # Only show typing analysis if there were actual attempts at coding:
    actual_attempts = False
    if coding_questions.exists():
        sub = getattr(inv, 'submission', None)
        if sub and sub.answers:
            actual_attempts = any(k.startswith('acq_') for k in sub.answers.keys())
    
    # Only show the in-depth forensic behavioral report if there were actual coding attempts.
    # We ignore raw logs for purely objective (MCQ) exams to keep the report clean.
    if actual_attempts:
        try:
            # Main Section Heading
            story.append(Paragraph('Coding Behavior & Malpractice Analysis', styles['SectionHeader']))
            story.append(Paragraph('Exhaustive behavioral audit using complexity-adjusted timing and fingerprint analysis to detect automation or assisted drafting.', styles['Normal']))
            story.append(Spacer(1, 15))

            logs_qs = KeystrokeLog.objects.filter(invitation=inv).order_by('created_at')
            keystroke_logs = list(logs_qs)
            if keystroke_logs:
                print(f"[report] Typing analysis logs found: {len(keystroke_logs)} for invitation {inv.id}")
                total_keystrokes = 0
                total_time_diffs = []
                long_pauses = 0
                burst_events = 0
                backspace_count = 0
                first_timestamp = None
                last_timestamp = None
                rhythm_records = 0
                rhythm_sample_count = 0
                pause_details = []
                
                for log in keystroke_logs:
                    events = log.events or []
                    total_keystrokes += len(events)
                    
                    for event in events:
                        time_diff = event.get('time_diff', 0)
                        ts = event.get('timestamp')
                        if ts:
                            if first_timestamp is None:
                                first_timestamp = ts
                            last_timestamp = ts
                        if time_diff > 0:
                            total_time_diffs.append(time_diff)
                            if time_diff > 20000:  # 20 seconds
                                long_pauses += 1
                                if len(pause_details) < 3:
                                    pause_details.append((ts or '-', time_diff))
                        if event.get('key') == 'Backspace':
                            backspace_count += 1
                    
                    if len(events) > 80:
                        burst_events += 1
                    if log.rhythm:
                        rhythm_records += 1
                        rhythm_sample_count += int(log.rhythm.get('sample_count', 0) or 0)
                
                avg_typing_speed = 0
                avg_time_diff = 0
                if total_time_diffs:
                    avg_time_diff = sum(total_time_diffs) / len(total_time_diffs)
                    if avg_time_diff > 0:
                        chars_per_ms = 1000 / avg_time_diff
                        avg_typing_speed = chars_per_ms * 60

                all_timestamps = []
                typing_events = []
                for log in keystroke_logs:
                    for event in log.events or []:
                        ts = _parse_timestamp(event.get('timestamp'))
                        if ts is not None:
                            all_timestamps.append(ts)
                            if _is_typing_key(event.get('key')):
                                typing_events.append({'timestamp': ts, 'key': event.get('key')})

                first_ts = min(all_timestamps) if all_timestamps else None
                last_ts = max(all_timestamps) if all_timestamps else None
                total_duration_ms = int((last_ts - first_ts).total_seconds() * 1000) if first_ts and last_ts else 0
                coding_minutes = total_duration_ms / 60000.0 if total_duration_ms > 0 else 0
                coding_time_display = f"{coding_minutes:.1f} min" if coding_minutes > 0 else '-'
                overall_average_speed = 0
                if coding_minutes > 0 and typing_events:
                    overall_average_speed = len(typing_events) / coding_minutes

                # Fingerprint match coverage
                rhythm_coverage = (rhythm_sample_count / total_keystrokes * 100) if total_keystrokes > 0 else 0

                # Split duration into 2 or 3 sections for analysis
                section_data = []
                if total_duration_ms > 0 and typing_events:
                    section_count = 3 if total_duration_ms >= 20 * 60 * 1000 else 2
                    section_boundaries = []
                    base_ms = total_duration_ms // section_count
                    extra = total_duration_ms % section_count
                    current_ms = 0
                    for i in range(section_count):
                        current_ms += base_ms + (1 if i < extra else 0)
                        section_boundaries.append(current_ms)

                    section_chars = [0] * section_count
                    for event in typing_events:
                        elapsed = int((event['timestamp'] - first_ts).total_seconds() * 1000)
                        section_index = next((idx for idx, boundary in enumerate(section_boundaries) if elapsed <= boundary), section_count - 1)
                        section_chars[section_index] += 1

                    section_start = 0
                    for idx, boundary in enumerate(section_boundaries):
                        section_ms = boundary - section_start
                        section_minutes = section_ms / 60000.0 if section_ms > 0 else 0
                        chars = section_chars[idx]
                        speed = chars / section_minutes if section_minutes > 0 else 0
                        section_data.append({
                            'id': idx + 1,
                            'chars': chars,
                            'minutes': section_minutes,
                            'speed': speed
                        })
                        section_start = boundary

                # ───── Consolidated Unified Interpretation Table ─────
                unified_rows = []

                # A. Difficulty Adjustment Logic
                difficulty_factor = 1.0 
                try:
                    coding_ids = [int(k.replace('acq_', '')) for k in coding_keys if k.replace('acq_', '').isdigit()]
                    difficulties = list(AssessmentCodingQuestion.objects.filter(id__in=coding_ids).values_list('difficulty', flat=True))
                    if 'hard' in difficulties: difficulty_factor = 0.8 
                    elif 'easy' in difficulties and 'medium' not in difficulties and 'hard' not in difficulties: 
                        difficulty_factor = 1.2 
                except: pass
                
                # 1. Basic Metadata
                unified_rows.append(["Total Coding Time", coding_time_display, "Session duration", "Low", f"The candidate spent a total of {coding_time_display} strictly focused on the coding challenge."])
                unified_rows.append(["Typing Log Batches", f"{len(keystroke_logs)}", "Save frequency", "Low", f"Behavioral patterns were captured across {len(keystroke_logs)} distinct data batches for analysis."])
                unified_rows.append(["First Keystroke", first_ts.strftime('%H:%M:%S  %d-%m-%Y') if first_ts else "-", "Start timestamp", "Low", "The exact chronological start of the candidate's implementation phase."])
                unified_rows.append(["Last Keystroke", last_ts.strftime('%H:%M:%S  %d-%m-%Y') if last_ts else "-", "End timestamp", "Low", "The exact chronological completion and submission of the code logic."])

                # Phase Performance Audit
                base_threshold = 300 * difficulty_factor
                for s in section_data:
                    s_lvl = "Low"
                    observation = f"{s['chars']} chars in {s['minutes']:.1f} min"
                    s_desc = f"Phase {s['id']} show steady, believable progress with a pace of {s['speed']:.1f} CPM."
                    if s['speed'] > base_threshold * 2.2:
                        s_lvl = "High"
                        s_desc = f"Velocity surge ({s['speed']:.1f} CPM) in Phase {s['id']} is anomalous; could indicate a code dump in this window."
                    elif s['speed'] < 10 and s['minutes'] > 4:
                        s_lvl = "Medium"
                        s_desc = f"Phase {s['id']} was nearly stagnant for {s['minutes']:.1f} minutes; suggests a significant distraction or halt."
                    unified_rows.append([f"Phase {s['id']} Auditor", observation, f"Phase {s['id']} activity", s_lvl, s_desc])

                # 1. Identity Fingerprint
                finger_risk = "Low"
                finger_msg = "Single User: Consistent typing pattern confirms same person throughout."
                
                if rhythm_coverage >= 90:
                    finger_risk = "Low"
                    finger_msg = "Single User: Consistent typing pattern; strongly indicates same person throughout."
                elif rhythm_coverage >= 60:
                    finger_risk = "Medium"
                    finger_msg = "Minor Variation: Slight rhythm inconsistencies; possible distractions or context switching."
                else:
                    finger_risk = "High"
                    finger_msg = "Multiple Patterns: Inconsistent typing rhythm; indicates potential multiple users or automation."
                
                # Handle special case of no fingerprint data with high volume
                if rhythm_records == 0 and total_keystrokes > 300:
                    finger_risk = "High"
                    finger_msg = "Identity Anomaly: Signature not found; consistent with automated drafting tools."

                unified_rows.append(["Identity Fingerprint", f"{rhythm_coverage:.0f}% coverage", "Identity audit", finger_risk, finger_msg])

                # 2. Typing Rhythm (Avg Time Gap)
                rhythm_lvl = "Low"
                rhythm_desc = f"With a {avg_time_diff:.1f}ms gap, the typing rhythm is fluid and consistent with human logic formulation."
                if avg_time_diff > 1200:
                    rhythm_lvl = "Medium"
                    rhythm_desc = "Higher time gaps suggest significant deliberation or potential search for external syntax help."
                unified_rows.append(["Typing Rhythm (Avg Time Gap)", f"{avg_time_diff:.1f} ms", "Raw key delay", rhythm_lvl, rhythm_desc])

                # 3. Active Typing Speed
                active_lvl = "Low"
                active_desc = f"An active speed of {avg_typing_speed:.1f} CPM shows a steady and believable pace during coding bursts."
                if avg_typing_speed > 450:
                    active_lvl = "High"
                    active_desc = "Extreme activity peaks detected; suggests high-speed typing or batch pasting of pre-written logic."
                unified_rows.append(["Active Typing Speed", f"{avg_typing_speed:.1f} chars/min", "Burst velocity", active_lvl, active_desc])

                # 4. Overall Drafting Speed
                overall_lvl = "Low"
                overall_desc = "Normal Speed: Standard human typing speed; ideal coding behavior."
                if overall_average_speed < 20:
                    overall_lvl = "Low"
                    overall_desc = "Slow Typing: Beginner pace or deep logical formulation."
                elif overall_average_speed <= 60:
                    overall_lvl = "Low"
                    overall_desc = "Normal Speed: Standard human typing speed; ideal coding behavior."
                elif overall_average_speed <= 120:
                    overall_lvl = "Medium"
                    overall_desc = "Fast Typing: Above average speed; suggests an experienced or confident coder."
                else:
                    overall_lvl = "High"
                    overall_desc = "Very Fast: Unusually high speed; possible automation or external reference usage."
                unified_rows.append(["Overall Drafting Speed", f"{overall_average_speed:.1f} CPM", "Aggregate velocity", overall_lvl, overall_desc])

                # 5. Total Keystrokes
                unified_rows.append(["Total Keystrokes", f"{total_keystrokes}", "Total volume", "Low", f"A total of {total_keystrokes} keystrokes were recorded, verifying the amount of manual effort applied."])

                precision_lvl = "Low"
                error_rate = (backspace_count / total_keystrokes * 100) if total_keystrokes > 0 else 0
                
                precision_lvl = "Low"
                precision_desc = "Natural Behavior: Balanced correction rate; strong indicator of genuine human coding."
                
                if error_rate < 2.0 and total_keystrokes > 100:
                    precision_lvl = "High"
                    precision_desc = "Too Perfect: Almost no corrections observed. Candidate may be copying or referencing external solution."
                elif error_rate < 5.0:
                    precision_lvl = "Low"
                    precision_desc = "Efficient Typing: Minimal corrections, likely an experienced coder or typing carefully."
                elif error_rate <= 15.0:
                    precision_lvl = "Low"
                    precision_desc = "Natural Behavior: Balanced correction rate matches human coding benchmarks."
                elif error_rate <= 30.0:
                    precision_lvl = "Medium"
                    precision_desc = "High Corrections: Candidate is refining logic or struggling with syntax."
                else:
                    precision_lvl = "High"
                    precision_desc = "Excessive Errors: Very high correction activity suggests unstable coding or lack of clarity."
                
                unified_rows.append(["Forensic Precision", f"{error_rate:.1f}% Error", "Correction ratio", precision_lvl, precision_desc])

                # 8. Forensic Summary Logic (Aggregate Risk Scoring)
                medium_count = sum(1 for r in unified_rows if r[3] == "Medium")
                high_count = sum(1 for r in unified_rows if r[3] == "High")

                # Integrity Violation Data
                tab_switches = (integrity.tab_switches or 0) if integrity else 0
                phone_hits = (integrity.phone_detections or 0) if integrity else 0
                multi_face = (integrity.multiface_detections or 0) if integrity else 0

                # --- Dynamic Interpretation Logic ---
                dynamic_notes = []
                if multi_face > 1: dynamic_notes.append("Multiple individuals detected in frame")
                elif multi_face == 1: dynamic_notes.append("Another individual appeared briefly in the background")
                
                no_face_v = (integrity.no_face_detections or 0) if integrity else 0
                if no_face_v > 3: 
                    dynamic_notes.append("Frequent face visibility interruptions")
                
                if phone_hits > 0: dynamic_notes.append("Potential mobile phone usage")
                
                if tab_switches >= 3: dynamic_notes.append("Repeated tab switching suggests external searching")
                elif tab_switches > 0: dynamic_notes.append("Occasional tab switching")
                
                if long_pauses >= 10: dynamic_notes.append("Frequent long pauses suggest external assistance")
                elif long_pauses >= 4: dynamic_notes.append("Unusual pausing patterns detected")
                
                if burst_events > 0: dynamic_notes.append("Rapid bulk text insertion suggests copy-paste behavior")
                
                if overall_average_speed > 120: dynamic_notes.append("Drafting velocity exceeds natural human benchmarks")
                elif error_rate < 2.0 and total_keystrokes > 200: dynamic_notes.append("Abnormally high precision suggests pre-drafted content")

                # Determine Risk Status and Verdict
                risk_status = "Low"
                verdict_title = "Organic Flow"
                
                # --- 1. High Risk Criteria (Critical Malpractice Evidence) ---
                if (multi_face > 1 or phone_hits > 0 or tab_switches >= 3 or burst_events >= 3 or
                    overall_average_speed > 180 or (error_rate < 0.5 and total_keystrokes > 400)):
                    risk_status = "High"
                    verdict_title = "High Risk Detected"
                    notes_str = ". ".join(dynamic_notes) if dynamic_notes else "Critical behavioral anomalies"
                    interpretation_text = f"Significant anomalies detected: {notes_str}. [Recommendation: Hold / Reject]"

                # --- 2. Medium Risk Criteria (Requires at least one suspicious indicator) ---
                elif (tab_switches >= 1 or multi_face == 1 or no_face_v > 3 or long_pauses > 3 or burst_events > 0):
                    risk_status = "Medium"
                    verdict_title = "Behavioral Caution"
                    notes_str = ". ".join(dynamic_notes) if dynamic_notes else "Atypical patterns detected"
                    interpretation_text = f"Atypical patterns detected: {notes_str}. [Recommendation: Manual Review]"

                # --- 3. Low Risk (Default - For natural or high-performance coding) ---
                else:
                    risk_status = "Low"
                    verdict_title = "Organic Flow"
                    if dynamic_notes:
                        notes_str = ", ".join(dynamic_notes)
                        interpretation_text = f"Minor anomalies detected ({notes_str}), but overall behavior remains within acceptable risk thresholds. [Recommendation: Selected]"
                    else:
                        interpretation_text = "Candidate behavior matches benchmarks for authentic manual coding; no significant anomalies or violations detected. [Recommendation: Selected]"

                # User Request: Ensure "Manual Review Required" is at the START of the interpretation
                if integrity_score < 70:
                    verdict_title = "HOLD - Manual Review Required"
                    interpretation_text = "<b>[Manual Review Required]</b> This assessment is on HOLD. " + interpretation_text
                elif risk_status != "Low":
                    interpretation_text = "<b>[Manual Review Required]</b> " + interpretation_text

                # --- Recruiter-Friendly Summary Card ---
                card_bg = "#f0fdf4" # Green bg
                border_color = "#16a34a"
                if risk_status == "Medium":
                    card_bg = "#fefce8" ; border_color = "#eab308"
                elif risk_status == "High":
                    card_bg = "#fef2f2" ; border_color = "#dc2626"

                # --- Enhanced Metrics for Summary Card ---
                tech_skill = "Low"
                if pct >= 80: tech_skill = "Strong"
                elif pct >= 50: tech_skill = "Medium"

                integrity_lvl = "Low"
                if integrity_score >= 85: integrity_lvl = "High"
                elif integrity_score >= 70: integrity_lvl = "Medium"

                # Build integrity explanation for Medium/Low scores
                violation_details = []
                total_violations = 0
                if integrity:
                    if (integrity.tab_switches or 0) > 0:
                        violation_details.append(f"tab switching ({integrity.tab_switches})")
                        total_violations += integrity.tab_switches
                    # Hide first 3 no-face events entirely; only count/show from 4th onwards
                    if (integrity.no_face_detections or 0) > 3:
                        penalty_count = integrity.no_face_detections - 3
                        violation_details.append(f"no face detected ({penalty_count})")
                        total_violations += penalty_count
                    if (integrity.multiface_detections or 0) > 0:
                        violation_details.append(f"multiple faces ({integrity.multiface_detections})")
                        total_violations += integrity.multiface_detections
                    if (integrity.phone_detections or 0) > 0:
                        violation_details.append(f"phone detection ({integrity.phone_detections})")
                        total_violations += integrity.phone_detections
                
                violation_summary = ""
                if violation_details:
                    violation_summary = f"{total_violations} Violation{'s' if total_violations > 1 else ''} : " + ", ".join(violation_details)
                elif integrity_lvl != "High":
                    violation_summary = f"Behavioral anomalies detected (Backspace count: {backspace_count})"

                # --- Recruiter-Friendly Summary Card ---
                card_bg = "#f0fdf4" # Green bg
                border_color = "#16a34a"
                if risk_status == "Medium":
                    card_bg = "#fefce8" ; border_color = "#eab308"
                elif risk_status == "High":
                    card_bg = "#fef2f2" ; border_color = "#dc2626"

                # Determine Recommendation based on Risk
                recommendation = "Selected"
                rec_color = "#16a34a" # Green
                if risk_status == "High":
                    recommendation = "Hold / Reject"
                    rec_color = "#dc2626" # Red
                elif risk_status == "Medium":
                    recommendation = "Manual Review"
                    rec_color = "#eab308" # Yellow

                # Create a balanced grid for metrics (3 columns)
                metrics_table = Table([
                    [_info_row('Risk Status', f'<font color="{border_color}">{risk_status}</font>', styles), 
                     _info_row('Authenticity', f"{rhythm_coverage:.0f}% Coverage", styles),
                     _info_row('Technical Skill', tech_skill, styles)],
                    [_info_row('Integrity Score', integrity_lvl, styles),
                     _info_row('Recommendation', f'<font color="{rec_color}">{recommendation}</font>', styles),
                     _info_row('Long Pauses', f"{long_pauses} times", styles)],
                    [_info_row('Backspaces', f"{backspace_count}", styles), "", ""]
                ], colWidths=[2.3 * inch, 2.3 * inch, 2.3 * inch])
                
                metrics_table.setStyle(TableStyle([
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('TOPPADDING', (0, 0), (-1, -1), 12), # Increased for space between 1st and 2nd line
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                    ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ]))

                summary_data = [
                    [Paragraph(f'<b>Forensic Integrity Verdict: <font color="{border_color}">{verdict_title}</font></b>', styles['InfoLabel'])],
                    [Paragraph(interpretation_text, styles['Normal'])],
                    [metrics_table]
                ]

                if violation_summary:
                    summary_data.append([Spacer(1, 2)]) # Decreased space before violations
                    summary_data.append([Paragraph(f"<b>Integrity Violations</b>", styles['InfoLabel'])])
                    summary_data.append([Paragraph(violation_summary, styles['Normal'])])
                
                summary_tbl = Table(summary_data, colWidths=[7.2 * inch])
                summary_tbl.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor(card_bg)),
                    ('BOX', (0, 0), (-1, -1), 1, colors.HexColor(border_color)),
                    ('TOPPADDING', (0, 0), (-1, -1), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                    ('LEFTPADDING', (0, 0), (-1, -1), 15),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 15),
                ]))
                story.append(summary_tbl)
                story.append(Spacer(1, 25))

                # Unified Data Table
                story.append(Paragraph('<b>Detailed Behavioral Audit</b>', styles['InfoLabel']))
                story.append(Spacer(1, 5))

                # 6. Backspace Count
                bs_lvl = "Low"
                bs_desc = f"{backspace_count} backspaces were used, reflecting a healthy, natural cycle of error correction and logic refinement."
                if total_keystrokes > 100:
                    bs_ratio = (backspace_count / total_keystrokes) * 100
                    if bs_ratio < 1.0:
                        bs_lvl = "High"
                        bs_desc = "Perfect typing with near-zero errors is highly suspicious; suggests code was dumped rather than drafted."
                    elif bs_ratio < 2.5:
                        bs_lvl = "Medium"
                        bs_desc = "Lower than average error correction noticed, showing high confidence or meticulous pre-planning."
                unified_rows.append(["Backspace Count", f"{backspace_count}", "Correction rate", bs_lvl, bs_desc])

                # 7. Long Pauses (>20s)
                if long_pauses >= 8:
                    pause_lvl = "High"
                    pause_desc = f"Candidate had {long_pauses} long idle gaps. This frequent disruption suggests possible context switching (research/help)."
                elif long_pauses >= 4:
                    pause_lvl = "Medium"
                    pause_desc = f"{long_pauses} significant pauses found; slightly unusual for a focused session, suggesting external consultation."
                else:
                    pause_lvl = "Low"
                    pause_desc = f"Normal thinking rhythm ({long_pauses} gaps) with standard periods of logical deliberation."
                unified_rows.append(["Long Pauses", f"{long_pauses} (>20s)", "Idle cycles", pause_lvl, pause_desc])

                # 8. Burst Typing (Paste Events)
                burst_lvl = "None Detected"
                burst_desc = "No abnormal code injections detected; the solution was built incrementally line-by-line."
                if burst_events > 0:
                    burst_lvl = "Medium"
                    burst_desc = f"{burst_events} sudden large injections found; suggests pasting of boilerplate code or small snippets."
                if burst_events > 3:
                    burst_lvl = "High"
                    burst_desc = "Frequent large bursts detected; indicates that logic was likely copied and pasted in large chunks."
                unified_rows.append(["Burst Typing", f"{burst_events}", "Bulk injections", burst_lvl, burst_desc])

                # 9. Behavioral Pattern Analysis
                pattern = "Steady"
                pattern_guidance = "Candidate showed a consistent flow, maintaining a similar rhythm throughout the session."
                if len(section_data) >= 2:
                    s1_speed = section_data[0]['speed']
                    s_last_speed = section_data[-1]['speed']
                    if s1_speed < 30 and s_last_speed > 100:
                        pattern = "Think -> Type"
                        pattern_guidance = "Natural pattern: Intial planning phase followed by active coding implementation."
                    elif s1_speed > 400 and s_last_speed < 100:
                        pattern = "Dump -> Edit"
                        pattern_guidance = "Potential Risk: High-volume initial injection followed only by minor refinements."
                unified_rows.append(["Behavioral Pattern", pattern, "Workflow rhythm", "Low", pattern_guidance])


                header_labels = ["Metric Analyzed", "Observed Value", "What It Means", "Risk Status", "Forensic Guidance"]
                headers = [Paragraph(f'<b>{h}</b>', styles['InfoLabel']) for h in header_labels]
                
                tbl_data = [headers]
                for row in unified_rows:
                    risk = row[3]
                    risk_color = "#16a34a" # Green (Low)
                    if risk == "Medium": risk_color = "#eab308"
                    if risk == "High": risk_color = "#dc2626"
                    
                    tbl_data.append([
                        Paragraph(row[0], styles['Normal']),
                        Paragraph(row[1], styles['Normal']),
                        Paragraph(row[2], styles['Normal']),
                        Paragraph(f'<b><font color="{risk_color}">{risk}</font></b>', styles['Normal']),
                        Paragraph(row[4], styles['Normal'])
                    ])
                
                # Optimized table design to fit A4 margins and wider status text
                col_ws = [1.1*inch, 1.0*inch, 1.1*inch, 1.1*inch, 2.8*inch]
                unified_tbl = Table(tbl_data, colWidths=col_ws)
                unified_tbl.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f8fafc')),
                    ('LINEBELOW', (0,0), (-1,0), 1, colors.HexColor('#cbd5e1')),
                    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                    ('TOPPADDING', (0,0), (-1,-1), 10),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 10),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#f1f5f9')),
                ]))
                story.append(unified_tbl)
                story.append(Spacer(1, 20))

                if pause_details:
                    story.append(Paragraph('Long Pause Samples', styles['InfoLabel']))
                    for pause_ts, pause_ms in pause_details:
                        story.append(Paragraph(f'- {pause_ts} : {pause_ms} ms', styles['Normal']))
                    story.append(Spacer(1, 12))
            else:
                print(f"[report] No keystroke logs found for invitation {inv.id}")
                story.append(Paragraph('No typing logs were recorded for this candidate.', styles['Normal']))
                story.append(Spacer(1, 12))
        except Exception as e:
            print(f"Error generating typing analysis for report: {e}")
            import traceback
            traceback.print_exc()

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

    # ════════════════════════════════════════════════════════════════════════
    # 6. INTEGRITY VIOLATIONS LOG
    # ════════════════════════════════════════════════════════════════════════
    try:
        integrity_screenshots = list(IntegrityScreenshot.objects.filter(invitation=inv).order_by('timestamp'))
        if integrity_screenshots:
            story.append(PageBreak())
            story.append(Paragraph('Integrity Violations Log', styles['SectionHeader']))
            story.append(Paragraph('The following screenshots were captured automatically when integrity warnings were triggered.', styles['Normal']))
            story.append(Spacer(1, 12))

            from collections import defaultdict
            groups = defaultdict(list)
            no_face_skip_count = 0
            
            for snap in integrity_screenshots:
                evt = str(snap.event_type).lower().strip()
                group_name = ""
                
                if evt in ['window_switch', 'window_blur', 'blur', 'focus_lost']:
                    group_name = 'Window Switch'
                elif evt in ['no_face_detection', 'face_detection_lost', 'face_detection_lost_rechecked', 'no_face']:
                    no_face_skip_count += 1
                    if no_face_skip_count <= 3:
                        continue # Hide first 3 face warnings from screenshots too
                    group_name = 'No Face Detection'
                elif evt in ['multiface_detection', 'multiple_faces', 'multi_face']:
                    group_name = 'Multipeople Detection'
                elif evt in ['tab_switch', 'tab_switched', 'visibility_hidden']:
                    group_name = 'Tab Switch'
                elif evt in ['phone_detection', 'cell_phone', 'phone']:
                    group_name = 'Phone Detection'
                else:
                    group_name = evt.replace('_', ' ').title()
                
                if group_name:
                    groups[group_name].append(snap)

            for group_name, snaps in groups.items():
                story.append(Paragraph(f"<b>Warning: {group_name}</b>", styles['InfoValue']))
                story.append(Spacer(1, 6))

                for i in range(0, len(snaps), 3):
                    chunk = snaps[i:i+3]
                    
                    img_row = []
                    text_row = []
                    
                    for snap in chunk:
                        img = None
                        if snap.screenshot and snap.screenshot.name and os.path.exists(snap.screenshot.path):
                            img = _make_rl_image(snap.screenshot.path, 2.2 * inch, 1.6 * inch)
                        elif snap.webcam_screenshot and snap.webcam_screenshot.name and os.path.exists(snap.webcam_screenshot.path):
                            img = _make_rl_image(snap.webcam_screenshot.path, 2.2 * inch, 1.6 * inch)
                        
                        ts_str = timezone.localtime(snap.timestamp).strftime('%I:%M:%S %p')
                        from reportlab.lib.styles import ParagraphStyle
                        center_style = ParagraphStyle('CenterStyle', parent=styles['Normal'], alignment=1, fontSize=8, textColor=colors.HexColor('#64748b'))
                        text_row.append(Paragraph(f"{ts_str}", center_style))
                        
                        if img:
                            img_row.append(img)
                        else:
                            img_row.append(Paragraph('<i>No image</i>', center_style))
                    
                    while len(img_row) < 3:
                        img_row.append("")
                        text_row.append("")

                    tbl_data = [img_row, text_row]
                    col_widths = [2.4 * inch, 2.4 * inch, 2.4 * inch]
                    snap_tbl = Table(tbl_data, colWidths=col_widths)
                    snap_tbl.setStyle(TableStyle([
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
                        ('TOPPADDING', (0, 0), (-1, -1), 2),
                    ]))
                    story.append(snap_tbl)
                    story.append(Spacer(1, 8))
                
                story.append(HRFlowable(width='100%', thickness=0.5, color=colors.HexColor('#e2e8f0'), spaceAfter=12))

    except Exception as e:
        print(f"Error fetching integrity screenshots for report: {e}")
        import traceback
        traceback.print_exc()

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