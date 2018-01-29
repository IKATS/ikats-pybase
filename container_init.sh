
set -xe

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

#!/bin/bash

root_path=$(pwd)"/"
# SPARK_HOME environment variable
spark_home=/opt/spark-1.6.1
# Specify the build path
build_path=/build/

# Managing path
settings="settings.environ"

# Build path
echo -e "\nGenerating path"
mkdir -p ${build_path} || exit 1;
mkdir -p /logs || exit 1;

# Sources path
sources_path=${root_path}_sources/

# Building deploy src structure
echo -e "\nBuilding deployed structure"
cd ${build_path}
cp -rf ${sources_path}ikats_core/src/* ${build_path} || exit 1;
cp -rf ${sources_path}ikats_algos/src/* ${build_path} || exit 1;
cp -rf ${sources_path}ikats_django/src/* ${build_path} || exit 1;

cp ${root_path}gunicorn.py.ini ${build_path} || exit 1;

cd ${build_path}

echo -e "\nConfiguring python"

# Overriding ikats config
echo "Configuring the node"
config_file=${build_path}ikats/core/config/ikats.conf
sed -i -e "s/opentsdb\.read\.ip.*$/opentsdb.read.ip = ${OPENTSDB_READ_HOST}/" ${config_file}
sed -i -e "s/opentsdb\.read\.port.*$/opentsdb.read.port = ${OPENTSDB_READ_PORT}/" ${config_file}
sed -i -e "s/opentsdb\.write\.ip.*$/opentsdb.write.ip = ${OPENTSDB_WRITE_HOST}/" ${config_file}
sed -i -e "s/opentsdb\.write\.port.*$/opentsdb.write.port = ${OPENTSDB_WRITE_PORT}/" ${config_file}
sed -i -e "s/tdm\.ip.*$/tdm.ip = ${TDM_HOST}/" ${config_file}
sed -i -e "s/tdm\.port.*$/tdm.port = ${TDM_PORT}/" ${config_file}
sed -i    "s/spark.url=.*/spark.url=$SPARK_MASTER/g" ${config_file}
node_name=$(hostname)
sed -i -e "s/node\.name.*$/node.name = ${node_name}/" ${config_file}

if test -d /usr/local/bin/
then
   PATH=$PATH:/usr/local/bin/
fi

# Handling SPARK needs
export SPARK_HOME=${spark_home}
export PYSPARK_PYTHON=${build_path}bin/python
echo -e "SPARK_HOME set to ${SPARK_HOME}"
export PYTHONPATH=${build_path}ikats/processing

cd ${build_path}ikats/processing

# Starting new Gunicorn
echo -e "\nStarting Gunicorn"
export DJANGO_SETTINGS_MODULE="ikats_processing.settings.docker"

echo "gunicorn -c /build/gunicorn.py.ini --bind 0.0.0.0:8000 ikats_processing.wsgi:application"
sleep infinity
# gunicorn launched foreground (daemon false)
gunicorn -c ${build_path}gunicorn.py.ini --bind 0.0.0.0:8000 ikats_processing.wsgi:application
