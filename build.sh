#!/usr/bin/env bash
# Build script for Render (set as the service's Build Command: ./build.sh).
# Render's free plan has no shell, so database migrations and the admin
# account are handled here on every deploy.
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate --noinput
python manage.py ensure_superuser
