import streamlit as st
from datetime import datetime
import base64
from pathlib import Path
from utils.prediction import predict_daily, predict_hourly

st.markdown("""
<style>
/* إزالة الفراغات بالكامل */
html, body, [data-testid="stAppViewContainer"] {
    margin: 0 !important;
    padding: 0 !important;
}

/* إزالة padding الافتراضي */
[data-testid="block-container"] {
    padding: 0 !important;
    max-width: 100% !important;
}

/* إخفاء السايدبار نهائياً */
[data-testid="stSidebar"] {
    display: none !important;
}

/* يخلي الصفحة تملى العرض كامل */
.main {
    padding: 0 !important;
}
</style>
""", unsafe_allow_html=True)

st.set_page_config(page_title="Marsad", page_icon="🏥", layout="wide")


def image_to_base64(path):
    return base64.b64encode(Path(path).read_bytes()).decode()


logo_base64 = image_to_base64("assets/logo.png")

if "page" not in st.session_state:
    st.session_state.page = "welcome"

if "user_input" not in st.session_state:
    st.session_state.user_input = None

if "daily_df" not in st.session_state:
    st.session_state.daily_df = None

if "hourly_df" not in st.session_state:
    st.session_state.hourly_df = None


st.html(f"""
<style>
[data-testid="block-container"] {{
    padding: 0 !important;
    max-width: 100% !important;
}}

[data-testid="stAppViewContainer"] {{
    background: linear-gradient(180deg, #ffffff 0%, #f5fbff 100%) !important;
}}

.welcome-page {{
    min-height: 100vh;
    text-align: center;
    padding: 20px 60px 40px 60px;
    font-family: Arial, sans-serif;
    position: relative;
    overflow: hidden;
    position: relative;
    z-index: 1;   
}}

.shape-left {{
    position: absolute;
    top: -140px;
    left: -120px;
    width: 360px;
    height: 340px;
    background: #2f80c4;
    border-bottom-right-radius: 230px;
    z-index: 0;
}}

.shape-right {{
    position: absolute;
    bottom: -220px;
    right: -160px;
    width: 420px;
    height: 340px;
    background: #2f80c4;
    border-top-left-radius: 250px;
    z-index: 0;
}}

.logo {{
    width: 330px;
    display: block;
    margin: -20px auto -25px auto;
}}

.subtitle {{
    color: #075ba8;
    font-size: 24px;
    margin-bottom: 24px;
}}

.desc {{
    max-width: 900px;
    margin: auto;
    color: #0f2545;
    font-size: 20px;
    line-height: 1.6;
}}

.help-title {{
    margin: 34px 0 22px 0;
    color: #075ba8;
    font-size: 28px;
    font-weight: 800;
}}

.cards {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 22px;
    max-width: 1120px;
    margin: auto;
}}

.card {{
    background: white;
    border: 1px solid #dbeeff;
    border-radius: 18px;
    padding: 24px 18px;
    min-height: 215px;
    box-shadow: 0 12px 28px rgba(31,111,174,0.12);
}}

.card h4 {{
    color: #075ba8;
    font-size: 21px;
    font-weight: 800;
}}

.card p {{
    color: #0f2545;
    font-size: 15px;
}}

.bottom-box {{
    background: #eaf4ff;
    max-width: 720px;
    margin: 28px auto 20px auto;
    padding: 20px 34px;
    border-radius: 18px;
    color: #0f2545;
    font-size: 18px;
}}
.icon {{
    width: 70px;
    height: 70px;
    margin: 0 auto 14px auto;
    border-radius: 50%;
    background: #e9f3ff;
    display: flex;
    align-items: center;
    justify-content: center;
}}

.icon svg {{
width: 40px;
    height: 40px;
    stroke: #1f6fae;
    stroke-width: 2.8;
    fill: none;
    stroke-linecap: round;
    stroke-linejoin: round;
    }}
.logo,
.subtitle,
.desc,
.help-title,
.cards,
.bottom-box {{
    position: relative;
    z-index: 2;
}}

.welcome-page {{
    position: relative;
    overflow: hidden;
}}

div.stButton {{
    display: flex;
    justify-content: center;
}}

div.stButton > button {{
    width: 310px;
    height: 55px;
    border-radius: 12px;
    border: none;
    color: white;
    font-size: 19px;
    font-weight: 700;
    background: linear-gradient(90deg, #1f6fae, #4a9be0);
}}

</style>
""")


