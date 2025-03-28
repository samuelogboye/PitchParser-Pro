# # from celery import Celery
# # from flask import Flask
# # from pitch.config import Config

# # def make_celery(app: Flask) -> Celery:
# #     celery = Celery(
# #         app.import_name,
# #         broker=app.config['CELERY_BROKER_URL'],
# #         backend=app.config['CELERY_RESULT_BACKEND']
# #     )
# #     celery.conf.update(app.config)
# #     return celery

# # from __future__ import absolute_import, unicode_literals
# # from celery import Celery
# # from pitch import create_app

# # app = create_app()
# # celery = Celery(
# #     app.import_name,
# #     broker=app.config['CELERY_BROKER_URL'],
# #     backend=app.config['CELERY_RESULT_BACKEND']
# # )
# # celery.conf.update(app.config)

# # # This will expose the task decorator
# # @celery.task(bind=True)
# # def debug_task(self):
# #     print('Request: {0!r}'.format(self.request))


# # pitch/celery/celery.py
# from celery import Celery

# celery = Celery(__name__)

# def init_celery(app):
#     celery.conf.update(app.config)
#     celery.conf.update(
#         task_serializer='json',
#         accept_content=['json'],
#         result_serializer='json',
#         timezone='UTC',
#         enable_utc=True,
#         task_track_started=True,
#         task_time_limit=300  # 5 minutes
#     )
#     return celery

# from __future__ import absolute_import
# from celery import Celery
# import os

# celery = Celery(__name__)

# def make_celery(app):
#     required_configs = ['CELERY_RESULT_BACKEND', 'CELERY_BROKER_URL']
#     for config in required_configs:
#         if config not in app.config:
#             raise ValueError(f"Missing required Celery configuration: {config}")
        
#     # celery = Celery(
#     #     app.import_name,
#     #     backend=app.config['CELERY_RESULT_BACKEND'],
#     #     broker=app.config['CELERY_BROKER_URL']
#     # )
#     # celery.conf.update(app.config)
#     # Configure the existing instance
#     celery.conf.update(
#         backend=app.config['CELERY_RESULT_BACKEND'],
#         broker=app.config['CELERY_BROKER_URL']
#     )
#     celery.conf.update(app.config)
    
#     class ContextTask(celery.Task):
#         def __call__(self, *args, **kwargs):
#             with app.app_context():
#                 return self.run(*args, **kwargs)

#     celery.Task = ContextTask

#     # Import tasks after Celery is configured
#     from pitch.celery import tasks  # This ensures tasks are registered
#     return celery
from __future__ import absolute_import
from celery import Celery
import os

CELERY_BROKER_URL="amqp://guest:guest@rabbitmq:5672//"
CELERY_RESULT_BACKEND="redis://redis:6379/0" #"redis://localhost:6379/0"

def make_celery(app=None):
    # Create a new Celery instance for each app
    celery = Celery(
        'pitch',
        backend=CELERY_RESULT_BACKEND,
        broker=CELERY_BROKER_URL,
        broker_connection_retry_on_startup=True,
        broker_connection_retry=True,
        broker_connection_max_retries=10
    )
    
    # Update configuration
    if app:
        celery.conf.update(app.config)
    
    celery.conf.update(
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
        timezone='UTC',
        enable_utc=True,
        imports=['pitch.celery.tasks'],  # Explicitly tell Celery where to find tasks
        broker_transport_options={
            'visibility_timeout': 3600,  # 1 hour
            'retry_policy': {
                'timeout': 5.0
            }
        },
        result_backend_transport_options={
            'retry_policy': {
                'timeout': 5.0
            },
            'retry_on_timeout': True,
            'socket_connect_timeout': 5,
            'socket_keepalive': True
        }
    )
    
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            if app:
                with app.app_context():
                    return self.run(*args, **kwargs)
            return self.run(*args, **kwargs)
                

    celery.Task = ContextTask
    return celery

# Create a default celery instance for imports
celery_app = make_celery()
