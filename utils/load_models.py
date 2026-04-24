import streamlit as st
import torch
from pytorch_forecasting import TemporalFusionTransformer, TimeSeriesDataSet


def load_dataset_safely(path):
    original_torch_load = torch.load

    def patched_torch_load(*args, **kwargs):
        kwargs["weights_only"] = False
        return original_torch_load(*args, **kwargs)

    torch.load = patched_torch_load
    dataset = TimeSeriesDataSet.load(path)
    torch.load = original_torch_load

    return dataset


@st.cache_resource
def load_daily_model():
    model = TemporalFusionTransformer.load_from_checkpoint(
        "models/tft_model.ckpt",
        map_location=torch.device("cpu"),
        weights_only=False
    )

    dataset = load_dataset_safely("models/dataset.pkl")

    return model, dataset


@st.cache_resource
def load_hourly_model():
    model = TemporalFusionTransformer.load_from_checkpoint(
        "models/tft_model_hours.ckpt",
        map_location=torch.device("cpu"),
        weights_only=False
    )

    dataset = load_dataset_safely("models/dataset_hours.pkl")

    return model, dataset