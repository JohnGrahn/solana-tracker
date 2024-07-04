import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'postgresql://user:password@db/solana_tracker'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SOLANA_RPC_URL = os.environ.get('SOLANA_RPC_URL') or 'https://api.mainnet-beta.solana.com'
    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL') or 'redis://redis:6379/0'
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND') or 'redis://redis:6379/0'