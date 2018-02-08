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
import logging

from django.http.response import JsonResponse

from apps.algo.catalogue.models.orm.implem import ImplementationDao
from apps.algo.custom.models.business.custo_facade import CustomFacade
from apps.algo.custom.models.orm.algo import CustomizedAlgoDao
from apps.algo.custom.models.ws.algo import CustomizedAlgoWs
from apps.algo.custom.models.ws.json_facade import CustomJsonFacade
from ikats.core.json_util.rest_utilities import LevelInfo
from ikats.core.library.exception import IkatsException, IkatsInputError, IkatsNotFoundError
from ikats_processing.core.http import HttpCommonsIkats, HttpResponseFactory
from ikats_processing.core.json.http_response import DjangoHttpResponseFactory

LOG_WS_CUSTOM = logging.getLogger(__name__)

ERR_CRUD_CUSTOM_ALGO = "Failed to %s customized algorithm %s"


def not_allowed_method(http_request):
    """
    Generates the "NOT ALLOWED METHOD" response
    :param http_request: the http request
    :type http_request: django.http.HttpRequest
    :return: the "NOT ALLOWED METHOD" response
    :rtype:  JsonResponse
    """
    msg = "Rejected HTTP method in the context: {}".format(http_request.path)
    LOG_WS_CUSTOM.error(msg)
    response_builder = DjangoHttpResponseFactory()
    return response_builder.get_json_response_bad_method(ikats_error=msg)


def pattern_custom_algos_with_id(http_request, customized_algo_id):
    """
    The entry point of the url configuration named 'pattern_custom_algos_with_id'
    in the configuration apps/algo/custom/urls.py.

    This entry point is calling the relevant function:
      - get_custom_algo with http method GET
      - update_custom_algo with http method PUT
      - delete_custom_algo with http method DELETE
      - otherwise: not_allowed_method

    :param http_request: the request
    :type http_request: HttpRequest
    :param customized_algo_id: the ID of the customizedAlgo resource
    :type customized_algo_id: str or int
    :return: the response
    :rtype: HttpResponse or JsonResponse
    """
    if http_request.method == 'GET':
        return get_custom_algo(http_request, customized_algo_id, http_request.GET)
    elif http_request.method == 'PUT':
        return update_custom_algo(http_request, customized_algo_id)
    elif http_request.method == 'DELETE':
        return delete_custom_algo(http_request, customized_algo_id)
    else:
        return not_allowed_method(http_request)


def pattern_custom_algos_dummy(http_request):
    """
    The entry point of the url configuration named 'pattern_custom_algos_dummy'
    in the configuration apps/algo/custom/urls.py.

    This entry point is calling the relevant function:
      - find_custom_algo with method GET
      - create_custom_algo with method POST
      - otherwise: not_allowed_method

    :param http_request: the request
    :type http_request: HttpRequest
    :return: the response
    :rtype: HttpResponse or JsonResponse
    """
    if http_request.method == 'GET':
        return find_custom_algo(http_request, http_request.GET)
    elif http_request.method == 'POST':
        return create_custom_algo(http_request)
    else:
        return not_allowed_method(http_request)


def get_custom_algo(http_request, customized_algo_id, query_dict):
    """
    Reads the CustomizedAlgo specified
    :param http_request: the request
    :type http_request: HttpRequest
    :param customized_algo_id: the database ID of the CustomizedAlgo
    :type customized_algo_id: str of int
    :param query_dict: the query parameters
    :type query_dict: QueryDict
    :return: the Json response (nominal or error).
    :rtype: JsonResponse
    """

    # Builds the response in blocks try: or except:
    response_builder = DjangoHttpResponseFactory()
    try:
        # info-level is used to adapt the returned content of resource
        my_level = HttpCommonsIkats.get_info_level(http_request, query_dict)

        my_id = CustomizedAlgoDao.parse_dao_id(customized_algo_id)
        buzz_custom_algo = CustomizedAlgoDao.find_business_elem_with_key(primary_key=my_id)

        LOG_WS_CUSTOM.info("Found customized algo with id=%s: %s", customized_algo_id, buzz_custom_algo)

        # CustomizedAlgoWs is wrapping the business resource
        # => manages the user rendering: json format, according to info-level
        ws_custom_algo = CustomizedAlgoWs(buzz_custom_algo)
        dict_custom_algo = ws_custom_algo.to_dict(level=my_level)

        my_response = JsonResponse(dict_custom_algo, safe=False)

    except CustomizedAlgoDao.DoesNotExist:
        # Example: customized_algo_id=99999999 is not matching a resource in database
        msg = "Does not exist: customized algo with id=%s" % customized_algo_id
        LOG_WS_CUSTOM.error(msg)
        my_response = response_builder.get_json_response_not_found(ikats_error=msg)

    except IkatsInputError as err:
        # Example: invalid info_level value in query params ...
        LOG_WS_CUSTOM.exception(err)
        msg = "Bad request in get_custom_algo with id={}".format(customized_algo_id)
        LOG_WS_CUSTOM.error(msg)
        my_response = response_builder.get_json_response_bad_request(ikats_error=msg, exception=err)

    except Exception as err:
        # Any unexpected error: database crash ...
        LOG_WS_CUSTOM.exception(err)
        msg = "Unexpected server error in get_custom_algo with id={}".format(customized_algo_id)
        LOG_WS_CUSTOM.error(msg)
        my_response = response_builder.get_json_response_internal_server_error(ikats_error=msg)

    return my_response


