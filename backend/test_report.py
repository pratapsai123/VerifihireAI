"""Test AI Interview Report Generation"""
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'VerifiHireAI_backend.settings')
import django
django.setup()

from ai_candidates.models import Candidate
from django.conf import settings
import io, base64
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage, PageBreak
from reportlab.lib.units import inch

TOTAL_INTERVIEW_QUESTIONS = 13
c = Candidate.objects.get(pk=3)
print("Testing report for: %s (ID=%d)" % (c.full_name, c.id))

try:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=50)
    styles = getSampleStyleSheet()
    elements = []
    if 'Small' not in styles:
        styles.add(ParagraphStyle(name='Small', parent=styles['Normal'], fontSize=8, leading=10, textColor=colors.grey))
    if 'Italic' not in styles:
        styles.add(ParagraphStyle(name='Italic', parent=styles['Normal'], fontName='Helvetica-Oblique'))

    elements.append(Paragraph("VerifiHireAI Interview Report", styles['Heading1']))
    elements.append(Paragraph("Candidate: %s" % c.full_name, styles['Heading2']))
    elements.append(Spacer(1, 15))
    print("[OK] Header done")

    deepface_dir = os.path.abspath(os.path.join(settings.BASE_DIR, '..', 'deepface', 'data', 'registered_faces'))
    person_id = str(c.public_token).lower()
    face_path = os.path.join(deepface_dir, person_id, "face_0.jpg")
    if os.path.exists(face_path):
        img_elem = RLImage(face_path, width=2.0*inch, height=1.5*inch)
        print("[OK] Photo found")
    else:
        img_elem = Paragraph("No photo", styles['Normal'])
        print("[MISS] No photo at: %s" % face_path)

    total_possible_marks = TOTAL_INTERVIEW_QUESTIONS * 10
    integrity_obj = getattr(c, 'integrity', None)
    integrity_score = integrity_obj.integrity_score if integrity_obj else 100.0
    integrity_penalty = max(0, 100.0 - integrity_score)
    base_score_pct = (c.score / total_possible_marks * 100) if total_possible_marks > 0 else 0
    final_performance_pct = max(0, round(base_score_pct - integrity_penalty, 1))
    print("[OK] Scores computed")

    info_data = [
        ["Full Name", c.full_name], ["Email", c.email],
        ["Job Title", c.job_title or "N/A"],
        ["Score", "%d / %d" % (c.score, total_possible_marks)],
        ["Status", c.status],
        ["Date", c.completed_at.strftime('%B %d, %Y %I:%M %p') if c.completed_at else 'Incomplete'],
    ]
    summary_table = Table(info_data, colWidths=[1.4*inch, 2.8*inch])
    layout_table = Table([[img_elem, summary_table]], colWidths=[2.2*inch, 4.3*inch])
    elements.append(layout_table)
    elements.append(Spacer(1, 25))
    print("[OK] Info table done")

    elements.append(Paragraph("Transcript", styles['Heading2']))
    if isinstance(c.interview_summary, list) and c.interview_summary:
        for i, turn in enumerate(c.interview_summary, 1):
            elements.append(Paragraph("Q%d" % i, styles['Heading4']))
            elements.append(Paragraph(turn.get('question', 'N/A'), styles['Normal']))
            elements.append(Paragraph(turn.get('answer', 'N/A'), styles['Normal']))
            elements.append(Spacer(1, 12))
        print("[OK] Transcript done (%d turns)" % len(c.interview_summary))

    elements.append(PageBreak())
    elements.append(Paragraph("Integrity", styles['Heading2']))
    logs = c.integrity_logs.all().order_by('timestamp')
    print("[OK] Logs: %d" % logs.count())

    if logs.exists():
        elements.append(Paragraph("Violations: %d" % logs.count(), styles['Normal']))
        all_images = []
        for log in logs:
            if log.webcam_screenshot_base64:
                try:
                    b64 = log.webcam_screenshot_base64.split(',')[-1]
                    img_data = base64.b64decode(b64)
                    img_io = io.BytesIO(img_data)
                    rl_img = RLImage(img_io, width=1.5*inch, height=1.1*inch)
                    ts = log.timestamp.strftime('%H:%M:%S') if log.timestamp else 'N/A'
                    all_images.append((rl_img, "Webcam %s (%s)" % (log.event_type, ts)))
                except Exception as e:
                    print("[WARN] Webcam: %s" % str(e))
            if log.screenshot_base64:
                try:
                    b64 = log.screenshot_base64.split(',')[-1]
                    img_data = base64.b64decode(b64)
                    img_io = io.BytesIO(img_data)
                    rl_img = RLImage(img_io, width=1.5*inch, height=1.1*inch)
                    ts = log.timestamp.strftime('%H:%M:%S') if log.timestamp else 'N/A'
                    all_images.append((rl_img, "Desktop %s (%s)" % (log.event_type, ts)))
                except Exception as e:
                    print("[WARN] Desktop: %s" % str(e))
        print("[OK] Images: %d" % len(all_images))
        if all_images:
            row = []
            for img, caption in all_images:
                row.append([img, Paragraph(caption, styles['Small'])])
                if len(row) == 4:
                    t = Table([row], colWidths=[1.5*inch]*4)
                    elements.append(t)
                    row = []
            if row:
                while len(row) < 4:
                    row.append("")
                t = Table([row], colWidths=[1.5*inch]*4)
                elements.append(t)
        print("[OK] Grid done")

    doc.build(elements)
    buffer.seek(0)
    print("\n=== SUCCESS! PDF size: %d bytes ===" % len(buffer.getvalue()))

except Exception as e:
    import traceback
    print("\n=== FAILED ===")
    print(str(e))
    traceback.print_exc()
