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
    CandidateIntegrity, IntegrityScreenshot, KeystrokeLog, BehaviorLog
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

    # Add Integrity Score if available
    try:
        integrity = CandidateIntegrity.objects.get(invitation=inv)
        
        # Color coding the integrity score based on value (e.g. < 70 is warning)
        int_score = integrity.integrity_score
        int_color = colors.HexColor('#16a34a') if int_score >= 80 else (colors.HexColor('#eab308') if int_score >= 50 else colors.HexColor('#dc2626'))
        
        # Formatting total violations
        violations = integrity.tab_switches + integrity.phone_detections + integrity.multiface_detections + integrity.no_face_detections
        
        results_data.append([
            Paragraph('Integrity Score', styles['InfoLabel']),
            Paragraph(f'<font color="{int_color}">{int_score:.1f}%</font> ({violations} Violations)', styles['InfoValue'])
        ])
    except CandidateIntegrity.DoesNotExist:
        pass

    story.append(_kv_table(results_data, styles))
    story.append(Spacer(1, 12))

    # ════════════════════════════════════════════════════════════════════════
    # 4.5. TYPING GAP ANALYSIS
    # ════════════════════════════════════════════════════════════════════════
    try:
        # Get all keystroke logs for this invitation
        keystroke_logs = KeystrokeLog.objects.filter(invitation=inv)
        
        story.append(Paragraph('Typing Gap Analysis', styles['SectionHeader']))
        
        if keystroke_logs.exists():
            print(f"[report] Typing analysis logs found: {keystroke_logs.count()} for invitation {inv.id}")
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

            # Split duration into 2 or 3 sections for reporting
            section_rows = []
            if total_duration_ms > 0 and typing_events:
                section_count = 3 if total_duration_ms >= 20 * 60 * 1000 else 2
                section_boundaries = []
                base_ms = total_duration_ms // section_count
                extra = total_duration_ms % section_count
                current_ms = 0
                for i in range(section_count):
                    current_ms += base_ms + (1 if i < extra else 0)
                    section_boundaries.append(current_ms)

                section_counts = [0] * section_count
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
                    section_rows.append(
                        f"Section {idx + 1}: {chars} chars in {section_minutes:.1f} min = {speed:.1f} chars/min"
                    )
                    section_start = boundary

            typing_data = [
                _info_row('Typing Log Batches', f"{keystroke_logs.count()}", styles),
                _info_row('Total Keystrokes', f"{total_keystrokes}", styles),
                _info_row('Rhythm Records', f"{rhythm_records}", styles),
                _info_row('Rhythm Sample Count', f"{rhythm_sample_count}", styles),
                _info_row('Average Time Diff', f"{avg_time_diff:.1f} ms", styles),
                _info_row('Average Typing Speed', f"{avg_typing_speed:.1f} chars/min", styles),
                _info_row('Coding Time', coding_time_display, styles),
                _info_row('Overall Average Typing Speed', f"{overall_average_speed:.1f} chars/min" if overall_average_speed else '-', styles),
                _info_row('Long Pauses (>20s)', f"{long_pauses}", styles),
                _info_row('Burst Typing Batches', f"{burst_events}", styles),
                _info_row('Backspace Count', f"{backspace_count}", styles),
                _info_row('First Keystroke Timestamp', first_ts.isoformat().replace('+00:00', 'Z') if first_ts else '-', styles),
                _info_row('Last Keystroke Timestamp', last_ts.isoformat().replace('+00:00', 'Z') if last_ts else '-', styles),
            ]

            story.append(_kv_table(typing_data, styles))
            story.append(Spacer(1, 12))

            if section_rows:
                story.append(Paragraph('Coding Time Section Breakdown', styles['InfoLabel']))
                for row in section_rows:
                    story.append(Paragraph(row, styles['Normal']))
                story.append(Spacer(1, 6))
                story.append(Paragraph('Calculation Notes:', styles['InfoLabel']))
                story.append(Paragraph(
                    f'Overall Average Typing Speed is calculated using total printable typed characters ' \
                    f'({len(typing_events)}) divided by the total coding duration ({coding_minutes:.1f} min).',
                    styles['Normal']
                ))
                story.append(Paragraph(
                    f'Example: {len(typing_events)} chars ÷ {coding_minutes:.1f} min = {overall_average_speed:.1f} chars/min.',
                    styles['Normal']
                ))
                story.append(Paragraph(
                    'Section speeds are calculated by splitting the total coding duration into equal time segments, ' \
                    'counting chars typed in each segment, and then computing chars per minute for each section.',
                    styles['Normal']
                ))
                story.append(Spacer(1, 12))

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
            for snap in integrity_screenshots:
                evt = str(snap.event_type)
                if evt in ['window_switch', 'window_blur']:
                    group_name = 'Window Switch'
                elif evt in ['no_face_detection', 'face_detection_lost', 'face_detection_lost_rechecked']:
                    group_name = 'No Face Detection'
                elif evt == 'multiface_detection':
                    group_name = 'Multipeople Detection'
                elif evt == 'tab_switch':
                    group_name = 'Tab Switch'
                elif evt == 'phone_detection':
                    group_name = 'Phone Detection'
                else:
                    group_name = evt.replace('_', ' ').title()
                
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
