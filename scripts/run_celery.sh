#!/bin/sh
celery -A pitch.tasks worker --loglevel INFO