import os
from io import BytesIO
from datetime import datetime
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.colors import HexColor, white
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import A4


def _safe_get(obj, key, default="N/A"):
    """Safely extracts values whether obj is a dict, sqlite3.Row, or object."""
    if obj is None:
        return default
    if isinstance(obj, dict):
        return obj.get(key, default)
    try:
        # For sqlite3.Row or objects with key access
        val = obj[key]
        return val if val is not None else default
    except Exception:
        pass
    try:
        # For class instances
        return getattr(obj, key, default)
    except Exception:
        return default


def generate_student_pdf(student, filename_or_prediction=None, confidence=None, recommendation=None):
    """
    Generates a PDF report.
    Compatible with:
      - 4 arguments (Streamlit in-memory download): generate_student_pdf(student, prediction, confidence, recommendation)
      - 2 arguments (Disk export): generate_student_pdf(student, filename)
    """
    is_buffer = False

    # Extract student fields safely
    name = str(_safe_get(student, "student_name", "N/A"))
    s_id = str(_safe_get(student, "student_id", _safe_get(student, "id", "N/A")))
    attendance = str(_safe_get(student, "attendance_percentage", 0))
    study_hours = str(_safe_get(student, "study_hours_per_day", 0))
    assignment = str(_safe_get(student, "assignment_score", 0))
    midterm = str(_safe_get(student, "midterm_score", 0))
    final_exam = str(_safe_get(student, "final_exam_score", 0))
    participation = str(_safe_get(student, "participation_score", 0))
    sleep = str(_safe_get(student, "sleep_hours", 0))

    # Check if second parameter is a disk filename/path or a prediction string
    if isinstance(filename_or_prediction, str) and (
        filename_or_prediction.endswith(".pdf") or "/" in filename_or_prediction or "\\" in filename_or_prediction
    ):
        target = filename_or_prediction
        pred = str(_safe_get(student, "prediction", "N/A"))
        conf = _safe_get(student, "confidence_score", 0.0)
        rec = str(_safe_get(student, "recommendation", "No AI recommendation available."))
    else:
        # In-memory buffer for Streamlit st.download_button
        target = BytesIO()
        is_buffer = True
        pred = str(filename_or_prediction) if filename_or_prediction is not None else str(_safe_get(student, "prediction", "N/A"))
        conf = confidence if confidence is not None else _safe_get(student, "confidence_score", 0.0)
        rec = str(recommendation) if recommendation is not None else str(_safe_get(student, "recommendation", "No AI recommendation available."))

    doc = SimpleDocTemplate(
        target,
        pagesize=A4,
        rightMargin=35,
        leftMargin=35,
        topMargin=40,
        bottomMargin=35,
    )

    styles = getSampleStyleSheet()

    title = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        alignment=TA_CENTER,
        textColor=HexColor("#0d6efd"),
        spaceAfter=8
    )

    subtitle = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Heading2'],
        alignment=TA_CENTER,
        textColor=HexColor("#555555"),
        spaceAfter=15
    )

    heading = ParagraphStyle(
        'DocHeading2',
        parent=styles['Heading2'],
        textColor=HexColor("#0d6efd"),
        spaceBefore=10,
        spaceAfter=10
    )

    normal = ParagraphStyle(
        'DocBodyText',
        parent=styles['BodyText'],
        leading=18,
        spaceAfter=8
    )

    elements = []

    # Title & Header
    elements.append(Paragraph("EduInsight AI", title))
    elements.append(Paragraph(
        "Artificial Intelligence-Based Student Performance Prediction Report",
        subtitle,
    ))
    elements.append(
        Paragraph(
            f"Generated on: {datetime.now().strftime('%d %B %Y %I:%M %p')}",
            normal,
        )
    )
    elements.append(HRFlowable(width="100%", thickness=1, color=HexColor("#0d6efd")))
    elements.append(Spacer(1, 18))

    # 1. Student Information
    elements.append(Paragraph("1. Student Information", heading))
    
    conf_str = f"{conf:.2f}%" if isinstance(conf, (int, float)) else f"{conf}%"

    student_table = Table(
        [
            ["Student Name", name],
            ["Student ID", s_id],
            ["Prediction Result", pred],
            ["Confidence Score", conf_str],
        ],
        colWidths=[2.3 * inch, 4.3 * inch],
    )

    student_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), HexColor("#0d6efd")),
        ("TEXTCOLOR", (0, 0), (0, -1), white),
        ("BACKGROUND", (1, 0), (1, -1), colors.whitesmoke),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
    ]))
    elements.append(student_table)
    elements.append(Spacer(1, 18))

    # 2. Academic Performance
    elements.append(Paragraph("2. Academic Performance", heading))
    performance = Table(
        [
            ["Attendance Percentage", f"{attendance}%"],
            ["Study Hours per Day", f"{study_hours} Hours"],
            ["Assignment Score", assignment],
            ["Midterm Examination", midterm],
            ["Final Examination", final_exam],
            ["Class Participation", participation],
            ["Average Sleep Hours", f"{sleep} Hours"],
        ],
        colWidths=[3.1 * inch, 3.5 * inch],
    )

    performance.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), HexColor("#198754")),
        ("TEXTCOLOR", (0, 0), (-1, 0), white),
        ("BACKGROUND", (0, 1), (-1, -1), HexColor("#f8f9fa")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ]))
    elements.append(performance)
    elements.append(Spacer(1, 18))

    # 3. AI Recommendation
    elements.append(Paragraph("3. AI Recommendation", heading))
    clean_rec = rec.strip()
    if len(clean_rec) > 1500:
        clean_rec = clean_rec[:1500] + "... (continued)"

    for p in clean_rec.split("\n"):
        p_clean = p.strip()
        if p_clean:
            elements.append(Paragraph(p_clean, normal))

    elements.append(Spacer(1, 15))

    # 4. Prediction Summary
    elements.append(Paragraph("4. Prediction Summary", heading))
    summary_table = Table(
        [
            ["Prediction Result", pred],
            ["Confidence Score", conf_str],
            ["Attendance", f"{attendance}%"],
            ["Prediction Model", "Support Vector Machine (SVM)"],
            ["Recommendation Engine", "Groq API (LLaMA 3.1)"],
            ["Generated By", "EduInsight AI Student Performance Prediction System"],
        ],
        colWidths=[2.8 * inch, 3.8 * inch],
    )

    summary_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), HexColor("#ffc107")),
        ("BACKGROUND", (1, 0), (1, -1), colors.whitesmoke),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 18))

    # 5. AI Interpretation
    elements.append(Paragraph("5. AI Interpretation", heading))
    if pred == "High Performance":
        interpretation = (
            "The AI model predicts that the student is likely to achieve excellent "
            "academic performance. Continue maintaining the current study habits."
        )
    elif pred == "Moderate Performance":
        interpretation = (
            "The AI model predicts satisfactory academic performance with room for "
            "improvement through consistent study, participation and attendance."
        )
    else:
        interpretation = (
            "The AI model predicts that the student is currently experiencing academic "
            "challenges based on the analysed learning indicators. Early academic intervention, "
            "improved attendance, stronger study habits and regular teacher support are recommended."
        )
    elements.append(Paragraph(interpretation, normal))
    elements.append(Spacer(1, 18))

    # 6. Report Information
    elements.append(Paragraph("6. Report Information", heading))
    footer = Table(
        [
            ["Generated By", "EduInsight AI Student Performance Prediction System"],
            ["Prediction Model", "Support Vector Machine (SVM)"],
            ["Artificial Intelligence", "Groq API (LLaMA 3.1)"],
            ["Institution", "Universiti Teknikal Malaysia Melaka (UTeM)"],
            ["Faculty", "Faculty of Artificial Intelligence and Cybersecurity (FAIX)"],
            ["Generated Date", datetime.now().strftime("%d %B %Y")],
            ["Generated Time", datetime.now().strftime("%I:%M %p")],
        ],
        colWidths=[2.7 * inch, 3.9 * inch],
    )

    footer.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), HexColor("#0d6efd")),
        ("TEXTCOLOR", (0, 0), (0, -1), white),
        ("BACKGROUND", (1, 0), (1, -1), colors.whitesmoke),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
    ]))
    elements.append(footer)
    elements.append(Spacer(1, 20))

    disclaimer = """
<b>Disclaimer:</b><br/><br/>
This report has been automatically generated by the EduInsight AI Student Performance Prediction System.
Prediction results are produced using a Support Vector Machine (SVM) classification model, while personalised recommendations are generated using the Groq LLaMA 3.1 large language model.
The generated insights are intended to assist teachers in monitoring student academic performance and planning early interventions. Final academic decisions should always be made by qualified educators using their professional judgement.
"""
    elements.append(Paragraph(disclaimer, normal))
    
    doc.build(elements)

    if is_buffer:
        target.seek(0)
        pdf_bytes = target.getvalue()
        target.close()
        return pdf_bytes
    return target

# Aliases
generate_pdf = generate_student_pdf 