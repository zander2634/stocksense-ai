"""
Train XGBoost model for demand forecasting.
"""

import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib
import os

def load_data():
    """Load sales data"""
    data_path = os.path.join(os.path.dirname(__file__), "data", "sales_data.csv")
    df = pd.read_csv(data_path)
    df['date'] = pd.to_datetime(df['date'])
    return df

def engineer_features(df):
    """Create features for ML model"""
    df = df.sort_values(['product_id', 'date']).reset_index(drop=True)
    
    # Lag features (previous days' sales)
    for lag in [1, 3, 7, 14, 30]:
        df[f'lag_{lag}'] = df.groupby('product_id')['quantity_sold'].shift(lag)
    
    # Rolling averages
    for window in [7, 14, 30]:
        df[f'rolling_mean_{window}'] = df.groupby('product_id')['quantity_sold'].transform(
            lambda x: x.rolling(window, min_periods=1).mean()
        )
    
    # Rolling std (volatility)
    df['rolling_std_7'] = df.groupby('product_id')['quantity_sold'].transform(
        lambda x: x.rolling(7, min_periods=1).std()
    )
    
    return df

def train_model():
    """Train XGBoost regression model"""
    
    print("📊 Loading data...")
    df = load_data()
    print(f"   Loaded {len(df)} records")
    
    print("🔧 Engineering features...")
    df = engineer_features(df)
    
    # Drop rows with NaN (from lag features)
    df = df.dropna()
    print(f"   After feature engineering: {len(df)} records")
    
    # Define features and target
    feature_cols = [
        'product_id', 'day_of_week', 'day_of_month', 'month',
        'lag_1', 'lag_3', 'lag_7', 'lag_14', 'lag_30',
        'rolling_mean_7', 'rolling_mean_14', 'rolling_mean_30',
        'rolling_std_7'
    ]
    
    X = df[feature_cols]
    y = df['quantity_sold']
    
    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    print(f"📈 Training set: {len(X_train)} | Test set: {len(X_test)}")
    
    # Train XGBoost
    print("🤖 Training XGBoost model...")
    model = xgb.XGBRegressor(
        n_estimators=100,
        max_depth=6,
        learning_rate=0.1,
        objective='reg:squarederror',
        random_state=42
    )
    
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)
    
    print(f"\n📊 Model Performance:")
    print(f"   MAE:  {mae:.2f}")
    print(f"   RMSE: {rmse:.2f}")
    print(f"   R²:   {r2:.4f}")
    
    # Save model
    model_path = os.path.join(os.path.dirname(__file__), "models", "xgboost_model.pkl")
    joblib.dump(model, model_path)
    print(f"\n✅ Model saved to: {model_path}")
    
    # Save feature columns for prediction
    features_path = os.path.join(os.path.dirname(__file__), "models", "features.pkl")
    joblib.dump(feature_cols, features_path)
    
    return model

if __name__ == "__main__":
    train_model()