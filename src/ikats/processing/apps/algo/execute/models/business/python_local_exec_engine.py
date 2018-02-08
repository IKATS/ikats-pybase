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

import importlib
import json
import logging
import sys

from apps.algo.custom.models.business.check_engine import CheckEngine, CheckError
from apps.algo.execute.models.business.exec_engine import ExecEngine, EngineException, AlgoException

LOGGER = logging.getLogger(__name__)


class PythonLocalExecEngine(ExecEngine):
    """
    This Engine allows the execution of python function as defined by self.executable_algo:
    see run_command() documentation.
    Required on executable_algo.custom_algo.implementation (typed Implementation):
      - implementation._execution_plugin is "apps.algo.execute.models.business.exec_engine.PythonLocalExecEngine"
         (this is required by FacadeExecution)
      - implementation.lib_path must respect syntax: <function module>::<function name>

    Usage:

        ea = FacadeExecution.factory.build...Algo(...)
        ea.set_data_source(name, source)
        ...
        ea.set_data_receiver( "result", source )
        ...
        engine = PythonLocalExecEngine( ea )

        # ExecStatus instance is gathering global information about execution
        exec_status = engine.execute()
        print( exec_status )

        # Results: available on data receivers defined on ExecutableAlgorithm ea:
                   they are not stocked by the engine
        result = ea.get_data_receiver("result").get_value()

    See also:

        FacadeExecution which provides easy ways to launch algo executions
    """

    def __init__(self, executable_algo, debug=False, dao_managed=False):
        super(PythonLocalExecEngine, self).__init__(executable_algo, debug, dao_managed)

        # internal use: string configuring the python function
        self.__lib_path = None

        # internal use: evaluated python function definition
        self.__evaluated_python_function = None

        self.__checker = CheckEngine(checked_resource=self.executable_algo.custom_algo,
                                     checked_value_context="Running custom algo from " + self.__class__.__name__)

    def __evaluate_python_function(self):
        """
        Private method called once on the engine instance: evaluate the python function
        and assign it to the self.__evaluated_python_function
        """
        try:
            my_custo_algo = self.executable_algo.custom_algo
            my_implem = my_custo_algo.implementation

            self.__lib_path = my_implem.library_address

            self.add_msg("lib_path=%s" % self.__lib_path)

            my_parsed_lib_path = self.__parse_lib_path(self.__lib_path)

            # already checked: parsed parts
            my_module_path = my_parsed_lib_path[0]
            self.add_msg("module path=%s" % my_module_path)
            my_function = my_parsed_lib_path[1]
            self.add_msg("function name=%s" % my_function)

            # !!! keep this variable my_module declared !!!
            my_module = importlib.import_module(my_module_path)

            evaluated_function_str = "my_module.%s" % my_function
            self.add_msg('evaluating "%s"' % evaluated_function_str)

            self.__evaluated_python_function = eval(evaluated_function_str)

        except Exception as err:
            trace_back = sys.exc_info()[2]
            LOGGER.exception(err)
            raise EngineException(
                "PythonLocalExecEngine failed to evaluate configured python function [%s] from executable algo [%s]" %
                (self.__lib_path, self.executable_algo)).with_traceback(trace_back)

    @staticmethod
    def __parse_lib_path(lib_path):
        split_after_module = lib_path.split("::")
        return split_after_module

    def run_command(self):
        """
         Implements the calling of python function defined by self.executable_algo:
           - python function is evaluated once: it is fully defined by executable_algo.custom_algo.implementation:
             - implementation.lib_path must respect syntax: <function module>::<function name>
           - then evaluated function is called according to input and output profiles configured in
             executable_algo.custom_algo.implementation:
                - input arguments are consumed on self.executable_algo: using ExecutableAlgo::consume(...)
                  and  ExecutableAlgo::get_ordered_input_names(...)
                - output result(s) are produced on self.executable_algo: using ExecutableAlgo::produce(...)
                and  ExecutableAlgo::get_ordered_output_names(...)
        """
        if self.__evaluated_python_function is None:
            self.__evaluate_python_function()

        args = []
        try:
            LOGGER.debug("self.executable_algo.get_ordered_input_names() : %s",
                         str(self.executable_algo.get_ordered_input_names()))
            implem = self.executable_algo.custom_algo.implementation
            for input_name in self.executable_algo.get_ordered_input_names():

                profile_item = implem.find_by_name_input_item(input_name)

                value_consumed = self.executable_algo.consume_value(input_name)

                self.__checker.check_type(profile_item, value_consumed)
                status = self.__checker.check_domain(profile_item, value_consumed)

                if status.has_errors():
                    raise CheckError("CheckEngine has detected errors.", status)

                args.append(value_consumed)

        except CheckError as error:
            trace_back = sys.exc_info()[2]
            msg = "PythonLocalExecEngine aborted run: incorrect inputs " + \
                  "from executed python function {} for algo {}: see detailed status={}"

            readable_status = json.dumps(obj=error.status().to_dict(), indent=2)

            # We consider that the bad input error is almost like AlgoException:
            # because the EngineException errors are reserved to technical errors on the server
            #
            raise AlgoException(msg.format(self.__lib_path,
                                           self.executable_algo,
                                           readable_status),
                                error).with_traceback(trace_back)

        except Exception as err_pre:
            trace_back = sys.exc_info()[2]
            raise EngineException(
                "PythonLocalExecEngine failed to consume inputs from executable algo [%s]" %
                self.executable_algo, err_pre).with_traceback(trace_back)

        result = tuple()

        try:
            result = self.__evaluated_python_function(*args)

        except Exception as err:
            trace_back = sys.exc_info()[2]
            raise AlgoException(
                "PythonLocalExecEngine received error from executed python function [%s] for algo [%s]" %
                (self.__lib_path, self.executable_algo), err).with_traceback(trace_back)

        try:

            res_names = self.executable_algo.get_ordered_output_names()

            if type(result) is tuple:

                assert (len(result) == len(res_names))

                for output_name, output_value in zip(res_names, result):
                    self.executable_algo.produce_value(
                        output_name, output_value)

            elif len(res_names) == 1:
                LOGGER.info("Expected unique result, with name=" + res_names[0])
                if result is None:
                    LOGGER.warning(
                        "No result => skipped step: executable_algo.produce_values : there is no output defined "
                        "for implementation")
                    LOGGER.warning(str(self.executable_algo.get_custom_algo().get_implementation()))
                else:
                    self.executable_algo.produce_value(res_names[0], result)
            else:
                # void functions : like statistics builders ...
                LOGGER.info(
                    "No result => skipped step: executable_algo.produce_values : there is no output defined for "
                    "implementation")

        except Exception as err_post:
            trace_back = sys.exc_info()[2]
            raise EngineException(
                "PythonLocalExecEngine failed to produce outputs into executable algo [%s]" %
                self.executable_algo, err_post).with_traceback(trace_back)
