"""
Copyright 2018 CS Systèmes d'Information

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

"""
import json
import logging

from django.core import serializers
from django.http.response import JsonResponse

from apps.algo.catalogue.models.business.algorithm import Algorithm
from apps.algo.catalogue.models.business.family import FunctionalFamily
from apps.algo.catalogue.models.business.implem import Implementation
from apps.algo.catalogue.models.orm.algorithm import AlgorithmDao
from apps.algo.catalogue.models.orm.family import FunctionalFamilyDao
from apps.algo.catalogue.models.orm.implem import ImplementationDao
from apps.algo.catalogue.models.orm.profile import ProfileItemDao
from apps.algo.catalogue.models.ws.algorithm import AlgorithmWs
from apps.algo.catalogue.models.ws.element import ElementWs
from apps.algo.catalogue.models.ws.implem import ImplementationWs
from ikats.core.json_util.rest_utilities import LevelInfo
from ikats_processing.core.json.http_response import DjangoHttpResponseFactory

LOGGER = logging.getLogger(__name__)


def export_all_implementations(http_request):
    data_family = serializers.serialize("json", FunctionalFamilyDao.objects.all())
    data_algo = serializers.serialize("json", AlgorithmDao.objects.all())
    data_impl = serializers.serialize("json", ImplementationDao.objects.all())
    data_profileitem = serializers.serialize("json", ProfileItemDao.objects.all())

    data = {'functional_families': json.loads(data_family),
            'algo': json.loads(data_algo),
            'implementations': json.loads(data_impl),
            'profile_items': json.loads(data_profileitem)}

    return JsonResponse(data, safe=False)


def get_family_list(http_request):
    """
    Get the list of FunctionalFamily resources defined under the catalogue:
    returned as json list based upon ElementWs

    Example of requests:
      - "http://127.0.0.1:80/ikats/algo/catalogue/families/"
      equivalent to
      - "http://127.0.0.1:80/ikats/algo/catalogue/families"
      equivalent to
      - "http://127.0.0.1:80/ikats/algo/catalogue/families?info_level=1"

    Summary of families:
      - "http://127.0.0.1:80/ikats/algo/catalogue/families?info_level=0"

    Detailed content of families
      - "http://127.0.0.1:80/ikats/algo/catalogue/families?info_level=2"

    :param http_request: request http
    :type http_request: django.http.HttpRequest
    :return: json list of ElementWs::to_dict()
        :rtype: JsonResponse
    """
    return __get_json_list(http_request=http_request,
                           dao_class=FunctionalFamilyDao,
                           business_class=FunctionalFamily,
                           webservice_class=ElementWs,
                           default_level_info=LevelInfo.NORMAL, method_name="get_family_list")


def get_algorithm_list(http_request):
    """
    Get the list of Algorithm resources defined under the catalogue:
    returned as json list based upon AlgorithmWs

    Example of requests:
      - "http://127.0.0.1:80/ikats/algo/catalogue/algorithms/"
      equivalent to
      - "http://127.0.0.1:80/ikats/algo/catalogue/algorithms"
      equivalent to
      - "http://127.0.0.1:80/ikats/algo/catalogue/algorithms?info_level=1"

    Summary of implementations:
      - "http://127.0.0.1:80/ikats/algo/catalogue/algorithms?info_level=0"

    Detailed content of implementations
      - "http://127.0.0.1:80/ikats/algo/catalogue/algorithms?info_level=2"

    :param http_request: request http
    :type http_request: django.http.HttpRequest
    :return: json list of AlgorithmWs::to_dict()
        :rtype: JsonResponse
    """
    return __get_json_list(http_request=http_request,
                           dao_class=AlgorithmDao,
                           business_class=Algorithm,
                           webservice_class=AlgorithmWs,
                           default_level_info=LevelInfo.NORMAL, method_name="get_algorithm_list")


