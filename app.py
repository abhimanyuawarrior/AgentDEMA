import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

from agri_platform.pipeline import run_pipeline
from agri_platform.storage import load_layer, save_upload


st.set_page_config(
    page_title="AgriAgent | Agentic Agricultural Data Platform",
    page_icon="🌱",
    layout="wide",
)


st.markdown(
    """
    <style>
        :root {
            --bg-soft: #0b1220;
            --bg-white: #121b2a;
            --bg-panel: rgba(17, 26, 39, 0.92);
            --bg-green: #122c2a;
            --line: rgba(148, 181, 172, 0.12);
            --primary: #39d98a;
            --primary-dark: #1d8a64;
            --text: #edf9f5;
            --muted: #9bb7c1;
            --success: #22c783;
            --soft-blue: #1a2940;
            --soft-gold: #382d16;
        }

        .stApp {
            background: radial-gradient(circle at top, #112833 0%, #0b111c 38%, #070d15 100%);
            color: var(--text);
        }

        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0d1c1d 0%, #0a131a 100%);
            border-right: 1px solid rgba(156, 209, 196, 0.1);
        }

        .sidebar-brand {
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 1.1rem 0.8rem;
            margin-bottom: 1rem;
            border-radius: 22px;
            background: rgba(255,255,255,0.06);
            border: 1px solid rgba(255,255,255,0.08);
        }

        .brand-icon { font-size: 2.8rem; margin-right: 0.8rem; }
        .brand-title {
            font-size: 1.2rem;
            font-weight: 800;
            line-height: 1.1;
            color: #ebfff4;
            letter-spacing: -0.05em;
        }
        .brand-sub { color: #ccefe0; font-size: 0.72rem; margin-top: 0.4rem; }

        .side-menu {
            display: flex;
            flex-direction: column;
            gap: 0.65rem;
            margin-top: 0.5rem;
        }

        .nav-item {
            width: 100%;
            display: flex;
            align-items: center;
            gap: 0.7rem;
            padding: 0.8rem 0.9rem;
            border-radius: 12px;
            color: #ebfff4;
            background: rgba(255,255,255,0.02);
            border: 1px solid transparent;
            font-weight: 700;
        }

        .nav-item.active {
            background: rgba(255,255,255,0.08);
            border-color: rgba(157, 255, 220, 0.24);
        }

        [data-testid="stSidebarNav"] {
            padding-top: 0.3rem;
        }

        [data-testid="stSidebar"] .stButton > button {
            width: 100%;
            justify-content: flex-start;
            border-radius: 12px;
            padding: 0.8rem 0.9rem;
            background: rgba(255,255,255,0.04);
            color: #ebfff4;
            border: 1px solid rgba(255,255,255,0.06);
            font-weight: 700;
            box-shadow: none;
            min-height: 48px;
        }

        [data-testid="stSidebar"] .stButton > button:hover {
            border-color: rgba(160, 255, 215, 0.25);
            background: rgba(255,255,255,0.08);
        }

        [data-testid="stSidebar"] .stButton > button[kind="primary"] {
            background: linear-gradient(180deg, rgba(126, 238, 185, 0.22), rgba(255,255,255,0.06));
            border: 1px solid rgba(159, 255, 214, 0.28);
            color: #f0fff8;
            box-shadow: inset 0 0 0 1px rgba(168, 255, 226, 0.08);
        }

        .main .block-container {
            padding-top: 1rem;
            padding-bottom: 2rem;
            max-width: 1500px;
        }

        .powered-box {
            margin-top: auto;
            padding: 1rem 0.8rem 0.4rem 0.8rem;
            color: #dffcf0;
            text-align: center;
            border-top: 1px solid rgba(255,255,255,0.08);
            font-size: 0.78rem;
        }

        .topbar {
            display: flex;
            justify-content: flex-end;
            align-items: center;
            padding: 0.2rem 0.3rem 1rem 0.3rem;
            gap: 0.75rem;
        }

        .status-pill {
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.45rem 0.9rem;
            border-radius: 999px;
            background: rgba(241, 253, 249, 0.7);
            border: 1px solid rgba(31, 191, 133, 0.2);
            color: #165d4d;
            font-weight: 700;
            font-size: 0.8rem;
        }
        .status-dot {
            width: 9px;
            height: 9px;
            border-radius: 50%;
            background: #2fc784;
            box-shadow: 0 0 12px rgba(47,199,132,0.7);
        }
        .avatar {
            width: 30px;
            height: 30px;
            border-radius: 50%;
            background: linear-gradient(180deg, #effaf6, #cfe9dd);
            color: #0d3a37;
            font-weight: 800;
            display: flex;
            align-items: center;
            justify-content: center;
            border: 2px solid rgba(17, 123, 92, 0.2);
        }

        .hero-banner {
            position: relative;
            overflow: hidden;
            border-radius: 28px;
            min-height: 170px;
            background: linear-gradient(90deg, rgba(8, 19, 28, 0.78), rgba(9, 27, 29, 0.55)), url('https://images.unsplash.com/photo-1501004318641-b39e6451bec6?auto=format&fit=crop&w=1400&q=80') center/cover no-repeat;
            border: 1px solid rgba(134, 214, 181, 0.16);
            box-shadow: 0 16px 30px rgba(12, 56, 42, 0.18);
            padding: 1.4rem 1.6rem;
            display: flex;
            align-items: center;
        }
        .hero-badge {
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            font-size: 0.8rem;
            font-weight: 700;
            color: #dffcf2;
            background: rgba(95, 228, 176, 0.12);
            border: 1px solid rgba(121, 228, 176, 0.18);
            border-radius: 999px;
            padding: 0.4rem 0.8rem;
            margin-bottom: 0.6rem;
        }
        .hero-tag { color: #7ef0bc; }
        .hero-title {
            font-size: clamp(2rem, 3vw, 3.5rem);
            font-weight: 900;
            letter-spacing: -0.06em;
            color: #f2fff9;
            margin: 0;
            text-shadow: 0 2px 12px rgba(0,0,0,0.28);
        }
        .hero-sub {
            color: #d8f7ed;
            font-size: 1.1rem;
            margin-top: 0.5rem;
            font-weight: 600;
        }

        .stat-card {
            border-radius: 18px;
            padding: 1rem 1rem 0.8rem;
            min-height: 110px;
            border: 1px solid var(--line);
            background: rgba(18, 29, 37, 0.96);
            box-shadow: 0 8px 18px rgba(6, 14, 20, 0.26);
        }
        .stat-card.green { background: linear-gradient(135deg, rgba(18, 44, 42, 0.96), rgba(10, 22, 24, 0.96)); }
        .stat-card.blue { background: linear-gradient(135deg, rgba(19, 29, 51, 0.96), rgba(11, 20, 31, 0.96)); }
        .stat-card.purple { background: linear-gradient(135deg, rgba(33, 27, 49, 0.96), rgba(16, 15, 29, 0.96)); }
        .stat-card.gold { background: linear-gradient(135deg, rgba(48, 35, 14, 0.96), rgba(28, 21, 10, 0.96)); }
        .stat-top {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 0.6rem;
        }
        .stat-value {
            font-size: clamp(2rem, 2vw, 2.5rem);
            font-weight: 800;
            letter-spacing: -0.06em;
            color: #ebfff8;
        }
        .stat-icon { font-size: 1.7rem; }
        .stat-label {
            margin-top: 0.5rem;
            color: #b6d0d9;
            font-size: 0.96rem;
            font-weight: 700;
        }

        .panel {
            background: rgba(17, 27, 39, 0.92);
            border-radius: 22px;
            border: 1px solid var(--line);
            padding: 1rem 1.1rem;
            box-shadow: 0 12px 24px rgba(5, 9, 14, 0.26);
        }
        .panel-head {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 0.8rem;
            margin-bottom: 0.6rem;
        }
        .panel-title {
            font-size: clamp(1.4rem, 1.5vw, 2rem);
            font-weight: 800;
            letter-spacing: -0.05em;
            color: #edf9f7;
        }
        .ai-pill {
            background: rgba(57, 217, 138, 0.12);
            border: 1px solid rgba(30, 180, 123, 0.2);
            color: #a8f7d5;
            font-size: 0.76rem;
            padding: 0.4rem 0.7rem;
            border-radius: 999px;
            font-weight: 700;
        }
        .location-panel {
            background: linear-gradient(180deg, rgba(18, 37, 33, 0.96), rgba(14, 22, 28, 0.96));
        }
        .location-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 0.8rem;
            margin-bottom: 0.9rem;
        }
        .location-stats {
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 0.7rem;
            margin-top: 0.8rem;
        }
        .mini-stat {
            background: rgba(255,255,255,0.03);
            border: 1px solid rgba(155, 201, 184, 0.12);
            border-radius: 14px;
            padding: 0.75rem 0.7rem;
        }
        .mini-stat .label {
            color: #a8c4cf;
            font-size: 0.7rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            font-weight: 800;
        }
        .mini-stat .value {
            margin-top: 0.35rem;
            color: #ebfff8;
            font-size: 1.8rem;
            font-weight: 800;
            letter-spacing: -0.05em;
        }

        @media (max-width: 1100px) {
            .stat-card { min-height: 90px; }
        }
    </style>
    """,
    unsafe_allow_html=True,
)


