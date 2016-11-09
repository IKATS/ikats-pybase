#!/bin/bash

echo -e "\nIkats Sources gathering Script\n"

root_path=`pwd`/

# Default values
branch=master
git_login="undefined"
proxy_login="undefined"
no_color=false

while [[ $# -gt 0 ]]
do
   key="$1"

   case $key in
      -g|--git-auth)
         read git_login git_password <<< $(echo $2 | sed 's/:/ /')
         shift
         ;;
      -b|--branch)
         branch="$2"
         shift
         ;;
      --no-color)
         no_color=true
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
         echo -e "   -b|--branch <branch>"
         echo -e "                       use Git branch <branch> to deploy"
         echo -e "                       Default: master"
         echo -e ""
         echo -e "   -g|--git-auth"
         echo -e "                       Specify the Git credentials"
         echo -e ""
         echo -e ""
         echo -e "RETURN STATUS"
         echo -e "-------------"
         echo -e ""
         echo -e "   0: nominal "
         echo -e "   1: Git error"
         echo -e "   2: no sources found"
         echo -e "   3: copy error"
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

host=`hostname`
echo -e "${YELLOW}hostname = $host${OFF}"

# Sources path
sources_path=${root_path}_sources/
if test ${git_login} == "undefined"
then
   echo -e "${RED}  No Git Credentials, assuming projects are already cloned${OFF}"
   if test ! -d ${sources_path}
   then
      echo "  Source path not found !"
      exit 2;
   fi
else
   echo -e "\n${YELLOW}Generating sources path${OFF}"
   rm -rf ${sources_path};
   mkdir -p ${sources_path} || exit 3;

   # Cloning into sources
   echo -e "\n${YELLOW}Getting sources${OFF}"
   cd ${sources_path}

   git clone https://${git_login}:${git_password}@thor.si.c-s.fr/git/ikats_core
   git clone https://${git_login}:${git_password}@thor.si.c-s.fr/git/ikats_algos
   git clone https://${git_login}:${git_password}@thor.si.c-s.fr/git/ikats_django
   
   #Switching to requested branch (or 'master' if not found)
   cd ${sources_path}ikats_core
   git checkout ${branch} 2>/dev/null || echo "branch ${branch} doesn't exist for ikats_core"
   
   cd ${sources_path}ikats_algos
   git checkout ${branch} 2>/dev/null || echo "branch ${branch} doesn't exist for ikats_algos"
   
   cd ${sources_path}ikats_django
   git checkout ${branch} 2>/dev/null || echo "branch ${branch} doesn't exist for ikats_django"
   

fi
exit 0
