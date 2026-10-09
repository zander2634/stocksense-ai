from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base

from app.models.user import User
from app.models.category import Category
from app.models.product import Product
from app.models.supplier import Supplier
from app.models.sale import Sale   # ← IDAGDAG ITO

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="StockSense AI",
    description="Intelligent Inventory Forecasting and Smart Stock Management System",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoint
@app.get("/")
def root():
    return {
        "message": "Welcome to StockSense AI API",
        "version": "1.0.0",
        "status": "running"
    }

# Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "healthy"}

from app.routes import auth, category, product, supplier, sale, forecast, dashboard, alerts

app.include_router(auth.router)
app.include_router(category.router)
app.include_router(product.router)
app.include_router(supplier.router)
app.include_router(sale.router)
app.include_router(forecast.router)
app.include_router(dashboard.router)
app.include_router(alerts.router)