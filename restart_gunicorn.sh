#!/bin/sh

if test ${USER} != 'ikats'
then
   echo "You must be ikats to run this script"
   exit 1;
fi

log_path=/home/ikats/logs/
export SPARK_HOME=/usr/hdp/current/spark-client/
export PYSPARK_PYTHON=/home/ikats/code/bin/python

ps aux | grep gunicorn-with-settings | grep -v grep | grep ikats_processing | awk '{ print $2 }' | xargs -i kill {}

OFF="\033[0m"
RED="\033[31m"
GREEN="\033[32m"

# Starting new gunicorn
my_ip=`hostname -I| sed 's/ //g'`
/home/ikats/code/bin/gunicorn-with-settings --name ikats --bind ${my_ip}:8000 --timeout 7200 --workers 13 --log-level=DEBUG ikats_processing.wsgi:application > ${log_path}ikats_gunicorn.log 2>&1 &

if test `ps aux | grep gunicorn-with-settings | grep -v grep | grep ikats_processing | awk '{ print $2 }' | wc -l` -eq 0
then
  echo -e "${RED}Gunicorn can't be started${OFF}"
  exit 4;
else 
  echo -e "${GREEN}Gunicorn started${OFF}"
fi

