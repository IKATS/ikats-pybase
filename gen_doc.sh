#!/bin/bash


root_path=`pwd`/

# Default values
merged_src_path=${root_path}_build/
no_color=false
doc_path=${root_path}doc/

while [[ $# -gt 0 ]]
do
   key="$1"

   case $key in
      --no-color)
         no_color=true
         ;;
      -d)
         doc_path="$2"
         shift
         ;;
      -h|--help)
         echo -e "USAGE"
         echo -e "-----"
         echo -e ""
         echo -e "   gen_doc.sh [-h] [--no-color] [-d <doc_path>]"
         echo -e ""
         echo -e "       -h"
         echo -e "            Display this help"
         echo -e ""
         echo -e "       -d <doc_path>"
         echo -e "            Define the doc path to <doc_path>"
         echo -e ""
         echo -e "       --no-color"
         echo -e "            Don't use color during script run"
         echo -e ""
         echo -e "RETURN STATUS"
         echo -e "-------------"
         echo -e ""
         echo -e "   0: nominal "
         echo -e "   1: Copy error"
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

echo -e "\n${YELLOW}${UNDERLINE}Ikats Python Documentation Generation Script${OFF}\n"

# Build path
echo -e "\n${YELLOW}Generating path${OFF}"
rm -rf ${merged_src_path} || exit 1;
mkdir -p ${merged_src_path} || exit 1;

# Sources path
clone_src_path=${root_path}_sources/

# Building deploy src structure
echo -e "\n${YELLOW}Building deployed structure${OFF}"
cd ${merged_src_path}
cp -rf ${clone_src_path}ikats_core/src/* ${merged_src_path} || exit 1;
cp -rf ${clone_src_path}ikats_algos/src/* ${merged_src_path} || exit 1;
cp -rf ${clone_src_path}ikats_django/src/* ${merged_src_path} || exit 1;

# Define and clean space
rm -rf ${doc_path}
mkdir -p ${doc_path}

# Copy items needed by generation
cd ${doc_path}
cp ${root_path}ikats_logo.png ${doc_path}
cp ${root_path}conf.py ${doc_path}
cp ${root_path}Makefile ${doc_path}
cp ${root_path}index.rst ${doc_path}

export PYTHONPATH=${merged_src_path}:$PYTHONPATH

# Generate documentation
sphinx-apidoc  -fPe -o ${doc_path} ${merged_src_path}ikats/
make html
echo "index.html available at : \n  ${doc_path}_build/html/index.html"

exit 0;