def find_custom_algo(http_request, query_dict):
    """
    Find all customized algo which are accepted by filter, according to the query parameters in url:
    name, label, desc.
    :param http_request: the django request built by custom app, driven by its urls.py
    :type http_request: HttpRequest
    :param query_dict: the query dictionary containing optional filtering criteria
    :type query_dict: QueryDict
    :return: the Json response (nominal or error).
    :rtype: JsonResponse
    """
    # Builds the response in try: or except: blocks:
    response_builder = DjangoHttpResponseFactory()
    # Required for encoding messages in try: or except: blocks
    spec_crit = {}
    try:

        name = query_dict.get("name", None)
        label = query_dict.get("label", None)
        desc = query_dict.get("desc", None)

        # info-level is used to adapt the returned content of resource
        my_level = HttpCommonsIkats.get_info_level(http_request, query_dict, default=LevelInfo.SUMMARY)

        spec_crit = {'name': name, 'label': label, 'desc': desc}

        business_list = CustomFacade.search_with_criteria(name=name,
                                                          label=label,
                                                          desc_content=desc)

        if len(business_list) > 0:
            ids = [x.db_id for x in business_list]
            LOG_WS_CUSTOM.info("Found customized algo for ids=%s, matching search criteria %s", ids, spec_crit)

            # Encodes the result in json format, list of resources with the defined info-level
            serializable_list = CustomJsonFacade.convert_to_ws_list_custom_algo(business_list,
                                                                                level=my_level)
            my_response = JsonResponse(serializable_list, safe=False)

        else:
            msg = "Does not exist: customized algo matching search criteria %s" % spec_crit
            LOG_WS_CUSTOM.error(msg)

            my_response = response_builder.get_json_response_not_found(ikats_error=msg)

    except IkatsInputError as err:
        # Example: invalid info_level value in query params ...
        LOG_WS_CUSTOM.exception(err)
        msg = "Bad request in find_custom_algo for criteria={}".format(spec_crit)
        LOG_WS_CUSTOM.error(msg)
        my_response = response_builder.get_json_response_bad_request(ikats_error=msg, exception=err)

    except Exception as err:
        # Any unexpected error: database crash ...
        LOG_WS_CUSTOM.exception(err)
        msg = "Unexpected server error in find_custom_algo for criteria={}".format(spec_crit)
        LOG_WS_CUSTOM.error(msg)
        my_response = response_builder.get_json_response_internal_server_error(ikats_error=msg)

    return my_response