if "active_nav" not in st.session_state:
    st.session_state.active_nav = "Home"
if "district_filter" not in st.session_state:
    st.session_state.district_filter = "Pune"
if "season_filter" not in st.session_state:
    st.session_state.season_filter = "Kharif"


with st.sidebar:
    st.markdown(
        """
        <div class="sidebar-brand">
            <div class="brand-icon">🌾</div>
            <div>
                <div class="brand-title">Agentic</div>
                <div class="brand-title">Agricultural</div>
                <div class="brand-title">Data Platform</div>
                <div class="brand-sub">Smarter Farming.</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    nav_items = [
        ("Home", "🏠"),
        ("Crop Suitability", "🌿"),
        ("Reports", "🧾"),
        ("Live Agriculture Intelligence APIs", "🌍"),
        ("About", "ℹ️"),
    ]

    st.markdown('<div class="side-menu">', unsafe_allow_html=True)
    for label, icon in nav_items:
        is_active = label == st.session_state.active_nav
        button = st.button(
            f"{icon} {label}",
            key=f"nav_{label}",
            use_container_width=True,
            type="primary" if is_active else "secondary",
        )
        if button:
            st.session_state.active_nav = label
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(
        """
        <div class="powered-box">
            <div>⚡ Powered by AI Agents</div>
            <div style="margin-top: 0.3rem;">for Sustainable Agriculture</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def get_default_data_path():
    return Path(__file__).parent / "data" / "Indian_crop_production_yield_dataset.csv"


def get_district_options(data_path=None):
    path = data_path or get_default_data_path()
    if not path.exists():
        return ["Pune", "Nagpur", "Belagavi", "Shimoga", "Ludhiana"]
    df = pd.read_csv(path)
    districts = sorted(df["District_Name"].dropna().astype(str).str.strip().unique().tolist())
    return districts or ["Pune", "Nagpur", "Belagavi", "Shimoga", "Ludhiana"]


def get_season_options(data_path=None):
    path = data_path or get_default_data_path()
    if not path.exists():
        return ["Kharif", "Rabi", "Summer"]
    df = pd.read_csv(path)
    seasons = sorted(df["Season"].dropna().astype(str).str.strip().unique().tolist())
    return seasons or ["Kharif", "Rabi", "Summer"]


def compute_crop_suitability(district, season, data_path=None):
    path = data_path or get_default_data_path()
    if not path.exists():
        return [("Rice", 92), ("Maize", 88), ("Soybean", 84), ("Groundnut", 80), ("Cotton", 75)]

    df = pd.read_csv(path)
    district_df = df[df["District_Name"].astype(str).str.strip().str.lower() == district.strip().lower()].copy()
    if season:
        district_df = district_df[district_df["Season"].astype(str).str.strip().str.lower() == season.strip().lower()]
    if district_df.empty:
        district_df = df[df["District_Name"].astype(str).str.strip().str.lower() == district.strip().lower()].copy()
    if district_df.empty:
        return [("Rice", 92), ("Maize", 88), ("Soybean", 84), ("Groundnut", 80), ("Cotton", 75)]

    summary = district_df.groupby("Crop", as_index=False)["yield"].mean().sort_values("yield", ascending=False).head(5)
    if summary.empty:
        return [("Rice", 92), ("Maize", 88), ("Soybean", 84), ("Groundnut", 80), ("Cotton", 75)]

    max_yield = float(summary["yield"].max()) if not summary.empty else 1.0
    results = []
    for _, row in summary.iterrows():
        score = max(60.0, min(99.0, round((float(row["yield"]) / max_yield) * 100.0, 1)))
        results.append((str(row["Crop"]), score))
    return results


def generate_ai_recommendation(district, season, top_crop):
    try:
        from agri_platform.services import generate_text

        prompt = (
            f"Provide a concise agronomy recommendation for {district} during {season}. "
            f"The best supported crop is {top_crop}. Include ideal soil pH, rainfall pattern, and practical field actions in 3 bullet points in plain text."
        )
        answer = generate_text(prompt, system_instruction="You are an expert agriculture advisor for Indian farmers.")
        return answer["text"].strip()
    except Exception:
        return (
            f"For {district} in the {season} season, {top_crop} is the most suitable option. Maintain soil pH in the 6.2-7.0 range, "
            "target moderate rainfall and avoid waterlogging, and use balanced nutrient management with timely weeding and irrigation."
        )


def soil_profile_for_district(district):
    profiles = {
        "Pune": {"soil_ph": 6.8, "rainfall": 672, "temperature": 28},
        "Nagpur": {"soil_ph": 6.6, "rainfall": 910, "temperature": 29},
        "Belagavi": {"soil_ph": 6.9, "rainfall": 1240, "temperature": 27},
        "Shimoga": {"soil_ph": 6.7, "rainfall": 1500, "temperature": 26},
        "Ludhiana": {"soil_ph": 7.2, "rainfall": 620, "temperature": 30},
    }
    return profiles.get(district, {"soil_ph": 6.8, "rainfall": 800, "temperature": 28})


def build_dashboard_pdf():
    from io import BytesIO
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.graphics.charts.barcharts import VerticalBarChart
    from reportlab.graphics.shapes import Drawing
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=0.75 * inch, leftMargin=0.75 * inch, topMargin=0.6 * inch, bottomMargin=0.6 * inch)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("TitleStyle", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=18, leading=22, textColor=colors.HexColor("#0B4F46"))
    section_style = ParagraphStyle("SectionStyle", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=12, leading=14, textColor=colors.HexColor("#174A43"))
    normal_style = ParagraphStyle("BodyText", parent=styles["BodyText"], fontName="Helvetica", fontSize=9, leading=12)

    data_path = get_default_data_path()
    df = pd.read_csv(data_path) if data_path.exists() else pd.DataFrame()
    rows = len(df)
    districts = df["District_Name"].nunique() if not df.empty else 0
    crops = df["Crop"].nunique() if not df.empty else 0
    seasons = df["Season"].nunique() if not df.empty else 0
    summary = df.groupby("Crop")["yield"].mean().sort_values(ascending=False).head(5) if not df.empty else pd.Series({"Rice": 92, "Maize": 88})

    story = [Paragraph("Agricultural Dashboard Report", title_style), Spacer(1, 0.2 * inch)]
    story.append(Paragraph("Operational analytics based on the default agricultural dataset.", normal_style))
    story.append(Spacer(1, 0.2 * inch))
    stat_table = Table([
        ["Total rows", f"{rows:,}"],
        ["Districts", f"{districts}"],
        ["Crop types", f"{crops}"],
        ["Seasons", f"{seasons}"],
    ], colWidths=[2.7 * inch, 2.3 * inch])
    stat_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#EAF8F4")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#91D0BF")),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#0A4A41")),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
    ]))
    story.append(stat_table)
    story.append(Spacer(1, 0.3 * inch))
    story.append(Paragraph("Top crop yield summary", section_style))
    chart_data = [list(summary.values)]
    chart = VerticalBarChart()
    chart.x = 50
    chart.y = 40
    chart.height = 150
    chart.width = 430
    chart.data = chart_data
    chart.categoryAxis.categoryNames = [str(c) for c in summary.index]
    chart.valueAxis.valueMin = 0
    chart.valueAxis.valueMax = max(100, int(summary.max()) + 10)
    chart.bars.strokeColor = colors.HexColor("#2FBF9F")
    chart.bars.fillColor = colors.HexColor("#7AE0C0")
    d = Drawing(500, 220)
    d.add(chart)
    story.append(d)
    story.append(Spacer(1, 0.2 * inch))
    story.append(Paragraph("This dashboard captures yield performance, crop diversity, and district-season distribution across the agricultural dataset.", normal_style))
    doc.build(story)
    return buffer.getvalue()


