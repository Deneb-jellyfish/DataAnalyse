# RandomForest Baseline Notes

## Setup
- Features: `outputs\features\X_train.npy` / `outputs\features\X_test.npy`
- Labels: `outputs\features\y_train.npy` / `outputs\features\y_test.npy`
- Split alignment: `outputs\features\split_index.csv`
- Model: `RandomForestRegressor(n_estimators=100, random_state=42)`

## Test Metrics
- MSE: **0.602919**
- RMSE: **0.776479**
- MAE: **0.522847**

## Outputs
- Model: `outputs\models\rf_baseline.joblib`
- Predictions: `outputs\features\predictions_rf.csv`
- Metrics CSV: `outputs\logs\rf_baseline_metrics.csv`
