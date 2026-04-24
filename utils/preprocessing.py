import pandas as pd
import numpy as np


def add_time_features_daily(df):
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").reset_index(drop=True)

    df["time_idx"] = range(len(df))
    df["series_id"] = "ED_1"
    df["series_id"] = df["series_id"].astype(str)

    df["dayofweek"] = df["date"].dt.dayofweek
    df["month"] = df["date"].dt.month

    df["dow_sin"] = np.sin(2 * np.pi * df["dayofweek"] / 7)
    df["dow_cos"] = np.cos(2 * np.pi * df["dayofweek"] / 7)

    df["month_sin"] = np.sin(2 * np.pi * df["month"] / 12)
    df["month_cos"] = np.cos(2 * np.pi * df["month"] / 12)

    return df


def add_time_features_hourly(df):
    df["datetime"] = pd.to_datetime(df["datetime"])
    df = df.sort_values("datetime").reset_index(drop=True)

    df["time_idx"] = range(len(df))
    df["series_id"] = "ED_1"
    df["series_id"] = df["series_id"].astype(str)

    df["hour_sin"] = np.sin(2 * np.pi * df["hour"] / 24)
    df["hour_cos"] = np.cos(2 * np.pi * df["hour"] / 24)

    df["date"] = pd.to_datetime(df["date"])
    df["dayofweek"] = df["date"].dt.dayofweek
    df["month"] = df["date"].dt.month

    df["dow_sin"] = np.sin(2 * np.pi * df["dayofweek"] / 7)
    df["dow_cos"] = np.cos(2 * np.pi * df["dayofweek"] / 7)

    df["month_sin"] = np.sin(2 * np.pi * df["month"] / 12)
    df["month_cos"] = np.cos(2 * np.pi * df["month"] / 12)

    return df
