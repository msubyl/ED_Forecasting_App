import numpy as np
import pandas as pd


def calculate_monitoring_metrics_from_df(
    test_df,
    model_name,
    actual_col="ED_visits",
    pred_col="Predicted_ED_Visits"
):
    y_true = test_df[actual_col].astype(float)
    y_pred = test_df[pred_col].astype(float)

    mae = np.mean(np.abs(y_true - y_pred))
    rmse = np.sqrt(np.mean((y_true - y_pred) ** 2))

    non_zero_mask = y_true != 0

    if non_zero_mask.sum() > 0:
        mape = np.mean(
            np.abs(
                (y_true[non_zero_mask] - y_pred[non_zero_mask])
                / y_true[non_zero_mask]
            )
        ) * 100
    else:
        mape = np.nan

    actual_mean = y_true.mean()
    pred_mean = y_pred.mean()

    actual_std = y_true.std()
    pred_std = y_pred.std()

    mean_shift = abs(pred_mean - actual_mean)
    std_shift = abs(pred_std - actual_std)

    mae_ratio = mae / actual_mean if actual_mean != 0 else np.nan
    rmse_ratio = rmse / actual_mean if actual_mean != 0 else np.nan
    std_shift_ratio = std_shift / actual_std if actual_std != 0 else np.nan

    # ═════════════════════════════════════════════════════════════════════
    # Performance Status
    # Measures prediction accuracy using MAE and RMSE relative to actual mean.
    # ═════════════════════════════════════════════════════════════════════

    if mae_ratio <= 0.25 and rmse_ratio <= 0.35:
        performance_status = "Good"
        performance_icon = "🟢"
        performance_issue = (
            f"{model_name} performance on the test set is within an acceptable range."
        )
    elif mae_ratio <= 0.45 and rmse_ratio <= 0.60:
        performance_status = "Needs Monitoring"
        performance_icon = "🟡"
        performance_issue = (
            f"{model_name} performance shows moderate error and should be monitored."
        )
    else:
        performance_status = "Needs Review"
        performance_icon = "🔴"
        performance_issue = (
            f"{model_name} performance shows high error and may require model review."
        )

    # ═════════════════════════════════════════════════════════════════════
    # Mean Shift Status
    # Measures whether prediction mean is far from actual test-set mean.
    # ═════════════════════════════════════════════════════════════════════

    if actual_std == 0 or np.isnan(actual_std):
        mean_shift_status = "Unknown"
        mean_shift_icon = "⚪"
        mean_shift_issue = "Mean shift cannot be evaluated because actual std is zero."
    elif mean_shift <= 0.5 * actual_std:
        mean_shift_status = "Low"
        mean_shift_icon = "🟢"
        mean_shift_issue = "Prediction mean is close to the actual test-set mean."
    elif mean_shift <= actual_std:
        mean_shift_status = "Medium"
        mean_shift_icon = "🟡"
        mean_shift_issue = "Prediction mean shows a moderate shift from the actual test-set mean."
    else:
        mean_shift_status = "High"
        mean_shift_icon = "🔴"
        mean_shift_issue = "Prediction mean is far from the actual test-set mean."

    # ═════════════════════════════════════════════════════════════════════
    # Standard Deviation Shift Status
    # Measures whether prediction variation is far from actual variation.
    # ═════════════════════════════════════════════════════════════════════

    if np.isnan(std_shift_ratio):
        std_shift_status = "Unknown"
        std_shift_icon = "⚪"
        std_shift_issue = "Std shift cannot be evaluated because actual std is zero."
    elif std_shift_ratio <= 0.30:
        std_shift_status = "Low"
        std_shift_icon = "🟢"
        std_shift_issue = "Prediction variation is close to the actual test-set variation."
    elif std_shift_ratio <= 0.60:
        std_shift_status = "Medium"
        std_shift_icon = "🟡"
        std_shift_issue = "Prediction variation differs moderately from the actual test-set variation."
    else:
        std_shift_status = "High"
        std_shift_icon = "🔴"
        std_shift_issue = "Prediction variation is very different from the actual test-set variation."

    # ═════════════════════════════════════════════════════════════════════
    # Overall Monitoring Status
    # Important:
    # Bad performance is not always drift.
    # Drift is based on mean/std shift.
    # Performance is based on MAE/RMSE.
    # ═════════════════════════════════════════════════════════════════════

    if (
        performance_status == "Needs Review"
        and (mean_shift_status == "High" or std_shift_status == "High")
    ):
        monitoring_status = "High Drift Risk"
        monitoring_icon = "🔴"
        recommendation = (
            "Review the model predictions, preprocessing steps, and test-set distribution. "
            "Retraining may be needed if both high error and distribution drift continue."
        )
        alert_bg = "#fff1f1"
        alert_border = "#f1b6b6"
        alert_color = "#b42318"

    elif mean_shift_status == "High" or std_shift_status == "High":
        monitoring_status = "High Drift Risk"
        monitoring_icon = "🔴"
        recommendation = (
            "A strong distribution shift is detected. Review the test-set distribution, "
            "recent input data, and preprocessing steps. Retraining may be needed if this drift continues."
        )
        alert_bg = "#fff1f1"
        alert_border = "#f1b6b6"
        alert_color = "#b42318"

    elif performance_status == "Needs Review":
        monitoring_status = "Performance Needs Review"
        monitoring_icon = "🟡"
        recommendation = (
            "No strong drift is detected because the predicted mean and standard deviation "
            "are close to the actual test-set distribution. However, prediction error is high, "
            "so review the model accuracy, low-visit hours, and preprocessing steps."
        )
        alert_bg = "#fff8e8"
        alert_border = "#f0d28a"
        alert_color = "#b87900"

    elif (
        performance_status == "Needs Monitoring"
        or mean_shift_status == "Medium"
        or std_shift_status == "Medium"
    ):
        monitoring_status = "Medium Drift Risk"
        monitoring_icon = "🟡"
        recommendation = (
            "Continue monitoring the model. Some performance or distribution indicators "
            "show moderate risk, but the model is not failing."
        )
        alert_bg = "#fff8e8"
        alert_border = "#f0d28a"
        alert_color = "#b87900"

    else:
        monitoring_status = "Low Drift Risk"
        monitoring_icon = "🟢"
        recommendation = (
            "Model performance and prediction distribution look stable on the test set."
        )
        alert_bg = "#eaf4ff"
        alert_border = "#d0e4f5"
        alert_color = "#1560a8"

    return {
        "mae": mae,
        "rmse": rmse,
        "mape": mape,
        "actual_mean": actual_mean,
        "pred_mean": pred_mean,
        "actual_std": actual_std,
        "pred_std": pred_std,
        "mean_shift": mean_shift,
        "std_shift": std_shift,
        "mae_ratio": mae_ratio,
        "rmse_ratio": rmse_ratio,
        "std_shift_ratio": std_shift_ratio,
        "performance_status": performance_status,
        "performance_icon": performance_icon,
        "performance_issue": performance_issue,
        "mean_shift_status": mean_shift_status,
        "mean_shift_icon": mean_shift_icon,
        "mean_shift_issue": mean_shift_issue,
        "std_shift_status": std_shift_status,
        "std_shift_icon": std_shift_icon,
        "std_shift_issue": std_shift_issue,
        "monitoring_status": monitoring_status,
        "monitoring_icon": monitoring_icon,
        "recommendation": recommendation,
        "alert_bg": alert_bg,
        "alert_border": alert_border,
        "alert_color": alert_color,
    }
