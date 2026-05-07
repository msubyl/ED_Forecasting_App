import streamlit as st
from datetime import datetime, timezone, timedelta
import base64
import pandas as pd
import numpy as np
from pathlib import Path
from utils.prediction import predict_daily, predict_hourly, predict_daily_test_set
from utils.monitoring import calculate_monitoring_metrics_from_df
import re

# ── Page config (only once) ──────────────────────────────────────────────────
st.set_page_config(
    page_title="Marsad",
    page_icon="assets/img.png",
    layout="wide"
)

# ── Asset loaders ────────────────────────────────────────────────────────────
def img_to_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def image_to_base64(path):
    return base64.b64encode(Path(path).read_bytes()).decode()

logo_base64 = image_to_base64("assets/logo.png")

with open("assets/time.svg", "r", encoding="utf-8") as f:
    time_svg = f.read()
time_svg = time_svg.replace('fill="#000000"', 'fill="#1560a8"')
time_icon = base64.b64encode(time_svg.encode("utf-8")).decode("utf-8")

with open("assets/analysis.svg", "r", encoding="utf-8") as f:
    analysis_svg = f.read()
analysis_svg = analysis_svg.replace('fill="#000000"', 'fill="#1560a8"')
ana_icon = base64.b64encode(analysis_svg.encode("utf-8")).decode("utf-8")

with open("assets/doctor.svg", "r", encoding="utf-8") as f:
    doctor_svg = f.read()
doctor_svg = doctor_svg.replace('fill="#999999"', 'fill="#1560a8"')
doctor_svg = doctor_svg.replace('fill="#F9C0C0"', 'fill="#1560a8"')
doctor_svg = doctor_svg.replace('fill="#CE0202"', 'fill="#1560a8"')
doctor_icon = base64.b64encode(doctor_svg.encode("utf-8")).decode("utf-8")

with open("assets/handup.svg", "r", encoding="utf-8") as f:
    hand_svg = f.read()
hand_svg = re.sub(r'<\?xml[^>]*\?>', '', hand_svg)
hand_svg = re.sub(r'<!--.*?-->', '', hand_svg, flags=re.DOTALL)
hand_svg = hand_svg.replace('fill="#000000"', 'fill="#1560a8"')
hand_icon = base64.b64encode(hand_svg.encode("utf-8")).decode("utf-8")

# ── Session state ────────────────────────────────────────────────────────────
if "page"       not in st.session_state: st.session_state.page       = "welcome"
if "user_input" not in st.session_state: st.session_state.user_input = None
if "daily_df"   not in st.session_state: st.session_state.daily_df   = None
if "hourly_df"  not in st.session_state: st.session_state.hourly_df  = None
if "daily_xai" not in st.session_state: st.session_state.daily_xai = None
if "hourly_xai" not in st.session_state: st.session_state.hourly_xai = None

    

# ── Global LTR / Arabic locale fix (runs on every page) ─────────────────────
st.markdown("""
<style>
/* Fix Arabic locale — target only content elements, never icon spans */
html, body { direction: ltr !important; }
.stApp { direction: ltr !important; }
.block-container { direction: ltr !important; }

/* Text and input elements only — excludes span to protect Material Icons */
p, label, h1, h2, h3, h4, h5, h6,
input, textarea, select,
table, td, th, tr, caption {
    direction: ltr !important;
    font-family: Arial, Helvetica, sans-serif !important;
}

/* Number inputs specifically for Arabic numeral fix */
div[data-testid="stNumberInput"] input,
div[data-testid="stDateInput"] input,
div[data-testid="stTextInput"] input {
    font-family: Arial, Helvetica, sans-serif !important;
    direction: ltr !important;
}

/* Protect Streamlit icon font — never override span font-family */
</style>
""", unsafe_allow_html=True)


def get_xai_figures(model, training_dataset, future_df):
    """
    Generate TFT interpretation figures for daily or hourly model.
    Returns figures dict or None.
    """
    prediction_data = training_dataset.from_dataset(
        training_dataset,
        future_df,
        predict=True,
        stop_randomization=True,
    )

    prediction_loader = prediction_data.to_dataloader(
        train=False,
        batch_size=32,
        num_workers=0,
    )

    predictions = model.predict(
        prediction_loader,
        mode="raw",
        return_x=True,
    )

    if hasattr(predictions, "output"):
        raw_predictions = predictions.output
    elif isinstance(predictions, tuple):
        raw_predictions = predictions[0]
    else:
        raw_predictions = predictions

    interpretation = model.interpret_output(
        raw_predictions,
        reduction="sum",
    )

    figures = model.plot_interpretation(interpretation)
    return figures


