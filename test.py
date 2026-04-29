import streamlit as st
from datetime import datetime
import base64
from pathlib import Path
from utils.prediction import predict_daily, predict_hourly
import streamlit as st
import streamlit as st
import base64

st.set_page_config(page_title="Marsad", layout="wide")


def img_to_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


st.set_page_config(
    page_title="Marsad",
    page_icon="assets/img.png",
    layout="wide"
)


def image_to_base64(path):
    return base64.b64encode(Path(path).read_bytes()).decode()


logo_base64 = image_to_base64("assets/logo.png")

# time_icon
with open("assets/time.svg", "r", encoding="utf-8") as f:
    time_svg = f.read()

time_svg = time_svg.replace('fill="#000000"', 'fill="#1560a8"')

time_icon = base64.b64encode(time_svg.encode("utf-8")).decode("utf-8")

# analisis_icon
with open("assets/analysis.svg", "r", encoding="utf-8") as f:
    analysis_svg = f.read()
analysis_svg = analysis_svg.replace('fill="#000000"', 'fill="#1560a8"')
ana_icon = base64.b64encode(analysis_svg.encode("utf-8")).decode("utf-8")
import base64

# doctor_icon
with open("assets/doctor.svg", "r", encoding="utf-8") as f:
    doctor_svg = f.read()

doctor_svg = doctor_svg.replace('fill="#999999"', 'fill="#1560a8"')
doctor_svg = doctor_svg.replace('fill="#F9C0C0"', 'fill="#1560a8"')
doctor_svg = doctor_svg.replace('fill="#CE0202"', 'fill="#1560a8"')

doctor_icon = base64.b64encode(doctor_svg.encode("utf-8")).decode("utf-8")

# people_icon
import base64
import re

with open("assets/handup.svg", "r", encoding="utf-8") as f:
    hand_svg = f.read()

hand_svg = re.sub(r'<\?xml[^>]*\?>', '', hand_svg)
hand_svg = re.sub(r'<!--.*?-->', '', hand_svg, flags=re.DOTALL)

hand_svg = hand_svg.replace('fill="#000000"', 'fill="#1560a8"')

hand_icon = base64.b64encode(hand_svg.encode("utf-8")).decode("utf-8")
# ________
if "page" not in st.session_state:
    st.session_state.page = "welcome"

if "user_input" not in st.session_state:
    st.session_state.user_input = None

if "daily_df" not in st.session_state:
    st.session_state.daily_df = None

if "hourly_df" not in st.session_state:
    st.session_state.hourly_df = None

logo = img_to_base64("assets/logo.png")