def get_implementation_list(http_request):
    """
    Get the list of Implementation defined under the catalogue:
    returned as json list based upon ImplementationWs

    Example of requests:
      - "http://127.0.0.1:80/ikats/algo/catalogue/implementations/"
      equivalent to
      - "http://127.0.0.1:80/ikats/algo/catalogue/implementations"
      equivalent to summary level of information:
      - "http://127.0.0.1:80/ikats/algo/catalogue/implementations?info_level=0"

    Standard description, more detailed:
      - "http://127.0.0.1:80/ikats/algo/catalogue/implementations?info_level=1"

    Detailed content of implementations
      - "http://127.0.0.1:80/ikats/algo/catalogue/implementations?info_level=2"

    :param http_request: request http
    :type http_request: django.http.HttpRequest
    :return : json list of ImplementationWs::to_dict()
    :rtype: JsonResponse
        """

    return __get_json_list(http_request=http_request,
                           dao_class=ImplementationDao,
                           business_class=Implementation,
                           webservice_class=ImplementationWs,
                           default_level_info=LevelInfo.SUMMARY, method_name="get_implementation_list")


def get_family_by_name(http_request, name):
    """
    Get the unique Family resource defined under the catalogue, for the functional name.
    returned as json object based upon ElementWs

    Example of requests:
        - "http://127.0.0.1:80/ikats/algo/catalogue/families/my_func_name"
        equivalent to
        - "http://127.0.0.1:80/ikats/algo/catalogue/families/my_func_name?info_level=1"

    Summary:
        - "http://127.0.0.1:80/ikats/algo/catalogue/families/my_func_name?info_level=0"

    Detailed content:
        - "http://127.0.0.1:80/ikats/algo/catalogue/families/my_func_name?info_level=2"

    :param http_request: request http
    :type http_request: django.http.HttpRequest
    :param name: functional name of searched resource
    :type name: str
    :return : json object issued from ElementWs::to_dict()
    :rtype: JsonResponse
        """
    return __get_json_with_name(http_request=http_request,
                                searched_name=name,
                                dao_class=FunctionalFamilyDao,
                                webservice_class=ElementWs,
                                default_level_info=LevelInfo.NORMAL,
                                method_name="get_family_by_name")


def get_algorithm_by_name(http_request, name):
    """
    Get the unique Algorithm resource defined under the catalogue, for the functional name.
    returned as json object based upon AlgorithmWs

    Example of requests:
        - "http://127.0.0.1:80/ikats/algo/catalogue/algorithms/my_func_name"
        equivalent to
        - "http://127.0.0.1:80/ikats/algo/catalogue/algorithms/my_func_name?info_level=1"

    Summary:
        - "http://127.0.0.1:80/ikats/algo/catalogue/algorithms/my_func_name?info_level=0"

    Detailed content:
        - "http://127.0.0.1:80/ikats/algo/catalogue/algorithms/my_func_name?info_level=2"

    :param http_request: request http
    :type http_request: django.http.HttpRequest
    :param name: functional name of searched resource
    :type name: str
    :return: json object issued from AlgorithmWs::to_dict()
    :rtype: JsonResponse
        """
    return __get_json_with_name(http_request=http_request,
                                searched_name=name,
                                dao_class=AlgorithmDao,
                                webservice_class=AlgorithmWs,
                                default_level_info=LevelInfo.NORMAL,
                                method_name="get_algorithm_by_name")


def get_implem_by_name(http_request, name):
    """
    Get the unique Implementation resource defined under the catalogue, for the functional name.
    returned as json object based upon ImplementationWs

    Example of requests:
        - "http://127.0.0.1:80/ikats/algo/catalogue/implementations/my_func_name"
        equivalent to
        - "http://127.0.0.1:80/ikats/algo/catalogue/implementations/my_func_name?info_level=1"

    Summary:
        - "http://127.0.0.1:80/ikats/algo/catalogue/implementations/my_func_name?info_level=0"

    Detailed content:
        - "http://127.0.0.1:80/ikats/algo/catalogue/implementations/my_func_name?info_level=2"

    :param http_request: request http
    :type http_request: django.http.HttpRequest
    :param name: functional name of searched resource
    :type name: str
    :return: json object issued from ImplementationWs::to_dict()
    :rtype: JsonResponse
        """
    return __get_json_with_name(http_request=http_request,
                                searched_name=name,
                                dao_class=ImplementationDao,
                                webservice_class=ImplementationWs,
                                default_level_info=LevelInfo.NORMAL,
                                method_name="get_implem_by_name")


