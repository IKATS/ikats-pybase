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

import ikats_processing.core.json.decode as json_utils
from apps.algo.custom.models.business.check_engine import CheckError
from apps.algo.execute.models.business.scripts import execalgo
from apps.algo.execute.models.orm.algo import ExecutableAlgoDao
from apps.algo.execute.models.ws.algo import ExecutableAlgoWs
from apps.algo.execute.models.ws.exec_status import ExecutionStatusWs
from ikats.core.library.exception import IkatsInputError, IkatsNotFoundError, IkatsException
from ikats.core.resource.client.exceptions import ServerError
from ikats_processing.core.json.http_response import DjangoHttpResponseFactory

LOGGER = logging.getLogger(__name__)


def get_json_error_data(code, exception):
    """
    Prepare json data for http response in error case
    :param code: http status
    :type code: int
    :param exception: the error
    :type exception:
    """

    msg = "{0}".format(exception)

    return {'http_code': code, 'http_msg': msg}


def run(http_request, algo_name):
    """
    =======
    Summary
    =======
    Web service implementation of 'ikats/algo/execute/runalgo'
    This service wraps the execution of any algorithm

    ===================
    Technical interface
    ===================

    ------------
    Http Request:
    ------------
    * service method is POST
    * url: <url base>/<id>
     * where <url base> is the url defined by django configuration (see files urls.py)
     * where <id> is a path parameter:
      * either the id of the Implementation, when json option 'custo_algo' is set to False
      * or the id of the CustomizedAlgo, when json option 'custo_algo' is set to True
    * request content type is 'application/json_util'
    * request json content:
          { 'opts': { 'async': ..., 'custo_algo': ..., 'debug': ... },
            'args': { <name1>: <value1>, ... <nameN>: <valueN> }
          }
    -------------
    Http Response
    -------------
     * Http response status:
     * 200: OK: see Nominal Response below
     * 400: bad request from client: not processed: see Error response below
     * 500: error occurred computing statistics: see Error response below
    ^^^^^^^^^^^^^^^^
    Nominal Response
    ^^^^^^^^^^^^^^^^
     * service produces the following json structure:
            | { 'http_code' : <http code>
            |   'http_msg' : <http message>
            |   'exec_algo' : <execution_algo>
            |   'exec_status' : <execution_status> }
     * where <http code> is a integer: the http service status
       (see https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html)
     * where <http message> is a string: the high level message associated to <http code>
     * where  <execution_algo> is optional: matching the executed resource ExecutionAlgo with the json content:
            |   { "process_id": <process id>,
            |      "exec_state": <execution_algo_state>,
            |      "start_date": start date of execution,
            |      "end_date": end date of execution,
            |      "duration": execution duration
            |    }

      * where <process id> is the reference of <execution_algo>

      * where <execution_algo_state> is internal status INIT|RUN|OK|ALGO_KO|ENGINE_KO

      * where dates may be optional: undefined in asynchronous mode

      * where  <execution_status> is optional: matching the executed resource ExecutionStatus with json content:
            |   { "msg": [ "msg1", ... "msgN" ]
            |      "error": <error>
            |    }

        * where "error" is optional: caught error,

        * where "msg" is a list of internal messages: info, warnings, or trace backs if available

    ^^^^^^^^^^^^^^^^
    Error Response
    ^^^^^^^^^^^^^^^^
            | { 'http_code' : <http code>
            |   'http_msg' : <http message>
            |   'internal_error' : ...
            |   'exec_algo' : <execution_algo>
            |   'exec_status' : <execution_status> }
     * at least: http_code and http_msg properties are filled
     * at most:
            | internal_error: optional information about the internal error:
            | useful when exec_status is below undefined
            | exec_algo exec_status should be filled when resources have been
            | defined before failure

    :param http_request: http request
    :type http_request:
    :param algo_name: algorithm identifier
    :type algo_name: str
    """
    factory_response = DjangoHttpResponseFactory()
    try:
        if http_request.method != 'POST':
            return factory_response.get_json_response_bad_request(ikats_error="Expecting POST http method")

        input_json = json_utils.decode_json_from_http_request(http_request)

        input_args_list = []
        input_args_values_list = []

        in_options = {'async': False, 'custo_algo': False, 'debug': False}

        for param in input_json:
            # if input options exist
            if param == 'opts':
                options = input_json['opts']

                for opt in options:
                    if opt not in in_options:
                        raise IkatsInputError("option %s not expected" % opt)
                    else:
                        in_options[opt] = options[opt]

            # if input arguments exist
            elif param == 'args':
                arguments = input_json['args']
                # checks made later ...
                for param in arguments:
                    input_args_list.append(param)
                    input_args_values_list.append(arguments[param])

            # undefined parameter in input_json
            else:
                raise IkatsInputError("parameter %s not expected" % param)

        # call to script algo execution
        my_exec_status = execalgo.run(algo_name=algo_name,
                                      arg_names=input_args_list,
                                      arg_values=input_args_values_list,
                                      asynchro=in_options['async'],
                                      is_customized_algo=in_options['custo_algo'],
                                      run_debug=in_options['debug'])

        LOGGER.info(my_exec_status.__str__())

        if my_exec_status.has_error():
            LOGGER.info("ExecutionStatus successfully built with error => interpreted as server error")
            my_ws__exec_status = ExecutionStatusWs(my_exec_status)
            return my_ws__exec_status.to_json_response(http_code=500, http_msg="Server Error")
        else:
            my_ws__exec_status = ExecutionStatusWs(my_exec_status)
            return my_ws__exec_status.to_json_response()

    except CheckError as check_error:
        check_status = check_error.status
        context = "Cancelled request in views.algo.run: incorrect input values detected by the checker CheckEngine"
        LOGGER.error(context)
        LOGGER.error(check_error.msg)
        LOGGER.error(json.dumps(obj=check_status.to_dict(), indent=2))
        my_code = factory_response.BAD_REQUEST_HTTP_STATUS
        return factory_response.get_json_response_error_with_data(http_status_code=my_code,
                                                                  http_msg=context,
                                                                  data_name="check_error",
                                                                  data=check_status.to_dict())
    except (IkatsInputError, TypeError) as exception:
        LOGGER.exception(exception)

        context = "Bad Request in views.algo.run"
        return factory_response.get_json_response_bad_request(ikats_error=context, exception=exception)

    except IkatsNotFoundError as exception:
        LOGGER.exception(exception)
        factory_response = DjangoHttpResponseFactory()
        context = "Resource not found in views.algo.run"
        return factory_response.get_json_response_not_found(ikats_error=context, exception=exception)

    except (IkatsException, ServerError, BaseException) as exception:
        LOGGER.exception(exception)
        factory_response = DjangoHttpResponseFactory()
        context = "Server error in views.algo.run"
        return factory_response.get_json_response_internal_server_error(ikats_error=context, exception=exception)


