#!/bin/bash


root_path=`pwd`/
proxy_addr="proxy3.si.c-s.fr:3128"

# Default values
# Target
target="local"
# SPARK_HOME environment variable
custom_spark_home=false
spark_home=~/tools/spark-1.5.2-bin-hadoop2.6
# Don't run gunicorn by default
run_gunicorn=false
# Do not keep old eggs
clean_eggs=false
# Specify the build path
custom_build_path=false
build_path=${root_path}_build/
proxy_login="undefined"
no_color=false

while [[ $# -gt 0 ]]
do
   key="$1"

   case $key in
      -t|--target)
         target="$2"
         shift
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
         echo -e "   -r|--run-gunicorn"
         echo -e "                       Run GUNICORN for this target"
         echo -e "                       Default: don't run gunicorn"
         echo -e ""
         echo -e "   -t|--target <platform>"
         echo -e "                       Specify the current platform [int|preprod|local|pic]"
         echo -e "                       Default: local"
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
target=`echo $target | tr '[:upper:]' '[:lower:]'`

echo -e "\n${YELLOW}${UNDERLINE}Ikats Deployment Script${OFF}\n"

host=`hostname`
echo -e "${YELLOW}Target = $target${OFF} "
echo -e "${YELLOW}Hostname = $host${OFF} "


# Managing path depending on target
case $target in
   "int")
      buildout_settings_target="settings.int"
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
      if test ${custom_build_path} == false
      then
         # Use default build path
         build_path=${root_path}_build/
      fi
      log_path=${build_path}logs/
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
rm -rf ${build_path} || exit 1;
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

# Add spark lib to pythonpath
echo "    ${spark_home}python" > add.txt
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
$py_cmd bootstrap.py || exit 2;

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
   
   # Migrate
   echo -e "\n${YELLOW}Running Django migration${OFF}"
   ${build_path}bin/django migrate --settings=ikats_processing.${buildout_settings_target} || exit 3;

   echo -e "\n${YELLOW}Running Gunicorn${OFF}"

   # Killing old gunicorn processes
   ps aux | grep gunicorn-with-settings | grep -v grep | grep ikats_processing | awk '{ print $2 }' | xargs -i kill {}
   
   # Starting new gunicorn
   my_ip=`hostname -I| sed 's/ //g'`
   ${build_path}bin/gunicorn-with-settings --bind $my_ip:8000 ikats_processing.wsgi:application > ${log_path}ikats_gunicorn.log 2>&1 &
   
   # Test if gunicron well started
   if test `ps aux | grep gunicorn-with-settings | grep -v grep | grep ikats_processing | awk '{ print $2 }' | wc -l` -eq 0
   then
      echo -e "${RED}Gunicorn can't be started${OFF}"
      exit 4;
   else 
      echo -e "${GREEN}Gunicorn started${OFF}"
   fi
  
fi

# Exit with nominal status
exit 0