def render_xai_comparison(daily_xai, hourly_xai):
    """
    Show Daily and Hourly XAI side by side:
    - attention charts
    - variables charts
    """

    st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)

    st.html("""
    <div class="sec-hdr">
        <span class="sec-hdr-lbl">🔎 &nbsp;Forecast Explanation</span>
    </div>
    """)

    st.html("""
    <div style="
        background:white;
        border:1px solid #d0e4f5;
        border-radius:16px;
        box-shadow:0 4px 16px rgba(21,96,168,0.07);
        padding:18px 22px;
        margin-bottom:18px;
        font-family:Arial, sans-serif;
    ">
        <div style="color:#1560a8;font-size:15px;font-weight:800;margin-bottom:6px;">
            What does this explanation show?
        </div>
        <div style="color:#1e3550;font-size:14px;line-height:1.7;">
            This section compares the daily and hourly forecast explanations.
            The attention charts show which previous time steps the model focused on,
            while the variable charts show which input factors influenced the forecast.
        </div>
    </div>
    """)

    daily_figures = None
    hourly_figures = None

    if daily_xai is not None:
        try:
            daily_figures = get_xai_figures(
                model=daily_xai["model"],
                training_dataset=daily_xai["training_dataset"],
                future_df=daily_xai["future_df"],
            )
        except Exception as e:
            st.error(f"Daily XAI failed: {e}")

    if hourly_xai is not None:
        try:
            hourly_figures = get_xai_figures(
                model=hourly_xai["model"],
                training_dataset=hourly_xai["training_dataset"],
                future_df=hourly_xai["future_df"],
            )
        except Exception as e:
            st.error(f"Hourly XAI failed: {e}")

    # ── Attention charts  ─────────────────────────────
    with st.expander("Which previous time steps did the model focus on?", expanded=True):
        st.caption(
            "Higher values mean the model relied more on that previous day or hour when making the forecast."
        )

        col_daily, col_hourly = st.columns(2)

        with col_daily:
            st.markdown("#### Daily Attention")
            if isinstance(daily_figures, dict) and "attention" in daily_figures:
                st.pyplot(daily_figures["attention"])
            else:
                st.info("Daily attention explanation is not available.")

        with col_hourly:
            st.markdown("#### Hourly Attention")
            if isinstance(hourly_figures, dict) and "attention" in hourly_figures:
                st.pyplot(hourly_figures["attention"])
            else:
                st.info("Hourly attention explanation is not available.")

    # ── Variable importance  ──────────────────────────
    with st.expander("Which input factors influenced the forecast?", expanded=True):
        st.caption(
            "These charts show which variables were more important for the model prediction."
        )

        col_daily, col_hourly = st.columns(2)

        with col_daily:
            st.markdown("#### Daily Variables")

            if isinstance(daily_figures, dict):
                if "encoder_variables" in daily_figures:
                    st.pyplot(daily_figures["encoder_variables"])
                elif "decoder_variables" in daily_figures:
                    st.pyplot(daily_figures["decoder_variables"])
                elif "static_variables" in daily_figures:
                    st.pyplot(daily_figures["static_variables"])
                else:
                    st.info("Daily variable explanation is not available.")
            else:
                st.info("Daily variable explanation is not available.")

        with col_hourly:
            st.markdown("#### Hourly Variables")

            if isinstance(hourly_figures, dict):
                if "encoder_variables" in hourly_figures:
                    st.pyplot(hourly_figures["encoder_variables"])
                elif "decoder_variables" in hourly_figures:
                    st.pyplot(hourly_figures["decoder_variables"])
                elif "static_variables" in hourly_figures:
                    st.pyplot(hourly_figures["static_variables"])
                else:
                    st.info("Hourly variable explanation is not available.")
            else:
                st.info("Hourly variable explanation is not available.")


