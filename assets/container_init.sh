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
  "SPARK_MASTER_HOST"
  "SPARK_MASTER_PORT"
  "POSTGRES_HOST"
  "POSTGRES_PORT"
)

for v in "${env_variables[@]}"
do
  test_for_variable $v
done

# Overriding ikats config
config_file=${IKATS_PATH}/ikats/core/config/ikats.conf
sed -i -e "s/opentsdb\.read\.ip.*$/opentsdb.read.ip = ${OPENTSDB_READ_HOST}/" ${config_file}
sed -i -e "s/opentsdb\.read\.port.*$/opentsdb.read.port = ${OPENTSDB_READ_PORT}/" ${config_file}
sed -i -e "s/opentsdb\.write\.ip.*$/opentsdb.write.ip = ${OPENTSDB_WRITE_HOST}/" ${config_file}
sed -i -e "s/opentsdb\.write\.port.*$/opentsdb.write.port = ${OPENTSDB_WRITE_PORT}/" ${config_file}
sed -i -e "s/tdm\.ip.*$/tdm.ip = ${TDM_HOST}/" ${config_file}
sed -i -e "s/tdm\.port.*$/tdm.port = ${TDM_PORT}/" ${config_file}
sed -i -e "s/spark\.url.*$/spark.url = spark:\/\/${SPARK_MASTER_HOST}:${SPARK_MASTER_PORT}/" ${config_file}
node_name=$(hostname)
sed -i -e "s/node\.name.*$/node.name = ${node_name}/" ${config_file}

if test -d /usr/local/bin/
then
   PATH=$PATH:/usr/local/bin/
fi

# Updating PYTHONPATH
source ikats.env

# Choose between Spark and Gunicorn
if [[ -z ${SPARK_MODE} ]]
then
  # SPARK_MODE is not defined as environment variable, start gunicorn
  bash ${IKATS_PATH}/start_gunicorn.sh
else
  # SPARK_MODE is defined (master or slave), start spark
  bash /start_spark.sh
fi