def find_custom_algos_for_implem(http_request, implementation_id):
    """
    Finds all customized algo which are customizing specified implementation.
    :param http_request: the django request built by custom app, driven by its urls.py
    :type http_request: HttpRequest
    :param implementation_id: the identifier of the implementation
    :type implementation_id: int or parsable str
    :return: the Json response (nominal or error).
    :rtype: JsonResponse
    """

    # Rejecting not allowed method cases: POST, PUT or DELETE
    if http_request.method != 'GET':
        return not_allowed_method(http_request)

    # ... dealing with the expected GET method
    #
    # Will help to build the response in try: or except: bodies
    response_builder = DjangoHttpResponseFactory()

    # Returned object
    my_response = None

    try:
        query_dict = http_request.GET

        # info-level is used to adapt the returned content of resource
        my_level = HttpCommonsIkats.get_info_level(http_request, query_dict, default=LevelInfo.SUMMARY)

        business_list = CustomFacade.search_with_criteria(implem_id=implementation_id)
        if len(business_list) > 0:
            ids = [x.db_id for x in business_list]
            LOG_WS_CUSTOM.info("Found customized algo versions %s of implementation id=%s", ids, implementation_id)

            serializable_list = CustomJsonFacade.convert_to_ws_list_custom_algo(business_list,
                                                                                level=my_level)

            my_response = JsonResponse(serializable_list, safe=False)

        elif len(business_list) == 0:
            my_implem_key = ImplementationDao.parse_dao_id(implementation_id)
            try:
                ImplementationDao.find_business_elem_with_key(primary_key=my_implem_key)

                LOG_WS_CUSTOM.info("Does not exist: customized algo of implementation id=%s", implementation_id)

                my_response = JsonResponse([], safe=False)

            except ImplementationDao.DoesNotExist:
                # Example: implementation_id does not exist in database
                msg = "Unknown Implementation ID={} occurred in find_custom_algos_for_implem"
                msg = msg.format(implementation_id)
                LOG_WS_CUSTOM.error(msg)

                my_response = response_builder.get_json_response_not_found(ikats_error=msg)

    except IkatsInputError as err:
        # Example: invalid info_level value in query params ...
        LOG_WS_CUSTOM.exception(err)
        msg = "Bad request in find_custom_algos_for_implem with id={}".format(implementation_id)
        LOG_WS_CUSTOM.error(msg)
        my_response = response_builder.get_json_response_bad_request(ikats_error=msg, exception=err)

    except Exception as err:
        # Example: database is down
        LOG_WS_CUSTOM.exception(err)
        msg = "Unexpected server error in find_custom_algos_for_implem with id={}".format(implementation_id)
        LOG_WS_CUSTOM.error(msg)
        my_response = response_builder.get_json_response_internal_server_error(ikats_error=msg)

    # Finally returned: nominal response or error response
    return my_response


def delete_custom_algo(http_request, customized_algo_id):
    """
    Deletes the customized algorithm.
    :param http_request: the request
    :type http_request: HttpRequest
    :param  customized_algo_id: the ID of the deleted resource
    :type customized_algo_id: int, str
    :return: the response
    :rtype: HttpResponse in nominal case, JsonResponse otherwise
    """

    # http_request param is passed by django dispatcher even if not used

    response_builder = DjangoHttpResponseFactory()
    try:
        CustomFacade.delete_custom_algo(customized_algo_id)
        my_response = response_builder.response_empty_ok()

    except IkatsNotFoundError as not_found_err:
        LOG_WS_CUSTOM.exception(not_found_err)
        msg = "DELETE failed on CustomizedAlgo with id={}: resource not found"
        msg = msg.format(customized_algo_id)
        LOG_WS_CUSTOM.error(msg)
        my_response = response_builder.get_json_response_not_found(ikats_error=msg, exception=not_found_err)

    except Exception as err:
        # Example: database is down
        LOG_WS_CUSTOM.exception(err)
        msg = "DELETE failed on CustomizedAlgo with id={}: server error".format(customized_algo_id)
        LOG_WS_CUSTOM.error(msg)
        my_response = response_builder.get_json_response_internal_server_error(ikats_error=msg, exception=err)

    # Finally returned: nominal response or error response
    return my_response


def create_custom_algo(http_request):
    """
    CREATE Rest service on CustomizedAlgo
    :param http_request: the request
    :type http_request: HttpRequest
    :return: the response
    :rtype: JsonResponse
    """
    return write_custom_algo(http_request=http_request,
                             customized_algo_id=None,
                             operation_info="CREATE",
                             facade_function=CustomFacade.create_custom_algo,
                             nominal_http_status=HttpResponseFactory.CREATED_HTTP_STATUS)


def update_custom_algo(http_request, customized_algo_id):
    """
    UPDATE Rest service on CustomizedAlgo
    :param http_request:
    :type http_request:
    :param customized_algo_id: ID from the URL
    :type customized_algo_id: str or int are accepted
    :return: the response
    :rtype: JsonResponse
    """
    return write_custom_algo(http_request=http_request,
                             customized_algo_id=customized_algo_id,
                             operation_info="UPDATE",
                             facade_function=CustomFacade.update_custom_algo,
                             nominal_http_status=HttpResponseFactory.OK_HTTP_STATUS)


