"""Generates a professional PDF risk report using ReportLab."""
from __future__ import annotations

import io
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    HRFlowable,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

PRIMARY = colors.HexColor("#0d9488")
DARK = colors.HexColor("#0f172a")
RISK_COLORS = {
    "Low Risk": colors.HexColor("#16a34a"),
    "Moderate Risk": colors.HexColor("#d97706"),
    "High Risk": colors.HexColor("#dc2626"),
}


def build_report(user: dict, prediction: dict) -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4, topMargin=18 * mm, bottomMargin=18 * mm,
        leftMargin=18 * mm, rightMargin=18 * mm, title="NCD Shield AI Report",
    )
    styles = getSampleStyleSheet()
    h1 = ParagraphStyle("h1", parent=styles["Heading1"], textColor=PRIMARY, fontSize=20)
    h2 = ParagraphStyle("h2", parent=styles["Heading2"], textColor=DARK, fontSize=13)
    normal = styles["Normal"]
    small = ParagraphStyle("small", parent=normal, fontSize=8, textColor=colors.grey)

    el: list = []
    el.append(Paragraph("🛡️ NCD Shield AI", h1))
    el.append(Paragraph("AI-Powered Early Screening for Non-Communicable Diseases", small))
    el.append(Spacer(1, 4))
    el.append(HRFlowable(width="100%", color=PRIMARY, thickness=2))
    el.append(Spacer(1, 10))

    # Patient information
    el.append(Paragraph("Patient Information", h2))
    inputs = prediction["inputs"]
    patient_rows = [
        ["Name", user.get("full_name", "—"), "Report Date",
         datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")],
        ["Email", user.get("email", "—"), "Age", str(inputs.get("age", "—"))],
        ["Gender", str(inputs.get("gender", "—")).title(), "BMI", str(prediction["bmi"])],
    ]
    t = Table(patient_rows, colWidths=[28 * mm, 55 * mm, 28 * mm, 55 * mm])
    t.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("TEXTCOLOR", (0, 0), (0, -1), colors.grey),
        ("TEXTCOLOR", (2, 0), (2, -1), colors.grey),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    el.append(t)
    el.append(Spacer(1, 10))

    # Entered data
    el.append(Paragraph("Entered Health Data", h2))
    data_rows = [
        ["Height", f"{inputs.get('height_cm')} cm", "Weight", f"{inputs.get('weight_kg')} kg"],
        ["Blood Pressure", f"{inputs.get('systolic_bp')} mmHg",
         "Blood Sugar", f"{inputs.get('blood_sugar')} mg/dL"],
        ["Cholesterol", f"{inputs.get('cholesterol')} mg/dL",
         "Exercise", f"{inputs.get('exercise_freq')} days/wk"],
        ["Sleep", f"{inputs.get('sleep_hours')} hrs", "Stress",
         str(inputs.get("stress_level", "—")).title()],
        ["Smoking", "Yes" if inputs.get("smoking") else "No",
         "Alcohol", "Yes" if inputs.get("alcohol") else "No"],
        ["Family History", "Yes" if inputs.get("family_history") else "No",
         "Existing Conditions", ", ".join(inputs.get("existing_diseases") or []) or "None"],
    ]
    dt = Table(data_rows, colWidths=[35 * mm, 48 * mm, 35 * mm, 48 * mm])
    dt.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#e2e8f0")),
        ("TEXTCOLOR", (0, 0), (0, -1), colors.grey),
        ("TEXTCOLOR", (2, 0), (2, -1), colors.grey),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    el.append(dt)
    el.append(Spacer(1, 12))

    # Prediction result
    el.append(Paragraph("Screening Result", h2))
    risk_color = RISK_COLORS.get(prediction["risk_level"], DARK)
    result_rows = [
        ["Risk Level", prediction["risk_level"]],
        ["Risk Score", f"{prediction['risk_score']} %"],
        ["Health Score", f"{prediction['health_score']} / 100"],
    ]
    rt = Table(result_rows, colWidths=[50 * mm, 116 * mm])
    rt.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 11),
        ("TEXTCOLOR", (1, 0), (1, 0), risk_color),
        ("FONTNAME", (1, 0), (1, 0), "Helvetica-Bold"),
        ("TEXTCOLOR", (0, 0), (0, -1), colors.grey),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    el.append(rt)
    el.append(Spacer(1, 12))

    # Recommendations
    el.append(Paragraph("Personalized Recommendations", h2))
    for r in prediction["recommendations"]:
        el.append(Paragraph(
            f"<b>[{r['priority'].upper()}] {r['title']}</b> — {r['detail']}", normal))
        el.append(Spacer(1, 3))
    el.append(Spacer(1, 12))

    # Hospital visit suggestion
    el.append(Paragraph("Next Steps", h2))
    if prediction["risk_class"] == 2:
        msg = ("Your screening indicates HIGH risk. We strongly recommend scheduling an "
               "appointment with a physician or visiting a hospital for a full evaluation.")
    elif prediction["risk_class"] == 1:
        msg = ("Your screening indicates MODERATE risk. Consider a routine medical check-up "
               "and monitor your key health indicators.")
    else:
        msg = ("Your screening indicates LOW risk. Maintain your healthy habits and continue "
               "periodic check-ups.")
    el.append(Paragraph(msg, normal))
    el.append(Spacer(1, 14))

    el.append(HRFlowable(width="100%", color=colors.grey, thickness=0.5))
    el.append(Spacer(1, 4))
    el.append(Paragraph(prediction.get("disclaimer", ""), small))

    doc.build(el)
    return buf.getvalue()
