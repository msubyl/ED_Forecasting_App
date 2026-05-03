import pandas as pd
import numpy as np

from utils.load_models import load_daily_model, load_hourly_model
from utils.preprocessing import add_time_features_daily, add_time_features_hourly


def extract_median_prediction(predictions):
    """
    TFT with QuantileLoss may return multiple quantiles.
    This function extracts the median prediction safely.
    """
    if hasattr(predictions, "detach"):
        preds = predictions.detach().cpu().numpy()
    elif hasattr(predictions, "cpu"):
        preds = predictions.cpu().numpy()
    else:
        preds = np.array(predictions)

    if preds.ndim == 3:
        preds = preds[:, :, preds.shape[2] // 2]

    return preds.flatten()


def inverse_standard_scale(preds, original_series):
    """
    Used for the daily model.
    Converts normalized predictions back to the original ED_visits scale.
    """
    mean_val = original_series.mean()
    std_val = original_series.std()

    values = preds * std_val + mean_val
    values = np.maximum(values, 0)
    values = np.round(values).astype(int)

    return values


def predict_daily(user_input):
    model, dataset = load_daily_model()

    df = pd.read_csv("data/clean_ED_data.csv")
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").reset_index(drop=True)

    df["series_id"] = "ED_1"
    df = add_time_features_daily(df)

    target_date = pd.to_datetime(user_input["date"])

    # Daily model setting from training:
    # max_encoder_length = 60
    # max_prediction_length = 14
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

        # Future target is unknown
        new_row["ED_visits"] = 0

        # User inputs
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
    ).to_dataloader(train=False, batch_size=64, num_workers=0)

    predictions = model.predict(dataloader)
    preds = extract_median_prediction(predictions)

    daily_values = inverse_standard_scale(
        preds,
        df["ED_visits"]
    )

    n = min(len(future_df), len(daily_values))

    result = pd.DataFrame({
        "Date": future_df["date"].dt.date.astype(str).values[:n],
        "Predicted_ED_Visits": daily_values[:n]
    })

    daily_xai = {
    "model": model,
    "training_dataset": dataset,
    "future_df": prediction_data
    }


    return result, daily_xai


def predict_hourly(user_input):
    model, dataset = load_hourly_model()

    df = pd.read_csv("data/clean_ED_data_hours.csv")

    df["datetime"] = pd.to_datetime(df["datetime"])
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("datetime").reset_index(drop=True)

    df["series_id"] = "ED_1"
    df = add_time_features_hourly(df)

    # Hourly model setting from training:
    # max_encoder_length = 48
    # max_prediction_length = 12
    history_df = df.tail(48).copy()

    last_time_idx = int(history_df["time_idx"].iloc[-1])
    last_row = history_df.iloc[-1].copy()

    start_datetime = pd.to_datetime(user_input["date"]) + pd.Timedelta(
        hours=int(user_input["start_hour"])
    )

    future_rows = []

    for i in range(12):
        future_datetime = start_datetime + pd.Timedelta(hours=i)

        new_row = last_row.copy()
        new_row["datetime"] = future_datetime
        new_row["date"] = future_datetime.date()
        new_row["hour"] = future_datetime.hour
        new_row["min"] = 0
        new_row["time_idx"] = last_time_idx + i + 1
        new_row["series_id"] = "ED_1"

        # Future target is unknown
        new_row["ED_visits"] = 0

        # User inputs
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
    prediction_data = add_time_features_hourly(prediction_data)
    prediction_data["series_id"] = "ED_1"

    dataloader = dataset.from_dataset(
        dataset,
        prediction_data,
        predict=True,
        stop_randomization=True
    ).to_dataloader(train=False, batch_size=64, num_workers=0)

    predictions = model.predict(dataloader)
    preds = extract_median_prediction(predictions)

    # Hourly model was trained using log1p(ED_visits),
    # so we reverse it with expm1.
    hourly_values = np.expm1(preds)
    hourly_values = np.maximum(hourly_values, 0)
    hourly_values = np.round(hourly_values).astype(int)

    n = min(len(future_df), len(hourly_values))

    result = pd.DataFrame({
        "Time": future_df["datetime"].dt.strftime("%Y-%m-%d %H:%M").values[:n],
        "Hour": future_df["hour"].values[:n],
        "Predicted_ED_Visits": hourly_values[:n]
    })

    return result
