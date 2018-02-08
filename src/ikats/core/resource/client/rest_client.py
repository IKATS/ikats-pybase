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

# Logging
import logging
from enum import Enum

# Documentation about 'requests' module: http://docs.python-requests.org/en/latest/
import requests

from ikats.core.config.ConfigReader import ConfigReader
from ikats.core.resource.client import ServerError
from ikats.core.resource.client import is_url_valid, build_json_files, TEMPLATES, close_files


class RestClientResponse(object):
    """
    New wrapper of the result returned from module requests: it is returned by _send() method

    Available fields:
      - status
      - headers (new)
      - content_type (new)
      - url
      - json
      - text
      - content
      - raw

    You can use get_appropriate_content() in order to have the specified type of content
    """
    DEFAULT_JSON_INIT = "{}"

    def __init__(self, result):

        # The user ought to know which field to use
        #
        # => try to fill all fields (except self.json: lazily computed)
        # Reason: backward-compatibility (even if not optimal for memory)
        #
        # To be improved in next versions:
        # we ought to manage only one attr self.__result and use delegate design-pattern to
        # implement self properties text, raw, content (...) and associated getter functions
        # (see example with self.json)
        self.status = result.status_code
        self.headers = result.headers
        self.content_type = self.headers.get('Content-type', None)
        self.url = result.url
        self.__json = None
        self.text = result.text
        self.raw = result.raw
        self.content = result.content
        self.__result = result

    def get_json(self):
        """
        The json getter: also available from self.json property.

        Note that there is a lazy computing of self.__json value, calling self.__result.json()
        made only once.

        :return: the effective json content deduced from self.__result. In case of error/empty body,
          RestClientResponse.DEFAULT_JSON_INIT is returned.
        """
        if self.__json is None:
            # default value backward-compatible with previous interface
            self.__json = RestClientResponse.DEFAULT_JSON_INIT
            try:
                self.__json = self.__result.json()
            except ValueError:
                # If the content is not json formatted, let the empty json fills the json field
                pass
        return self.__json

    def __str__(self):
        msg = "url={} content_type={} headers={} status_code={}"
        return msg.format(self.url,
                          self.content_type,
                          self.headers,
                          self.status)

    def get_appropriate_content(self, default_content=None):
        """
        Return the appropriate content according to the parsed content-type

        :param default_content: optional default None: if not None,
          this object is returned instead of throwing UnresolvedContentType
        :type default_content: object

        :return: appropriate content according to the self.content_type
        :rtype: object, str, or bytes

        :raises UnresolvedContentType: error when there is no content specifically determined by content_type.
               You can in that case inspect RestClientResponse fields: json, text, content, raw
        """
        if self.content_type == 'application/octet-stream':
            return self.content
        elif self.content_type == 'application/json':
            return self.json
        elif self.content_type == 'text/plain':
            return self.text
        else:
            if default_content is not None:
                return default_content
            else:
                raise TypeError("Failed to find appropriate content for content-type=%s", self.content_type)

    json = property(get_json, None, None, "")


class RestClient(object):
    """
    Generic class to communicate using REST API
    """

    class VERB(Enum):
        """
        Definition of possibilities for HTTP verb
        Only the following 4 are managed because they are the only allowed verbs for CRUD interface
        * CREATE -> POST
        * READ -> GET
        * UPDATE -> PUT
        * DELETE -> DELETE
        """
        POST = 0
        GET = 1
        PUT = 2
        DELETE = 3

    def __init__(self, host=None, port=None):
        """
        Initializer

        :param host: host to connect to
        :param port: port to use for connection
        """

        # Create the logger object
        self.logger = logging.getLogger(__name__)

        # Configuration file
        self.config_reader = ConfigReader()

        # Host to connect to (IP address or known host name)
        self._host = None
        if host is not None:
            self.host = host
        else:
            self.host = self.config_reader.get('cluster', 'tdm.ip')

        # Port Number to connect to
        self._port = None
        if port is not None:
            self.port = port
        else:
            self.port = int(self.config_reader.get('cluster', 'tdm.port'))

    @property
    def host(self):
        """
        Host address
        :getter: provide the stored host address
        :setter: check host validity

        :raises TypeError: if host has a wrong type (in setter)
        :raises ValueError: if host is not an understandable URL (in setter)
        """
        return self._host

    @host.setter
    def host(self, value):
        """
        See getter
        """
        if type(value) is not None:
            if type(value) is not str:
                raise TypeError("Host must be a string (got %s)" % type(value))
            if value == "":
                raise ValueError("Host must be filled")
            if not is_url_valid(value):
                raise ValueError("Host not a valid URL : %s" % value)
        self._host = value

    @property
    def port(self):
        """
        port number
        :getter: provide the stored port address
        :setter: check port validity

        :raises TypeError: if port is not a number
        :raises ValueError: if port is not a correct port number
        """
        return self._port

    @port.setter
    def port(self, value):
        """
        See getter
        """
        if type(value) is not int:
            raise TypeError("Port must be a number (got %s)" % type(value))
        if value <= 0 or value >= 65535:
            raise ValueError("Port must be within ]0:65535] (got %s)" % value)
        self._port = value

    def _send(self,
              verb=None,
              template="",
              uri_params=None,
              q_params=None,
              files=None,
              data=None,
              json_data=None,
              headers=None):
        """
        Generic call command that should not be called directly

        It performs the following actions:
        * checks the input type validity
        * calls the correct verb method from the library (get, post, put, delete)
        * formats the output (utf-8)
        * Handles the status from the server
        * decode the output
        * return the data

        :param template: optional, default "": key matching the template to use for url building:
          see dict ikats.core.resource.client.utils.TEMPLATES
        :param uri_params:  optional, default None: parameters applied to the template
        :param verb:  optional, default None: HTTP method to call
        :type verb: IkatsRest.VERB
        :param q_params: optional, default None: list of query parameters
        :type q_params: dict or None
        :param files: optional, default None: files full path to attach to request
        :type files: str or list or None
        :param data: optional, default None: data input consumed by request
            -note: when data is not None, json must be None
        :type data: object
        :param json_data: optional, default None: json input consumed by request
            -note: when json is not None, data must be None
        :type json_data: object
        :return: the response as a anonymous class containing the following attributes:
            class Result:
                url = *url of the request performed*
                json = *body content parsed from json*
                text = *body content parsed as text*
                raw = *raw response content*
                status = *HTTP status code*
                reason = *reason (useful in case of HTTP status code 4xx or 5xx)
            This way to return results improve readability of the code.
            Example:
                r = self.send(...)
                if r.status == 200:
                    print(r.text)
        :rtype: anonymous class

        .. note:
           Timeout set to following values:
              - 120 seconds for GET and POST
              - 120 seconds for PUT and DELETE

        :raises TypeError: if VERB is incorrect
        :raises TypeError: if FORMAT is incorrect
        :raises ValueError: if a parameter of uri_param contains spaces
                            if there are unexpected argument values
        :raises ServerError: if receiving HTTP error code 5xx
        """

        # Check the validity of inputs
        assert (template in TEMPLATES), "Template is not defined: %s" % template

        if not isinstance(verb, RestClient.VERB):
            self.logger.error('Verb type is %s whereas IkatsRest.VERB is expected', type(verb))
            raise TypeError("Verb type is %s whereas IkatsRest.VERB is expected", type(verb))

        if (data is not None) and (json_data is not None):
            raise ValueError("Integrity error: arguments data and json_data are mutually exclusive.")

        # Build the URL
        if uri_params is None:
            uri_params = {}
        if 'host' not in uri_params:
            uri_params['host'] = self.host
        if 'port' not in uri_params:
            uri_params['port'] = self.port
        url = TEMPLATES[template]['pattern'] % uri_params

        # Converts file to 'requests' module format
        json_file = build_json_files(files)

        # Dispatch method
        try:
            if verb == RestClient.VERB.POST:
                result = requests.post(url,
                                       data=data,
                                       json=json_data,
                                       files=json_file,
                                       params=q_params,
                                       timeout=600,
                                       headers=headers)
            elif verb == RestClient.VERB.GET:
                result = requests.get(url,
                                      params=q_params,
                                      timeout=600,
                                      headers=headers)
            elif verb == RestClient.VERB.PUT:
                result = requests.put(url,
                                      params=q_params,
                                      timeout=600,
                                      headers=headers)
            elif verb == RestClient.VERB.DELETE:
                result = requests.delete(url,
                                         params=q_params,
                                         timeout=600,
                                         headers=headers)
            else:
                self.logger.error("Verb [%s] is unknown, shall be one defined by VERB Enumerate", verb)
                raise RuntimeError("Verb [%s] is unknown, shall be one defined by VERB Enumerate" % verb)

            # Format output encoding
            result.encoding = 'utf-8'

            # Debug information
            if result.status_code == 400 or result.status_code >= 500:
                self.logger.debug("Sending request:")
                self.logger.debug("  %-6s: %s", str(verb)[5:], result.url)
                self.logger.debug("  Status: %s", result.status_code)
                self.logger.debug("  Data: %s", data)
        except Exception as exception:
            self.logger.error("ERROR OCCURRED DURING THE HTTP SEND ACTION (details below)")
            self.logger.error(exception)
            raise
        finally:
            # Close potential opened files
            close_files(json_file)

        # Error handling
        if 500 <= result.status_code < 600:
            self.logger.error('%s Server Error: %s', result.status_code, result.reason)
            raise ServerError('%s Server Error: %s %s %s' % (result.status_code, verb, url, result.text))

        return RestClientResponse(result)
