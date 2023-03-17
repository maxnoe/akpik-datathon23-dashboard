#! /bin/sh
set -e

# apply database migrations
flask db upgrade

# start the server
gunicorn --bind 0.0.0.0:$PORT "akpik_datathon_dashboard:create_app()"