# ════════════════════════════════════════════════════════════════════════════
# PAGE 1 — Welcome
# ════════════════════════════════════════════════════════════════════════════
if st.session_state.page == "welcome":

    st.markdown("""
    <style>
    .stApp { background: white; }
    header, footer, #MainMenu { visibility: hidden; }
    .block-container { padding: 0 !important; max-width: 100% !important; }
    </style>
    """, unsafe_allow_html=True)

    st.html(f"""
    <style>
    .page {{
        min-height: 100vh;
        background: linear-gradient(160deg, #e8f3fc 0%, #f5fbff 50%, #e8f3fc 100%);
        display: flex; flex-direction: column; align-items: center;
        padding: 32px 40px 48px;
        position: relative; overflow: hidden;
        font-family: Arial, sans-serif;
    }}
    .blob-tl {{ position:absolute; top:-80px; left:-80px; width:300px; height:260px; background:#c8e3f5; border-bottom-right-radius:200px; opacity:0.7; z-index:0; }}
    .blob-tr {{ position:absolute; top:-60px; right:-60px; width:220px; height:180px; background:#c8e3f5; border-bottom-left-radius:160px; opacity:0.5; z-index:0; }}
    .blob-br {{ position:absolute; bottom:-100px; right:-80px; width:320px; height:260px; background:#c8e3f5; border-top-left-radius:220px; opacity:0.6; z-index:0; }}
    .dots-left  {{ position:absolute; top:40px; left:20px;  display:grid; grid-template-columns:repeat(6,1fr); gap:8px; opacity:0.25; z-index:0; }}
    .dots-right {{ position:absolute; top:40px; right:20px; display:grid; grid-template-columns:repeat(6,1fr); gap:8px; opacity:0.25; z-index:0; }}
    .dot {{ width:4px; height:4px; border-radius:50%; background:#1a6baf; }}
    .ecg-left  {{ position:absolute; left:0;  top:45%; width:180px; opacity:0.12; z-index:0; }}
    .ecg-right {{ position:absolute; right:0; top:45%; width:180px; opacity:0.12; z-index:0; transform:scaleX(-1); }}
    .content {{ position:relative; z-index:1; width:100%; display:flex; flex-direction:column; align-items:center; }}
    .logo-sub {{ font-size:17px; color:#1560a8; text-align:center; margin-bottom:0; }}
    .desc {{ max-width:700px; text-align:center; color:#0d1e3a; font-size:15px; line-height:1.7; margin:18px auto 10px; }}
    .section-title {{ display:flex; align-items:center; gap:14px; font-size:19px; font-weight:800; color:#1560a8; margin:20px 0 18px; width:100%; max-width:900px; justify-content:center; }}
    .section-title::before, .section-title::after {{ content:''; width:60px; height:1px; background:#1560a8; opacity:0.4; }}
    .dot-accent {{ width:8px; height:8px; border-radius:50%; background:#1560a8; display:inline-block; margin:0 2px; }}
    .cards {{ display:grid; grid-template-columns:repeat(4,1fr); gap:16px; max-width:900px; width:100%; margin-bottom:24px; }}
    .card {{ background:white; border-radius:16px; border:1px solid #d0e8f8; padding:24px 16px 20px; display:flex; flex-direction:column; align-items:center; text-align:center; box-shadow:0 6px 20px rgba(21,96,168,0.08); }}
    .card-icon {{ width:62px; height:62px; border-radius:50%; background:#e9f3ff; display:flex; align-items:center; justify-content:center; margin-bottom:14px; }}
    .card-icon img {{ width:44px; height:44px; display:block; object-fit:contain; }}
    .card h4 {{ color:#1560a8; font-size:14px; font-weight:800; margin-bottom:8px; line-height:1.3; }}
    .card p  {{ color:#0d1e3a; font-size:12px; line-height:1.5; margin:0; }}
    .bottom-box {{ background:#e6f2fc; border-radius:16px; max-width:700px; width:100%; padding:18px 28px; display:flex; align-items:center; gap:18px; margin-bottom:28px; }}
    .bottom-box p {{ color:#0d1e3a; font-size:14px; line-height:1.6; margin:0; }}
    .target-icon {{ width:70px; height:70px; background:#e9f3ff; border-radius:50%; display:flex; align-items:center; justify-content:center; }}
    .target-icon img {{ width:40px; height:40px; display:block; }}
    </style>

    <div class="page">
        <div class="blob-tl"></div><div class="blob-tr"></div><div class="blob-br"></div>
        <div class="dots-left">{'<div class="dot"></div>' * 36}</div>
        <div class="dots-right">{'<div class="dot"></div>' * 36}</div>
        <svg class="ecg-left" viewBox="0 0 200 60" fill="none">
            <path d="M0 30 L40 30 L50 10 L60 50 L70 20 L80 40 L90 30 L200 30" stroke="#1560a8" stroke-width="2"/>
        </svg>
        <svg class="ecg-right" viewBox="0 0 200 60" fill="none">
            <path d="M0 30 L40 30 L50 10 L60 50 L70 20 L80 40 L90 30 L200 30" stroke="#1560a8" stroke-width="2"/>
        </svg>
        <div class="content">
            <div style="display:flex;flex-direction:column;align-items:center;margin-bottom:10px;">
                <img src="data:image/png;base64,{logo_base64}" style="width:300px;margin-bottom:2px;">
                <div class="logo-sub">Emergency Department Forecasting System</div>
            </div>
            <div class="desc">
                Marsad is a forecasting system for emergency department demand, using historical data and key external factors.<br><br>
                It presents results through an interactive interface, helping healthcare teams understand trends and make better planning decisions.
            </div>
            <div class="section-title">
                <span class="dot-accent"></span>It helps hospitals to:<span class="dot-accent"></span>
            </div>
            <div class="cards">
                <div class="card">
                    <div class="card-icon"><img src="data:image/svg+xml;base64,{hand_icon}"></div>
                    <h4>Reduce overcrowding</h4>
                    <p>Anticipate patient surges and manage capacity effectively.</p>
                </div>
                <div class="card">
                    <div class="card-icon"><img src="data:image/svg+xml;base64,{doctor_icon}"></div>
                    <h4>Optimize staff and<br>resource allocation</h4>
                    <p>Align the right resources with predicted demand.</p>
                </div>
                <div class="card">
                    <div class="card-icon"><img src="data:image/svg+xml;base64,{time_icon}"></div>
                    <h4>Minimize patient waiting times</h4>
                    <p>Improve patient flow and enhance overall experience.</p>
                </div>
                <div class="card">
                    <div class="card-icon"><img src="data:image/svg+xml;base64,{ana_icon}"></div>
                    <h4>Support proactive decision-making</h4>
                    <p>Enable data-driven decisions for better preparedness.</p>
                </div>
            </div>
            <div class="bottom-box">
                <div class="target-icon">
                    <img src="data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxNjAiIGhlaWdodD0iMTYwIiB2aWV3Qm94PSIwIDAgMTAwIDEwMCIgZmlsbD0ibm9uZSI+CiAgPGNpcmNsZSBjeD0iNTAiIGN5PSI1MiIgcj0iMzgiIGZpbGw9IiMxNTYwYTgiLz4KICA8Y2lyY2xlIGN4PSI1MCIgY3k9IjUyIiByPSIyOSIgZmlsbD0id2hpdGUiLz4KICA8Y2lyY2xlIGN4PSI1MCIgY3k9IjUyIiByPSIyMCIgZmlsbD0iIzE1NjBhOCIvPgogIDxjaXJjbGUgY3g9IjUwIiBjeT0iNTIiIHI9IjExIiBmaWxsPSJ3aGl0ZSIvPgogIDxjaXJjbGUgY3g9IjUwIiBjeT0iNTIiIHI9IjUiIGZpbGw9IiMxNTYwYTgiLz4KICA8bGluZSB4MT0iODAiIHkxPSIxOCIgeDI9IjU0IiB5Mj0iNDkiIHN0cm9rZT0iIzE1NjBhOCIgc3Ryb2tlLXdpZHRoPSIzIiBzdHJva2UtbGluZWNhcD0icm91bmQiLz4KICA8cG9seWdvbiBwb2ludHM9IjU0LDQ5IDYxLDQxIDU5LDUxIiBmaWxsPSIjMGQzZDdhIi8+CiAgPHBvbHlnb24gcG9pbnRzPSI4MCwxOCA3MywxNSA3NSwyMiIgZmlsbD0iIzE1NjBhOCIvPgogIDxwb2x5Z29uIHBvaW50cz0iODAsMTggODMsMjUgNzUsMjIiIGZpbGw9IiMwZDNkN2EiLz4KICA8bGluZSB4MT0iODAiIHkxPSIxOCIgeDI9Ijc0IiB5Mj0iMTEiIHN0cm9rZT0iIzE1NjBhOCIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiLz4KICA8bGluZSB4MT0iODAiIHkxPSIxOCIgeDI9Ijg3IiB5Mj0iMjMiIHN0cm9rZT0iIzBkM2Q3YSIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiLz4KPC9zdmc+">
                </div>
                <p>Marsad transforms data into actionable insights, enabling smarter and more efficient healthcare operations.</p>
            </div>
        </div>
    </div>
    """)

    st.markdown("""
    <style>
    div.stButton { display:flex; justify-content:center; margin-top:-90px; }
    div.stButton > button {
        background-color:#1560a8 !important; color:white !important;
        border:none !important; border-radius:12px !important;
        height:52px !important; font-size:18px !important; font-weight:700 !important;
        box-shadow:0 6px 16px rgba(21,96,168,0.25);
    }
    div.stButton > button:hover { background-color:#0d4f8f !important; }
    </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        if st.button("Start Forecasting →", use_container_width=True):
            st.session_state.page = "input"
            st.rerun()


# ════════════════════════════════════════════════════════════════════════════
# PAGE 2 — Forecast Input
# ════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "input":

    # Use UTC+3 (Saudi Arabia time) regardless of server timezone
    riyadh_tz = timezone(timedelta(hours=3))
    current_hour = datetime.now(riyadh_tz).hour

    st.markdown("""
    <style>
    .stApp { background: linear-gradient(160deg, #e8f3fc 0%, #f5fbff 50%, #e8f3fc 100%); }
    header, footer, #MainMenu { visibility: hidden; }
    .block-container { padding: 2rem 2rem 3rem !important; max-width: 860px !important; }

    .blob-tl2 { position:fixed; top:-80px; left:-80px; width:300px; height:260px; background:#c8e3f5; border-bottom-right-radius:200px; opacity:0.7; z-index:0; pointer-events:none; }
    .blob-br2 { position:fixed; bottom:-100px; right:-80px; width:320px; height:260px; background:#c8e3f5; border-top-left-radius:220px; opacity:0.6; z-index:0; pointer-events:none; }
    .ecg-l2   { position:fixed; left:0;  top:40%; width:180px; opacity:0.08; z-index:0; pointer-events:none; }
    .ecg-r2   { position:fixed; right:0; top:40%; width:180px; opacity:0.08; z-index:0; transform:scaleX(-1); pointer-events:none; }
    .dots-grid2 { display:grid; grid-template-columns:repeat(6,4px); gap:8px; opacity:0.22; z-index:0; pointer-events:none; }
    .dots-tl2 { position:fixed; top:40px; left:20px; }
    .dots-br2 { position:fixed; bottom:40px; right:20px; }
    .bg-dot2  { width:4px; height:4px; border-radius:50%; background:#1a6baf; }

    .page-title   { text-align:center; font-size:32px; font-weight:900; color:#1560a8; margin:0 0 4px; }
    .page-sub     { text-align:center; font-size:14px; color:#3a5f82; line-height:1.6; margin:0; }
    .page-divider { width:60px; height:3px; background:#1560a8; border-radius:2px; margin:12px auto 28px; opacity:0.4; }

    .section-header { display:flex; align-items:center; gap:14px; margin-bottom:20px; margin-top:4px; padding:12px 16px; background:linear-gradient(135deg,#eaf4ff 0%,#f0f8ff 100%); border-radius:12px; border-left:4px solid #1560a8; }
    .section-icon  { display:none; }
    .section-label { font-size:16px; font-weight:800; color:#1560a8; }
    .section-num   { margin-left:auto; font-size:11px; font-weight:700; color:#1560a8; opacity:0.4; letter-spacing:1px; text-transform:uppercase; }
    .sep           { height:1px; background:#e8f3fc; margin:24px 0; }

    .info-band { width:100%; background:#e6f1fb; border-radius:12px; padding:14px 20px; display:flex; align-items:center; gap:14px; font-size:13.5px; color:#1e3550; line-height:1.6; margin-top:8px; }
    .info-band svg { width:22px; height:22px; stroke:#1560a8; fill:none; stroke-width:2; stroke-linecap:round; flex-shrink:0; }

    div[data-testid="stNumberInput"] input,
    div[data-testid="stDateInput"] input { border-radius:10px !important; border:1.5px solid #d0e4f5 !important; background:#f7fbff !important; font-size:15px !important; color:#1e3550 !important; height:46px !important; }
    div[data-testid="stNumberInput"] input:focus,
    div[data-testid="stDateInput"] input:focus { border-color:#1560a8 !important; box-shadow:0 0 0 3px rgba(21,96,168,0.1) !important; background:white !important; }
    div[data-testid="stSelectbox"] > div > div { border-radius:10px !important; border:1.5px solid #d0e4f5 !important; background:#f7fbff !important; color:#1e3550 !important; height:46px !important; }
    div[data-testid="stNumberInput"] label,
    div[data-testid="stDateInput"]   label,
    div[data-testid="stSlider"]      label,
    div[data-testid="stSelectbox"]   label { font-size:12px !important; font-weight:700 !important; color:#3a5f82 !important; letter-spacing:0.5px !important; text-transform:uppercase !important; }

    /* Slider thumb */
    [data-testid="stSlider"] [role="slider"] {
        background-color: #1560a8 !important;
        border-color: #1560a8 !important;
        box-shadow: 0 0 0 3px rgba(21,96,168,0.2) !important;
    }
    /* Slider value label (number above thumb) */
    [data-testid="stSlider"] p { color: #1560a8 !important; }
    [data-testid="stSliderThumbValue"] {
        background: transparent !important;
        color: #1560a8 !important;
        border: none !important;
        box-shadow: none !important;
    }
    /* Tooltip box — make transparent */
    [data-baseweb="tooltip"], [data-baseweb="tooltip"] div {
        background: transparent !important;
        box-shadow: none !important;
        border: none !important;
    }
    /* Filled track only */
    [data-testid="stSlider"] > div > div > div > div:first-child {
        background: #1560a8 !important;
    }
    [data-baseweb="slider"] > div > div > div:first-child {
        background-color: #1560a8 !important;
    }

    div[data-testid="stNumberInput"] button { background:#e6f1fb !important; color:#1560a8 !important; border-color:#d0e4f5 !important; border-radius:8px !important; }
    div[data-testid="stForm"] { background:white !important; border-radius:20px !important; border:1px solid #d0e4f5 !important; box-shadow:0 8px 30px rgba(21,96,168,0.09) !important; padding:28px 32px !important; }
    div[data-testid="stFormSubmitButton"] > button { height:52px !important; border-radius:12px !important; border:none !important; background:#1560a8 !important; color:white !important; font-size:15px !important; font-weight:800 !important; box-shadow:0 6px 20px rgba(21,96,168,0.3) !important; width:100% !important; }
    div[data-testid="stFormSubmitButton"] > button:hover { background:#0d4f8f !important; }
    div[data-testid="stButton"] > button { height:52px !important; border-radius:12px !important; border:1.5px solid #d0e4f5 !important; background:white !important; color:#1560a8 !important; font-size:15px !important; font-weight:700 !important; width:100% !important; }
    div[data-testid="stButton"] > button:hover { border-color:#1560a8 !important; background:#f0f8ff !important; }
    </style>
    """, unsafe_allow_html=True)

    dots_html = '<div class="bg-dot2"></div>' * 36
    st.html(f"""
    <div class="blob-tl2"></div>
    <div class="blob-br2"></div>
    <svg class="ecg-l2" viewBox="0 0 200 60" fill="none">
        <path d="M0 30 L40 30 L50 10 L60 50 L70 20 L80 40 L90 30 L200 30" stroke="#1560a8" stroke-width="2"/>
    </svg>
    <svg class="ecg-r2" viewBox="0 0 200 60" fill="none">
        <path d="M0 30 L40 30 L50 10 L60 50 L70 20 L80 40 L90 30 L200 30" stroke="#1560a8" stroke-width="2"/>
    </svg>
    <div class="dots-grid2 dots-tl2">{dots_html}</div>
    <div class="dots-grid2 dots-br2">{dots_html}</div>
    """)

    st.html("""
    <div class="page-title">Forecast Parameters</div>
    <div class="page-sub">Enter the target day details to generate an accurate ED demand forecast.</div>
    <div class="page-divider"></div>
    """)

    with st.form("forecast_form"):

        st.html("""
        <div class="section-header">
            <div class="section-icon"></div>
            <span class="section-label">&#128197;&nbsp; Date &amp; Time</span>
            <span class="section-num">01 / 03</span>
        </div>
        """)
        col1, col2 = st.columns(2)
        with col1:
            date = st.date_input("Target Date")
        with col2:
            start_hour = st.slider("Start Hour for Hourly Forecast", 0, 23, current_hour, format="%d:00")

        st.html("""
        <div class="sep"></div>
        <div class="section-header">
            <div class="section-icon"></div>
            <span class="section-label">&#127780;&#65039;&nbsp; Weather Conditions</span>
            <span class="section-num">02 / 03</span>
        </div>
        """)
        col3, col4, col5 = st.columns(3)
        with col3:
            avg_weather_C = st.number_input("Average Temperature (°C)", value=30.0)
        with col4:
            avg_precip = st.number_input("Average Precipitation (mm)", value=0.0)
        with col5:
            avg_snow = st.number_input("Average Snow (cm)", value=0.0)

        st.html("""
        <div class="sep"></div>
        <div class="section-header">
            <div class="section-icon"></div>
            <span class="section-label">&#128197;&nbsp; Day Classification</span>
            <span class="section-num">03 / 03</span>
        </div>
        """)
        col6, col7 = st.columns(2)
        with col6:
            is_weekend = st.selectbox("Is Weekend?", [0, 1],
                                      format_func=lambda x: "Weekday" if x == 0 else "Weekend")
        with col7:
            is_holiday = st.selectbox("Is Holiday?", [0, 1],
                                      format_func=lambda x: "Regular Day" if x == 0 else "Holiday")

        st.html("""
        <div class="info-band">
            <svg viewBox="0 0 24 24">
                <circle cx="12" cy="12" r="10"/>
                <line x1="12" y1="8" x2="12" y2="12"/>
                <line x1="12" y1="16" x2="12.01" y2="16"/>
            </svg>
            <span>The forecast covers the <strong style="color:#1560a8;">next 14 days</strong>, with hourly details for the first <strong style="color:#1560a8;">12 hours</strong> starting from your selected time.</span>
        </div>
        <br>
        """)

        submitted = st.form_submit_button("Generate Forecast →")

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
    col_back, col_mid, col_right = st.columns([1, 2, 1])
    with col_back:
        if st.button("← Back to Welcome"):
            st.session_state.page = "welcome"
            st.rerun()

    if submitted:
        user_input = {
            "date": str(date),
            "start_hour": start_hour,
            "avg_weather_C": avg_weather_C,
            "avg_precip": avg_precip,
            "avg_snow": avg_snow,
            "is_weekend": is_weekend,
            "is_holiday": is_holiday,
        }
    
        st.session_state.user_input = user_input
    
        with st.spinner("Generating forecast..."):
            daily_df, daily_xai = predict_daily(user_input)
            hourly_df, hourly_xai = predict_hourly(user_input)
    
            # Adjust hourly predictions to align with daily prediction
            first_day_prediction = daily_df.iloc[0]["Predicted_ED_Visits"]
            hourly_sum = hourly_df["Predicted_ED_Visits"].sum()
    
            if hourly_sum > 0:
                hourly_df["Predicted_ED_Visits"] = (
                    hourly_df["Predicted_ED_Visits"] / hourly_sum
                ) * first_day_prediction * 0.5
    
            hourly_df["Predicted_ED_Visits"] = (
                hourly_df["Predicted_ED_Visits"].round().astype(int)
            )
    
        st.session_state.daily_df = daily_df
        st.session_state.hourly_df = hourly_df
        st.session_state.daily_xai = daily_xai
        st.session_state.hourly_xai = hourly_xai
    
        st.session_state.page = "results"
        st.rerun()



        
      

# ════════════════════════════════════════════════════════════════════════════
# PAGE 3 — Results
# ════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "results":

    daily_df   = st.session_state.daily_df
    hourly_df  = st.session_state.hourly_df
    user_input = st.session_state.user_input
    daily_xai = st.session_state.daily_xai
    hourly_xai = st.session_state.hourly_xai

    st.markdown("""
    <style>
    .stApp { background: linear-gradient(160deg, #e8f3fc 0%, #f5fbff 50%, #e8f3fc 100%); }
    header, footer, #MainMenu { visibility: hidden; }
    .block-container { padding: 2rem 2rem 3rem !important; max-width: 960px !important; }

    .blob-tl3 { position:fixed; top:-80px; left:-80px; width:300px; height:260px; background:#c8e3f5; border-bottom-right-radius:200px; opacity:0.7; z-index:0; pointer-events:none; }
    .blob-br3 { position:fixed; bottom:-100px; right:-80px; width:320px; height:260px; background:#c8e3f5; border-top-left-radius:220px; opacity:0.6; z-index:0; pointer-events:none; }
    .ecg-l3   { position:fixed; left:0;  top:40%; width:180px; opacity:0.08; z-index:0; pointer-events:none; }
    .ecg-r3   { position:fixed; right:0; top:40%; width:180px; opacity:0.08; z-index:0; transform:scaleX(-1); pointer-events:none; }
    .dots-grid3 { display:grid; grid-template-columns:repeat(6,4px); gap:8px; opacity:0.22; z-index:0; pointer-events:none; }
    .dots-tl3 { position:fixed; top:40px; left:20px; }
    .dots-br3 { position:fixed; bottom:40px; right:20px; }
    .bg-dot3  { width:4px; height:4px; border-radius:50%; background:#1a6baf; }

    .res-title   { text-align:center; font-size:32px; font-weight:900; color:#1560a8; margin:0 0 4px; }
    .res-sub     { text-align:center; font-size:14px; color:#3a5f82; line-height:1.6; margin:0; }
    .res-divider { width:60px; height:3px; background:#1560a8; border-radius:2px; margin:12px auto 28px; opacity:0.4; }

    .sum-cards { display:grid; grid-template-columns:repeat(3,1fr); gap:16px; margin-bottom:28px; }
    .sum-card  { background:white; border-radius:16px; border:1px solid #d0e4f5; box-shadow:0 4px 16px rgba(21,96,168,0.07); padding:22px 24px; display:flex; flex-direction:column; gap:6px; }
    .sum-card.blue { background:linear-gradient(135deg,#1560a8 0%,#1a7fd4 100%); border-color:#1560a8; }
    .sum-lbl { font-size:11px; font-weight:700; letter-spacing:0.8px; text-transform:uppercase; color:#3a5f82; }
    .sum-card.blue .sum-lbl { color:rgba(255,255,255,0.75); }
    .sum-val { font-size:38px; font-weight:900; color:#1560a8; line-height:1.1; }
    .sum-card.blue .sum-val { color:white; }
    .sum-hint { font-size:12px; color:#7a9ab8; }
    .sum-card.blue .sum-hint { color:rgba(255,255,255,0.6); }

    .sec-hdr { display:flex; align-items:center; gap:10px; padding:12px 18px; margin-bottom:18px; background:linear-gradient(135deg,#eaf4ff 0%,#f0f8ff 100%); border-radius:12px; border-left:4px solid #1560a8; }
    .sec-hdr-lbl { font-size:16px; font-weight:800; color:#1560a8; }

    div[data-testid="stArrowVegaLiteChart"],
    div[data-testid="stVegaLiteChart"] { border-radius:12px !important; overflow:hidden !important; border:1px solid #e0effa !important; box-shadow:0 2px 10px rgba(21,96,168,0.06) !important; }
    div[data-testid="stExpander"] { border-radius:12px !important; border:1px solid #d0e4f5 !important; background:white !important; overflow:hidden !important; }
    div[data-testid="stExpander"] details summary p { font-weight:700 !important; color:#1560a8 !important; font-size:14px !important; }
    div[data-testid="stMetric"] { background:white; border-radius:14px; border:1px solid #d0e4f5; padding:18px 22px; box-shadow:0 4px 14px rgba(21,96,168,0.07); margin-bottom:16px; }
    div[data-testid="stMetricValue"] { font-size:44px !important; font-weight:900 !important; color:#1560a8 !important; }
    div[data-testid="stMetricLabel"] { font-size:12px !important; font-weight:700 !important; color:#3a5f82 !important; text-transform:uppercase !important; letter-spacing:0.5px !important; }

    div[data-testid="stButton"] > button { height:52px !important; border-radius:12px !important; font-size:15px !important; font-weight:700 !important; width:100% !important; }
    div[data-testid="stButton"]:first-of-type > button { background:#1560a8 !important; color:white !important; border:none !important; box-shadow:0 6px 20px rgba(21,96,168,0.3) !important; }
    div[data-testid="stButton"]:first-of-type > button:hover { background:#0d4f8f !important; }
    div[data-testid="stButton"]:last-of-type  > button { background:white !important; color:#1560a8 !important; border:1.5px solid #d0e4f5 !important; }
    div[data-testid="stButton"]:last-of-type  > button:hover { border-color:#1560a8 !important; background:#f0f8ff !important; }
    div[data-testid="stAlert"] { border-radius:12px !important; border:1px solid #d0e4f5 !important; }
    </style>
    """, unsafe_allow_html=True)

    if daily_df is None or hourly_df is None:
        st.warning("No forecast results found. Please go back and enter forecast parameters first.")
        if st.button("← Go to Input Page"):
            st.session_state.page = "input"
            st.rerun()

    else:
        first_day_prediction = daily_df.iloc[0]["Predicted_ED_Visits"]
        hourly_total = hourly_df["Predicted_ED_Visits"].sum()
        peak_row = hourly_df.loc[hourly_df["Predicted_ED_Visits"].idxmax()]
        try:
            peak_hour_str = str(peak_row["Time"]).split(" ")[-1][:5]
        except:
            peak_hour_str = "—"

        dots_html = '<div class="bg-dot3"></div>' * 36
        st.html(f"""
        <div class="blob-tl3"></div>
        <div class="blob-br3"></div>
        <svg class="ecg-l3" viewBox="0 0 200 60" fill="none">
            <path d="M0 30 L40 30 L50 10 L60 50 L70 20 L80 40 L90 30 L200 30" stroke="#1560a8" stroke-width="2"/>
        </svg>
        <svg class="ecg-r3" viewBox="0 0 200 60" fill="none">
            <path d="M0 30 L40 30 L50 10 L60 50 L70 20 L80 40 L90 30 L200 30" stroke="#1560a8" stroke-width="2"/>
        </svg>
        <div class="dots-grid3 dots-tl3">{dots_html}</div>
        <div class="dots-grid3 dots-br3">{dots_html}</div>
        """)

        st.html(f"""
        <div class="res-title">Forecast Results</div>
        <div class="res-sub">ED demand forecast for <strong>{user_input['date']}</strong> — generated based on your inputs.</div>
        <div class="res-divider"></div>
        """)

        st.html(f"""
        <div class="sum-cards">
            <div class="sum-card blue">
                <div class="sum-lbl">Predicted Visits Today</div>
                <div class="sum-val">{int(first_day_prediction)}</div>
                <div class="sum-hint">Expected ED visits on {user_input['date']}</div>
            </div>
            <div class="sum-card">
                <div class="sum-lbl">Next 12-Hour Total</div>
                <div class="sum-val">{int(hourly_total)}</div>
                <div class="sum-hint">Cumulative visits in the next 12 hours</div>
            </div>
            <div class="sum-card">
                <div class="sum-lbl">Peak Hour</div>
                <div class="sum-val" style="font-size:30px;">{peak_hour_str}</div>
                <div class="sum-hint">Hour with highest expected patient volume</div>
            </div>
        </div>
        """)

        def make_table(rows, col1_label, col2_label):
            rows_html = ""
            for i, (c1, c2) in enumerate(rows):
                bg = "#f0f8ff" if i % 2 == 0 else "white"
                rows_html += f"""
                <tr style="background:{bg};">
                    <td style="padding:11px 20px;color:#1e3550;font-size:14px;font-weight:600;border-bottom:1px solid #e0f0ff;">{c1}</td>
                    <td style="padding:11px 20px;color:#1560a8;font-size:14px;font-weight:700;text-align:center;border-bottom:1px solid #e0f0ff;">{c2}</td>
                </tr>"""
            return f"""
            <div style="border-radius:14px;border:1.5px solid #c8e1f7;overflow:hidden;box-shadow:0 4px 16px rgba(21,96,168,0.07);margin-top:14px;">
                <table style="width:100%;border-collapse:collapse;font-family:Arial,sans-serif;direction:ltr;">
                    <thead>
                        <tr style="background:#2a7fd4;">
                            <th style="padding:13px 20px;color:white;font-size:12px;font-weight:700;text-align:left;letter-spacing:0.8px;text-transform:uppercase;">{col1_label}</th>
                            <th style="padding:13px 20px;color:white;font-size:12px;font-weight:700;text-align:center;letter-spacing:0.8px;text-transform:uppercase;">{col2_label}</th>
                        </tr>
                    </thead>
                    <tbody>{rows_html}</tbody>
                </table>
            </div>"""

        # ── Section 1: Daily Forecast ─────────────────────────────────────────
        st.html("""
        <div class="sec-hdr">
            <span class="sec-hdr-lbl">&#128197; &nbsp;Daily Forecast — Next 14 Days</span>
        </div>
        """)
        st.metric(
            label=f"Predicted ED Visits — {user_input['date']}",
            value=f"{int(first_day_prediction)}"
        )
        with st.expander("14-day Forecast Chart & Data", expanded=True):
            st.line_chart(daily_df.set_index("Date")["Predicted_ED_Visits"], color="#1560a8")
            daily_rows = [(str(row["Date"])[:10], int(row["Predicted_ED_Visits"])) for _, row in daily_df.iterrows()]
            st.html(make_table(daily_rows, "Date", "Predicted Visits"))

        st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)

        # ── Section 2: Hourly Forecast ────────────────────────────────────────
        st.html("""
        <div class="sec-hdr">
            <span class="sec-hdr-lbl">&#128336; &nbsp;Next 12-Hour Forecast</span>
        </div>
        """)
        with st.expander("12-Hour Forecast Chart & Data", expanded=True):
            st.caption("Expected patient flow for the next 12 hours starting from the selected hour.")
            st.line_chart(hourly_df.set_index("Time")["Predicted_ED_Visits"], color="#1560a8")
            hourly_rows = []
            for _, row in hourly_df.iterrows():
                t = str(row["Time"])
                m = re.search(r'\d{2}:\d{2}', t)
                hourly_rows.append((m.group() if m else t, int(row["Predicted_ED_Visits"])))
            st.html(make_table(hourly_rows, "Hour", "Predicted Visits"))

        st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)

        # ── Section 3: Monitoring & Drift Detection ──────────────────────────
        st.html("""
        <div class="sec-hdr">
            <span class="sec-hdr-lbl">🩺 &nbsp;Monitoring & Drift Detection</span>
        </div>
        """)
        
        # ═════════════════════════════════════════════════════════════════════
        # Model Monitoring
        # ═════════════════════════════════════════════════════════════════════
        
        daily_test_df = pd.read_csv("data/test_data_daily.csv")
        daily_test_df["date"] = pd.to_datetime(daily_test_df["date"])
        daily_test_df = daily_test_df.sort_values("date").reset_index(drop=True)
        daily_test_df["ED_visits"] = np.expm1(daily_test_df["ED_visits"])
        
        
        daily_test_predictions = predict_daily_test_set(daily_test_df)
        
        daily_test_df = daily_test_df.iloc[:len(daily_test_predictions)].copy()
        daily_test_df["Predicted_ED_Visits"] = daily_test_predictions
        
        daily_monitor = calculate_monitoring_metrics_from_df(
            test_df=daily_test_df,
            model_name="Model",
            actual_col="ED_visits",
            pred_col="Predicted_ED_Visits"
        )
        
        # Raw metrics are still kept internally
        daily_mae = daily_monitor["mae"]
        daily_rmse = daily_monitor["rmse"]
        daily_mape = daily_monitor["mape"]
        
        # Display ratios instead of raw MAE/RMSE
        daily_mae_ratio = daily_monitor["mae_ratio"]
        daily_rmse_ratio = daily_monitor["rmse_ratio"]
        
        daily_actual_mean = daily_monitor["actual_mean"]
        daily_prediction_mean = daily_monitor["pred_mean"]
        daily_actual_std = daily_monitor["actual_std"]
        daily_prediction_std = daily_monitor["pred_std"]
        
        daily_mean_shift = daily_monitor["mean_shift"]
        daily_std_shift = daily_monitor["std_shift"]
        
        daily_performance_status = daily_monitor["performance_status"]
        daily_performance_icon = daily_monitor["performance_icon"]
        daily_performance_issue = daily_monitor["performance_issue"]
        
        daily_shift_status = daily_monitor["mean_shift_status"]
        daily_shift_icon = daily_monitor["mean_shift_icon"]
        daily_shift_issue = daily_monitor["mean_shift_issue"]
        
        daily_std_status = daily_monitor["std_shift_status"]
        daily_std_icon = daily_monitor["std_shift_icon"]
        daily_std_issue = daily_monitor["std_shift_issue"]
        
        daily_monitoring_status = daily_monitor["monitoring_status"]
        daily_monitoring_icon = daily_monitor["monitoring_icon"]
        daily_recommendation = daily_monitor["recommendation"]
        
        daily_alert_bg = daily_monitor["alert_bg"]
        daily_alert_border = daily_monitor["alert_border"]
        daily_alert_color = daily_monitor["alert_color"]
        
        daily_mape_text = "N/A" if np.isnan(daily_mape) else f"{daily_mape:.2f}%"
        daily_mae_ratio_text = "N/A" if np.isnan(daily_mae_ratio) else f"{daily_mae_ratio:.2f}"
        daily_rmse_ratio_text = "N/A" if np.isnan(daily_rmse_ratio) else f"{daily_rmse_ratio:.2f}"
        
        st.html(f"""
        <div style="
            background:white;
            border:1px solid #d0e4f5;
            border-radius:18px;
            box-shadow:0 4px 16px rgba(21,96,168,0.07);
            padding:20px 22px;
            margin-bottom:18px;
            font-family:Arial, sans-serif;
        ">
        
            <div style="
                color:#1560a8;
                font-size:16px;
                font-weight:800;
                margin-bottom:14px;
            ">
                Model Monitoring
            </div>
        
            <div style="
                display:grid;
                grid-template-columns:repeat(3,1fr);
                gap:14px;
                margin-bottom:14px;
            ">
        
                <div style="background:#f7fbff;border:1px solid #d0e4f5;border-radius:14px;padding:14px 16px;">
                    <div style="font-size:12px;color:#3a5f82;font-weight:700;text-transform:uppercase;margin-bottom:8px;">
                        Monitoring Status
                    </div>
                    <div style="font-size:18px;color:#1560a8;font-weight:800;">
                        {daily_monitoring_icon} {daily_monitoring_status}
                    </div>
                </div>
        
                <div style="background:#f7fbff;border:1px solid #d0e4f5;border-radius:14px;padding:14px 16px;">
                    <div style="font-size:12px;color:#3a5f82;font-weight:700;text-transform:uppercase;margin-bottom:8px;">
                        Performance
                    </div>
                    <div style="font-size:18px;color:#1560a8;font-weight:800;">
                        {daily_performance_icon} {daily_performance_status}
                    </div>
                </div>
        
                <div style="background:#f7fbff;border:1px solid #d0e4f5;border-radius:14px;padding:14px 16px;">
                    <div style="font-size:12px;color:#3a5f82;font-weight:700;text-transform:uppercase;margin-bottom:8px;">
                        Mean Shift Risk
                    </div>
                    <div style="font-size:18px;color:#1560a8;font-weight:800;">
                        {daily_shift_icon} {daily_shift_status}
                    </div>
                </div>
        
            </div>
        
            <div style="
                display:grid;
                grid-template-columns:repeat(3,1fr);
                gap:14px;
                margin-bottom:14px;
            ">
        
                <div style="background:white;border:1px solid #e0effa;border-radius:12px;padding:12px 14px;">
                    <div style="font-size:12px;color:#3a5f82;font-weight:700;margin-bottom:6px;">
                        MAE Ratio
                    </div>
                    <div style="font-size:16px;color:#1560a8;font-weight:800;">
                        {daily_mae_ratio_text}
                    </div>
                    <div style="font-size:11px;color:#6b7f95;margin-top:4px;">
                        MAE relative to actual mean
                    </div>
                </div>
        
                <div style="background:white;border:1px solid #e0effa;border-radius:12px;padding:12px 14px;">
                    <div style="font-size:12px;color:#3a5f82;font-weight:700;margin-bottom:6px;">
                        RMSE Ratio
                    </div>
                    <div style="font-size:16px;color:#1560a8;font-weight:800;">
                        {daily_rmse_ratio_text}
                    </div>
                    <div style="font-size:11px;color:#6b7f95;margin-top:4px;">
                        RMSE relative to actual mean
                    </div>
                </div>
        
                <div style="background:white;border:1px solid #e0effa;border-radius:12px;padding:12px 14px;">
                    <div style="font-size:12px;color:#3a5f82;font-weight:700;margin-bottom:6px;">
                        MAPE
                    </div>
                    <div style="font-size:16px;color:#1560a8;font-weight:800;">
                        {daily_mape_text}
                    </div>
                    <div style="font-size:11px;color:#6b7f95;margin-top:4px;">
                        Percentage error on test set
                    </div>
                </div>
        
            </div>
        
            <div style="
                display:grid;
                grid-template-columns:repeat(2,1fr);
                gap:14px;
                margin-bottom:14px;
            ">
        
                <div style="background:white;border:1px solid #e0effa;border-radius:12px;padding:12px 14px;">
                    <div style="font-size:12px;color:#3a5f82;font-weight:700;margin-bottom:6px;">
                        Mean Shift
                    </div>
                    <div style="font-size:16px;color:#1560a8;font-weight:800;">
                        {daily_mean_shift:.2f}
                    </div>
                    <div style="font-size:11px;color:#6b7f95;margin-top:4px;">
                        Actual mean: {daily_actual_mean:.2f} | Predicted mean: {daily_prediction_mean:.2f}
                    </div>
                </div>
        
                <div style="background:white;border:1px solid #e0effa;border-radius:12px;padding:12px 14px;">
                    <div style="font-size:12px;color:#3a5f82;font-weight:700;margin-bottom:6px;">
                        Std Shift
                    </div>
                    <div style="font-size:16px;color:#1560a8;font-weight:800;">
                        {daily_std_icon} {daily_std_status} — {daily_std_shift:.2f}
                    </div>
                    <div style="font-size:11px;color:#6b7f95;margin-top:4px;">
                        Actual std: {daily_actual_std:.2f} | Predicted std: {daily_prediction_std:.2f}
                    </div>
                </div>
        
            </div>
        
            <div style="
                background:{daily_alert_bg};
                border:1px solid {daily_alert_border};
                border-radius:12px;
                padding:13px 16px;
                color:#1e3550;
                font-size:14px;
                line-height:1.6;
                margin-bottom:12px;
            ">
                <strong style="color:{daily_alert_color};">Performance Insight:</strong> {daily_performance_issue}<br>
                <strong style="color:{daily_alert_color};">Mean Shift Insight:</strong> {daily_shift_issue}<br>
                <strong style="color:{daily_alert_color};">Std Shift Insight:</strong> {daily_std_issue}<br>
                <strong style="color:#1560a8;">Recommendation:</strong> {daily_recommendation}
            </div>
        
            <div style="
                margin-top:12px;
                color:#6b7f95;
                font-size:12px;
                line-height:1.5;
            ">
                Note: This section evaluates the model using test-set performance ratios and early drift-risk indicators based on mean and standard deviation shifts.
            </div>
        
        </div>
        """)
                       

        # ── Section 4:  Forecast Explanation ───────────────
        if daily_xai is not None or hourly_xai is not None:
            render_xai_comparison(daily_xai, hourly_xai)
        else:
            st.warning("Forecast explanation is not available for this prediction.")
      

        st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)

        # ── Action buttons ────────────────────────────────────────────────────
        col1, col2 = st.columns(2)
        with col1:
            if st.button("New Forecast", use_container_width=True):
                st.session_state.page = "input"
                st.rerun()
        with col2:
            if st.button("Back to Welcome", use_container_width=True):
                st.session_state.page = "welcome"
                st.rerun()
