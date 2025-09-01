#!/usr/bin/env sh
set -e

# Config via env (with sensible defaults)
: "${PORT:=8000}"
: "${DEV:=0}"                 # set DEV=1 to use runserver
: "${COLLECTSTATIC:=1}"       # set COLLECTSTATIC=0 to skip
: "${CREATE_SUPERUSER:=0}"    # set CREATE_SUPERUSER=1 to attempt createsuperuser

echo "==> Applying database migrations..."
python manage.py migrate --noinput

if [ "$COLLECTSTATIC" = "1" ]; then
  echo "==> Collecting static files..."
  python manage.py collectstatic --noinput
fi

# Optional: create a superuser non-interactively (only if all 3 vars are provided)
if [ "$CREATE_SUPERUSER" = "1" ] && \
   [ -n "${DJANGO_SUPERUSER_USERNAME:-}" ] && \
   [ -n "${DJANGO_SUPERUSER_EMAIL:-}" ] && \
   [ -n "${DJANGO_SUPERUSER_PASSWORD:-}" ]; then
  echo "==> Ensuring superuser exists..."
  python manage.py shell <<'PY'
import os
from django.contrib.auth import get_user_model
User = get_user_model()
u = os.environ['DJANGO_SUPERUSER_USERNAME']
e = os.environ['DJANGO_SUPERUSER_EMAIL']
p = os.environ['DJANGO_SUPERUSER_PASSWORD']
if not User.objects.filter(username=u).exists():
    User.objects.create_superuser(username=u, email=e, password=p)
    print("Superuser created:", u)
else:
    print("Superuser already exists:", u)
PY
fi

echo "==> Starting server..."
if [ "$DEV" = "1" ]; then
  exec python manage.py runserver 0.0.0.0:"$PORT"
else
  exec gunicorn filelines.wsgi:application --bind 0.0.0.0:"$PORT" \
       --workers "${GUNICORN_WORKERS:-3}" --timeout "${GUNICORN_TIMEOUT:-60}"
fi
