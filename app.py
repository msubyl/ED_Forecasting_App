import streamlit as st
from datetime import datetime
from utils.prediction import predict_daily, predict_hourly

st.set_page_config(
    page_title="Marsad",
    page_icon="🏥",
    layout="wide"
)

# -------------------------
# Session State
# -------------------------
if "page" not in st.session_state:
    st.session_state.page = "welcome"

if "user_input" not in st.session_state:
    st.session_state.user_input = None

if "daily_df" not in st.session_state:
    st.session_state.daily_df = None

if "hourly_df" not in st.session_state:
    st.session_state.hourly_df = None


# -------------------------
# CSS
# -------------------------
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background:
        radial-gradient(circle at top left, rgba(47,128,196,0.22), transparent 24%),
        radial-gradient(circle at bottom right, rgba(47,128,196,0.22), transparent 26%),
        linear-gradient(180deg, #ffffff 0%, #f4f9ff 100%);
}

[data-testid="block-container"] {
    padding-top: 2rem;
    max-width: 1300px;
}

.title {
    text-align: center;
    font-size: 58px;
    font-weight: 800;
    color: #1f6fae;
    margin-top: 8px;
}

.subtitle {
    text-align: center;
    font-size: 22px;
    color: #075ba8;
    margin-bottom: 28px;
}

.description {
    text-align: center;
    font-size: 20px;
    color: #0f2545;
    max-width: 900px;
    margin: auto;
    line-height: 1.7;
}

.section-title {
    text-align: center;
    font-size: 28px;
    font-weight: 800;
    color: #075ba8;
    margin-top: 42px;
    margin-bottom: 25px;
}

.feature-card {
    background: rgba(255,255,255,0.95);
    border: 1px solid #dbeeff;
    border-radius: 20px;
    padding: 30px 22px;
    min-height: 255px;
    text-align: center;
    box-shadow: 0 14px 34px rgba(31,111,174,0.12);
}

.icon-circle {
    width: 78px;
    height: 78px;
    background: #e9f3ff;
    color: #1f6fae;
    border-radius: 50%;
    margin: 0 auto 18px auto;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 38px;
    font-weight: 800;
}

.feature-card h4 {
    color: #075ba8;
    font-size: 23px;
    line-height: 1.25;
    margin-bottom: 20px;
}

.feature-card p {
    color: #0f2545;
    font-size: 16px;
    line-height: 1.55;
}

.bottom-box {
    background: #eaf4ff;
    color: #0f2545;
    border-radius: 18px;
    padding: 24px 36px;
    max-width: 760px;
    margin: 35px auto 20px auto;
    font-size: 20px;
    line-height: 1.55;
    box-shadow: 0 10px 28px rgba(31,111,174,0.10);
    text-align: center;
}

div.stButton {
    display: flex;
    justify-content: center;
}

div.stButton > button {
    background: linear-gradient(90deg, #1f6fae, #4a9be0);
    color: white;
    width: 320px;
    height: 56px;
    border-radius: 12px;
    border: none;
    font-size: 19px;
    font-weight: 700;
}

div.stButton > button:hover {
    background: linear-gradient(90deg, #155f99, #3488cf);
    color: white;
}
</style>
""", unsafe_allow_html=True)


# -------------------------
# Page 1: Welcome
# -------------------------
if st.session_state.page == "welcome":

    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        st.image("assets/logo.png", width=160)

    st.markdown('<div class="title">Marsad</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="subtitle">Emergency Department Forecasting System</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="description">
        Marsad is an intelligent predictive system that uses artificial intelligence 
        and machine learning to forecast patient demand in emergency departments.
        <br><br>
        The system analyzes historical data along with key external factors such as 
        weather conditions, holidays, and time patterns to generate accurate predictions.
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-title">It helps hospitals to:</div>',
        unsafe_allow_html=True
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(
            """
            <div class="feature-card">
                <div class="icon-circle">◎</div>
                <h4>Reduce overcrowding</h4>
                <p>Anticipate patient surges and manage capacity effectively.</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            """
            <div class="feature-card">
                <div class="icon-circle">▣</div>
                <h4>Optimize staff and resource allocation</h4>
                <p>Align the right resources with predicted demand.</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:
        st.markdown(
            """
            <div class="feature-card">
                <div class="icon-circle">◷</div>
                <h4>Minimize patient waiting times</h4>
                <p>Improve patient flow and enhance overall experience.</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col4:
        st.markdown(
            """
            <div class="feature-card">
                <div class="icon-circle">↗</div>
                <h4>Support proactive decision-making</h4>
                <p>Enable data-driven decisions for better preparedness.</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown(
        """
        <div class="bottom-box">
        Marsad transforms data into actionable insights, enabling smarter and more efficient healthcare operations.
        </div>
        """,
        unsafe_allow_html=True
    )

    if st.button("Start Forecasting"):
        st.session_state.page = "input"
        st.rerun()


# -------------------------
# Page 2: Input
# -------------------------
elif st.session_state.page == "input":

    st.title("Forecast Input")
    st.write("Please enter the target day information to generate the forecast.")

    current_hour = datetime.now().hour

    with st.form("forecast_form"):
        col1, col2 = st.columns(2)

        with col1:
            date = st.date_input("Target Date")
            start_hour = st.slider(
                "Start Hour for Hourly Forecast",
                min_value=0,
                max_value=23,
                value=current_hour
            )
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

            # Post-processing:
            # The hourly model predicts the next 12 hours.
            # We scale the 12-hour total to represent half of the daily forecast.
            hourly_sum = hourly_df["Predicted_ED_Visits"].sum()
            target_12h_total = first_day_prediction * 0.5

            if hourly_sum > 0:
                hourly_df["Predicted_ED_Visits"] = (
                    hourly_df["Predicted_ED_Visits"] / hourly_sum
                ) * target_12h_total

            hourly_df["Predicted_ED_Visits"] = (
                hourly_df["Predicted_ED_Visits"]
                .round()
                .astype(int)
            )

        st.session_state.daily_df = daily_df
        st.session_state.hourly_df = hourly_df
        st.session_state.page = "results"
        st.rerun()

    if st.button("Back to Welcome"):
        st.session_state.page = "welcome"
        st.rerun()


# -------------------------
# Page 3: Results
# -------------------------
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
            st.line_chart(
                daily_df.set_index("Date")["Predicted_ED_Visits"]
            )
            st.dataframe(daily_df)

        st.divider()

        st.subheader("Next 12-Hour Forecast")

        st.caption(
            "The hourly forecast shows the expected patient flow for the next 12 hours "
            "starting from the selected hour."
        )

        st.line_chart(
            hourly_df.set_index("Time")["Predicted_ED_Visits"]
        )

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