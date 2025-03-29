#!/bin/sh
celery -A pitch.celery_worker.celery worker --loglevel INFO