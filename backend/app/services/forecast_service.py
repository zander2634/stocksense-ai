"""
Service for AI-powered demand forecasting.
Gumagamit ng trained XGBoost model para mag-predict ng future demand.
"""

import os
import joblib
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict
from sqlalchemy.orm import Session

from app.models.sale import Sale
from app.models.product import Product

# Path sa ML model - nasa root folder ng project
# __file__ = backend/app/services/forecast_service.py
# 4 levels up = stocksense-ai/ (root)
ML_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
    "ml"
)
MODEL_PATH = os.path.join(ML_DIR, "models", "xgboost_model.pkl")
FEATURES_PATH = os.path.join(ML_DIR, "models", "features.pkl")
# Cache ng model
_model = None
_features = None


def load_model():
    """Load XGBoost model (cached)"""
    global _model, _features
    if _model is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(
                f"Model not found at {MODEL_PATH}. Please run 'python ml/train_model.py' first."
            )
        _model = joblib.load(MODEL_PATH)
        _features = joblib.load(FEATURES_PATH)
    return _model, _features


def get_historical_sales(db: Session, product_id: int, days: int = 90) -> pd.DataFrame:
    """Kunin ang historical sales data para sa isang product
    
    NOTE: A-aggregate ang lahat ng sales per day, para ang bawat row ay
    isang araw ng sales (hindi bawat transaction).
    """
    
    cutoff = datetime.utcnow() - timedelta(days=days)
    
    sales = db.query(Sale).filter(
        Sale.product_id == product_id,
        Sale.sale_date >= cutoff
    ).order_by(Sale.sale_date).all()
    
    if not sales:
        return pd.DataFrame()
    
    # Group by date - aggregate all sales per day
    data = {}
    for sale in sales:
        date_key = sale.sale_date.strftime("%Y-%m-%d")
        # Sum lahat ng quantity para sa araw na iyon
        data[date_key] = data.get(date_key, 0) + sale.quantity
    
    df = pd.DataFrame([
        {"date": pd.to_datetime(k), "quantity_sold": v}
        for k, v in sorted(data.items())  # sorted para tama ang order
    ])
    df = df.sort_values("date").reset_index(drop=True)
    
    return df


def prepare_features(product_id: int, df: pd.DataFrame) -> pd.DataFrame:
    """I-prepare ang features para sa prediction"""
    
    # Fill missing dates (kung may gaps)
    if len(df) > 0:
        date_range = pd.date_range(start=df['date'].min(), end=df['date'].max(), freq='D')
        df = df.set_index('date').reindex(date_range).fillna(0).reset_index()
        df.columns = ['date', 'quantity_sold']
    
    # Lag features
    for lag in [1, 3, 7, 14, 30]:
        df[f'lag_{lag}'] = df['quantity_sold'].shift(lag)
    
    # Rolling averages
    for window in [7, 14, 30]:
        df[f'rolling_mean_{window}'] = df['quantity_sold'].rolling(window, min_periods=1).mean()
    
    df['rolling_std_7'] = df['quantity_sold'].rolling(7, min_periods=1).std()
    
    # Add time-based features for the prediction date (next day)
    last_date = df['date'].max()
    next_date = last_date + timedelta(days=1)
    
    df['day_of_week'] = df['date'].dt.weekday
    df['day_of_month'] = df['date'].dt.day
    df['month'] = df['date'].dt.month
    df['product_id'] = product_id
    
    return df, next_date


