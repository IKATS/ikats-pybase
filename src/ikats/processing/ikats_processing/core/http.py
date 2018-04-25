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

from django.conf import settings
from django.core.urlresolvers import reverse
from django.http.response import HttpResponse

import json

from ikats.core.json_util.rest_utilities import LevelInfo
from ikats.core.library.exception import IkatsInputError, IkatsInputContentError

"""
Module grouping common services carrying about Http response/request services
in the django context.
"""


class HttpCommonsIkats(object):
    """
    This class groups some services commonly used in
    the context of IKATS within Django: services aimed at applications under ikats.processing.
    """

    @staticmethod
    def get_resource_location(view_name, resource_id, http_request=None):
        """
        Retrieves the relative path of resource from the django view name matching the resource with id argument.
        The returned path is completed by the server+port is possible from http_query.
        :param view_name: the django view name of READ service on the resource (defined in urls.py definitions)
        :type view_name: str
        :param resource_id: the identifier of the resource
        :type resource_id: int or str
        :param http_request: optional, default is None: if not None: the request from which the prefix can be deduced.
        :type http_request:
        :return: the URL encoded path: [<prefix>]<relative path>
        :rtype: str
        """

        relative_path = reverse(viewname=view_name, args=[resource_id])
        prefix = ""
        if http_request:
            prefix_full_url = http_request.META.get('HTTP_REFERER', "")
            cut_index = prefix_full_url.find(settings.URL_PATH_IKATS_ALGO)
            if cut_index > -1:
                prefix = prefix_full_url[0:cut_index]
        return prefix + relative_path

    @staticmethod
    def load_json_from_request(http_request):
        """
        Computes the python object loaded from the json in the request body
        :param http_request: the request having a body type application/json_util
        :type http_request: HttpRequest
        :return: the loaded python object
        :rtype: object
        """
        try:
            json_str = (http_request.body.decode('utf-8'))
            my_obj = json.loads(json_str)
        except Exception as cause:
            raise IkatsInputContentError("Failed to read json content in Http request: cause={}".format(cause))
        return my_obj

    @staticmethod
    def load_json_from_response(http_response):
        """
        Computes the python object loaded from the json in the response body
        :param http_response: the request having a body type application/json_util
        :type http_response: HttpResponse
        :return: the loaded python object
        :rtype: object
        """
        try:
            json_str = (http_response.content.decode('utf-8'))
            my_obj = json.loads(json_str)
        except Exception as cause:
            raise IkatsInputContentError("Failed to read json content in Http request: cause={}".format(cause))
        return my_obj

    @staticmethod
    def get_info_level(http_request, query_dict, default=LevelInfo.NORMAL):
        """
        Returns the ikats info_level in specified HttpRequest or in default
        :param http_request: the request
        :type http_request: django.http.HttpRequest
        :param query_dict: the query dict of the request
        :type query_dict: QueryDict
        :param default: specify the default level to apply
        :type default: LevelInfo
        :return: the level
        :rtype: LevelInfo
        """
        if query_dict is None:
            return default

        # Default is typed enum LevelInfo
        # => two steps
        str_info_level = query_dict.get('info_level', default=None)
        if str_info_level is None:
            info_level = default
        else:
            try:
                info_level = LevelInfo.parse(int(str_info_level))
            except Exception:
                msg = "Bad value [{}] of query param named 'info_level' in the context: {}"
                raise IkatsInputError(msg.format(str_info_level, http_request.path))
        return info_level


class HttpResponseFactory(object):
    """
    Superclass HttpResponseFactory defines all reused code/constants: reused by subclasses
    """
    OK_HTTP_STATUS = 200
    CREATED_HTTP_STATUS = 201
    NO_CONTENT_HTTP_STATUS = 204
    BAD_REQUEST_HTTP_STATUS = 400
    NOT_ALLOWED_METHOD_HTTP_STATUS = 405
    NOT_FOUND_HTTP_STATUS = 404
    CONFLICT_HTTP_STATUS = 409
    SERVER_ERROR_HTTP_STATUS = 500

    @classmethod
    def response_empty_ok(cls):
        """
        Returns http response for NO_CONTENT_HTTP_STATUS
        :param cls:
        :type cls:
        :return: the empty response
        :rtype: django.http.HttpResponse
        """
        return HttpResponse(status=cls.NO_CONTENT_HTTP_STATUS)

    @classmethod
    def response_resource_created_ok(cls, view_name, resource_id, http_request=None):
        """
        Returns the specified http response for CREATED_HTTP_STATUS:
        the header Location property is completed.
        :param cls:
        :type cls:
        :param view_name: view name is an alias of the URL django configuration of the
         GET Rest service on the created resource
        :type view_name: str
        :param resource_id: ID of created resource
        :type resource_id: int or str
        :param http_request: handled request
        :type http_request:  django.http.HttpRequest
        :return: the response for CREATED_HTTP_STATUS
        :rtype: django.http.HttpResponse
        """
        return cls.response_resource_written_ok(view_name, resource_id, cls.CREATED_HTTP_STATUS, http_request)

    @classmethod
    def response_resource_updated_ok(cls, view_name, resource_id, http_request=None):
        """
        Returns the specified http response for Rest service updating specified resource:
        the header Location property is completed.
        :param cls:
        :type cls:
        :param view_name: view name is an alias of the URL django configuration of the
         UPDATE Rest service on the updated resource
        :type view_name: str
        :param resource_id: ID of updated resource
        :type resource_id: int or str
        :param http_request: handled request
        :type http_request:  django.http.HttpRequest
        :return: the response of UPDATE service
        :rtype: django.http.HttpResponse
        """
        return cls.response_resource_written_ok(view_name, resource_id, cls.OK_HTTP_STATUS, http_request)

    @classmethod
    def response_resource_written_ok(cls, view_name, resource_id, http_status, http_request=None):
        """
        Internal building of response for Rest services CREATE or UPDATE:
        the header Location property is completed.
        :param cls:
        :type cls:
        :param view_name:view name is an alias of the URL django configuration of the
         Rest service writing the resource
        :type view_name: str
        :param resource_id: ID of written resource
        :type resource_id: int or str
        :param http_status: specified Http code
        :type http_status: int
        :param http_request: the request source of this response, optional default None:
          may be required for the location property prefix in the response
        :type http_request: django.http.HttpRequest
        :return: the response of the writing service
        :rtype: django.http.HttpResponse
        """

        response = HttpResponse()
        response.status_code = http_status
        response['Location'] = HttpCommonsIkats.get_resource_location(view_name, resource_id, http_request)
        return response
