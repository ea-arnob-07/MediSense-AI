from __future__ import annotations

from io import BytesIO
import os
from pathlib import Path
import re
from typing import Any
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import KeepTogether, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.i18n_bn import RISK_BN, URGENCY_BN, bilingual, category_bn, disease_bn, symptom_bn

PURPLE_950 = colors.HexColor("#10091E")
PURPLE_900 = colors.HexColor("#180D2C")
PURPLE_800 = colors.HexColor("#29134A")
PURPLE_600 = colors.HexColor("#7547D6")
PURPLE_400 = colors.HexColor("#B58AFF")
PINK_400 = colors.HexColor("#E781FF")
CYAN_400 = colors.HexColor("#63DFFF")
GREEN_400 = colors.HexColor("#67E8A8")
AMBER_400 = colors.HexColor("#FFD071")
RED_400 = colors.HexColor("#FF758E")
INK = colors.HexColor("#231B2F")
MUTED = colors.HexColor("#665C72")
SOFT = colors.HexColor("#F6F1FC")
LINE = colors.HexColor("#E8DDF5")

FONT_REGULAR = "Helvetica"
FONT_BOLD = "Helvetica-Bold"
PDF_BANGLA_ENABLED = False

_BENGALI_RANGE = r"\u0964\u0965\u0980-\u09FF\u200C\u200D"


def _clean_pdf_text(value: Any) -> str:
    """Return bilingual text when shaping is available, otherwise safe English-only text."""
    text = str(value or "-")
    if PDF_BANGLA_ENABLED:
        return text

    # Remove parenthesized Bangla translations first, then any remaining Bangla glyphs.
    text = re.sub(rf"\s*\([^()]*[{_BENGALI_RANGE}][^()]*\)", "", text)
    text = re.sub(rf"\s*/\s*[{_BENGALI_RANGE}\s]+(?=,|;|$)", "", text)
    text = re.sub(rf"[{_BENGALI_RANGE}]", "", text)
    text = re.sub(r"\(\s*\)", "", text)
    text = re.sub(r"\s*/\s*(?=,|;|$)", "", text)
    text = re.sub(r"\s{2,}", " ", text)
    return text.strip(" /,") or "-"


def _existing_font_pair() -> tuple[Path, Path] | None:
    custom_regular = os.getenv("MEDISENSE_BANGLA_FONT_REGULAR")
    custom_bold = os.getenv("MEDISENSE_BANGLA_FONT_BOLD")
    candidates = [
        (custom_regular, custom_bold or custom_regular),
        (
            "/usr/share/fonts/truetype/noto/NotoSansBengali-Regular.ttf",
            "/usr/share/fonts/truetype/noto/NotoSansBengali-Bold.ttf",
        ),
        (
            "/usr/share/fonts/truetype/noto/NotoSansBengaliUI-Regular.ttf",
            "/usr/share/fonts/truetype/noto/NotoSansBengaliUI-Bold.ttf",
        ),
        (
            "/usr/share/fonts/truetype/lohit-bengali/Lohit-Bengali.ttf",
            "/usr/share/fonts/truetype/lohit-bengali/Lohit-Bengali.ttf",
        ),
        ("C:/Windows/Fonts/Nirmala.ttf", "C:/Windows/Fonts/NirmalaB.ttf"),
        ("C:/Windows/Fonts/vrinda.ttf", "C:/Windows/Fonts/vrindab.ttf"),
    ]
    for regular_value, bold_value in candidates:
        if not regular_value:
            continue
        regular = Path(regular_value)
        bold = Path(bold_value or regular_value)
        if regular.exists():
            return regular, bold if bold.exists() else regular
    return None


def _register_fonts() -> None:
    global FONT_REGULAR, FONT_BOLD, PDF_BANGLA_ENABLED
    font_pair = _existing_font_pair()
    if not font_pair:
        return

    # ReportLab needs uharfbuzz for correct Bengali shaping. Without it, the
    # PDF intentionally falls back to English-only text rather than broken glyphs.
    try:
        import uharfbuzz  # noqa: F401
    except Exception:
        return

    regular, bold = font_pair
    try:
        pdfmetrics.registerFont(TTFont("MediSenseBangla", str(regular), shapable=True))
        pdfmetrics.registerFont(TTFont("MediSenseBanglaBold", str(bold), shapable=True))
        FONT_REGULAR = "MediSenseBangla"
        FONT_BOLD = "MediSenseBanglaBold"
        PDF_BANGLA_ENABLED = True
    except Exception:
        PDF_BANGLA_ENABLED = False


_register_fonts()


def _styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "MediSenseTitle", parent=base["Title"], fontName=FONT_BOLD, fontSize=22,
            leading=27, textColor=PURPLE_900, alignment=TA_LEFT, spaceAfter=2,
        ),
        "subtitle": ParagraphStyle(
            "MediSenseSubtitle", parent=base["Normal"], fontName=FONT_REGULAR, fontSize=9.5,
            leading=14, textColor=MUTED,
        ),
        "section": ParagraphStyle(
            "MediSenseSection", parent=base["Heading2"], fontName=FONT_BOLD, fontSize=12.5,
            leading=16, textColor=PURPLE_800, spaceBefore=5, spaceAfter=7,
        ),
        "normal": ParagraphStyle(
            "MediSenseNormal", parent=base["Normal"], fontName=FONT_REGULAR, fontSize=8.6,
            leading=13, textColor=INK,
        ),
        "small": ParagraphStyle(
            "MediSenseSmall", parent=base["Normal"], fontName=FONT_REGULAR, fontSize=7.4,
            leading=10.5, textColor=MUTED,
        ),
        "small_bold": ParagraphStyle(
            "MediSenseSmallBold", parent=base["Normal"], fontName=FONT_BOLD, fontSize=7.6,
            leading=10.5, textColor=INK,
        ),
        "white": ParagraphStyle(
            "MediSenseWhite", parent=base["Normal"], fontName=FONT_REGULAR, fontSize=8.2,
            leading=11.5, textColor=colors.white,
        ),
        "white_bold": ParagraphStyle(
            "MediSenseWhiteBold", parent=base["Normal"], fontName=FONT_BOLD, fontSize=10.5,
            leading=14, textColor=colors.white,
        ),
        "center": ParagraphStyle(
            "MediSenseCenter", parent=base["Normal"], fontName=FONT_REGULAR, fontSize=8,
            leading=11, alignment=TA_CENTER, textColor=INK,
        ),
        "disclaimer": ParagraphStyle(
            "MediSenseDisclaimer", parent=base["Normal"], fontName=FONT_REGULAR, fontSize=7.3,
            leading=10.4, textColor=MUTED,
        ),
    }


def _p(text: Any, style: ParagraphStyle) -> Paragraph:
    return Paragraph(escape(_clean_pdf_text(text)), style)


def _html(text: str, style: ParagraphStyle) -> Paragraph:
    return Paragraph(_clean_pdf_text(text), style)


def _source_label(field: str, patient: dict[str, Any]) -> str:
    provided = set(patient.get("provided_measurements") or [])
    optional = {
        "respiratory_rate_bpm", "spo2_percent", "systolic_bp",
        "diastolic_bp", "random_glucose_mg_dl",
    }
    if field in optional and field not in provided:
        return " (default normal / স্বাভাবিক ডিফল্ট)"
    return ""


