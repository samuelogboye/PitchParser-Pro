#!/bin/sh
cd app  
su -m app -c "gunicorn -w 2 -b 0.0.0.0:5000 run:app"  