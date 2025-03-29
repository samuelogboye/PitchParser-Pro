from pitch import create_app
from pitch.extensions import celery

flask_app = create_app()
celery.conf.update(flask_app.config)