def _patient_rows(patient: dict[str, Any], styles: dict[str, ParagraphStyle]) -> list[list[Paragraph]]:
    feet = patient.get("height_feet")
    inches = patient.get("height_inches")
    cm = patient.get("height_cm")
    height = "-"
    if feet is not None and cm is not None:
        height = f"{feet} ft {float(inches or 0):g} in / {float(cm):.2f} cm"
    elif cm is not None:
        height = f"{float(cm):.2f} cm"

    temp_f = patient.get("temperature_f")
    temp_c = patient.get("temperature_c")
    temperature = f"{float(temp_f):.1f} F / {float(temp_c):.2f} C" if temp_f is not None else f"{float(temp_c):.2f} C"

    items = [
        ("Patient name (রোগীর নাম)", patient.get("patient_name") or "Anonymous / নাম উল্লেখ নেই"),
        ("Age (বয়স)", f"{patient.get('age', '-')} years / বছর"),
        ("Sex (লিঙ্গ)", patient.get("sex", "-")),
        ("Height (উচ্চতা)", height),
        ("Weight (ওজন)", f"{patient.get('weight_kg', '-')} kg"),
        ("BMI (বিএমআই)", patient.get("bmi", "-")),
        ("Temperature (তাপমাত্রা)", temperature),
        ("Heart rate (হৃদস্পন্দন)", f"{patient.get('heart_rate_bpm', '-')} bpm"),
        ("Respiratory rate (শ্বাসের হার)", f"{patient.get('respiratory_rate_bpm', '-')} /min{_source_label('respiratory_rate_bpm', patient)}"),
        ("Oxygen saturation (অক্সিজেন স্যাচুরেশন)", f"{patient.get('spo2_percent', '-')}%{_source_label('spo2_percent', patient)}"),
        ("Blood pressure (রক্তচাপ)", f"{patient.get('systolic_bp', '-')}/{patient.get('diastolic_bp', '-')} mmHg{_source_label('systolic_bp', patient)}"),
        ("Random glucose (র‌্যান্ডম গ্লুকোজ)", f"{patient.get('random_glucose_mg_dl', '-')} mg/dL{_source_label('random_glucose_mg_dl', patient)}"),
        ("Pain score (ব্যথার মাত্রা)", f"{patient.get('pain_score_0_10', '-')} / 10"),
        ("Duration and onset (সময়কাল ও শুরু)", f"{patient.get('symptom_duration_days', '-')} days / দিন, {patient.get('onset_type', '-')}"),
    ]

    rows: list[list[Paragraph]] = []
    for index in range(0, len(items), 2):
        pair = items[index:index + 2]
        row: list[Paragraph] = []
        for label, value in pair:
            row.extend([
                _html(f"<b>{escape(label)}</b>", styles["small_bold"]),
                _p(value, styles["small"]),
            ])
        while len(row) < 4:
            row.extend([_p("", styles["small"]), _p("", styles["small"])] )
        rows.append(row)
    return rows


