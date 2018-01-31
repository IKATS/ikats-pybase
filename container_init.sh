#!/bin/bash

root_path=$(pwd)"/"

function test_for_variable {
  vname=$1
  vvalue=${!vname}
  default_value=$2

  if [ -z "$vvalue" ]
  then
    if [ -z "$2" ]
    then
      # No fallback has been given to the function
      echo "The environment variable ${vname} must have a value"
      exit 1
    else
      # Setting the variable value to the provided default
      eval $vname=$default_value
    fi
  fi
}

env_variables=(
  "OPENTSDB_READ_HOST"
  "OPENTSDB_READ_PORT"
  "OPENTSDB_WRITE_HOST"
  "OPENTSDB_WRITE_PORT"
  "TDM_HOST"
  "TDM_PORT"
  "SPARK_MASTER"
  "POSTGRES_HOST"
  "POSTGRES_PORT"
)

for v in "${env_variables[@]}"
do
  test_for_variable $v
done

# Overriding ikats config
echo "Configuring the node"
config_file=${IKATS_PATH}/ikats/core/config/ikats.conf
sed -i -e "s/opentsdb\.read\.ip.*$/opentsdb.read.ip = ${OPENTSDB_READ_HOST}/" ${config_file}
sed -i -e "s/opentsdb\.read\.port.*$/opentsdb.read.port = ${OPENTSDB_READ_PORT}/" ${config_file}
sed -i -e "s/opentsdb\.write\.ip.*$/opentsdb.write.ip = ${OPENTSDB_WRITE_HOST}/" ${config_file}
sed -i -e "s/opentsdb\.write\.port.*$/opentsdb.write.port = ${OPENTSDB_WRITE_PORT}/" ${config_file}
sed -i -e "s/tdm\.ip.*$/tdm.ip = ${TDM_HOST}/" ${config_file}
sed -i -e "s/tdm\.port.*$/tdm.port = ${TDM_PORT}/" ${config_file}
sed -i    "s/spark.url=.*/spark.url=${SPARK_MASTER}/g" ${config_file}
node_name=$(hostname)
sed -i -e "s/node\.name.*$/node.name = ${node_name}/" ${config_file}

if test -d /usr/local/bin/
then
   PATH=$PATH:/usr/local/bin/
fi

cd ${IKATS_PATH}/ikats/processing
python3 manage.py migrate --settings=ikats_processing.settings.docker

# Starting new Gunicorn
echo -e "Starting Gunicorn"

# Gunicorn launched foreground (daemon false)
gunicorn \
    --chdir ${IKATS_PATH}/ikats/processing \
    --config ${IKATS_PATH}/gunicorn.py.ini \
    --error-logfile /logs/ikats_gunicorn_error.log \
    --env SPARK_HOME=${SPARK_HOME} \
    --env PYSPARK_PYTHON=${PYSPARK_PYTHON} \
    --env DJANGO_SETTINGS_MODULE=ikats_processing.settings.docker \
    --pythonpath "${IKATS_PATH}/processing" \
    --pythonpath "${IKATS_PATH}/algo/contrib" \
    --pythonpath "${IKATS_PATH}" \
    --bind 0.0.0.0:8000 ikats_processing.wsgi

# Print logs to stdout
# (temporary trick)
#tail -f /logs/ikats_django.log &
tail -f /logs/ikats_processing.log &
tail -f /logs/ikats_gunicorn_error.log &

sleep infinity