def forecast_product(db: Session, product_id: int, days_ahead: int = 7) -> Dict:
    """Generate demand forecast para sa isang product"""
    
    model, feature_cols = load_model()
    
    # Kunin ang historical data
    df = get_historical_sales(db, product_id, days=90)
    
    if len(df) < 30:
        # Hindi sapat ang data — gumamit ng fallback (average)
        avg_demand = df['quantity_sold'].mean() if len(df) > 0 else 1
        return {
            "product_id": product_id,
            "forecast_days": days_ahead,
            "predicted_demand": [int(avg_demand)] * days_ahead,
            "total_predicted_demand": int(avg_demand * days_ahead),
            "average_daily_demand": float(avg_demand),
            "confidence": "low",
            "method": "average_fallback",
            "note": "Insufficient historical data. Using average-based prediction."
        }
    
    # Prepare features
    df, next_date = prepare_features(product_id, df)
    
    # Predict for each day ahead
    predictions = []
    current_df = df.copy()
    
    for day in range(days_ahead):
        # Get last row features
        last_row = current_df.iloc[-1:].copy()
        
        # Update date features
        pred_date = next_date + timedelta(days=day)
        last_row['day_of_week'] = pred_date.weekday()
        last_row['day_of_month'] = pred_date.day
        last_row['month'] = pred_date.month
        last_row['product_id'] = product_id
        
        # Select features
        X = last_row[feature_cols].fillna(0)
        
        # Predict
        pred = model.predict(X)[0]
        pred = max(0, int(round(pred)))  # Ensure non-negative integer
        predictions.append(pred)
        
        # Append prediction to current_df for next iteration
        new_row = pd.DataFrame({
            'date': [pred_date],
            'quantity_sold': [pred],
            'day_of_week': [pred_date.weekday()],
            'day_of_month': [pred_date.day],
            'month': [pred_date.month],
            'product_id': [product_id]
        })
        
        # Recompute lag features
        combined = pd.concat([current_df[['date', 'quantity_sold']], new_row[['date', 'quantity_sold']]], ignore_index=True)
        
        for lag in [1, 3, 7, 14, 30]:
            combined[f'lag_{lag}'] = combined['quantity_sold'].shift(lag)
        for window in [7, 14, 30]:
            combined[f'rolling_mean_{window}'] = combined['quantity_sold'].rolling(window, min_periods=1).mean()
        combined['rolling_std_7'] = combined['quantity_sold'].rolling(7, min_periods=1).std()
        combined['day_of_week'] = combined['date'].dt.weekday
        combined['day_of_month'] = combined['date'].dt.day
        combined['month'] = combined['date'].dt.month
        combined['product_id'] = product_id
        
        current_df = combined
    
    total_demand = sum(predictions)
    avg_daily = total_demand / len(predictions) if predictions else 0
    
    return {
        "product_id": product_id,
        "forecast_days": days_ahead,
        "predicted_demand": predictions,
        "total_predicted_demand": total_demand,
        "average_daily_demand": round(avg_daily, 2),
        "confidence": "high" if len(df) >= 60 else "medium",
        "method": "xgboost",
        "forecast_start_date": next_date.strftime("%Y-%m-%d")
    }


def get_reorder_recommendation(db: Session, product: Product) -> Dict:
    """Generate smart reorder recommendation"""
    
    forecast = forecast_product(db, product.id, days_ahead=30)
    
    # Kunin ang lead time (default 7 days kung walang supplier)
    lead_time_days = 7  # Pwede nating i-link sa supplier later
    
    # Compute reorder point
    avg_daily_demand = forecast['average_daily_demand']
    safety_stock = avg_daily_demand * 3  # 3 days safety stock
    reorder_point = (avg_daily_demand * lead_time_days) + safety_stock
    
    # Compute reorder quantity
    # Formula: (avg daily demand × lead time) + safety stock - current stock
    recommended_qty = max(
        0,
        int((avg_daily_demand * lead_time_days) + safety_stock - product.stock_quantity)
    )
    
    # Determine urgency
    if product.stock_quantity <= 0:
        urgency = "critical"
    elif product.stock_quantity <= reorder_point * 0.5:
        urgency = "high"
    elif product.stock_quantity <= reorder_point:
        urgency = "medium"
    else:
        urgency = "low"
    
    return {
        "product_id": product.id,
        "product_name": product.name,
        "current_stock": product.stock_quantity,
        "reorder_level": product.reorder_level,
        "average_daily_demand": avg_daily_demand,
        "lead_time_days": lead_time_days,
        "safety_stock": round(safety_stock, 2),
        "reorder_point": round(reorder_point, 2),
        "recommended_reorder_quantity": recommended_qty,
        "urgency": urgency,
        "should_reorder": product.stock_quantity <= reorder_point,
        "forecast_30_days": forecast
    }