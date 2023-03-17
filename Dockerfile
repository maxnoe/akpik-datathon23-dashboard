FROM python:3.10-slim

# we always want to serve the member_database app
ENV FLASK_APP=akpik_datathon_dashboard \
	PORT=5000 \
	PIP_NO_CACHE_DIR=1 \
	PIP_DISABLE_PIP_VERSION_CHECK=1 \
	PYTHONUNBUFFERED=1

# everything should run as unprivileged user
RUN useradd --system --user-group -m akpik

RUN pip install poetry==1.3.1
WORKDIR /home/akpik/

# this will be our startup script
COPY --chown=akpik:akpik run.sh celery_worker.py .

# migrations are needed at startup
COPY --chown=akpik:akpik migrations migrations

# copy relevant files
COPY --chown=akpik:akpik pyproject.toml poetry.lock ./

# install production dependencies
# this is our production server
# on top, for production we use postgresql, which needs psycopg2 and
# pg_config
# this will create a wheel file that contains all dependencies
RUN poetry config virtualenvs.create false \
	&& poetry install --only main,deploy

COPY --chown=akpik:akpik akpik_datathon_dashboard ./akpik_datathon_dashboard

# switch to our production user
USER akpik
CMD ./run.sh
