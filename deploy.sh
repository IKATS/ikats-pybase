#!/bin/bash

if [[ $(whoami) != 'ikats' ]]
then
   echo "This script should be run using ikats user only !!! (user is $(whoami))"
fi


root_path=$(pwd)"/"
proxy_addr="proxy3.si.c-s.fr:3128"

# Default values
# Target
target="local"
# SPARK_HOME environment variable
custom_spark_home=false
spark_home=/opt/spark-1.6.2-bin-hadoop2.6/
# Don't run gunicorn by default
run_gunicorn=false
# Do not keep old eggs
clean_eggs=false
# Specify the build path
custom_build_path=false
build_path=${root_path}_build/
proxy_login="undefined"
no_color=false
keep_previous_buildout=false

while [[ $# -gt 0 ]]
do
   key="$1"

   case ${key} in
      -t|--target)
         target="$2"
         shift
         ;;
      -k|--keep)
         keep_previous_buildout=true
         ;;
      -s|--spark-home)
         custom_spark_home=true
         spark_home="$2"
         shift
         ;;
      --no-color)
         no_color=true
         ;;
      -x|--proxy-auth)
         read proxy_login proxy_password <<< $(echo $2 | sed 's/:/ /')
         shift
         ;;
      -p|--build-path)
         custom_build_path=true
         build_path="$2"
         shift
         ;;
      -r|--run-gunicorn)
         run_gunicorn=true
         ;;
      -c|--clean-eggs)
         clean_eggs=true
         ;;
      -h|--help)
         echo -e "USAGE"
         echo -e "-----"
         echo -e ""
         echo -e "   deploy.sh [options]"
         echo -e ""
         echo -e "   -h|--help"
         echo -e "                       Displays this help page"
         echo -e ""
         echo -e "   --no-color"
         echo -e "                       Don't use colors"
         echo -e ""
         echo -e "   -c|--clean-eggs"
         echo -e "                       Don't backup the eggs formerly compiled"
         echo -e "                       Default: backup old eggs"
         echo -e ""
         echo -e "   -k|--keep"
         echo -e "                       Keep previous buildout run (don't rm all)"
         echo -e "                       Default: don't keep"
         echo -e ""
         echo -e "   -r|--run-gunicorn"
         echo -e "                       Run GUNICORN for this target"
         echo -e "                       Default: don't run gunicorn"
         echo -e ""
         echo -e "   -t|--target <platform>"
         echo -e "                       Specify the current platform [int|int-b|preprod|local|docker]"
         echo -e ""
         echo -e "   -p|--build-path <path>"
         echo -e "                       Specify a specific build-path"
         echo -e "                       Default: depends on target platform"
         echo -e ""
         echo -e "   -x|--proxy-auth login:pass"
         echo -e "                       Specify the proxy credentials"
         echo -e "                       Default: environment defined"
         echo -e ""
         echo -e "   -s|--spark-home <path>"
         echo -e "                       Specify the SPARK_HOME environment variable defined by <path>"
         echo -e "                       Default: ~/tools/spark-1.5.2-bin-hadoop2.6"
         echo -e ""
         echo -e ""
         echo -e "RETURN STATUS"
         echo -e "-------------"
         echo -e ""
         echo -e "   0: nominal "
         echo -e "   1: Copy error"
         echo -e "   2: Bootstrap/Buildout error"
         echo -e "   3: Django error"
         echo -e "   4: Gunicorn error"
         echo -e "   5: Target error"
         echo -e "   6: no sources found"
         exit 0;
         ;;
      *)
         # Unknown option
         echo -e "--> Option [$1] ignored !"
         ;;
   esac
   shift
done

if test ${no_color} == false
then
   # Colors
   OFF="\033[0m"
   RED="\033[31m"
   GREEN="\033[32m"
   YELLOW="\033[33m"
   BLUE="\033[34m"
   MAGENTA="\033[35m"
   CYAN="\033[36m"
   WHITE="\033[37m"
   UNDERLINE="\033[4m"
   HIDDEN="\033[8m"
fi

# Converting target to lowercase
target=`echo ${target} | tr '[:upper:]' '[:lower:]'`

echo -e "\n${YELLOW}${UNDERLINE}Ikats Deployment Script${OFF}\n"

host=`hostname`
echo -e "${YELLOW}Target = $target${OFF} "
echo -e "${YELLOW}Hostname = $host${OFF} "


