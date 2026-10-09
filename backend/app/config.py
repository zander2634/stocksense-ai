class Settings:
    # App
    APP_NAME = "StockSense AI"
    APP_VERSION = "1.0.0"
    
    # JWT
    SECRET_KEY = "your-super-secret-key-change-this-in-production"
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours
    
    # Database - PALITAN ANG PASSWORD!
    DATABASE_URL = "postgresql://postgres:sanderxb1@localhost:5432/stocksense"
        # reCAPTCHA
    RECAPTCHA_SECRET_KEY = "6Lde4-YtAAAAAMb53-c8bqRlu-X3e7-JUifxLKre"   # ← IDAGDAG

settings = Settings()
