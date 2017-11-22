
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

cd /ikats_py_deploy

buildout_conf_file=buildout.cfg

# Filling the buildout file
sed -i 's/my_ip=.*/my_ip="0.0.0.0"/' deploy.sh
sed -i "s/parts = .*/parts = sysegg/" ${buildout_conf_file}
sed -i "s/numpy.*//g" ${buildout_conf_file}
sed -i "s/scipy.*//g" ${buildout_conf_file}
sed -i "s/scikit-learn.*//g" ${buildout_conf_file}
cat >> ${buildout_conf_file} << EOF

[sysegg]
recipe = syseggrecipe
force-sysegg = true
eggs =
  numpy
  scipy
  scikit-learn

EOF

# Unsetting daemon mode for gunicorn
sed -i 's/daemon = True/daemon = False/g' gunicorn.py.ini


chmod +x deploy.sh

./deploy.sh \
  --build-path /build/ \
  --target environ \
  --skip-migration \
  --spark-home /opt/spark-1.6.1 \
  --expose \
  -r

sleep infinity

# Changing configuration for environment one
# /!\ Already done in deploy.sh

# conf_file=/build/ikats/core/config/ikats.conf
# sed -i "s/opentsdb.read.ip=.*/opentsdb.read.ip=$OPENTSDB_READ_HOST/g" $conf_file
# sed -i "s/opentsdb.read.port=.*/opentsdb.read.port=$OPENTSDB_READ_PORT/g" $conf_file
# sed -i "s/opentsdb.write.ip=.*/opentsdb.write.ip=$OPENTSDB_WRITE_HOST/g" $conf_file
# sed -i "s/opentsdb.write.port=.*/opentsdb.write.port=$OPENTSDB_WRITE_PORT/g" $conf_file
# sed -i "s/tdm.ip=.*/tdm.ip=$TDM_HOST/g" $conf_file
# sed -i "s/tdm.port=.*/tdm.ip=$TDM_PORT/g" $conf_file
# sed -i "s/spark.url=.*/spark.url=$SPARK_MASTER/g" $conf_file