st.markdown("""
<style>
.stApp {
    background: white;
}

header, footer, #MainMenu {
    visibility: hidden;
}

.block-container {
    padding: 0 !important;
    max-width: 100% !important;
}

.marsad-page {
    width: 100vw;
    height: 100vh;
    overflow: hidden;
    position: relative;
    font-family: Arial, Helvetica, sans-serif;
    background:
        radial-gradient(circle at 4% 5%, rgba(226,244,255,0.95) 0%, rgba(226,244,255,0.55) 20%, transparent 38%),
        radial-gradient(circle at 96% 88%, rgba(226,244,255,0.95) 0%, rgba(226,244,255,0.55) 21%, transparent 40%),
        #ffffff;
}

/* corner shapes */
.top-blue {
    position:absolute;
    top:-155px;
    left:-120px;
    width:520px;
    height:330px;
    background:#1174ba;
    border-bottom-right-radius:270px;
    z-index:1;
}

.top-light {
    position:absolute;
    top:-92px;
    left:-45px;
    width:475px;
    height:300px;
    background:#eaf6ff;
    border-bottom-right-radius:270px;
    z-index:2;
}

.bottom-blue {
    position:absolute;
    right:-130px;
    bottom:-135px;
    width:520px;
    height:330px;
    background:#1174ba;
    border-top-left-radius:270px;
    z-index:1;
}

.bottom-light {
    position:absolute;
    right:-50px;
    bottom:-78px;
    width:475px;
    height:295px;
    background:#eaf6ff;
    border-top-left-radius:270px;
    z-index:2;
}

/* dots */
.dots {
    position:absolute;
    width:190px;
    height:190px;
    opacity:.35;
    background-image: radial-gradient(#9ccbea 1.4px, transparent 1.4px);
    background-size: 16px 16px;
    z-index:2;
}

.dots-right {
    top:33px;
    right:95px;
}

.dots-left {
    bottom:55px;
    left:35px;
}

/* heartbeat */
.heart-line {
    position:absolute;
    width:270px;
    height:80px;
    opacity:.18;
    z-index:2;
}

.heart-line svg {
    width:100%;
    height:100%;
}

.heart-left {
    left:0;
    top:258px;
}

.heart-right {
    right:0;
    top:258px;
}

.content {
    position:relative;
    z-index:5;
    text-align:center;
    height:100%;
    padding-top:27px;
}

/* logo */
.logo {
    width:132px;
    display:block;
    margin:0 auto -2px auto;
}

.title {
    font-size:64px;
    line-height:1;
    color:#1672b9;
    font-weight:800;
    margin:0;
}

.subtitle {
    color:#1b6fb3;
    font-size:18px;
    font-weight:600;
    margin-top:5px;
    margin-bottom:26px;
}

.desc {
    color:#1f2f44;
    font-size:17px;
    line-height:1.45;
    margin-bottom:18px;
}

.help-title {
    display:flex;
    align-items:center;
    justify-content:center;
    gap:18px;
    margin-top:22px;
    margin-bottom:10px;
}

.help-title h2 {
    margin:0;
    font-size:23px;
    color:#0e65a8;
    font-weight:800;
}

.line {
    width:110px;
    height:2px;
    background:linear-gradient(to right, transparent, #b8d5ef, #1c78bd);
    position:relative;
}

.line.right {
    background:linear-gradient(to left, transparent, #b8d5ef, #1c78bd);
}

.line::after {
    content:"";
    width:8px;
    height:8px;
    background:#1c78bd;
    border-radius:50%;
    position:absolute;
    top:-3px;
    right:0;
}

.line.right::after {
    left:0;
    right:auto;
}

/* cards */
.cards {
    display:grid;
    grid-template-columns: repeat(4, 238px);
    justify-content:center;
    gap:18px;
    margin-top:8px;
}

.card {
    height:215px;
    background:rgba(255,255,255,.93);
    border:1px solid #e6eef7;
    border-radius:13px;
    box-shadow:0 5px 18px rgba(39,99,157,.09);
    padding:18px;
}

.icon-circle {
    width:76px;
    height:76px;
    background:#eef6ff;
    border-radius:50%;
    margin:0 auto 12px;
    display:flex;
    align-items:center;
    justify-content:center;
}

.icon-circle svg {
    width:42px;
    height:42px;
    fill:#1474bb;
    stroke:#1474bb;
}

.card h3 {
    color:#0868ad;
    font-size:17px;
    font-weight:800;
    line-height:1.15;
    margin:0 0 14px 0;
}

.card p {
    color:#24344a;
    font-size:15px;
    line-height:1.45;
    margin:0;
}

/* insight */
.insight {
    width:650px;
    height:92px;
    margin:12px auto 10px;
    background:#edf7ff;
    border-radius:12px;
    display:flex;
    align-items:center;
    text-align:left;
    padding:0 28px;
    gap:24px;
}

.target {
    width:70px;
    height:70px;
    background:#dff0ff;
    border-radius:50%;
    display:flex;
    align-items:center;
    justify-content:center;
    flex-shrink:0;
}

.target svg {
    width:44px;
    height:44px;
    fill:none;
    stroke:#1474bb;
    stroke-width:3.5;
}

.insight p {
    color:#1e3550;
    font-size:18px;
    line-height:1.45;
    margin:0;
}
.card-icon img {
    width: 42px;
    height: 42px;
}

.start-btn {
    width:325px;
    height:50px;
    border-radius:7px;
    background:#1374bb;
    color:white;
    font-size:20px;
    font-weight:800;
    box-shadow:0 6px 14px rgba(19,116,187,.35);
    display:flex;
    align-items:center;
    justify-content:center;
    gap:55px;
    margin:0 auto;
}

.start-btn span {
    font-size:30px;
    line-height:1;
}

</style>
""", unsafe_allow_html=True)

