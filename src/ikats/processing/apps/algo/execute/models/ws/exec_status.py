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

import logging

from apps.algo.execute.models.business.exec_status import ExecutionStatus
from apps.algo.execute.models.ws.algo import ExecutableAlgoWs
from ikats_processing.core.json.http_response import DjangoHttpResponseFactory

LOGGER = logging.getLogger(__name__)


class ExecutionStatusWs(object):
    """
    The Execution status in the Web service model: business ExecutionStatus + http code
    """

    def __init__(self, business_execution_status):
        """
        Constructor
        :param business_execution_status: business status
        :type business_execution_status:  apps.algo.execute.models.business.exec_status.ExecutionStatus
        :param http_code: the http code
        :type http_code: int as defined in constants of ikats_processing.core.http
        """
        assert (isinstance(business_execution_status, ExecutionStatus)), \
            "Expects ExecutionStatus type for argument business_execution_status in ExecutionStatusWs constructor"

        self.__mdl = business_execution_status

    def to_dict(self):
        """
        returns a dictionary Json-serializable resource ExecutionStatusWs

        {
            "exec_algo": { "process_id": ...,
                           "start_date": ...
                           "duration": ...
                           "end_date": ...
                           "status": ...
                         }
            "exec_status": { "messages": [ "...", ... , "..." ]
                             "error": "..."
            "check_status": <diagnostic>
        }

        where <diagnostic> is the content of self.__check_engine_status or null when undefined
        """

        data = {}

        if self.__mdl.get_algo() is not None:
            algo_ws = ExecutableAlgoWs(self.__mdl.get_algo())
            exec_algo = algo_ws.to_dict()
            data['exec_algo'] = exec_algo

        exec_status = {}
        my_msg = self.__mdl.get_msg_list()
        if my_msg is not None:
            if isinstance(my_msg, list):
                exec_status['messages'] = [ascii(x) for x in my_msg]
            else:
                exec_status['messages'] = ascii(my_msg)
        else:
            exec_status['messages'] = []

        my_error = self.__mdl.get_error()
        if my_error is not None:
            exec_status["error"] = ascii(str(my_error))

        data['exec_status'] = exec_status

        return data

    def to_json_response(self, http_code=200, http_msg="ok", error=None):
        """
        Encode the json response for the resource wrapper ExecutableAlgoWs

        TODO: move that code up to a superclass ? same code than ExecutionalgoWs::to_json_response

        :param http_code: http code, optional: default 200
        :type http_code: int
        :param http_msg: http message, optional: default "ok"
        :type http_msg: str
        :param error: optional error: if None: the error will be evaluated from wrapped ExecutionStatus
        :type error: BaseException subclass
        """
        as_dict = self.to_dict()
        as_dict['http_code'] = http_code
        as_dict['http_msg'] = http_msg
        if error is not None:
            as_dict['error'] = ascii(str(error))

        factory = DjangoHttpResponseFactory()

        if http_code == 200:
            response = factory.get_json_response_nominal(as_dict)
        else:
            response = factory.get_json_response_error(http_status_code=http_code, ikats_error=None,
                                                       exception=None, data=as_dict)
        return response
