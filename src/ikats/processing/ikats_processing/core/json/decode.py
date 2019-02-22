"""
Copyright 2018-2019 CS Systèmes d'Information

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
from io import BytesIO, StringIO

LOGGER = logging.getLogger(__name__)


def decode_json_from_http_request(request):
    """
    Decode the json request content (assuming: content-type is "application/json")
    :param request: http request holding json encoded data
    :type request: django.http.HttpRequest
    :return: decoded python object, mapping the json content of the request, using package json
    :rtype: dict
    """
    input_io = BytesIO(request.body)
    json_string_io = StringIO(input_io.read().decode('utf-8'))
    json_string = json_string_io.read()
    input_json = json.loads(json_string)
    return input_json


def decode_json_from_http_response(http_response):
    """
    Decode the json response content (assuming: content-type is "application/json")
    :param http_response: the response
    :type http_response: HttpResponse or JsonResponse
    :return: python object equivalent to json content
    :rtype: dict
    """
    if (http_response.content is None) or (len(http_response.content) == 0):
        return None
    body_io = BytesIO(http_response.content)
    json_string_io = StringIO(body_io.read().decode('utf-8'))
    json_string = json_string_io.read()
    output_json = json.loads(json_string)

    return output_json
