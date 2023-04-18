#! /bin/sh
set -e

# apply database migrations
flask db upgrade

# start the server
waitress-serve --host 0.0.0.0 --port $PORT --call "akpik_datathon_dashboard:create_app"
