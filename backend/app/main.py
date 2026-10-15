from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base

from app.models.user import User
from app.models.category import Category
from app.models.product import Product
from app.models.supplier import Supplier
from app.models.sale import Sale   # ← IDAGDAG ITO
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

def get_global_key(request):
    return "global"

limiter = Limiter(key_func=get_global_key)

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
    allow_origins=["*"],  # Temporary — i-restrict later sa Vercel URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

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