# page 1
if st.session_state.page == "welcome":

    dots_html = "".join(['<div class="dot"></div>' * 36])

    st.html(f"""
    <style>
    .page {{
        min-height: 100vh;
        background: linear-gradient(160deg, #e8f3fc 0%, #f5fbff 50%, #e8f3fc 100%);
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 32px 40px 48px;
        position: relative;
        overflow: hidden;
        font-family: Arial, sans-serif;
    }}
    .blob-tl {{
        position: absolute; top: -80px; left: -80px;
        width: 300px; height: 260px;
        background: #c8e3f5;
        border-bottom-right-radius: 200px;
        opacity: 0.7; z-index: 0;
    }}
    .blob-tr {{
        position: absolute; top: -60px; right: -60px;
        width: 220px; height: 180px;
        background: #c8e3f5;
        border-bottom-left-radius: 160px;
        opacity: 0.5; z-index: 0;
    }}
    .blob-br {{
        position: absolute; bottom: -100px; right: -80px;
        width: 320px; height: 260px;
        background: #c8e3f5;
        border-top-left-radius: 220px;
        opacity: 0.6; z-index: 0;
    }}
    .dots-left {{
       position: absolute; top: 40px; left: 20px;
        display: grid; grid-template-columns: repeat(6,1fr); gap: 8px;
        opacity: 0.25; z-index: 0;
    }}
    .dots-right {{
        position: absolute; top: 40px; right: 20px;
        display: grid; grid-template-columns: repeat(6,1fr); gap: 8px;
        opacity: 0.25; z-index: 0;
    }}
    .dot {{ width: 4px; height: 4px; border-radius: 50%; background: #1a6baf; }}
    .ecg-left {{
        position: absolute; left: 0; top: 45%;
        width: 180px; opacity: 0.12; z-index: 0;
    }}
    .ecg-right {{
        position: absolute; right: 0; top: 45%;
        width: 180px; opacity: 0.12; z-index: 0; transform: scaleX(-1);
    }}
    .content {{ position: relative; z-index: 1; width: 100%; display: flex; flex-direction: column; align-items: center; }}
    .logo-title {{ font-size: 44px; font-weight: 900; color: #1560a8; letter-spacing: -1px; text-align: center; margin: 4px 0 2px; }}
    .logo-sub {{ font-size: 17px; color: #1560a8; text-align: center; margin-bottom: 0; }}
    .desc {{ max-width: 700px; text-align: center; color: #0d1e3a; font-size: 15px; line-height: 1.7; margin: 18px auto 10px; }}
    .section-title {{
        display: flex; align-items: center; gap: 14px;
        font-size: 19px; font-weight: 800; color: #1560a8;
        margin: 20px 0 18px; width: 100%; max-width: 900px; justify-content: center;
    }}
    .section-title::before, .section-title::after {{
        content: ''; width: 60px; height: 1px; background: #1560a8; opacity: 0.4;
    }}
    .dot-accent {{ width: 8px; height: 8px; border-radius: 50%; background: #1560a8; display: inline-block; margin: 0 2px; }}
    .cards {{
        display: grid; grid-template-columns: repeat(4,1fr);
        gap: 16px; max-width: 900px; width: 100%; margin-bottom: 24px;
    }}
    .card {{
        background: white; border-radius: 16px; border: 1px solid #d0e8f8;
        padding: 24px 16px 20px; display: flex; flex-direction: column; align-items: center;
        text-align: center; box-shadow: 0 6px 20px rgba(21,96,168,0.08);
    }}
    .card-icon {{
        width: 62px; height: 62px; border-radius: 50%; background: #e9f3ff;
        display: flex; align-items: center; justify-content: center; margin-bottom: 14px;
    }}
    .card-icon svg {{ width: 32px; height: 32px; stroke: #1560a8; stroke-width: 2; fill: none; stroke-linecap: round; stroke-linejoin: round; }}
    .card h4 {{ color: #1560a8; font-size: 14px; font-weight: 800; margin-bottom: 8px; line-height: 1.3; }}
    .card p {{ color: #0d1e3a; font-size: 12px; line-height: 1.5; margin: 0; }}
    .bottom-box {{
        background: #e6f2fc; border-radius: 16px; max-width: 700px; width: 100%;
        padding: 18px 28px; display: flex; align-items: center; gap: 18px; margin-bottom: 28px;
    }}
    .bottom-box p {{ color: #0d1e3a; font-size: 14px; line-height: 1.6; margin: 0; }}
    .target-icon {{
    width: 70px;
    height: 70px;
    background: #e9f3ff;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
}}

.target-icon img {{
    width: 40px;
    height: 40px;
    display: block;

}}
.card-icon img {{
    width: 44px;
    height: 44px;
    display: block;
    object-fit: contain;
}}
    </style>

    <div class="page">
        <div class="blob-tl"></div>
        <div class="blob-tr"></div>
        <div class="blob-br"></div>

        <div class="dots-left">
            {'<div class="dot"></div>' * 36}
        </div>
        <div class="dots-right">
            {'<div class="dot"></div>' * 36}
        </div>

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
                <span class="dot-accent"></span>
                It helps hospitals to:
                <span class="dot-accent"></span>
            </div>

            <div class="cards">
               <div class="card">
                    <div class="card-icon">
                        <img src="data:image/svg+xml;base64,{hand_icon}">
                    </div>
                    <h4>Reduce overcrowding</h4>
                    <p>Anticipate patient surges and manage capacity effectively.</p>
                </div>
                <div class="card">
                    <div class="card-icon">
                        <img class="doctor-img" src="data:image/svg+xml;base64,{doctor_icon}">
                    </div>
                    <h4>Optimize staff and<br>resource allocation</h4>
                    <p>Align the right resources with predicted demand.</p>
                </div>
                <div class="card">
                     <div class="card-icon">
                            <img class="doctor-img" src="data:image/svg+xml;base64,{time_icon}">
                        </div>
                    <h4>Minimize patient waiting times</h4>
                    <p>Improve patient flow and enhance overall experience.</p>
                </div>
                <div class="card">

                        <div class="card-icon">
                            <img class="doctor-img" src="data:image/svg+xml;base64,{ana_icon}">
                        </div>

                    <h4>Support proactive decision-making</h4>
                    <p>Enable data-driven decisions for better preparedness.</p>
                </div>
            </div>

            <div class="bottom-box">
                <svg width="48" height="48" viewBox="0 0 48 48" fill="none">
                    <circle cx="24" cy="24" r="18" stroke="#1560a8" stroke-width="2.5"/>
                    <circle cx="24" cy="24" r="11" stroke="#1560a8" stroke-width="2.5"/>
                    <circle cx="24" cy="24" r="4" fill="#1560a8"/>
                    <path d="M34 14 L40 8" stroke="#1560a8" stroke-width="2.5" stroke-linecap="round"/>
                    <path d="M37 8 L40 8 L40 11" stroke="#1560a8" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
                   <div class="target-icon">
                      <img src="data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxNjAiIGhlaWdodD0iMTYwIiB2aWV3Qm94PSIwIDAgMTAwIDEwMCIgZmlsbD0ibm9uZSI+CiAgPGNpcmNsZSBjeD0iNTAiIGN5PSI1MiIgcj0iMzgiIGZpbGw9IiMxNTYwYTgiLz4KICA8Y2lyY2xlIGN4PSI1MCIgY3k9IjUyIiByPSIyOSIgZmlsbD0id2hpdGUiLz4KICA8Y2lyY2xlIGN4PSI1MCIgY3k9IjUyIiByPSIyMCIgZmlsbD0iIzE1NjBhOCIvPgogIDxjaXJjbGUgY3g9IjUwIiBjeT0iNTIiIHI9IjExIiBmaWxsPSJ3aGl0ZSIvPgogIDxjaXJjbGUgY3g9IjUwIiBjeT0iNTIiIHI9IjUiIGZpbGw9IiMxNTYwYTgiLz4KICA8bGluZSB4MT0iODAiIHkxPSIxOCIgeDI9IjU0IiB5Mj0iNDkiIHN0cm9rZT0iIzE1NjBhOCIgc3Ryb2tlLXdpZHRoPSIzIiBzdHJva2UtbGluZWNhcD0icm91bmQiLz4KICA8cG9seWdvbiBwb2ludHM9IjU0LDQ5IDYxLDQxIDU5LDUxIiBmaWxsPSIjMGQzZDdhIi8+CiAgPHBvbHlnb24gcG9pbnRzPSI4MCwxOCA3MywxNSA3NSwyMiIgZmlsbD0iIzE1NjBhOCIvPgogIDxwb2x5Z29uIHBvaW50cz0iODAsMTggODMsMjUgNzUsMjIiIGZpbGw9IiMwZDNkN2EiLz4KICA8bGluZSB4MT0iODAiIHkxPSIxOCIgeDI9Ijc0IiB5Mj0iMTEiIHN0cm9rZT0iIzE1NjBhOCIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiLz4KICA8bGluZSB4MT0iODAiIHkxPSIxOCIgeDI9Ijg3IiB5Mj0iMjMiIHN0cm9rZT0iIzBkM2Q3YSIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiLz4KPC9zdmc+" style="width:60px; height:60px;">
                    </div>

                <p>Marsad transforms data into actionable insights, enabling smarter and more efficient healthcare operations.</p>
            </div>
        </div>
    </div>
    """)

    st.markdown("""
    <style>
    div.stButton {
        display: flex;
        justify-content: center;
        margin-top: -90px;  
    }
    div.stButton > button {
    background-color: #1560a8 !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    height: 52px !important;
    font-size: 18px !important;
    font-weight: 700 !important;
    box-shadow: 0 6px 16px rgba(21, 96, 168, 0.25);
}

div.stButton > button:hover {
    background-color: #0d4f8f !important;
    color: white !important;
}
    </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        if st.button("Start Forecasting →", use_container_width=True):
            st.session_state.page = "input"
            st.rerun()

# page 2


elif st.session_state.page == "input":

    current_hour = datetime.now().hour
# ── Background & global styles ───────────────────────────────────────────
    st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(160deg, #e8f3fc 0%, #f5fbff 50%, #e8f3fc 100%);
        font-family: Arial, Helvetica, sans-serif;
    }
    header, footer, #MainMenu { visibility: hidden; }
    .block-container { padding: 2rem 2rem 3rem !important; max-width: 860px !important; }

    /* Fixed decorations */
    .blob-tl {
        position: fixed; top: -80px; left: -80px;
        width: 300px; height: 260px; background: #c8e3f5;
        border-bottom-right-radius: 200px; opacity: 0.7; z-index: 0; pointer-events: none;
    }
    .blob-br {
        position: fixed; bottom: -100px; right: -80px;
        width: 320px; height: 260px; background: #c8e3f5;
        border-top-left-radius: 220px; opacity: 0.6; z-index: 0; pointer-events: none;
    }
    .ecg-l {
        position: fixed; left: 0; top: 40%;
        width: 180px; opacity: 0.08; z-index: 0; pointer-events: none;
    }
    .ecg-r {
        position: fixed; right: 0; top: 40%;
        width: 180px; opacity: 0.08; z-index: 0;
        transform: scaleX(-1); pointer-events: none;
    }
    .dots-grid {
        display: grid; grid-template-columns: repeat(6, 4px); gap: 8px;
        opacity: 0.22; z-index: 0; pointer-events: none;
    }
    .dots-tl { position: fixed; top: 40px; left: 20px; }
    .dots-br { position: fixed; bottom: 40px; right: 20px; }
    .bg-dot { width: 4px; height: 4px; border-radius: 50%; background: #1a6baf; }

    /* Page header */
    .page-label {
        text-align: center; font-size: 13px; font-weight: 700;
        color: #1560a8; letter-spacing: 2px; text-transform: uppercase;
        opacity: 0.7; margin-bottom: 4px;
    }
    .page-title {
        text-align: center; font-size: 32px; font-weight: 900;
        color: #1560a8; margin: 0 0 4px;
    }
    .page-sub {
        text-align: center; font-size: 14px; color: #3a5f82; line-height: 1.6; margin: 0;
    }
    .page-divider {
        width: 60px; height: 3px; background: #1560a8;
        border-radius: 2px; margin: 12px auto 28px; opacity: 0.4;
    }

    /* Section headers */
    .section-header {
        display: flex; align-items: center; gap: 10px; margin-bottom: 16px; margin-top: 4px;
    }
    .section-icon {
        width: 38px; height: 38px; background: #e6f1fb; border-radius: 50%;
        display: flex; align-items: center; justify-content: center; flex-shrink: 0;
    }
    .section-icon svg {
        width: 20px; height: 20px; stroke: #1560a8; fill: none;
        stroke-width: 2; stroke-linecap: round; stroke-linejoin: round;
    }
    .section-label { font-size: 16px; font-weight: 800; color: #1560a8; }
    .sep { height: 1px; background: #e8f3fc; margin: 20px 0 24px; }

    /* Info band */
    .info-band {
        width: 100%; background: #e6f1fb; border-radius: 12px;
        padding: 14px 20px; display: flex; align-items: center; gap: 14px;
        font-size: 13.5px; color: #1e3550; line-height: 1.6; margin-top: 8px;
    }
    .info-band svg {
        width: 22px; height: 22px; stroke: #1560a8; fill: none;
        stroke-width: 2; stroke-linecap: round; flex-shrink: 0;
    }

    /* Streamlit widget overrides */
    div[data-testid="stNumberInput"] input,
    div[data-testid="stDateInput"] input {
        border-radius: 10px !important;
        border: 1.5px solid #d0e4f5 !important;
        background: #f7fbff !important;
        font-size: 15px !important;
        color: #1e3550 !important;
        height: 46px !important;
    }
    div[data-testid="stNumberInput"] input:focus,
    div[data-testid="stDateInput"] input:focus {
        border-color: #1560a8 !important;
        box-shadow: 0 0 0 3px rgba(21,96,168,0.1) !important;
        background: white !important;
    }
    div[data-testid="stSelectbox"] > div > div {
        border-radius: 10px !important;
        border: 1.5px solid #d0e4f5 !important;
        background: #f7fbff !important;
        color: #1e3550 !important;
        height: 46px !important;
    }
    div[data-testid="stNumberInput"] label,
    div[data-testid="stDateInput"] label,
    div[data-testid="stSlider"] label,
    div[data-testid="stSelectbox"] label {
        font-size: 12px !important; font-weight: 700 !important;
        color: #3a5f82 !important; letter-spacing: 0.5px !important;
        text-transform: uppercase !important;
    }
    div[data-testid="stSlider"] > div > div > div > div {
        background: #1560a8 !important;
    }

    /* Form card wrapper */
    div[data-testid="stForm"] {
        background: white !important;
        border-radius: 20px !important;
        border: 1px solid #d0e4f5 !important;
        box-shadow: 0 8px 30px rgba(21,96,168,0.09) !important;
        padding: 28px 32px !important;
    }

    /* Submit button */
    div[data-testid="stFormSubmitButton"] > button {
        height: 52px !important; border-radius: 12px !important;
        border: none !important; background: #1560a8 !important;
        color: white !important; font-size: 15px !important;
        font-weight: 800 !important;
        box-shadow: 0 6px 20px rgba(21,96,168,0.3) !important;
        width: 100% !important;
    }
    div[data-testid="stFormSubmitButton"] > button:hover {
        background: #0d4f8f !important;
    }

    /* Back button */
    div[data-testid="stButton"] > button {
        height: 52px !important; border-radius: 12px !important;
        border: 1.5px solid #d0e4f5 !important;
        background: white !important; color: #1560a8 !important;
        font-size: 15px !important; font-weight: 700 !important;
        width: 100% !important;
    }
    div[data-testid="stButton"] > button:hover {
        border-color: #1560a8 !important; background: #f0f8ff !important;
    }
    </style>
    """, unsafe_allow_html=True)