# Managing path depending on target
case ${target} in
   "int")
      buildout_settings_target="settings.int"
      opentsdb_r_ip="172.28.15.85"
      opentsdb_r_port="4242"
      opentsdb_w_ip="172.28.15.85"
      opentsdb_w_port="4242"
      tdm_ip="172.28.15.83"
      tdm_port="80"
      if test ${custom_build_path} == false
      then
         # Use default build path
         build_path=/home/ikats/code/
      fi
      if test ${custom_spark_home} == false
      then
         spark_home=/opt/spark/
      fi
      log_path=/home/ikats/logs/
      ;;
   "int-b")
      buildout_settings_target="settings.int-b"
      opentsdb_r_ip="172.28.15.15"
      opentsdb_r_port="4242"
      opentsdb_w_ip="172.28.15.15"
      opentsdb_w_port="4242"
      tdm_ip="172.28.15.13"
      tdm_port="80"
      if test ${custom_build_path} == false
      then
         # Use default build path
         build_path=/home/ikats/code/
      fi
      if test ${custom_spark_home} == false
      then
         spark_home=/opt/spark/
      fi
      log_path=/home/ikats/logs/
      ;;
   "preprod")
      buildout_settings_target="settings.preprod"
      opentsdb_r_ip="172.28.15.90"
      opentsdb_r_port="4242"
      opentsdb_w_ip="172.28.15.90"
      opentsdb_w_port="4242"
      tdm_ip="172.28.15.88"
      tdm_port="80"
      if test ${custom_build_path} == false
      then
         # Use default build path
         build_path=/home/ikats/code/
      fi
      if test ${custom_spark_home} == false
      then
         spark_home=/opt/spark/
      fi
      log_path=/home/ikats/logs/
      ;;
   "local")
      buildout_settings_target="settings"
      opentsdb_r_ip="172.28.15.15"
      opentsdb_r_port="4242"
      opentsdb_w_ip="172.28.15.15"
      opentsdb_w_port="4242"
      tdm_ip="172.28.15.13"
      tdm_port="80"
      if test ${custom_build_path} == false
      then
         # Use default build path
         build_path=${root_path}_build/
      fi
      log_path=${build_path}logs/
      ;;
   "docker")
      buildout_settings_target="settings.docker"
      opentsdb_r_ip="127.0.0.1"
      opentsdb_r_port="4242"
      opentsdb_w_ip="127.0.0.1"
      opentsdb_w_port="4243"
      tdm_ip="127.0.0.1"
      tdm_port="8080"
      if test ${custom_spark_home} == false
      then
         # Use default spark path
         spark_home=/opt/spark
      fi
      if test ${custom_build_path} == false
      then
         # Use default build path
         build_path=/home/ikats/code/
      fi
      log_path=/logs/
      ;;
   *)
      # Unknown Target
      echo -e "--> Unknown target [$1] !"
      exit 5;
      ;;
esac

# Build path
eggs_backup_path=eggs
if test -d ${eggs_backup_path}
then
   # Deleting old eggs (former unachieved build)
   rm -rf ${eggs_backup_path}
fi
if test -d ${build_path}eggs -a ${clean_eggs} == false
then
   # Backup existing eggs (to avoid getting them again)
   echo "Backup existing eggs"
   mv ${build_path}eggs ${eggs_backup_path}
fi

echo -e "\n${YELLOW}Generating path${OFF}"
[ ${keep_previous_buildout}=false ] && rm -rf ${build_path};
mkdir -p ${build_path} || exit 1;
mkdir -p ${log_path} || exit 1;

if test -d ${eggs_backup_path}
then
   # Restoring saved eggs
   echo "Restoring saved eggs"
   mv ${eggs_backup_path} ${build_path}
fi

# Sources path
sources_path=${root_path}_sources/
if test  ! -d ${sources_path}
then
   echo "Sources path not found at ${sources_path}";
   exit 6;
fi

