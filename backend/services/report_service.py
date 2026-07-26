"""
Report Generation Service — Generates executive PDF reports for contract risk analysis.
"""

import os
from datetime import datetime
from pathlib import Path
from sqlalchemy.orm import Session

from backend.config import get_settings
from backend.services.analysis_service import get_risks, get_summary
from backend.utils.exceptions import ContractAnalyzerError
from backend.utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()


def generate_pdf_report(contract_id: str, db: Session) -> Path:
    """
    Generate a professional PDF risk report for a contract.
    Returns the file Path to the generated PDF.
    """
    os.makedirs(settings.REPORTS_DIR, exist_ok=True)
    report_filename = f"Risk_Report_{contract_id}.pdf"
    pdf_path = Path(settings.REPORTS_DIR) / report_filename

    summary = get_summary(contract_id, db=db)
    risks = get_risks(contract_id, db=db)

    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable

        doc = SimpleDocTemplate(
            str(pdf_path),
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36,
        )

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'DocTitle',
            parent=styles['Heading1'],
            fontSize=22,
            leading=26,
            textColor=colors.HexColor('#0F172A'),
            spaceAfter=6,
        )
        heading_style = ParagraphStyle(
            'SectionHeader',
            parent=styles['Heading2'],
            fontSize=14,
            leading=18,
            textColor=colors.HexColor('#1E293B'),
            spaceBefore=12,
            spaceAfter=6,
        )
        body_style = ParagraphStyle(
            'BodyTextCustom',
            parent=styles['Normal'],
            fontSize=10,
            leading=14,
            textColor=colors.HexColor('#334155'),
        )

        story = []

        # Header Title
        story.append(Paragraph("AI Contract Risk Assessment Report", title_style))
        story.append(Paragraph(f"<b>Contract Name:</b> {summary.filename} &nbsp;|&nbsp; <b>ID:</b> {summary.contract_id}", body_style))
        story.append(Paragraph(f"<b>Report Date:</b> {datetime.utcnow().strftime('%B %d, %Y')} &nbsp;|&nbsp; <b>Overall Risk:</b> <font color='{'#DC2626' if summary.overall_risk_level == 'High' else '#D97706' if summary.overall_risk_level == 'Medium' else '#16A34A'}'>{summary.overall_risk_level.value.upper()}</font> (Score: {summary.risk_score}/100)", body_style))
        story.append(Spacer(1, 10))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#CBD5E1'), spaceAfter=15))

        # Executive Summary
        story.append(Paragraph("1. Executive Summary", heading_style))
        story.append(Paragraph(summary.executive_summary, body_style))
        story.append(Spacer(1, 10))

        # Key Concerns
        if summary.key_concerns:
            story.append(Paragraph("2. Top Key Concerns", heading_style))
            for concern in summary.key_concerns:
                story.append(Paragraph(f"• {concern}", body_style))
            story.append(Spacer(1, 10))

        # Clause Risk Matrix Table
        story.append(Paragraph("3. Clause Risk Analysis Matrix", heading_style))
        
        table_data = [["Clause Category", "Status", "Risk Level", "Confidence", "Summary & Recommendation"]]
        for clause in risks.clauses:
            status_text = clause.status.value if hasattr(clause.status, 'value') else str(clause.status)
            risk_text = clause.risk_level.value if hasattr(clause.risk_level, 'value') else str(clause.risk_level)
            conf_text = f"{int(clause.confidence_score * 100)}%"
            summary_p = Paragraph(f"{clause.summary}<br/><font color='#2563EB'><b>Rec:</b> {clause.suggested_improvement or 'None required'}</font>", body_style)
            table_data.append([clause.clause_type, status_text, risk_text, conf_text, summary_p])

        t = Table(table_data, colWidths=[110, 60, 65, 65, 240])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E293B')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
            ('TOPPADDING', (0, 0), (-1, 0), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        story.append(t)
        story.append(Spacer(1, 15))

        # Missing Clauses
        if risks.missing_clauses:
            story.append(Paragraph("4. Recommended Missing Clauses", heading_style))
            for m in risks.missing_clauses:
                story.append(Paragraph(f"<b>• {m.clause_type}:</b> {m.importance} — <i>{m.recommendation}</i>", body_style))

        doc.build(story)
        logger.info(f"Generated PDF report at: {pdf_path}")
        return pdf_path

    except Exception as e:
        logger.error(f"ReportLab PDF generation error: {e}. Writing HTML report fallback.")
        # Fallback HTML file
        html_path = Path(settings.REPORTS_DIR) / f"Risk_Report_{contract_id}.html"
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(f"<h1>Contract Risk Report: {summary.filename}</h1><p>Risk: {summary.overall_risk_level} ({summary.risk_score}/100)</p><p>{summary.executive_summary}</p>")
        return html_path