if st.session_state.page == "welcome":

    st.html(f"""
    <div class="welcome-page">
        <div class="shape-left"></div>
        <div class="shape-right"></div>

        <img class="logo" src="data:image/png;base64,{logo_base64}">

        <div class="subtitle">Emergency Department Forecasting System</div>

        <div class="desc">
            Marsad is an intelligent predictive system that uses artificial intelligence
            and machine learning to forecast patient demand in emergency departments.
            <br><br>
            The system analyzes historical data along with key external factors such as
            weather conditions, holidays, and time patterns to generate accurate predictions.
        </div>

        <div class="help-title">It helps hospitals to:</div>

        <div class="cards">
            <div class="card">
                <svg viewBox="0 0 24 24">
                <circle cx="9" cy="8" r="3"></circle>
                <circle cx="16" cy="9" r="2.5"></circle>
                <path d="M3 20c0-4 3-7 7-7"></path>
                <path d="M13 14c4 0 7 2.5 7 6"></path>
            </svg>
                <h4>Reduce overcrowding</h4>
                <p>Anticipate patient surges and manage capacity effectively.</p>
            </div>

            <div class="card">
                <svg viewBox="0 0 24 24">
                <path d="M4 19V5"></path>
                <path d="M4 19h16"></path>
                <path d="M7 15l4-4 3 3 5-7"></path>
            </svg>
                <h4>Optimize staff and resource allocation</h4>
                <p>Align the right resources with predicted demand.</p>
            </div>

            <div class="card">
                <svg viewBox="0 0 24 24">
                <circle cx="12" cy="12" r="9"></circle>
                <path d="M12 7v6l4 2"></path>
            </svg>
                <h4>Minimize patient waiting times</h4>
                <p>Improve patient flow and enhance overall experience.</p>
            </div>

            <div class="card">
                <svg viewBox="0 0 24 24">
                <path d="M4 18h16"></path>
                <path d="M7 16v-6"></path>
                <path d="M12 16V8"></path>
                <path d="M17 16V5"></path>
            </svg>
                <h4>Support proactive decision-making</h4>
                <p>Enable data-driven decisions for better preparedness.</p>
            </div>
        </div>

        <div class="bottom-box">
            Marsad transforms data into actionable insights, enabling smarter and more efficient healthcare operations.
        </div>
    </div>
    """)

    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        if st.button("Start Forecasting", use_container_width=True):
            st.session_state.page = "input"
            st.rerun()

elif st.session_state.page == "input":

    st.title("Forecast Input")
    st.write("Please enter the target day information to generate the forecast.")

    current_hour = datetime.now().hour

    with st.form("forecast_form"):
        col1, col2 = st.columns(2)

        with col1:
            date = st.date_input("Target Date")
            start_hour = st.slider("Start Hour for Hourly Forecast", 0, 23, current_hour)
            avg_weather_C = st.number_input("Average Temperature (°C)", value=30.0)

        with col2:
            avg_precip = st.number_input("Average Precipitation", value=0.0)
            avg_snow = st.number_input("Average Snow", value=0.0)
            is_weekend = st.selectbox("Is Weekend?", [0, 1])
            is_holiday = st.selectbox("Is Holiday?", [0, 1])

        submitted = st.form_submit_button("Generate Forecast")

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

            hourly_df["Predicted_ED_Visits"] = hourly_df["Predicted_ED_Visits"].round().astype(int)

        st.session_state.daily_df = daily_df
        st.session_state.hourly_df = hourly_df
        st.session_state.page = "results"
        st.rerun()

    if st.button("Back to Welcome"):
        st.session_state.page = "welcome"
        st.rerun()


elif st.session_state.page == "results":

    st.title("Forecast Results")

    daily_df = st.session_state.daily_df
    hourly_df = st.session_state.hourly_df
    user_input = st.session_state.user_input

    if daily_df is None or hourly_df is None:
        st.warning("No forecast results found. Please enter the forecast information first.")
        if st.button("Go to Input Page"):
            st.session_state.page = "input"
            st.rerun()

    else:
        first_day_prediction = daily_df.iloc[0]["Predicted_ED_Visits"]

        st.subheader("Daily Forecast")

        st.metric(
            label=f"Predicted ED Visits for {user_input['date']}",
            value=f"{first_day_prediction:.0f}"
        )

        with st.expander("Show full 14-day forecast"):
            st.line_chart(daily_df.set_index("Date")["Predicted_ED_Visits"])
            st.dataframe(daily_df)

        st.divider()

        st.subheader("Next 12-Hour Forecast")

        st.caption(
            "The hourly forecast shows the expected patient flow for the next 12 hours "
            "starting from the selected hour."
        )

        st.line_chart(hourly_df.set_index("Time")["Predicted_ED_Visits"])
        st.dataframe(hourly_df)

        st.divider()

        col1, col2 = st.columns(2)

        with col1:
            if st.button("New Forecast", use_container_width=True):
                st.session_state.page = "input"
                st.rerun()

        with col2:
            if st.button("Back to Welcome", use_container_width=True):
                st.session_state.page = "welcome"
                st.rerun()