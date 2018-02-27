#!/bin/bash

# Fill the environment variables
source ikats.env

# Skip the long tests by default (can be overriden)
export SKIP_LONG_TEST=${SKIP_LONG_TEST:-1}

# The Working directory is directly the location of the sources
nosetests --with-xunit

# Run the django specific tests
cd ikats/processing > /dev/null
python3 manage.py test --settings=ikats_processing.settings.docker
# python3 manage.py jenkins --enable-coverage
# python3 manage.py collectstatic --noinput
