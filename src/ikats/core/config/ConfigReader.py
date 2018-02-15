"""
LICENSE:
--------
Copyright 2017-2018 CS SYSTEMES D'INFORMATION

Licensed to CS SYSTEMES D'INFORMATION under one
or more contributor license agreements. See the NOTICE file
distributed with this work for additional information
regarding copyright ownership. CS licenses this file
to you under the Apache License, Version 2.0 (the
"License"); you may not use this file except in compliance
with the License. You may obtain a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an
"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
KIND, either express or implied. See the License for the
specific language governing permissions and limitations
under the License.

.. codeauthors::
    Fabien TORTORA <fabien.tortora@c-s.fr>
    Maxime PERELMUTER <maxime.perelmuter@c-s.fr>
"""

import configparser

from ikats.core.config import IKATS_CONFIG_PATH


class ConfigReader(object):
    """
    Class allowing to get information from the configuration file
    """

    def __init__(self):
        # Get the cluster configuration
        self.config = configparser.ConfigParser()
        self.config.read("%s/ikats.conf" % IKATS_CONFIG_PATH)

    def get(self, section, param):
        """
        Get the value of a parameter located inside section
        :param section: Section to find parameter in
        :param param: parameter name to get value from
        :type section: str
        :type param: str

        :return: the value of the parameter

        :raises ValueError: if section not well defined
        :raises ValueError: if param not well defined
        """

        if section is None or section == "" or not isinstance(section, str):
            raise ValueError("Section not well defined")

        if param is None or param == "" or not isinstance(param, str):
            raise ValueError("Parameter not well defined")

        return self.config[section][param]