# Building deploy src structure
echo -e "\n${YELLOW}Building deployed structure${OFF}"
cd ${build_path}
cp -rf ${sources_path}ikats_core/src/* ${build_path} || exit 1;
cp -rf ${sources_path}ikats_algos/src/* ${build_path} || exit 1;
cp -rf ${sources_path}ikats_django/src/* ${build_path} || exit 1;

cp ${root_path}setup.py ${build_path} || exit 1;
cp ${root_path}bootstrap.py ${build_path} || exit 1;
cp ${root_path}buildout.cfg ${build_path} || exit 1;
cp ${root_path}gunicorn.py.ini ${build_path} || exit 1;

cd ${build_path}

echo -e "\n${YELLOW}Configuring python${OFF}"
if test ${proxy_login} != "undefined"
then
   # Only if proxy settings are set
   echo "Using local proxy configuration"
   export http_proxy=http://${proxy_login}:${proxy_password}@${proxy_addr}
   export https_proxy=http://${proxy_login}:${proxy_password}@${proxy_addr}
   export no_proxy=thor.si.c-s.fr
else
   echo -e "${YELLOW}Assuming the proxy is set elsewhere${OFF}"
fi

# Overriding default settings
# Defining logs path
ls ${build_path}ikats/processing/ikats_processing/settings/*.py | xargs -i sed -i -e "s@REP_LOGS = .\+@REP_LOGS = \"${log_path}\"@g" {}
sed -i -e "s/settings = settings/settings = ${buildout_settings_target}/g" buildout.cfg
sed -i -e "s@log_path = .*@log_path = \"${log_path}\"@g" gunicorn.py.ini
cat gunicorn.py.ini | grep log_path

# Overriding ikats config
echo "Configuring the node"
config_file=${build_path}ikats/core/config/ikats.conf
sed -i -e "s/opentsdb\.read\.ip.*$/opentsdb.read.ip = ${opentsdb_r_ip}/" ${config_file}
sed -i -e "s/opentsdb\.read\.port.*$/opentsdb.read.port = ${opentsdb_r_port}/" ${config_file}
sed -i -e "s/opentsdb\.write\.ip.*$/opentsdb.write.ip = ${opentsdb_w_ip}/" ${config_file}
sed -i -e "s/opentsdb\.write\.port.*$/opentsdb.write.port = ${opentsdb_w_port}/" ${config_file}
sed -i -e "s/tdm\.ip.*$/tdm.ip = ${tdm_ip}/" ${config_file}
sed -i -e "s/tdm\.port.*$/tdm.port = ${tdm_port}/" ${config_file}
sed -i -e "s/cluster\.name.*$/cluster.name = ${target}/" ${config_file}
node_name=$(hostname)
sed -i -e "s/node\.name.*$/node.name = ${node_name}/" ${config_file}

# Add spark lib to pythonpath
echo "    ${spark_home}/python" > add.txt
sed -i -e '/extra-paths =/r add.txt' buildout.cfg
rm add.txt


# Get buildout using an available python interpreter
if test -d /usr/local/bin/
then
   PATH=$PATH:/usr/local/bin/
fi
py_cmd=python
if python3 --version > /dev/null 2>&1
then
   py_cmd=python3
elif python3.4 --version > /dev/null 2>&1
then
   py_cmd=python3.4
elif python3.5 --version > /dev/null 2>&1
then
   py_cmd=python3.5
fi
${py_cmd} bootstrap.py || exit 2;

# Run buildout
${build_path}bin/buildout || exit 2;

# Cleaning pycache
echo -e "${YELLOW}Cleaning pycache${OFF}"
find ${build_path}ikats/ -name "__pycache__" -o -name "*.py[cod]" | xargs -i ls -l {}

# Handling SPARK needs
export SPARK_HOME=${spark_home}
export PYSPARK_PYTHON=${build_path}bin/python
echo -e "${YELLOW}SPARK_HOME set to ${SPARK_HOME}${OFF}"

# Specific operations for node supporting Django
if test ${run_gunicorn} == true
then

   cd ${build_path}ikats/processing

   # Migrate
   echo -e "\n${YELLOW}Running Django migration${OFF}"
   ${build_path}bin/python manage.py migrate --settings=ikats_processing.${buildout_settings_target} || exit 3;

   echo -e "\n${YELLOW}Starting Gunicorn${OFF}"

   # Killing old Gunicorn processes
   ps -A -o pid,args | grep 'gunicorn.*ikats' | grep -v grep | awk '{ print $1 }' | xargs -i kill -9 {}

   # Just wait a bit to let the process to be killed
   sleep 3;

   # Starting new Gunicorn
   my_ip=`hostname -I| sed 's/ .*//g'`
   ${build_path}bin/gunicorn-with-settings -c ${build_path}gunicorn.py.ini --bind ${my_ip}:8000 ikats_processing.wsgi:application --log-file ${log_path}ikats_gunicorn.log

   # Test if Gunicorn well started
   if test `ps -A -o pid,args | grep 'gunicorn.*ikats' | grep -v grep | awk '{ print $1 }' | wc -l` -eq 0
   then
      echo -e "${RED}Gunicorn can't be started${OFF}"
      exit 4;
   else
      echo -e "${GREEN}Gunicorn started${OFF}"
   fi

fi

# Exit with nominal status
exit 0
