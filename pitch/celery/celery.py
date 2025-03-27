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

from __future__ import absolute_import
from celery import Celery
import os

celery = Celery(__name__)

def make_celery(app):
    required_configs = ['CELERY_RESULT_BACKEND', 'CELERY_BROKER_URL']
    for config in required_configs:
        if config not in app.config:
            raise ValueError(f"Missing required Celery configuration: {config}")
        
    # celery = Celery(
    #     app.import_name,
    #     backend=app.config['CELERY_RESULT_BACKEND'],
    #     broker=app.config['CELERY_BROKER_URL']
    # )
    # celery.conf.update(app.config)
    # Configure the existing instance
    celery.conf.update(
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    celery.conf.update(app.config)
    
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery