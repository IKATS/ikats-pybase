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
from ikats_processing.core.http import HttpResponseFactory
from django.http.response import JsonResponse

"""
Module grouping JSON http response services
"""


class DjangoHttpResponseFactory(HttpResponseFactory):
    """
    Class grouping services building the http response with django framework:
      - basic services from superclass HttpResponseFactory
      - json services from DjangoHttpResponseFactory
    """

    def __init__(self):
        """
        Constructor
        """
        pass

    def get_json_response_bad_method(self, ikats_error=None, exception=None):
        """
        Build and returns the response for status NOT_ALLOWED_METHOD_HTTP_STATUS
        :param ikats_error: optional, exclusive with data: high-level error, context, diagnostic
        :type ikats_error: str
        :param exception: optional, exclusive with data: internal error: details about the error
        :type exception: Exception or any object with appropriate __str__ method
        :return: encoded response with status and json ikats error content
        :rtype: JsonResponse
        """
        return self.get_json_response_error(http_status_code=self.NOT_ALLOWED_METHOD_HTTP_STATUS,
                                            ikats_error=ikats_error,
                                            exception=exception)

    def get_json_response_bad_request(self, ikats_error=None, exception=None):
        """
        Build and returns the response for status BAD_REQUEST_HTTP_STATUS
        :param ikats_error: optional, exclusive with data: high-level error, context, diagnostic
        :type ikats_error: str
        :param exception: optional, exclusive with data: internal error: details about the error
        :type exception: Exception or any object with appropriate __str__ method
        :return: encoded response with status and json ikats error content
        :rtype: JsonResponse
        """
        return self.get_json_response_error(http_status_code=self.BAD_REQUEST_HTTP_STATUS,
                                            ikats_error=ikats_error,
                                            exception=exception)

    def get_json_response_not_found(self, ikats_error=None, exception=None):
        """
        Build and returns the response for status NOT_FOUND_HTTP_STATUS
        :param ikats_error: optional, exclusive with data: high-level error, context, diagnostic
        :type ikats_error: str
        :param exception: optional, exclusive with data: internal error: details about the error
        :type exception: Exception or any object with appropriate __str__ method
        :return: encoded response with status and json ikats error content
        :rtype: JsonResponse
        """
        return self.get_json_response_error(http_status_code=self.NOT_FOUND_HTTP_STATUS,
                                            ikats_error=ikats_error,
                                            exception=exception)

    def get_json_response_conflict(self, ikats_error=None, exception=None):
        """
        Build and returns the response for status CONFLICT_HTTP_STATUS
        :param ikats_error: optional, exclusive with data: high-level error, context, diagnostic
        :type ikats_error: str
        :param exception: optional, exclusive with data: internal error: details about the error
        :type exception: Exception or any object with appropriate __str__ method
        :return: encoded response with status and json ikats error content
        :rtype: JsonResponse
        """
        return self.get_json_response_error(http_status_code=self.CONFLICT_HTTP_STATUS,
                                            ikats_error=ikats_error,
                                            exception=exception)

    def get_json_response_internal_server_error(self, ikats_error=None, exception=None):
        """
        Build and returns the response for status SERVER_ERROR_HTTP_STATUS
        :param ikats_error: optional, exclusive with data: high-level error, context, diagnostic
        :type ikats_error: str
        :param exception: optional, exclusive with data: internal error: details about the error
        :type exception: Exception or any object with appropriate __str__ method
        :return: encoded response with status and json ikats error content
        :rtype: JsonResponse
        """
        return self.get_json_response_error(http_status_code=self.SERVER_ERROR_HTTP_STATUS,
                                            ikats_error=ikats_error,
                                            exception=exception)

    @staticmethod
    def get_json_response_error_with_data(http_status_code, http_msg, data_name, data):
        """
        Generate a json http response encoded for errors with specific data (object json-friendly)
                and its property name.

           {
             'http_msg': <http_msg>
             <data_name>: <data>
           }
        :param http_status_code: http code
        :type http_status_code: int
        :param http_msg: summary message
        :type http_msg: str
        :param data_name: name of property data in the json encoded string
        :type data_name: str
        :param data: json-friendly python object
        :type data: dict or list or tuple or str
        """

        error = {'http_msg': http_msg, data_name: data}

        response = JsonResponse(error)
        response.status_code = http_status_code

        return response

    @staticmethod
    def get_json_response_error(http_status_code, ikats_error=None, exception=None, data=None):
        """
        Builds and returns the response ... generic version with HTTP code
        :param http_status_code:required HTTP code status (use DjangoHttpResponseFactory constants)
        :type http_status_code: int
        :param ikats_error: optional, exclusive with data: high-level error, context, diagnostic
        :type ikats_error: str or None
        :param exception: optional, exclusive with data: internal error: details about the error
        :type exception: Exception or None or any object with appropriate __str__ method
        :param data: !!! DEPRECATED USE (it is better to use get_json_response_error_with_data) !!! :
        optional, exclusive with ikats_error+exception: json content
        :type data: dict
        :return: encoded response with status and json ikats error content
        :rtype: JsonResponse
        """
        if data is None:
            # No data content defined => built from ikats_error and exception
            error = {}

        else:
            # In case of defined data; set it as json content
            if isinstance(data, dict):
                error = data
            else:
                error = {
                    'error': "Error in DjangoHttpResponseFactory::get_json_response_error():"
                             " arg is not dict: data={0}".format(repr(data))
                }

        if ikats_error:
            error['http_msg'] = "{}".format(ikats_error)
        else:
            error['http_msg'] = "Error is raised"

        if exception is not None:
            error['internal_error'] = "{}".format(exception)

        response = JsonResponse(error)
        response.status_code = http_status_code

        return response

    def get_json_response_nominal(self, data):
        """
        Returns response with http code 200, with content specified
        :param data: the json-friendly python dict defining the content
        :type data: dict
        :return: encoded response with status and json content specified by data
        :rtype: JsonResponse
        """
        if isinstance(data, dict):
            content = data
        else:
            content = {
                'content': "Error in DjangoHttpResponseFactory::get_json_response_nominal(): "
                           "arg is not dict: data={0}".format(repr(data))
            }

        data['http_msg'] = "ok"
        response = JsonResponse(content)
        response.status_code = self.OK_HTTP_STATUS
        return response
