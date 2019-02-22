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
import logging

from apps.algo.execute.models.business.algo import ExecutableAlgo
from ikats_processing.core.json.http_response import DjangoHttpResponseFactory

LOGGER = logging.getLogger(__name__)


class ExecutableAlgoWs(object):
    """
    The ExecutableAlgoWs is a wrapper of resource ExecutableAlgo: brings services
    for the web services concerned with ExecutableAlgo
    """

    def __init__(self, business_exec_algo):
        """
        Constructor
        """
        if business_exec_algo is not None:
            assert (isinstance(business_exec_algo, ExecutableAlgo)), \
                "Expects Implementation type for argument business_obj in ImplementationWs constructor"

        self.__mdl = business_exec_algo

    def to_dict(self):
        """
        returns a dictionary Json-serializable for the ExecutableAlgoWs wrapping the ExecutableAlgo
        """
        status = dict()
        if self.__mdl is not None:
            start_execution_date = self.__mdl.get_start_execution_date()

            # retrieve end date of execution
            end_execution_date = self.__mdl.get_end_execution_date()

            # calculate execution duration if execution is over
            if start_execution_date and end_execution_date:
                duration = end_execution_date - start_execution_date
                duration = float(duration)
            else:
                duration = None

            if start_execution_date:
                start_execution_date = float(start_execution_date)

            if end_execution_date:
                end_execution_date = float(end_execution_date)

            # encode dates result as json

            status['process_id'] = self.__mdl.process_id
            status['exec_state'] = self.__mdl.get_state().name
            status['start_date'] = start_execution_date
            status['end_date'] = end_execution_date
            status['duration'] = duration

        return status

    def to_json_response(self, http_code=200, http_msg="ok", error=None):
        """
        Encode the json response for the resource wrapper ExecutableAlgoWs
        :param http_code: http code, optional: default 200
        :type http_code: int
        :param http_msg: http message, optional: default "ok"
        :type http_msg: str
        :param error: optional error
        :type error: BaseException subclass
        """
        as_dict = self.to_dict()
        as_dict['http_code'] = http_code
        as_dict['http_msg'] = http_msg
        if error is not None:
            as_dict['error'] = ascii(error)

        factory = DjangoHttpResponseFactory()

        if http_code == 200:
            response = factory.get_json_response_nominal(as_dict)
        else:

            response = factory.get_json_response_error(http_status_code=http_code, ikats_error=None,
                                                       exception=None, data=as_dict)
        return response