def getstatus(http_request, process_id):
    """
    =======
    Summary
    =======
    Web service implementation of 'ikats/algo/execute/getstatus'
    This service returns :
        -execution state
        -start date of execution (float EPOCH time in second)
        -end date of execution (float EPOCH time in second)
        -execution duration (time in second)
    of any previously launched algorithm
    ===================
    Technical interface
    ===================
    ------------
    Http Request
    ------------
      * service method is POST
      * service input is a json structure
    -------------
    Http Response
    -------------
      * Http response status:
        * 200: OK: see Nominal Response below
        * 404: wrong input content from client: see Error response below
    ^^^^^^^^^^^^^^^^
    Nominal Response
    ^^^^^^^^^^^^^^^^
      * service produces the following json structure:
        | { 'http_code' : <http code>,
        |   'http_msg' : <http message>,
        |
        |   'process_id': <process id>,
        |   'exec_state': <execution_algo_state>,
        |   'start_date': start date of execution,
        |   'end_date': end date of execution,
        |   'duration': execution duration
        | }
        where <http code> is a integer: the http service status
        (see https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html)

        where <http message> is a string: the high level message associated to <http code>

        where <process id> is the reference of <execution_algo>
        where 'exec_state' defines internal status INIT|RUN|OK|ALGO_KO|ENGINE_KO

        where 'start_date', 'end_date', 'duration' defines the running period

    ^^^^^^^^^^^^^^^^
    Error Response
    ^^^^^^^^^^^^^^^^
      * service produces the following json structure:
        | { 'http_code' : <http code>,
        |   'http_msg' : <http message>,
        |
        |   'internal_error': ...
        | }
        where 'internal_error' is optional, defined in error cases

    :param http_request:
    :param process_id: process identifier
    :type process_id : int
    """
    response_factory = DjangoHttpResponseFactory()
    try:
        exec_algo = ExecutableAlgoDao.find_from_key(process_id)

        if exec_algo is None:
            my_context = "Resource not found in views.algo.getStatus"
            my_error = IkatsNotFoundError("ExecutableAlgorithm with process id %s not found." % process_id)
            LOGGER.error(my_context)
            LOGGER.exception(my_error)
            return response_factory.get_json_response_not_found(ikats_error=my_context, exception=my_error)

        else:
            ws_exec_algo = ExecutableAlgoWs(exec_algo)

            return ws_exec_algo.to_json_response()

    except Exception as err:
        msg = "Unexpected error searching ExecutableAlgorithm with process id %s" % process_id
        LOGGER.error(msg)
        LOGGER.exception(err)
        return response_factory.get_json_response_internal_server_error(msg, err)
