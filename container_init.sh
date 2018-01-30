#!/bin/bash

root_path=$(pwd)"/"
# SPARK_HOME environment variable
spark_home=/opt/spark-1.6.1
# Specify the build path
build_path=/build

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

# Build path
echo -e "Generating path"
mkdir -p ${build_path} || exit 1;
mkdir -p /logs || exit 1;

# Sources path
sources_path=${root_path}_sources/

# Building deploy src structure
echo -e "Building deployed structure"
cp -rf ${sources_path}ikats_core/src/* ${build_path} || exit 1;
cp -rf ${sources_path}ikats_algos/src/* ${build_path} || exit 1;
cp -rf ${sources_path}ikats_django/src/* ${build_path} || exit 1;

cp ${root_path}gunicorn.py.ini ${build_path} || exit 1;

# Overriding ikats config
echo "Configuring the node"
cd ${build_path}
config_file=${build_path}/ikats/core/config/ikats.conf
sed -i -e "s/opentsdb\.read\.ip.*$/opentsdb.read.ip = ${OPENTSDB_READ_HOST}/" ${config_file}
sed -i -e "s/opentsdb\.read\.port.*$/opentsdb.read.port = ${OPENTSDB_READ_PORT}/" ${config_file}
sed -i -e "s/opentsdb\.write\.ip.*$/opentsdb.write.ip = ${OPENTSDB_WRITE_HOST}/" ${config_file}
sed -i -e "s/opentsdb\.write\.port.*$/opentsdb.write.port = ${OPENTSDB_WRITE_PORTOPENTSDB_WRITE_PORT}/" ${config_file}
sed -i -e "s/tdm\.ip.*$/tdm.ip = ${TDM_HOST}/" ${config_file}
sed -i -e "s/tdm\.port.*$/tdm.port = ${TDM_PORT}/" ${config_file}
sed -i    "s/spark.url=.*/spark.url=$SPARK_MASTER/g" ${config_file}
node_name=$(hostname)
sed -i -e "s/node\.name.*$/node.name = ${node_name}/" ${config_file}

if test -d /usr/local/bin/
then
   PATH=$PATH:/usr/local/bin/
fi

sleep 15
cd ${build_path}/ikats/processing
python3 manage.py migrate --settings=ikats_processing.settings.docker

# Starting new Gunicorn
echo -e "Starting Gunicorn"

# Gunicorn launched foreground (daemon false)
gunicorn \
    -c ${build_path}/gunicorn.py.ini \
    --pythonpath "${build_path}" \
    --pythonpath "${build_path}/processing" \
    --pythonpath "${build_path}" \
    --pythonpath "${build_path}/algo/contrib" \
    --pythonpath "${build_path}" \
    --error-logfile - \
    --env SPARK_HOME=${spark_home} \
    --env PYSPARK_PYTHON=python3 \
    --env DJANGO_SETTINGS_MODULE=ikats_processing.settings.docker \
    --chdir ${build_path}/ikats/processing \
    --bind 0.0.0.0:8000 ikats_processing.wsgi || echo "Failed!"
