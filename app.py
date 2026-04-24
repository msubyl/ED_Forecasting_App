import streamlit as st
import pandas as pd
from utils.prediction import predict_daily, predict_hourly

st.set_page_config(
    page_title="ED Forecasting System",
    page_icon="🏥",
    layout="wide"
)

st.title("🏥 Emergency Department Forecasting System")

st.write(
    "This application predicts Emergency Department patient arrivals "
    "using trained Temporal Fusion Transformer models."
)

st.divider()

st.subheader("Enter Target Day Information")

with st.form("forecast_form"):
    col1, col2 = st.columns(2)

    with col1:
        date = st.date_input("Target Date")
        avg_weather_C = st.number_input("Average Temperature (°C)", value=30.0)
        avg_precip = st.number_input("Average Precipitation", value=0.0)

    with col2:
        avg_snow = st.number_input("Average Snow", value=0.0)
        is_weekend = st.selectbox("Is Weekend?", [0, 1])
        is_holiday = st.selectbox("Is Holiday?", [0, 1])

    submitted = st.form_submit_button("Generate Forecast")

if submitted:
    user_input = {
        "date": str(date),
        "avg_weather_C": avg_weather_C,
        "avg_precip": avg_precip,
        "avg_snow": avg_snow,
        "is_weekend": is_weekend,
        "is_holiday": is_holiday,
    }


    st.divider()
    st.subheader("Forecast Results")

    with st.spinner("Generating 14-day daily forecast..."):
        daily_df = predict_daily(user_input)

    st.subheader("Daily Forecast")

    first_day_prediction = daily_df.iloc[0]["Predicted_ED_Visits"]
    adjusted_prediction = first_day_prediction

    # Weekend effect
    if user_input["is_weekend"] == 1:
        adjusted_prediction *= 1.10

    # Holiday effect
    if user_input["is_holiday"] == 1:
        adjusted_prediction *= 1.20

    # High temperature effect
    if user_input["avg_weather_C"] >= 40:
        adjusted_prediction *= 1.05

    # Rain effect
    if user_input["avg_precip"] > 0:
        adjusted_prediction *= 1.03

    adjusted_prediction = round(adjusted_prediction)

    st.metric(
        label="Predicted ED Visits for Selected Day",
        value=f"{adjusted_prediction:.0f}"
    )

    with st.expander("Show full 14-day forecast"):
        st.line_chart(
            daily_df.set_index("Date")["Predicted_ED_Visits"]
        )
        st.dataframe(daily_df)

    st.divider()

    with st.spinner("Generating hourly forecast..."):
        hourly_df = predict_hourly(user_input)
        hourly_sum = hourly_df["Predicted_ED_Visits"].sum()

        if hourly_sum > 0:
            hourly_df["Predicted_ED_Visits"] = (
                                                       hourly_df["Predicted_ED_Visits"] / hourly_sum
                                               ) * adjusted_prediction

        hourly_df["Predicted_ED_Visits"] = hourly_df["Predicted_ED_Visits"].round().astype(int)

        hourly_sum = hourly_df["Predicted_ED_Visits"].sum()

        if hourly_sum > 0:
            hourly_df["Predicted_ED_Visits"] = (
                                                       hourly_df["Predicted_ED_Visits"] / hourly_sum
                                               ) * first_day_prediction

        hourly_df["Predicted_ED_Visits"] = hourly_df["Predicted_ED_Visits"].round().astype(int)

    st.subheader("Hourly Forecast Horizon")
    st.subheader("Hourly Forecast for Selected Day")

    st.line_chart(
        hourly_df.set_index("Hour")["Predicted_ED_Visits"]
    )

    st.dataframe(hourly_df)
