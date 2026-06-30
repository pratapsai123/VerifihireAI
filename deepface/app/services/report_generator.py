"""
Feature 16: Session Report Generation

Generates comprehensive PDF reports and JSON summaries for completed sessions.
Uses ReportLab for PDF creation.
"""

import io
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from app.config import REPORTS_DIR, REPORT_INCLUDE_FRAME_SNAPSHOTS, REPORT_MAX_SNAPSHOTS
from app.models import database as db

logger = logging.getLogger(__name__)


async def generate_json_report(session_id: str) -> Optional[Dict]:
    """
    Generate a JSON report for a session.

    Returns:
        Complete session report as a dictionary, or None if session not found.
    """
    session = await db.get_session(session_id)
    if not session:
        return None

    violations = await db.get_violations(session_id)
    violation_breakdown = await db.get_violation_breakdown(session_id)
    engagement_timeline = await db.get_engagement_timeline(session_id)

    # Compute verification success rate
    attempts = session.get("verification_attempts", 0)
    successes = session.get("verification_successes", 0)
    success_rate = (successes / attempts * 100) if attempts > 0 else 0.0

    # Compute engagement stats
    engagement_scores = [e["score"] for e in engagement_timeline]
    avg_engagement = sum(engagement_scores) / len(engagement_scores) if engagement_scores else 0.0
    min_engagement = min(engagement_scores) if engagement_scores else 0.0
    max_engagement = max(engagement_scores) if engagement_scores else 0.0

    # Compute duration
    started = session.get("started_at", "")
    ended = session.get("ended_at", "")
    duration = 0.0
    if started and ended:
        try:
            start_dt = datetime.fromisoformat(started)
            end_dt = datetime.fromisoformat(ended)
            duration = (end_dt - start_dt).total_seconds()
        except (ValueError, TypeError):
            pass

    # Compute integrity score (0-100)
    integrity_score = _compute_integrity_score(
        total_violations=session.get("total_violations", 0),
        total_frames=session.get("total_frames", 1),
        micro_score=session.get("micro_violation_score", 0.0),
        verification_rate=success_rate,
        avg_engagement=avg_engagement,
    )

    # Strip frame snapshots from violations for JSON (keep them for PDF)
    clean_violations = []
    for v in violations:
        v_copy = dict(v)
        v_copy.pop("frame_snapshot", None)
        clean_violations.append(v_copy)

    report = {
        "session_id": session_id,
        "person_id": session.get("person_id", ""),
        "started_at": started,
        "ended_at": ended,
        "duration_seconds": round(duration, 1),
        "status": session.get("status", "unknown"),
        "total_frames": session.get("total_frames", 0),
        "total_violations": session.get("total_violations", 0),
        "violation_breakdown": violation_breakdown,
        "avg_engagement_score": round(avg_engagement, 1),
        "min_engagement_score": round(min_engagement, 1),
        "max_engagement_score": round(max_engagement, 1),
        "final_micro_violation_score": round(
            session.get("micro_violation_score", 0.0), 2
        ),
        "verification_success_rate": round(success_rate, 1),
        "overall_integrity_score": round(integrity_score, 1),
        "violations": clean_violations,
        "engagement_timeline": engagement_timeline,
    }

    return report


