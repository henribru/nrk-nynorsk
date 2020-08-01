#!/usr/bin/env bash

set -e

poetry run python manage.py migrate
exec poetry run gunicorn --bind 0.0.0.0 "$@" nrk_nynorsk.wsgi