def _section_title(number: str, title: str, styles: dict[str, ParagraphStyle]) -> Table:
    table = Table([
        [_html(f"<b>{escape(number)}</b>", styles["white_bold"]), _html(f"<b>{escape(title)}</b>", styles["section"])]
    ], colWidths=[11 * mm, 164 * mm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, 0), PURPLE_600),
        ("TEXTCOLOR", (0, 0), (0, 0), colors.white),
        ("ALIGN", (0, 0), (0, 0), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BOX", (0, 0), (0, 0), 0.4, PURPLE_400),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    return table


def _page_decor(canvas, doc) -> None:
    width, height = A4
    canvas.saveState()
    canvas.setFillColor(PURPLE_950)
    canvas.rect(0, height - 31 * mm, width, 31 * mm, fill=1, stroke=0)
    canvas.setFillColor(PURPLE_800)
    canvas.circle(width - 20 * mm, height - 9 * mm, 22 * mm, fill=1, stroke=0)
    canvas.setFillColor(colors.Color(0.71, 0.45, 1, alpha=0.18))
    canvas.circle(width - 47 * mm, height - 33 * mm, 28 * mm, fill=1, stroke=0)

    canvas.setFillColor(PURPLE_400)
    canvas.roundRect(16 * mm, height - 21 * mm, 9 * mm, 9 * mm, 2.2 * mm, fill=1, stroke=0)
    canvas.setFillColor(colors.white)
    canvas.setFont(FONT_BOLD, 14)
    canvas.drawString(30 * mm, height - 14.4 * mm, "MediSense AI")
    canvas.setFont(FONT_REGULAR, 7.5)
    canvas.setFillColor(colors.HexColor("#CBB8E7"))
    canvas.drawString(30 * mm, height - 19.2 * mm, "Intelligent Disease Prediction & Health Risk Analysis")
    canvas.setFont(FONT_BOLD, 7.3)
    canvas.setFillColor(colors.HexColor("#E8D9FF"))
    canvas.drawRightString(width - 16 * mm, height - 15 * mm, "Developed by Estiuk Arafat Arnob")

    canvas.setStrokeColor(LINE)
    canvas.line(16 * mm, 13 * mm, width - 16 * mm, 13 * mm)
    canvas.setFont(FONT_REGULAR, 6.8)
    canvas.setFillColor(MUTED)
    canvas.drawString(16 * mm, 8.2 * mm, "MediSense AI - Educational decision-support report")
    canvas.drawCentredString(width / 2, 8.2 * mm, "Developed by Estiuk Arafat Arnob")
    canvas.drawRightString(width - 16 * mm, 8.2 * mm, f"Page {doc.page}")
    canvas.restoreState()


def create_prediction_pdf(result: dict[str, Any], patient: dict[str, Any]) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4, rightMargin=16 * mm, leftMargin=16 * mm,
        topMargin=37 * mm, bottomMargin=18 * mm,
        title="MediSense AI Health Assessment Report",
        author="Estiuk Arafat Arnob",
        subject="Educational disease prediction and risk analysis",
    )
    styles = _styles()
    story: list[Any] = []

    story.append(_html("<b>Personalized Health Assessment Report</b>", styles["title"]))
    if PDF_BANGLA_ENABLED:
        story.append(_p("ব্যক্তিগত স্বাস্থ্য মূল্যায়ন প্রতিবেদন", styles["subtitle"]))
    meta = f"Report ID: {result['prediction_id']}  |  Generated: {result['generated_at']}  |  Model: {result.get('model_version', '-') }"
    story.extend([_p(meta, styles["small"]), Spacer(1, 5 * mm)])

    story.append(_section_title("01", "Patient profile (রোগীর তথ্য)", styles))
    patient_table = Table(_patient_rows(patient, styles), colWidths=[36 * mm, 51.5 * mm, 36 * mm, 51.5 * mm])
    patient_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.white),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.white, SOFT]),
        ("GRID", (0, 0), (-1, -1), 0.35, LINE),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.extend([patient_table, Spacer(1, 5 * mm)])

    risk = result.get("risk_assessment", {})
    level = str(risk.get("risk_level", "Unknown"))
    risk_bn = RISK_BN.get(level, "অজানা")
    urgency = str(risk.get("urgency", "Review required"))
    urgency_bn = URGENCY_BN.get(urgency, "চিকিৎসকের পরামর্শ নিন")
    risk_color = {"Low": GREEN_400, "Moderate": AMBER_400, "High": RED_400, "Critical": RED_400}.get(level, PURPLE_400)
    risk_box = Table([
        [_html(f"<b>Clinical risk (ক্লিনিক্যাল ঝুঁকি)</b><br/><font size='16'>{escape(level)} ({escape(risk_bn)})</font>", styles["white"]),
         _html(f"<b>Risk score (ঝুঁকি স্কোর): {escape(str(risk.get('risk_score', '-')))}</b><br/>{escape(urgency)} ({escape(urgency_bn)})", styles["white"])]
    ], colWidths=[65 * mm, 110 * mm])
    risk_box.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), PURPLE_900),
        ("LINEBEFORE", (1, 0), (1, 0), 2.5, risk_color),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
        ("ROUNDEDCORNERS", [8]),
    ]))
    story.extend([risk_box, Spacer(1, 5 * mm)])

    story.append(_section_title("02", "Selected symptoms (নির্বাচিত লক্ষণ)", styles))
    symptom_rows = [[
        _html("<b>Symptom (লক্ষণ)</b>", styles["white"]),
        _html("<b>Severity (তীব্রতা)</b>", styles["white"]),
    ]]
    for item in result.get("input_summary", {}).get("active_symptoms", []):
        name = item.get("symptom", "")
        symptom_rows.append([
            _p(bilingual(item.get("display", name.replace("_", " ")), item.get("display_bn") or symptom_bn(name)), styles["small"]),
            _p(f"{item.get('severity', 0)} / 5", styles["center"]),
        ])
    if len(symptom_rows) == 1:
        symptom_rows.append([_p("No active symptoms / কোনো লক্ষণ নির্বাচন করা হয়নি", styles["small"]), _p("-", styles["center"])])
    symptom_table = Table(symptom_rows, colWidths=[145 * mm, 30 * mm], repeatRows=1)
    symptom_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), PURPLE_800),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, SOFT]),
        ("GRID", (0, 0), (-1, -1), 0.35, LINE),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (1, 1), (1, -1), "CENTER"),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.extend([symptom_table, Spacer(1, 5 * mm)])

    story.append(_section_title("03", "Possible conditions (সম্ভাব্য রোগসমূহ)", styles))
    prediction_rows = [[
        _html("<b>Rank</b>", styles["white"]),
        _html("<b>Possible condition (সম্ভাব্য রোগ)</b>", styles["white"]),
        _html("<b>Probability (সম্ভাবনা)</b>", styles["white"]),
        _html("<b>Category (বিভাগ)</b>", styles["white"]),
        _html("<b>Urgency (জরুরিতা)</b>", styles["white"]),
    ]]
    for index, item in enumerate(result.get("predictions", []), 1):
        disease = item.get("disease", "")
        condition = bilingual(item.get("disease_display", disease.replace("_", " ")), item.get("disease_display_bn") or disease_bn(disease))
        category = bilingual(str(item.get("category") or "Other").replace("_", " "), item.get("category_bn") or category_bn(item.get("category")))
        prediction_rows.append([
            _p(index, styles["center"]), _p(condition, styles["small"]),
            _p(f"{float(item.get('probability', 0)):.1%}", styles["center"]),
            _p(category, styles["small"]), _p(str(item.get("base_urgency", "Routine")).replace("_", " "), styles["small"]),
        ])
    prediction_table = Table(prediction_rows, colWidths=[11 * mm, 68 * mm, 26 * mm, 45 * mm, 25 * mm], repeatRows=1)
    prediction_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), PURPLE_800),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, SOFT]),
        ("GRID", (0, 0), (-1, -1), 0.35, LINE),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (0, 1), (0, -1), "CENTER"),
        ("ALIGN", (2, 1), (2, -1), "CENTER"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.extend([prediction_table, Spacer(1, 5 * mm)])

    flags = list(risk.get("red_flags") or []) + list(risk.get("abnormal_vitals") or [])
    if flags:
        warning_data = [[_html(f"<b>{index:02}</b>", styles["white_bold"]), _p(flag, styles["normal"])] for index, flag in enumerate(flags, 1)]
        warning_table = Table(warning_data, colWidths=[13 * mm, 162 * mm])
        warning_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, -1), RED_400),
            ("ROWBACKGROUNDS", (1, 0), (1, -1), [colors.white, colors.HexColor("#FFF3F5")]),
            ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#F3CDD5")),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 7),
            ("RIGHTPADDING", (0, 0), (-1, -1), 7),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))
        story.append(KeepTogether([
            _section_title("04", "Warning signs and measurements (সতর্কতামূলক লক্ষণ ও পরিমাপ)", styles),
            warning_table,
            Spacer(1, 5 * mm),
        ]))

    story.append(_section_title("05", "Care guidance (করণীয় নির্দেশনা)", styles))
    guidance = result.get("care_guidance", {})
    guidance_sections = [
        ("Recommended actions (প্রস্তাবিত করণীয়)", "recommended_actions"),
        ("What to monitor (যা পর্যবেক্ষণ করবেন)", "what_to_monitor"),
        ("A clinician may consider (চিকিৎসক যা বিবেচনা করতে পারেন)", "clinician_may_consider"),
        ("Medication safety (ওষুধের নিরাপত্তা)", "medication_safety"),
    ]
    for heading, key in guidance_sections:
        items = guidance.get(key) or []
        block: list[Any] = [_html(f"<b>{escape(heading)}</b>", styles["normal"]), Spacer(1, 1.2 * mm)]
        for index, item in enumerate(items, 1):
            block.append(_html(f"<font color='#7547D6'><b>{index:02}</b></font>&nbsp;&nbsp;{escape(str(item))}", styles["normal"]))
            block.append(Spacer(1, 0.7 * mm))
        story.append(KeepTogether(block))
        story.append(Spacer(1, 2.2 * mm))

    story.append(Spacer(1, 2 * mm))
    disclaimer = result.get("disclaimer", "Educational decision-support output only. This is not a medical diagnosis.")
    disclaimer_text = "<b>Important limitation (গুরুত্বপূর্ণ সীমাবদ্ধতা)</b><br/>" + escape(disclaimer)
    if PDF_BANGLA_ENABLED:
        disclaimer_text += (
            "<br/><br/>এই প্রতিবেদনটি শুধুমাত্র প্রাথমিক শিক্ষামূলক সহায়তার জন্য। "
            "এটি চিকিৎসকের রোগ নির্ণয়, পরীক্ষা বা চিকিৎসার বিকল্প নয়।"
        )
    disclaimer_box = Table([[
        _html(disclaimer_text, styles["disclaimer"])
    ]], colWidths=[175 * mm])
    disclaimer_box.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8F3FD")),
        ("BOX", (0, 0), (-1, -1), 0.7, colors.HexColor("#DCC8F4")),
        ("LEFTPADDING", (0, 0), (-1, -1), 9),
        ("RIGHTPADDING", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(disclaimer_box)

    doc.build(story, onFirstPage=_page_decor, onLaterPages=_page_decor)
    return buffer.getvalue()
