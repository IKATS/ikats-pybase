#!/bin/bash

# Script to call inside container to prepare test campaign

cd /ikats
chown ikats:ikats /ikats/*

# Install tests modules dependencies
pip3 install -r test_requirements.txt

# Add django_jenkins to INSTALLED_APPS
sed -i "/INSTALLED_APPS = \[/a  'django_jenkins'," /ikats/ikats/processing/ikats_processing/settings/docker.py
