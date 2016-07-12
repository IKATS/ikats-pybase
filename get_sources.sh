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
branch=master
git_login="undefined"
proxy_login="undefined"

while [[ $# -gt 0 ]]
do
   key="$1"

   case $key in
      -g|--git_auth)
         read git_login git_password <<< $(echo $2 | sed 's/:/ /')
         shift
         ;;
      -b|--branch)
         branch="$2"
         shift
         ;;
      -h|--help)
         echo -e "${UNDERLINE}USAGE${OFF}"
         echo -e ""
         echo -e "   deploy.sh [-h] [-b|--branch <branch>] -g|--git_auth login:pass"
         echo -e ""
         echo -e "   -h|--help"
         echo -e "                       Displays this help page"
         echo -e ""
         echo -e "   -b|--branch <branch>"
         echo -e "                       use Git branch <branch> to deploy"
         echo -e "                       Default: master"
         echo -e ""
         echo -e "   -g|--git_auth"
         echo -e "                       Specify the Git credentials"
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
echo -e "${YELLOW}hostname = $host${OFF} "

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
exit 0