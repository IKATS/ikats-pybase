#!/bin/bash

# Fill the environment variables
source ikats.env

# Skip the long tests by default (can be overriden)
export SKIP_LONG_TEST=${SKIP_LONG_TEST:-1}

cd ikats/processing > /dev/null
PYLINT_RCFILE=${IKATS_PATH}/pylint.rc
python3 manage.py jenkins --enable-coverage --keepdb --settings=ikats_processing.settings.docker ikats
