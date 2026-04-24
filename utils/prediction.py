from turtle import st

import pandas as pd
from utils.load_models import load_daily_model, load_hourly_model
from utils.preprocessing import add_time_features_daily, add_time_features_hourly
import numpy as np

def predict_daily(user_input):
    model, dataset = load_daily_model()

    df = pd.read_csv("data/clean_ED_data.csv")
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").reset_index(drop=True)

    df["series_id"] = "ED_1"
    df = add_time_features_daily(df)

    target_date = pd.to_datetime(user_input["date"])


    history_df = df[df["date"] < target_date].tail(60).copy()


    if len(history_df) < 60:
        history_df = df.tail(60).copy()

    last_time_idx = int(history_df["time_idx"].iloc[-1])
    last_row = history_df.iloc[-1].copy()

    future_rows = []

    for i in range(14):
        future_date = target_date + pd.Timedelta(days=i)

        new_row = last_row.copy()
        new_row["date"] = future_date
        new_row["time_idx"] = last_time_idx + i + 1
        new_row["series_id"] = "ED_1"

        new_row["ED_visits"] = 0
        new_row["avg_weather_C"] = user_input["avg_weather_C"]
        new_row["avg_precip"] = user_input["avg_precip"]
        new_row["avg_snow"] = user_input["avg_snow"]
        new_row["is_weekend"] = user_input["is_weekend"]
        new_row["is_holiday"] = user_input["is_holiday"]

        if "season" in history_df.columns:
            new_row["season"] = user_input.get("season", last_row["season"])

        future_rows.append(new_row)

    future_df = pd.DataFrame(future_rows)

    prediction_data = pd.concat([history_df, future_df], ignore_index=True)

    prediction_data = add_time_features_daily(prediction_data)
    prediction_data["series_id"] = "ED_1"

    dataloader = dataset.from_dataset(
        dataset,
        prediction_data,
        predict=True,
        stop_randomization=True
    ).to_dataloader(train=False, batch_size=1)

    prediction = model.predict(dataloader)

    raw_preds = prediction[0].detach().cpu().numpy().flatten()

    mean_val = df["ED_visits"].mean()
    std_val = df["ED_visits"].std()

    daily_values = raw_preds * std_val + mean_val
    daily_values = daily_values.round().astype(int)
    daily_values = np.maximum(daily_values, 0)

    result = pd.DataFrame({
        "Date": future_df["date"].dt.date.astype(str).values,
        "Predicted_ED_Visits": daily_values
    })

    return result


def predict_hourly(user_input):
    model, dataset = load_hourly_model()

    df = pd.read_csv("data/clean_ED_data_hours.csv")

    df["datetime"] = pd.to_datetime(df["datetime"])
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("datetime").reset_index(drop=True)

    df["series_id"] = "ED_1"
    df = add_time_features_hourly(df)

    last_row = df.iloc[-1].copy()
    last_time_idx = int(last_row["time_idx"])
    last_datetime = pd.to_datetime(last_row["datetime"])

    future_rows = []

    # نجهز 24 ساعة مستقبلية، لكن المودل سيُخرج حسب horizon الذي تدرب عليه
    for i in range(24):
        future_datetime = last_datetime + pd.Timedelta(hours=i + 1)

        new_row = last_row.copy()
        new_row["datetime"] = future_datetime
        new_row["date"] = future_datetime.date()
        new_row["hour"] = future_datetime.hour
        new_row["min"] = 0
        new_row["time_idx"] = last_time_idx + i + 1
        new_row["series_id"] = "ED_1"

        new_row["ED_visits"] = 0
        new_row["avg_weather_C"] = user_input["avg_weather_C"]
        new_row["avg_precip"] = user_input["avg_precip"]
        new_row["avg_snow"] = user_input["avg_snow"]
        new_row["is_weekend"] = user_input["is_weekend"]
        new_row["is_holiday"] = user_input["is_holiday"]

        if "season" in df.columns:
            new_row["season"] = user_input.get("season", last_row["season"])

        future_rows.append(new_row)

    future_df = pd.DataFrame(future_rows)

    full_df = pd.concat([df, future_df], ignore_index=True)
    full_df = add_time_features_hourly(full_df)
    full_df["series_id"] = "ED_1"

    prediction_data = full_df.tail(200)

    dataloader = dataset.from_dataset(
        dataset,
        prediction_data,
        predict=True,
        stop_randomization=True
    ).to_dataloader(train=False, batch_size=1)

    prediction = model.predict(dataloader)

    raw_preds = prediction[0].detach().cpu().numpy().flatten()

    mean_val = df["ED_visits"].mean()
    std_val = df["ED_visits"].std()

    hourly_values = raw_preds * std_val + mean_val

    result = pd.DataFrame({
        "Hour": list(range(len(hourly_values))),
        "Predicted_ED_Visits": hourly_values
    })

    return result