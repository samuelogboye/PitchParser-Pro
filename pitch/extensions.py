from celery import Celery
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
REDIS_URL = 'redis://redis:6379/0'
BROKER_URL = 'amqp://admin:mypass@rabbitmq//'

celery = Celery(__name__, broker='amqp://admin:mypass@rabbitmq//', backend='redis://redis:6379/0')