async def generate_pdf_report(session_id: str) -> Optional[Path]:
    """
    Generate a PDF report for a session.

    Returns:
        Path to the generated PDF file, or None if failed.
    """
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
        from reportlab.lib.units import inch, mm
        from reportlab.platypus import (
            SimpleDocTemplate,
            Paragraph,
            Spacer,
            Table,
            TableStyle,
            PageBreak,
        )
    except ImportError:
        logger.error("reportlab not installed. Cannot generate PDF reports.")
        return None

    report_data = await generate_json_report(session_id)
    if not report_data:
        return None

    pdf_path = REPORTS_DIR / f"{session_id}.pdf"
    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=A4,
        rightMargin=20 * mm,
        leftMargin=20 * mm,
        topMargin=20 * mm,
        bottomMargin=20 * mm,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Title"],
        fontSize=20,
        spaceAfter=20,
        textColor=colors.HexColor("#1e293b"),
    )
    heading_style = ParagraphStyle(
        "CustomHeading",
        parent=styles["Heading2"],
        fontSize=14,
        spaceBefore=15,
        spaceAfter=8,
        textColor=colors.HexColor("#4338ca"),
    )
    body_style = styles["Normal"]

    elements = []

    # Title
    elements.append(Paragraph("VerifiHireAI — Proctoring Report", title_style))
    elements.append(Spacer(1, 10))

    # Session Summary Table
    elements.append(Paragraph("Session Summary", heading_style))
    summary_data = [
        ["Session ID", report_data["session_id"]],
        ["Person ID", report_data["person_id"]],
        ["Status", report_data["status"]],
        ["Duration", f"{report_data['duration_seconds']:.0f} seconds"],
        ["Total Frames", str(report_data["total_frames"])],
        ["Total Violations", str(report_data["total_violations"])],
        ["Integrity Score", f"{report_data['overall_integrity_score']:.1f} / 100"],
    ]
    summary_table = Table(summary_data, colWidths=[150, 300])
    summary_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f1f5f9")),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#1e293b")),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ("PADDING", (0, 0), (-1, -1), 8),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 15))

    # Engagement Summary
    elements.append(Paragraph("Engagement Analysis", heading_style))
    eng_data = [
        ["Metric", "Value"],
        ["Average Score", f"{report_data['avg_engagement_score']:.1f}"],
        ["Minimum Score", f"{report_data['min_engagement_score']:.1f}"],
        ["Maximum Score", f"{report_data['max_engagement_score']:.1f}"],
        ["Verification Rate", f"{report_data['verification_success_rate']:.1f}%"],
        ["Micro-Violation Score", f"{report_data['final_micro_violation_score']:.2f}"],
    ]
    eng_table = Table(eng_data, colWidths=[200, 250])
    eng_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4338ca")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ("PADDING", (0, 0), (-1, -1), 8),
    ]))
    elements.append(eng_table)
    elements.append(Spacer(1, 15))

    # Violation Breakdown
    if report_data["violation_breakdown"]:
        elements.append(Paragraph("Violation Breakdown", heading_style))
        vb_data = [["Violation Type", "Count"]]
        for vtype, count in sorted(
            report_data["violation_breakdown"].items(),
            key=lambda x: x[1],
            reverse=True,
        ):
            vb_data.append([vtype.replace("_", " ").title(), str(count)])

        vb_table = Table(vb_data, colWidths=[300, 150])
        vb_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#ef4444")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ("PADDING", (0, 0), (-1, -1), 6),
        ]))
        elements.append(vb_table)
        elements.append(Spacer(1, 15))

    # Violation Timeline (last 50)
    violations = report_data.get("violations", [])[:50]
    if violations:
        elements.append(PageBreak())
        elements.append(Paragraph("Violation Timeline (Recent)", heading_style))
        vt_data = [["#", "Type", "Severity", "Time"]]
        for i, v in enumerate(violations, 1):
            vt_data.append([
                str(i),
                v.get("type", "").replace("_", " ").title(),
                v.get("severity", ""),
                v.get("timestamp", "")[:19],
            ])

        vt_table = Table(vt_data, colWidths=[30, 180, 80, 160])
        vt_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e293b")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ("PADDING", (0, 0), (-1, -1), 4),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [
                colors.white, colors.HexColor("#f8fafc")
            ]),
        ]))
        elements.append(vt_table)

    # Build PDF
    doc.build(elements)
    logger.info(f"PDF report generated: {pdf_path}")

    return pdf_path


def _compute_integrity_score(
    total_violations: int,
    total_frames: int,
    micro_score: float,
    verification_rate: float,
    avg_engagement: float,
) -> float:
    """
    Compute overall integrity score (0-100).

    Higher is better (more integrity).
    """
    if total_frames == 0:
        return 0.0

    # Violation density (lower is better)
    violation_density = total_violations / total_frames
    violation_penalty = min(40.0, violation_density * 500)

    # Micro-violation penalty
    micro_penalty = min(20.0, micro_score)

    # Verification bonus
    verification_bonus = (verification_rate / 100) * 20

    # Engagement bonus
    engagement_bonus = (avg_engagement / 100) * 20

    score = 100.0 - violation_penalty - micro_penalty + verification_bonus + engagement_bonus

    return max(0.0, min(100.0, score))