def build_gold_report_pdf():
    from io import BytesIO
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=0.75 * inch, leftMargin=0.75 * inch, topMargin=0.6 * inch, bottomMargin=0.6 * inch)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("TitleStyle", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=18, leading=22, textColor=colors.HexColor("#0B4F46"))
    normal_style = ParagraphStyle("BodyText", parent=styles["BodyText"], fontName="Helvetica", fontSize=9, leading=12)

    gold = load_layer("gold")
    story = [Paragraph("Gold Layer Data Export", title_style), Spacer(1, 0.2 * inch)]
    story.append(Paragraph("Engineered agricultural dataset with derived feature columns for downstream analytics and decision support.", normal_style))
    story.append(Spacer(1, 0.2 * inch))
    preview = gold.head(12).copy() if not gold.empty else pd.read_csv(get_default_data_path()).head(25)
    if preview.empty:
        preview = pd.DataFrame({"District_Name": ["Pune"], "Season": ["Kharif"], "Crop": ["Rice"], "yield": [92.2]})
    table_data = [[str(c) for c in preview.columns]]
    for _, row in preview.iterrows():
        table_data.append([str(item) for item in row.tolist()])
    table = Table(table_data, colWidths=[1.1 * inch, 1.0 * inch, 0.9 * inch, 1.1 * inch])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#DAF5ED")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#89C9B6")),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(table)
    story.append(Spacer(1, 0.2 * inch))
    story.append(Paragraph("This gold layer contains cleaned and feature-engineered agriculture data ready for model scoring and reporting workflows.", normal_style))
    doc.build(story)
    return buffer.getvalue()


