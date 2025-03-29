import os
from dotenv import load_dotenv

load_dotenv(".env")

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "test")
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'default_jwt_secret_key')

    # Database (PostgreSQL)
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///test.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    CACHE_DEFAULT_TIMEOUT = 300
    CACHE_TYPE = "SimpleCache"

    # Celery + RabbitMQ
    CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'amqp://admin:mypass@rabbitmq//')
    CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://redis:6379/0')

    # Redis (for caching)
    REDIS_URL = os.getenv('REDIS_URL', 'redis://redis:6379/0')

class DevelopmentConfig(Config): # pylint: disable=too-few-public-methods
    ''' Base Configuration for Development environment '''
    DEBUG = True

class TestingConfig(Config):# pylint: disable=too-few-public-methods
    ''' Base Configuration for Testing environment '''
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'

class ProductionConfig(Config):
    ''' Base Configuration for Production environment '''
    DEBUG = False
    