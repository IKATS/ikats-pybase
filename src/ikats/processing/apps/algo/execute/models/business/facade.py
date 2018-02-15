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
"""
import importlib

from apps.algo.catalogue.models.orm.implem import ImplementationDao
from apps.algo.execute.models.business.factory import FactoryExecAlgo


class FacadeExecution(object):
    """
    Provides services for the execution of algorithms.
    FacadeExecution.factory is an instance of FactoryExecAlgo, which must be used to
    instantiate separately executable algorithms

    Typical use of this facade:

        1) Simplest use:

            my_exec_algo, exec_status = FacadeExecution.execute( ... )


        2) Separating steps : initializing algo, connecting data sources and executing algo
            # It is useful to have a separate step connecting data sources, and receivers

            # create disconnected algo
            my_algo = FacadeExecution.factory.get_algo(...)

            # connect missing data sources and receivers
            my_algo.set_data_source( ...)
            ...
            my_algo.set_data_receiver( ...)
            ...

            # execute
            exec_status = FacadeExecution.execute_algo( my_algo )
    """

    @classmethod
    def __eval_exec_engine_class(cls, str_plugin_path, str_plugin):
        """
        private class method
        evaluate the configured engine from module+plugin
        :param cls:
        :type cls:
        :param str_plugin_path:
        :type str_plugin_path:
        :param str_plugin:
        :type str_plugin:
        :return: subclass of ExecEngine (!!! not an instance !!!)
        """
        my_module_path = str_plugin_path
        my_plugin = str_plugin

        try:

            my_module = importlib.import_module(my_module_path)

            evaluated_plugin_str = "my_module.%s" % my_plugin

            my_class = eval(evaluated_plugin_str)
        except Exception:
            raise Exception(
                "Failed to evaluate ExecEngine plugin %s.%s" % (str_plugin_path, str_plugin))
        return my_class

    factory = FactoryExecAlgo()

    @staticmethod
    def execute_algo_without_custom(implem, input_arg_names, input_data_sources, output_arg_names,
                                    output_data_receivers,
                                    exec_algo_db_id=None, run_debug=False, dao_managed=True):
        """
        Firstly build the ExecutableAlgo: initialized without customized parameters in database (Custom DB is ignored)

        Secondly run the service FacadeExecution.execute_algo on created algo.

        :param implem: executed implementation
        :type implem: Implementation
        :param input_arg_names: complete list of input names
        :type input_arg_names: list
        :param input_data_sources: complete list of input values (either explicit values or DataSource subclasses)
        :type input_data_sources: list
        :param output_arg_names: complete list of output names
        :type output_arg_names: list
        :param output_data_receivers: complete list of output receivers:
            same length than output_arg_names: each element is either None or instance of DataReceiver subclass)
        :type output_data_receivers: list
        :param exec_algo_db_id: optional value of primary key of executable algorithm when it is already created,
            default is None.
        :type exec_algo_db_id: int
        :param run_debug: optional flag: True when debug is activated. Default is False
        :type run_debug: bool
        :param dao_managed: optional flag: True when executable algorithm is managed in DB. Default is True
        :type dao_managed: bool
        :return: exec_algo, exec_status tuple: exec_algo is the initialized algorithm; exec_status is
                the execution status
        :rtype:  exec_algo is apps.algo.execute.models.business.algo.ExecutableAlgo
                 and exec_status is apps.algo.execute.models.business.exec_engine.ExecStatus
        """
        # executable algo building
        if isinstance(implem, str):
            my_implementation = ImplementationDao.find_business_elem_with_key(implem)
        else:
            my_implementation = implem
        my_exec_algo = FacadeExecution.factory.build_exec_algo_without_custom(
            implementation=my_implementation,
            input_names=input_arg_names,
            input_values_or_sources=input_data_sources,
            output_names=output_arg_names,
            output_receivers=output_data_receivers)

        # in case exec algo already defined in DB (asynchronous execution)
        if exec_algo_db_id is not None:
            # set algorithm db id
            my_exec_algo.set_process_id(exec_algo_db_id)

        return FacadeExecution.execute_algo(executable_algo=my_exec_algo,
                                            debug=run_debug,
                                            dao_managed=dao_managed)

    @staticmethod
    def execute_algo(executable_algo, debug=False, dao_managed=False):
        """
        Execute the algorithm according to configured plugin
          - Retrieves the ExecEngine subclass,
          - Intanciates the engine for the executable_algo
          - Execute the engine
        :param executable_algo: executable algorithm
        :type executable_algo: apps.algo.execute.models.business.algo.ExecutableAlgo
        :param debug: optional (default False): flag activating debug traces
        :type debug: boolean
        :param dao_managed: optional(default False): flag: when True: activates the persistence of ExecutableAlgo
                 + setting of process_id
        :type dao_managed:  boolean
        """
        parsed_plugin = executable_algo.get_execution_plugin().split("::")
        module_path = parsed_plugin[0]
        plugin_class_name = parsed_plugin[1]

        my_plugin_class = FacadeExecution.__eval_exec_engine_class(
            module_path, plugin_class_name)

        my_engine = my_plugin_class(executable_algo, debug, dao_managed)
        my_status = my_engine.execute()

        return my_engine.get_executable_algo(), my_status
