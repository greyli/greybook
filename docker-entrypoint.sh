#!/bin/bash
set -e

# run database migrations
flask db upgrade

# start Gunicorn
exec gunicorn --workers 4 --bind 0.0.0.0:5000 --access-logfile - --error-logfile - app:app