def get_implementation(http_request, id_implementation):
    """
    Get the web service resource for ImplementationDao defined under the catalogue

    Example of requests:
      - "http://127.0.0.1:80/ikats/algo/catalogue/implementations/1"
      - "http://127.0.0.1:80/ikats/algo/catalogue/implementations/00001"

    :param http_request: request http
    :type http_request: django HttpQuery
    :param id_implementation: database primary key (number)
    :type id_implementation: str coding the integer value
        :return: implementationDao in a json format
        :rtype: JsonResponse
    """
    response_builder = DjangoHttpResponseFactory()
    try:

        internal_id = int(id_implementation)

        business_obj = ImplementationDao.find_from_key(internal_id)

        if business_obj is None:
            return response_builder.get_json_response_not_found("Implementation resource not found for id=%s"
                                                                % str(internal_id))

        ws_obj = ImplementationWs(business_obj)

        return JsonResponse(ws_obj.to_dict())

    except Exception as err:
        LOGGER.exception(err)
        info = "WS: No such record: ImplementationDao id=%s" % (
            id_implementation)
        LOGGER.error(info)
        return JsonResponse({"error": {'ikats_error': info,
                                       'internal_error': ascii(str(err))}})


def __get_json_list(http_request, dao_class, business_class, webservice_class, default_level_info, method_name):
    response_builder = DjangoHttpResponseFactory()
    try:

        if http_request.method == 'GET':
            str_info_level = http_request.GET.get('info_level', default=None)
            if str_info_level is None:
                info_level = default_level_info
            else:
                try:
                    info_level = LevelInfo.parse(int(str_info_level))
                except Exception as err_query:
                    return response_builder.get_json_response_bad_request(
                        ikats_error="Bad value of query param named 'info_level' in %s" % method_name,
                        exception=err_query)
            serializable_list = [webservice_class(x.build_business()).to_dict(
                level=info_level) for x in dao_class.find_all_orm()]

            # save = False because serializable_list is not a dict
            return JsonResponse(serializable_list, safe=False)
        else:
            return response_builder.get_json_response_bad_request(
                ikats_error="Bad http method: service %s expects GET" % method_name)

    except Exception as err:
        LOGGER.exception(err)
        return response_builder.get_json_response_internal_server_error(
            ikats_error="Unexpected server error in %s" % method_name, exception=err)


def __get_json_with_name(http_request, searched_name,
                         dao_class,
                         webservice_class,
                         default_level_info,
                         method_name):
    response_builder = DjangoHttpResponseFactory()
    try:

        if http_request.method == 'GET':
            str_info_level = http_request.GET.get('info_level', default=None)
            if str_info_level is None:
                info_level = default_level_info
            else:
                try:
                    info_level = LevelInfo.parse(int(str_info_level))
                except Exception as err_query:
                    return response_builder.get_json_response_bad_request(
                        ikats_error="Bad value of query param named 'info_level' in " + method_name,
                        exception=err_query)

            serializable_list = [webservice_class(x).to_dict(level=info_level)
                                 for x in dao_class.find_business_elem_with_name(searched_name)]
            if len(serializable_list) > 1:
                my_detailed_error = "Unexpected multiple resources matched:"
                for json_item in serializable_list:
                    my_detailed_error = " [db_id=" + json_item.model_business.db_id + "]"
                my_error = "Unexpected conflict in {0}: service should retrieve at most one resource, name={1} \
                            should match a unique resource".format(method_name, searched_name)
                return response_builder.get_json_response_conflict(ikats_error=my_error,
                                                                   exception=my_detailed_error)
            elif len(serializable_list) == 0:
                my_error = "Resource not found in {0} with name={1}".format(method_name, searched_name)
                return response_builder.get_json_response_not_found(ikats_error=my_error)

            # save = False => do not check that serializable_list[0] is dict
            return JsonResponse(serializable_list[0], safe=False)
        else:
            return response_builder.get_json_response_bad_request(
                ikats_error="Bad http method: service %s expects GET" % method_name)

    except Exception as err:
        return response_builder.get_json_response_internal_server_error(
            ikats_error="Unexpected server error in " + method_name, exception=err)
