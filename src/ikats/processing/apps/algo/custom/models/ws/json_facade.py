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
    Mathieu BERAUD <mathieu.beraud@c-s.fr>
"""
import json

from apps.algo.custom.models.ws.algo import CustomizedAlgoWs
from ikats.core.library.exception import IkatsException
from ikats.core.json_util.rest_utilities import LevelInfo


class CustomJsonFacade(object):
    """
    Main ws services of custom app are grouped in this facade, as static methods
    """

    def __init__(self):
        pass

    @classmethod
    def convert_to_business_custo_algo(cls, custom_algo_from_json):
        """
        Returns the business CustomizedAlgo resource from the equivalent json string.
        the customized algorithm

        :param custom_algo_from_json: json input encoding the resource
        :type custom_algo_from_json: str or equivalent json-friendly dict
        :return: the business resource CustomizedAlgo
        :rtype: CustomizedAlgo
        """
        if type(custom_algo_from_json) is str:
            my_dict = json.loads(custom_algo_from_json)
        elif type(custom_algo_from_json) is dict:
            my_dict = custom_algo_from_json
        else:
            msg = "Unexpected type={} for arg custom_algo_from_json in convert_to_business_custo_algo()"
            raise IkatsException(msg.format(type(custom_algo_from_json).__name__))

        my_ws_custo_algo = CustomizedAlgoWs.load_from_dict(my_dict)

        return my_ws_custo_algo.get_customized_algo()

    @classmethod
    def convert_to_ws_custom_algo(cls, business_custom_algo, level=LevelInfo.NORMAL):
        """
        Returns the json-friendly dictionary matching the content view of
          - one CustomizedAlgo resource
          - according to specified level

        :param business_custom_algo: the business resource CustomizedAlgo
        :type business_custom_algo: CustomizedAlgo
        :param level: the specified level: optional, default value is NORMAL
        :type level: LevelInfo
        :return the json-friendly dictionary
        :rtype: dict
        """
        my_rest_api_dto = CustomizedAlgoWs(business_custom_algo)

        return my_rest_api_dto.to_dict(level=level)

    @classmethod
    def convert_to_ws_list_custom_algo(cls, custom_algo_list, level=LevelInfo.SUMMARY):
        """
        Returns the list of json-friendly dictionaries:
        each dictionary is matching the content view of
          - each CustomizedAlgo resource from custom_algo_list
          - according to specified level
        :param custom_algo_list: the list of business resources CustomizedAlgo
        :type custom_algo_list: list
        :param level: the specified level: optional, default value is SUMMARY
        :type level: LevelInfo
        :return: the json string coding the list of customized algo resources
        :rtype: list
        """
        my_rest_api_list = []
        for custom in custom_algo_list:
            my_ws = CustomizedAlgoWs(custom)
            my_rest_api_list.append(my_ws.to_dict(level=level))

        return my_rest_api_list