def write_custom_algo(http_request, customized_algo_id,
                      operation_info, facade_function, nominal_http_status):
    """
    Internal operation: factorized code for update/create operations on CustomizedAlgo
    :param http_request: the input request
    :type http_request: HttpRequest
    :param customized_algo_id: the parsed parameter from path pattern: string encoding the database key
    :type customized_algo_id: str or None
    :param operation_info: the internal message
    :type operation_info: str
    :param facade_function: the CRUD function called:  facade_function codes either CREATE or UPDATE
    :type facade_function: function
    :param nominal_http_status: the returned code is either 201 (CREATE) or 200 (UPDATE)
    :type nominal_http_status: int
    :return: the response
    :rtype: JsonResponse
    """
    response_builder = DjangoHttpResponseFactory()
    try:
        data = HttpCommonsIkats.load_json_from_request(http_request)

        LOG_WS_CUSTOM.debug("Starting %s CustomizedAlgo with posted_data=%s", operation_info,
                            json.dumps(obj=data, indent=2))
        # Translates object parsed from json into the business resource
        buzz_custom_algo = CustomJsonFacade.convert_to_business_custo_algo(data)
        if customized_algo_id:
            # ID path param defined inn update context only ...
            if (buzz_custom_algo.db_id is not None) and (customized_algo_id != buzz_custom_algo.db_id):
                # ... not forbidden to specify the ID in the json content ...
                # but it must match the path parameter coding the ID
                # => here ids are not equal => raise error
                raise IkatsInputError("Integrity error:" +
                                      " the ID from URL is different from the optional ID from posted data")
            my_key = CustomizedAlgoDao.parse_dao_id(customized_algo_id)
            # ... check that the resource exists in database
            CustomFacade.get_custom_algo(my_key)
        else:
            # No ID specified: CREATE mode
            # => check that no other custom algo have the same name
            search = CustomFacade.search_with_criteria(implem_id=None, name=buzz_custom_algo.name)
            if len(search) > 0:
                raise IkatsException("Conflict with existing name")

        # Called CRUD operation: facade_function is either CREATE or UPDATE
        # - see effective functions in the calling context of write_custom_algo
        (modified_buzz_custom_algo, check_status) = facade_function(buzz_custom_algo)

        if (check_status is None) or (not check_status.has_errors()):

            # Case when no error is detected in the definition of customized algorithm
            #
            if modified_buzz_custom_algo is None:
                # Server error dealt below ...
                raise IkatsException("Unexpected result with undefined CustomizedAlgo, and empty error list")

            else:
                # Algo successfully written
                my_id = modified_buzz_custom_algo.db_id
                LOG_WS_CUSTOM.info("%s success: CustomizedAlgo with id=%s", operation_info, my_id)

                my_response = HttpResponseFactory.response_resource_written_ok('pattern_custom_algos_with_id',
                                                                               modified_buzz_custom_algo.db_id,
                                                                               nominal_http_status,
                                                                               http_request)
                LOG_WS_CUSTOM.info("Success %s: CustomizedAlgo with url location=%s", operation_info,
                                   my_response.get('Location', "null"))
        else:
            # Deals with check errors:
            #  - unexpected type of value,
            #  - or value outside of configured domain
            context = "{} aborted: errors detected in the checker status:".format(operation_info)
            code = response_builder.BAD_REQUEST_HTTP_STATUS
            LOG_WS_CUSTOM.error(context)
            my_status = check_status.to_dict(data_info=data)

            LOG_WS_CUSTOM.error(json.dumps(obj=my_status, indent=2))

            my_response = response_builder.get_json_response_error_with_data(http_status_code=code,
                                                                             http_msg=context,
                                                                             data_name="check_error",
                                                                             data=check_status.to_dict())
    except IkatsInputError as input_err:
        # Example; any error detected in the request (different from conflict)
        LOG_WS_CUSTOM.exception(input_err)
        msg = ERR_CRUD_CUSTOM_ALGO % (operation_info, ": input error")
        LOG_WS_CUSTOM.error(msg)

        my_response = response_builder.get_json_response_bad_request(ikats_error=msg, exception=input_err)

    except IkatsNotFoundError as not_found_err:
        # Example: update: the resource does not exist
        # Example2: create: the referenced implementation does not exist
        LOG_WS_CUSTOM.exception(not_found_err)
        msg = ERR_CRUD_CUSTOM_ALGO % (operation_info, ": resource not found")
        LOG_WS_CUSTOM.error(msg)

        my_response = response_builder.get_json_response_not_found(ikats_error=msg, exception=not_found_err)

    except IkatsException as conflict_err:
        # Example: resource already created.
        LOG_WS_CUSTOM.exception(conflict_err)
        msg = ERR_CRUD_CUSTOM_ALGO % (operation_info, ": conflict error")
        LOG_WS_CUSTOM.error(msg)

        my_response = response_builder.get_json_response_conflict(ikats_error=msg, exception=conflict_err)

    except Exception as err:
        # Any other error: example: database is down
        LOG_WS_CUSTOM.exception(err)
        msg = ERR_CRUD_CUSTOM_ALGO % (operation_info, ": unexpected error")
        LOG_WS_CUSTOM.error(msg)
        my_response = response_builder.get_json_response_internal_server_error(ikats_error=msg,
                                                                               exception=err)
    # Finally returned: nominal response or error response
    return my_response
