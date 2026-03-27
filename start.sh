#!/usr/bin/env bash
set -euo pipefail

# Run migrations and collect static assets, then start Gunicorn
python manage.py migrate --noinput
python manage.py collectstatic --noinput

exec gunicorn Ecommerce.wsgi:application --bind "0.0.0.0:${PORT:-8000}"