# ── Decorative background elements ───────────────────────────────────────
dots_html = '<div class="bg-dot"></div>' * 36
st.html(f"""
    <div class="blob-tl"></div>
    <div class="blob-br"></div>
    <svg class="ecg-l" viewBox="0 0 200 60" fill="none">
        <path d="M0 30 L40 30 L50 10 L60 50 L70 20 L80 40 L90 30 L200 30"
              stroke="#1560a8" stroke-width="2"/>
    </svg>
    <svg class="ecg-r" viewBox="0 0 200 60" fill="none">
        <path d="M0 30 L40 30 L50 10 L60 50 L70 20 L80 40 L90 30 L200 30"
              stroke="#1560a8" stroke-width="2"/>
    </svg>
    <div class="dots-grid dots-tl">{dots_html}</div>
    <div class="dots-grid dots-br">{dots_html}</div>
    """)

# ── Page header ──────────────────────────────────────────────────────────
st.html("""
    <div class="page-label">Step 2 of 3</div>
    <div class="page-title">Forecast Parameters</div>
    <div class="page-sub">Enter the target day details to generate an accurate ED demand forecast.</div>
    <div class="page-divider"></div>
    """)

# ── Form ─────────────────────────────────────────────────────────────────
with st.form("forecast_form"):
    # Section 1 — Date & Time
    st.html("""
        <div class="section-header">
            <div class="section-icon">
                <svg viewBox="0 0 24 24">
                    <rect x="3" y="4" width="18" height="18" rx="2"/>
                    <line x1="16" y1="2" x2="16" y2="6"/>
                    <line x1="8" y1="2" x2="8" y2="6"/>
                    <line x1="3" y1="10" x2="21" y2="10"/>
                </svg>
            </div>
            <span class="section-label">Date &amp; Time</span>
        </div>
        """)

    col1, col2 = st.columns(2)
    with col1:
        date = st.date_input("Target Date")
    with col2:
        start_hour = st.slider("Start Hour for Hourly Forecast", 0, 23, current_hour, format="%d:00")

    # Section 2 — Weather
    st.html("""
        <div class="sep"></div>
        <div class="section-header">
            <div class="section-icon">
                <svg viewBox="0 0 24 24">
                    <path d="M12 2v6M12 18v4M4.93 4.93l4.24 4.24M14.83 14.83l4.24 4.24
                             M2 12h6M18 12h4M4.93 19.07l4.24-4.24M14.83 9.17l4.24-4.24"/>
                </svg>
            </div>
            <span class="section-label">Weather Conditions</span>
        </div>
        """)

    col3, col4, col5 = st.columns(3)
    with col3:
        avg_weather_C = st.number_input("Average Temperature (°C)", value=30.0, step=0.5)
    with col4:
        avg_precip = st.number_input("Average Precipitation (mm)", value=0.0, step=0.1, min_value=0.0)
    with col5:
        avg_snow = st.number_input("Average Snow (cm)", value=0.0, step=0.1, min_value=0.0)

    # Section 3 — Day Classification
    st.html("""
        <div class="sep"></div>
        <div class="section-header">
            <div class="section-icon">
                <svg viewBox="0 0 24 24">
                    <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
                    <circle cx="9" cy="7" r="4"/>
                    <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
                    <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
                </svg>
            </div>
            <span class="section-label">Day Classification</span>
        </div>
        """)

    col6, col7 = st.columns(2)
    with col6:
        is_weekend = st.selectbox("Is Weekend?", [0, 1],
                                  format_func=lambda x: "Weekday" if x == 0 else "Weekend")
    with col7:
        is_holiday = st.selectbox("Is Holiday?", [0, 1],
                                  format_func=lambda x: "Regular Day" if x == 0 else "Public Holiday")

    st.html("""
        <div class="info-band">
            <svg viewBox="0 0 24 24">
                <circle cx="12" cy="12" r="10"/>
                <line x1="12" y1="8" x2="12" y2="12"/>
                <line x1="12" y1="16" x2="12.01" y2="16"/>
            </svg>
            The forecast will cover the
            <strong style="color:#1560a8; margin: 0 4px;">next 7 days</strong>
            from the target date, with hourly breakdown starting from the selected hour.
        </div>
        <br>
        """)

    submitted = st.form_submit_button("Generate Forecast →")

# ── Back button ──────────────────────────────────────────────────────────
st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
col_back, col_mid, col_right = st.columns([1, 2, 1])
with col_back:
    if st.button("← Back to Welcome"):
        st.session_state.page = "welcome"
        st.rerun()

# ── On submit ────────────────────────────────────────────────────────────
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
        daily_df = predict_daily(user_input)
        hourly_df = predict_hourly(user_input)

        first_day_prediction = daily_df.iloc[0]["Predicted_ED_Visits"]
        hourly_sum = hourly_df["Predicted_ED_Visits"].sum()
        target_12h_total = first_day_prediction * 0.5

        if hourly_sum > 0:
            hourly_df["Predicted_ED_Visits"] = (
                                                       hourly_df["Predicted_ED_Visits"] / hourly_sum
                                               ) * target_12h_total

        hourly_df["Predicted_ED_Visits"] = (
            hourly_df["Predicted_ED_Visits"].round().astype(int)
        )

    st.session_state.daily_df = daily_df
    st.session_state.hourly_df = hourly_df
    st.session_state.page = "results"
    st.rerun()