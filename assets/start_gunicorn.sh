#!/bin/bash

# Starting new Gunicorn
echo -e "Starting Gunicorn"

cd ${IKATS_PATH}/ikats/processing
python3 manage.py migrate --settings=ikats_processing.settings.docker

# Gunicorn launched foreground (daemon false)
gunicorn \
    --chdir ${IKATS_PATH}/ikats/processing \
    --config ${IKATS_PATH}/gunicorn.py.ini \
    --error-logfile /logs/ikats_gunicorn_error.log \
    --env SPARK_HOME=${SPARK_HOME} \
    --env PYSPARK_PYTHON=${PYSPARK_PYTHON} \
    --env DJANGO_SETTINGS_MODULE=ikats_processing.settings.docker \
    --env PYTHONPATH=${PYTHONPATH} \
    --bind 0.0.0.0:${GUNICORN_PORT} ikats_processing.wsgi

# Print logs to stdout
# (temporary trick)
#tail -f /logs/ikats_django.log &
tail -f /logs/ikats_processing.log &

# Print logs to stdout
# (temporary trick)
#tail -f /logs/ikats_django.log &
tail -f /logs/ikats_processing.log &

sleep infinity