def build_crop_suitability_report_pdf(district=None, season=None):
    from io import BytesIO
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

    district = district or st.session_state.get("district_filter", "Pune")
    season = season or st.session_state.get("season_filter", "Kharif")
    results = compute_crop_suitability(district, season)
    top_crop = results[0][0] if results else "Rice"
    profile = soil_profile_for_district(district)
    recommendation = generate_ai_recommendation(district, season, top_crop)

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=0.75 * inch, leftMargin=0.75 * inch, topMargin=0.6 * inch, bottomMargin=0.6 * inch)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("TitleStyle", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=18, leading=22, textColor=colors.HexColor("#0B4F46"))
    section_style = ParagraphStyle("SectionStyle", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=12, leading=14, textColor=colors.HexColor("#114B44"))
    normal_style = ParagraphStyle("BodyText", parent=styles["BodyText"], fontName="Helvetica", fontSize=9, leading=12)

    story = [Paragraph("Crop Suitability Report", title_style), Spacer(1, 0.2 * inch)]
    story.append(Paragraph(f"District: {district} | Season: {season}", normal_style))
    story.append(Spacer(1, 0.15 * inch))
    metric_table = Table([
        ["Metric", "Value"],
        ["Recommended crop", top_crop],
        ["Soil pH", f"{profile['soil_ph']:.1f} (ideal)"],
        ["Rainfall", f"{profile['rainfall']} mm"],
        ["Temperature", f"{profile['temperature']}°C"],
    ], colWidths=[2.2 * inch, 2.5 * inch])
    metric_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#DDF6EE")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#8BC9B5")),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
    ]))
    story.append(metric_table)
    story.append(Spacer(1, 0.25 * inch))
    story.append(Paragraph("Suitability ranking", section_style))
    rank_rows = [["Rank", "Crop", "Suitability %"]]
    for idx, (crop, score) in enumerate(results, start=1):
        rank_rows.append([str(idx), crop, f"{score}%"])
    rank_table = Table(rank_rows, colWidths=[0.8 * inch, 2.0 * inch, 1.8 * inch])
    rank_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EEF9F5")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#8BC9B5")),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
    ]))
    story.append(rank_table)
    story.append(Spacer(1, 0.25 * inch))
    story.append(Paragraph("AI recommendation", section_style))
    story.append(Paragraph(recommendation, normal_style))
    doc.build(story)
    return buffer.getvalue()


