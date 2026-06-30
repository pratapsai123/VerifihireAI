"""
Reports Router — Session Report API

Endpoints:
  GET /reports/{session_id}     — Download PDF report
  GET /reports/{session_id}/json — Get report data as JSON
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.services.report_generator import generate_json_report, generate_pdf_report

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/{session_id}/json")
async def get_json_report(session_id: str):
    """Get session report data as JSON."""
    report = await generate_json_report(session_id)
    if not report:
        raise HTTPException(status_code=404, detail="Session not found")
    return report


@router.get("/{session_id}")
async def download_pdf_report(session_id: str):
    """Generate and download PDF report for a session."""
    pdf_path = await generate_pdf_report(session_id)
    if not pdf_path or not pdf_path.exists():
        raise HTTPException(status_code=404, detail="Report generation failed")

    return FileResponse(
        path=str(pdf_path),
        filename=f"proctoring_report_{session_id}.pdf",
        media_type="application/pdf",
    )
