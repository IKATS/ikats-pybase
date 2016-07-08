#!/bin/bash

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


echo -e "\n${YELLOW}${UNDERLINE}Ikats Deployment Script${OFF}\n"

root_path=`pwd`/

# Default values
# Target
target="local"
# SPARK_HOME environment variable
spark_home=~/tools/spark-1.5.2-bin-hadoop2.6
# Don't run gunicorn by default
run_gunicorn=false
# Do not keep old eggs
clean_eggs=false
# Specify the build path
custom_build_path=false
build_path=${root_path}_build/
# Branch to use for cloning
branch=master
git_login="undefined"
proxy_login="undefined"

while [[ $# -gt 0 ]]
do
   key="$1"

   case $key in
      -t|--target)
         target="$2"
         shift
         ;;
      -s|--spark-home)
         spark_home="$2"
         shift
         ;;
      -g|--git_auth)
         read git_login git_password <<< $(echo $2 | sed 's/:/ /')
         shift
         ;;
      -x|--proxy_auth)
         read proxy_login proxy_password <<< $(echo $2 | sed 's/:/ /')
         shift
         ;;
      -b|--branch)
         branch="$2"
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
         echo -e "${UNDERLINE}USAGE${OFF}"
         echo -e ""
         echo -e "   deploy.sh [-crh] [-t|--target <platform>] [-b|--branch <branch>] [-s|--spark-home <path>] [-p|--build-path <path>] [-x|--proxy_auth login:pass] -g|--git_auth login:pass"
         echo -e ""
         echo -e "   -h|--help"
         echo -e "                       Displays this help page"
         echo -e ""
         echo -e "   -c|--clean-eggs"
         echo -e "                       Don't backup the eggs formerly compiled"
         echo -e "                       Default: backup old eggs"
         echo -e ""
         echo -e "   -r|--run-gunicorn"
         echo -e "                       Run GUNICORN for this target"
         echo -e "                       Default: don't run gunicorn"
         echo -e ""
         echo -e "   -b|--branch <branch>"
         echo -e "                       use Git branch <branch> to deploy"
         echo -e "                       Default: master"
         echo -e ""
         echo -e "   -t|--target <platform>"
         echo -e "                       Specify the current platform [int|preprod|local|pic]"
         echo -e "                       Default: local"
         echo -e ""
         echo -e "   -p|--build-path <path>"
         echo -e "                       Specify a specific build-path"
         echo -e "                       Default: depends on target platform"
         echo -e ""
         echo -e "   -x|--proxy_auth login:pass"
         echo -e "                       Specify the proxy credentials"
         echo -e "                       Default: environment defined"
         echo -e ""
         echo -e "   -g|--git_auth"
         echo -e "                       Specify the Git credentials"
         echo -e ""
         echo -e "   -s|--spark-home <path>"
         echo -e "                       Specify the SPARK_HOME environment variable defined by <path>"
         echo -e "                       Default: ~/tools/spark-1.5.2-bin-hadoop2.6"
         echo -e ""
         exit 0;
         ;;
      *)
         # unknown option
         ;;
   esac
   shift
done

host=`hostname`
echo -e "${YELLOW}Target = $target${OFF} "
echo -e "${YELLOW}hostname = $host${OFF} "

case $target in
   "int")
      buildout_settings_target="settings.int"
      if test ${custom_build_path} == false
      then
         build_path=/home/ikats/code/
      fi
      ;;
   "preprod")
      buildout_settings_target="settings.preprod"
      if test ${custom_build_path} == false
      then
         build_path=/home/ikats/code/
      fi
      ;;
   "local"|"pic"|*)
      buildout_settings_target="settings"
      if test ${custom_build_path} == false
      then
         build_path=${root_path}_build/
      fi
      ;;
esac

# Build path
if test -d eggs
then 
   rm -rf eggs
fi
if test -d ${build_path}/eggs -a ${clean_eggs} == false
then
   # Backup existing eggs (to avoid getting them again)
   mv ${build_path}/eggs .
fi
echo -e "\n${YELLOW}Generating path${OFF}"
rm -rf ${build_path};
mkdir -p ${build_path}

log_path=${build_path}logs/
mkdir -p ${log_path}

if test -d eggs
then
   # Restoring saved eggs
   mv eggs ${build_path}
fi

# Sources path
sources_path=${root_path}_sources/
if test ${git_login} == "undefined"
then
   echo -e "${RED}  No Git Credentials, assuming projects are already cloned"
   if test ! -d ${sources_path}
   then
      echo "  Source path not found !"
      exit 6;
   fi
else
   echo -e "\n${YELLOW}Generating sources path${OFF}"
   rm -rf ${sources_path};
   mkdir -p ${sources_path}

   # Cloning into sources
   echo -e "\n${YELLOW}Getting sources${OFF}"
   cd ${sources_path}

   git clone -b ${branch} https://${git_login}:${git_password}@thor.si.c-s.fr/git/ikats_core || exit 1;
   git clone -b ${branch} https://${git_login}:${git_password}@thor.si.c-s.fr/git/ikats_algos || exit 1;
   git clone -b ${branch} https://${git_login}:${git_password}@thor.si.c-s.fr/git/ikats_django || exit 1;

fi

# Building deploy src structure
echo -e "\n${YELLOW}Building deployed structure${OFF}"
cd ${build_path}
cp -rf ${sources_path}ikats_core/src/* ${build_path}
cp -rf ${sources_path}ikats_algos/src/* ${build_path}
cp -rf ${sources_path}ikats_django/src/* ${build_path}

cp ${root_path}setup.py ${build_path}
cp ${root_path}bootstrap.py ${build_path}
cp ${root_path}buildout.cfg ${build_path}


cd ${build_path}

echo -e "\n${YELLOW}Configuring python${OFF}"
if test ${proxy_login} != "undefined"
then
   # Only if proxy settings are set
   export http_proxy=http://${proxy_login}:${proxy_password}@proxy3.si.c-s.fr:3128
   export https_proxy=http://${proxy_login}:${proxy_password}@proxy3.si.c-s.fr:3128
   export no_proxy=thor.si.c-s.fr
fi

# Overriding default settings
# Defining logs path
ls ${build_path}ikats/processing/ikats_processing/settings/*.py | xargs -i sed -i -e "s@REP_LOGS = .\+@REP_LOGS = \"${log_path}\"@g" {}
sed -i -e "s/settings = settings/settings = ${buildout_settings_target}/g" buildout.cfg

# Get buildout
python3 bootstrap.py || exit 2;

# Run buildout
${build_path}bin/buildout || exit 2;

# Cleaning pycache
echo -e "${YELLOW}Cleaning pycache${OFF}"
find ${build_path}ikats/ -name "__pycache__" -o -name "*.py[cod]" | xargs -i ls -l {}


# Handling SPARK needs
#TODO if
export SPARK_HOME=${spark_home}
export PYSPARK_PYTHON=${build_path}bin/python
echo -e "${YELLOW}SPARK_HOME set to ${SPARK_HOME}${OFF}"

if test ${run_gunicorn} == true
then
   
   # Migrate
   echo -e "\n${YELLOW}Running Django migration${OFF}"
   ${build_path}bin/django migrate --settings=ikats_processing.${buildout_settings_target} || exit 3;

   # Collect static
   ${build_path}bin/django collectstatic --noinput || exit 3;


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
   fi
  
fi

exit 0