def get_dashboard_dataset():
    result = st.session_state.get("pipeline_result")
    if result and isinstance(result.get("gold"), pd.DataFrame):
        return result["gold"].copy()
    gold = load_layer("gold")
    if not gold.empty:
        return gold.copy()
    default_path = get_default_data_path()
    if default_path.exists():
        return pd.read_csv(default_path)
    return pd.DataFrame()


def render_dashboard_home():
    st.markdown(
        """
        <div class="topbar">
            <div class="status-pill"><span class="status-dot"></span> Online</div>
            <div class="avatar">S</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="hero-banner">
            <div>
                <div class="hero-badge"><span class="hero-tag">●</span> Agentic AI</div>
                <h1 class="hero-title">Agentic Agricultural Data Platform</h1>
                <div class="hero-sub">Analyze • Predict • Get Smart Recommendations</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<div style='margin-top:1.2rem;'></div>", unsafe_allow_html=True)
    df = get_dashboard_dataset()

    if df.empty:
        st.warning("No cleaned dataset is available yet. Run the data pipeline to populate the gold layer.")
        return

    yield_col = next((c for c in df.columns if str(c).lower() == "yield"), None) or next((c for c in df.columns if "yield" in str(c).lower()), None)
    crop_col = next((c for c in df.columns if str(c).lower() == "crop"), None)
    season_col = next((c for c in df.columns if str(c).lower() == "season"), None)
    rainfall_col = next((c for c in df.columns if str(c).lower() in {"annual_rainfall", "rainfall"}), None)
    state_col = next((c for c in df.columns if str(c).lower() in {"state", "state_name"}), None)

    avg_yield = float(df[yield_col].mean()) if yield_col else 0
    total_rows = len(df)
    crop_count = df[crop_col].nunique() if crop_col else 0
    state_count = df[state_col].nunique() if state_col else 0
    quality_score = round(100 - (df.isna().sum().sum() / max(1, df.size)) * 100, 1)

    stats = [
        (f"{total_rows:,}", "Clean records", "green"),
        (f"{crop_count}", "Crop types", "blue"),
        (f"{state_count}", "States covered", "purple"),
        (f"{quality_score:.0f}%", "Data quality", "gold"),
    ]
    cols = st.columns(4)
    for i, (value, label, cls) in enumerate(stats):
        with cols[i]:
            st.markdown(
                f"""
                <div class="stat-card {cls}">
                    <div class="stat-top">
                        <div class="stat-value">{value}</div>
                        <div class="stat-icon">{'🗃️' if i == 0 else '🌾' if i == 1 else '📍' if i == 2 else '📊'}</div>
                    </div>
                    <div class="stat-label">{label}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("<div style='margin-top:1.4rem;'></div>", unsafe_allow_html=True)
    upload_col, meta_col = st.columns([2.0, 1.0])
    with upload_col:
        st.markdown(
            """
            <div class="panel">
                <div class="panel-head">
                    <div class="panel-title">Data Pipeline</div>
                    <div class="ai-pill">● Agentic</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        uploaded_file = st.file_uploader("Upload agriculture data", type=["csv", "json", "xlsx", "xls"], label_visibility="collapsed")
        if uploaded_file is not None:
            st.success(f"Selected file: {uploaded_file.name}")
        if st.button("Run Agentic Pipeline", type="primary", use_container_width=True):
            if uploaded_file is None:
                default_path = get_default_data_path()
                if default_path.exists():
                    with st.spinner("Processing default Indian crop dataset..."):
                        result = run_pipeline(str(default_path), auto_repair=True)
                    st.session_state["pipeline_result"] = result
                    st.success("Default crop dataset processed successfully.")
                else:
                    st.warning("Upload a CSV / Excel / JSON file to run the pipeline.")
            else:
                saved_path = save_upload(uploaded_file)
                with st.spinner("Processing uploaded data..."):
                    result = run_pipeline(saved_path, auto_repair=True)
                st.session_state["pipeline_result"] = result
                st.success("Pipeline completed successfully.")

    with meta_col:
        st.markdown(
            """
            <div class="panel" style="padding:1rem;">
                <div style="font-size:0.8rem; letter-spacing:0.08em; text-transform:uppercase; color:#bce5f5; font-weight:800;">Recommended Columns</div>
                <ul style="margin:0.7rem 0 0 1rem; color:#dfeef8; line-height:1.7; font-weight:600;">
                    <li>Soil pH</li>
                    <li>Nitrogen</li>
                    <li>Phosphorus</li>
                    <li>Potassium</li>
                    <li>Temperature</li>
                    <li>Humidity</li>
                    <li>Rainfall</li>
                    <li>Crop</li>
                    <li>Yield</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

    result = st.session_state.get("pipeline_result")
    if result:
        profile = result["profile"]
        df_clean = result["silver"]
        gold = result["gold"]
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Rows", f"{profile['rows']:,}")
        c2.metric("Columns", profile["columns"])
        c3.metric("Missing cells", profile["missing_cells"])
        c4.metric("Quality score", f"{result['quality']['score']:.1f}/100")

        tabs = st.tabs(["Overview", "Profiling", "Schema mapping", "Quality & ETL", "EDA"])
        with tabs[0]:
            a, b, c = st.columns(3)
            a.metric("Bronze", "Stored", "Raw data preserved")
            b.metric("Silver", "Ready", f"{len(df_clean):,} cleaned rows")
            c.metric("Gold", "Ready", f"{len(gold):,} engineered rows")
            st.dataframe(df_clean.head(20), use_container_width=True)
        with tabs[1]:
            st.json(profile)
        with tabs[2]:
            st.dataframe(result["mapping"], use_container_width=True)
        with tabs[3]:
            st.dataframe(pd.DataFrame(result["quality"]["checks"]), use_container_width=True)
        with tabs[4]:
            from agri_platform.services import generate_eda_summary

            numeric = df_clean.select_dtypes(include="number").columns.tolist()
            if numeric:
                selected = st.selectbox("Choose a numeric column", numeric)
                summary_df = df_clean[numeric].describe().T
                st.dataframe(summary_df, use_container_width=True)
                st.plotly_chart(px.histogram(df_clean, x=selected, marginal="box", title=f"Distribution of {selected}"), use_container_width=True)

                if len(numeric) > 1:
                    corr = df_clean[numeric].corr().round(2)
                    st.plotly_chart(px.imshow(corr, text_auto=True, aspect="auto", color_continuous_scale="RdYlGn", title="Correlation matrix"), use_container_width=True)

                insight = generate_eda_summary(df_clean)
                st.markdown("### EDA insight")
                st.markdown(insight.replace("\n", "<br>"), unsafe_allow_html=True)
            else:
                st.info("No numeric columns available for EDA.")


def render_crop_suitability_page():
    district_options = get_district_options()
    season_options = get_season_options()

    selected_district = st.session_state.get("district_filter", "Pune")
    selected_season = st.session_state.get("season_filter", "Kharif")
    district = st.selectbox("District", district_options, index=district_options.index(selected_district) if selected_district in district_options else 0)
    season = st.selectbox("Season", season_options, index=season_options.index(selected_season) if selected_season in season_options else 0)
    st.session_state.district_filter = district
    st.session_state.season_filter = season

    results = compute_crop_suitability(district, season)
    top_crop = results[0][0] if results else "Rice"
    profile = soil_profile_for_district(district)
    recommendation = generate_ai_recommendation(district, season, top_crop)

    left_col, right_col = st.columns([1.7, 1])
    with left_col:
        st.markdown(
            """
            <div class="panel" style="padding: 1rem 1.1rem;">
                <div class="panel-head">
                    <div class="panel-title">Crop Suitability Checker</div>
                    <div class="ai-pill">● AI Powered</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(f"<div style='font-size:1.5rem; font-weight:800; margin-top:1rem; color:#edf9f5;'>Top suitable crops for {district} ({season})</div>", unsafe_allow_html=True)
        for idx, (crop, score) in enumerate(results, start=1):
            st.markdown(
                f"""
                <div style="display:grid; grid-template-columns:32px 1fr 60px; gap:0.7rem; align-items:center; margin-top:1rem;">
                    <div style="width:32px; height:32px; border-radius:12px; background:linear-gradient(180deg, rgba(27,108,89,0.9), rgba(5,60,71,0.7)); color:#ecfff8; font-weight:800; display:flex; align-items:center; justify-content:center;">{idx}</div>
                    <div>
                        <div style="font-weight:700; color:#e7f7ff; font-size:1.04rem;">{crop}</div>
                        <div style="width:100%; height:10px; background:rgba(255,255,255,0.12); border-radius:999px; overflow:hidden; margin-top:0.35rem;">
                            <div style="height:100%; width:{score}%; border-radius:999px; background:linear-gradient(90deg, #36d399, #4db9ff);"></div>
                        </div>
                    </div>
                    <div style="text-align:right; color:#d7fff0; font-weight:800;">{score}%</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        st.success(f"{top_crop} is the most suitable crop for {district} in the {season} season.")

    with right_col:
        st.markdown(
            f"""
            <div class="panel location-panel">
                <div class="location-header">
                    <div class="panel-title" style="font-size:1.5rem;">Quick Insights</div>
                </div>
                <div class="location-stats">
                    <div class="mini-stat"><div class="label">Current weather</div><div class="value">{profile['temperature']}°C</div></div>
                    <div class="mini-stat"><div class="label">Rainfall</div><div class="value">{profile['rainfall']} mm</div></div>
                    <div class="mini-stat"><div class="label">Soil pH</div><div class="value">{profile['soil_ph']:.1f}</div></div>
                    <div class="mini-stat"><div class="label">Soil condition</div><div class="value">Ideal</div></div>
                </div>
                <div style="margin-top:1rem; background:rgba(142, 228, 182, 0.08); border:1px solid rgba(142, 228, 182, 0.18); border-radius:14px; padding:0.9rem; color:#eafef6; font-weight:600; line-height:1.5;">
                    {recommendation}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_reports_page():
    st.header("Reports")
    st.caption("Download structured PDF reports for dashboard analytics, gold-layer outputs, and crop suitability guidance.")

    dashboard_pdf = build_dashboard_pdf()
    gold_pdf = build_gold_report_pdf()
    crop_pdf = build_crop_suitability_report_pdf()

    report_cols = st.columns(3)
    with report_cols[0]:
        st.markdown(
            """
            <div class="panel">
                <div class="panel-title" style="font-size:1.3rem; color:#edf9f5;">Dashboard report</div>
                <div style="margin-top:0.6rem; color:#b6d5dc;">Upload analytics with crop performance charts and summary insights.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.download_button("Download Dashboard PDF", data=dashboard_pdf, file_name="dashboard_report.pdf", mime="application/pdf")
    with report_cols[1]:
        st.markdown(
            """
            <div class="panel">
                <div class="panel-title" style="font-size:1.3rem; color:#edf9f5;">Gold layer data</div>
                <div style="margin-top:0.6rem; color:#b6d5dc;">Feature-engineered and cleaned data export for downstream analysis.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.download_button("Download Gold Layer PDF", data=gold_pdf, file_name="gold_layer_report.pdf", mime="application/pdf")
    with report_cols[2]:
        st.markdown(
            """
            <div class="panel">
                <div class="panel-title" style="font-size:1.3rem; color:#edf9f5;">Crop suitability report</div>
                <div style="margin-top:0.6rem; color:#b6d5dc;">District and season-specific crop recommendations with soil and rainfall evaluation.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.download_button("Download Crop Suitability PDF", data=crop_pdf, file_name="crop_suitability_report.pdf", mime="application/pdf")


def render_api_page():
    from agri_platform.services import llm_status, generate_text, geocode_place, get_weather, get_soil

    st.header("🌍 Live Agriculture Intelligence APIs")
    st.caption("Gemini → Groq fallback • Open-Meteo weather • SoilGrids soil profile")
    status = llm_status()
    # s1, s2, s3, s4 = st.columns(4)
    # s1.metric("Gemini (Primary)", "Configured" if status["Gemini configured"] else "API key missing")
    # s2.metric("Groq (Backup)", "Configured" if status["Groq configured"] else "API key missing")
    # s3.metric("Open-Meteo", "No key required")
    # s4.metric("SoilGrids", "No key required")

    api_tab1, api_tab2 = st.tabs(["Location weather & soil", "Test AI assistant"])
    with api_tab1:
        place = st.text_input("Enter village / city / district", value="Kalyan, Maharashtra")
        days = st.slider("Weather forecast days", 1, 16, 7)
        if st.button("Fetch weather + soil data", type="primary"):
            try:
                with st.spinner("Finding location and fetching live datasets..."):
                    location = geocode_place(place)
                    st.session_state["agri_location"] = location
                    weather = get_weather(location["latitude"], location["longitude"], days)
                    st.session_state["agri_weather"] = weather
                    st.success(f"Weather fetched for {location['name']}, {location.get('admin1') or ''}, {location.get('country') or ''}")
                    st.json(weather.get("current", {}))
                    daily = weather.get("daily", {})
                    if daily.get("time"):
                        weather_df = pd.DataFrame(daily)
                        st.subheader("Forecast")
                        st.dataframe(weather_df, use_container_width=True)
                        st.download_button("Download weather forecast CSV", weather_df.to_csv(index=False).encode(), "open_meteo_forecast.csv", "text/csv")
                try:
                    with st.spinner("Querying SoilGrids..."):
                        soil = get_soil(location["latitude"], location["longitude"])
                        st.session_state["agri_soil"] = soil
                        st.subheader("SoilGrids topsoil profile (0–5 cm)")
                        st.json(soil)
                except Exception as soil_error:
                    st.warning("SoilGrids response unavailable right now. Details: " + str(soil_error)[:250])
            except Exception as exc:
                st.error(f"Could not fetch location/weather data: {exc}")
        elif st.session_state.get("agri_location"):
            loc = st.session_state["agri_location"]
            st.caption(f"Last selected location: {loc['name']} ({loc['latitude']:.4f}, {loc['longitude']:.4f})")
            if st.session_state.get("agri_weather"):
                st.json(st.session_state["agri_weather"].get("current", {}))
            if st.session_state.get("agri_soil"):
                st.json(st.session_state["agri_soil"])

    with api_tab2:
        prompt = st.text_area("Ask an agriculture question", placeholder="Example: Explain how rainfall, temperature and soil pH affect crop selection in this region.")
        if st.button("Ask Gemini / Groq", disabled=not bool(prompt.strip())):
            try:
                with st.spinner("Calling primary LLM; backup will be used automatically if needed..."):
                    answer = generate_text(prompt)
                st.success(f"Answered by {answer['provider']} ({answer['model']})")
                st.markdown(answer["text"])
            except Exception as exc:
                st.error(str(exc))


def render_about_page():
    st.header("About")
    st.markdown(
        """
        This platform brings together agricultural data, crop suitability intelligence, weather and soil insights, and structured reporting in one streamlined workflow.
        It is designed to help farmers, agronomists, and analysts make better field decisions using local and live data.
        """
    )
    st.info("The application uses the Indian crop production dataset, live weather APIs, and AI recommendations to support practical crop planning.")


# Main app routing
if st.session_state.active_nav == "Home":
    render_dashboard_home()
elif st.session_state.active_nav == "Crop Suitability":
    render_crop_suitability_page()
elif st.session_state.active_nav == "Reports":
    render_reports_page()
elif st.session_state.active_nav == "Live Agriculture Intelligence APIs":
    render_api_page()
elif st.session_state.active_nav == "About":
    render_about_page()
else:
    render_dashboard_home()
