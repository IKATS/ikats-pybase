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
import threading
import time

from apps.algo.catalogue.models.business.factory import FactoryCatalogue
from apps.algo.catalogue.models.business.profile import Parameter
from apps.algo.catalogue.models.orm.implem import ImplementationDao
from apps.algo.custom.models.business.check_engine import CheckEngine
from apps.algo.custom.models.business.check_engine import CheckError
from apps.algo.custom.models.orm.algo import CustomizedAlgoDao
from apps.algo.execute.models.business.exec_engine import ExecStatus
from apps.algo.execute.models.business.exec_status import ExecutionStatus
from apps.algo.execute.models.business.facade import FacadeExecution
from apps.algo.execute.models.business.factory import FactoryExecAlgo
from apps.algo.execute.models.orm.algo import ExecutableAlgoDao
from ikats.core.library.exception import IkatsInputError, IkatsNotFoundError, IkatsException

"""
Module grouping scripts which are only producing results into
Temporal Metadata.
Note: no result is produced in process data of Non Temporal Database.
"""

LOGGER = logging.getLogger(__name__)


def run(algo_name, arg_names, arg_values, asynchro=False, is_customized_algo=False, run_debug=True):
    """
    Launch the algorithm for the specified Implementation/CustomizedAlgo

    :param algo_name: the ID is matching an Implementation or a CustomizedAlgo according to the flag is_customized_algo
    :type algo_name: str
    :param arg_names: list of input names
    :type arg_names: list of string
    :param arg_values: list of input arguments values matching arg_names
    :type arg_values: list
    :param is_customized_algo: True if algo_name identifies CustomizedAlgo,
        otherwise False if algo_name identifies an Implementation
    :type is_customized_algo: boolean
    :param run_debug: TODO
    :type run_debug: boolean
    :return: <status> sums up the execution status:
        | You can get from status the process ID, the (error) message etc. : see ExecutionStatus documentation.
    :rtype: apps.algo.execute.models.business.exec_status.ExecutionStatus
    """

    engine_status = ExecStatus(debug=run_debug, msg="Initial status before starting the execution engine")
    execution_status = ExecutionStatus(algo=None, internal_status=engine_status)

    my_script_name = "RunAlgo"
    msg = "Execute: %s , arg_names=%s" % (my_script_name, str(arg_names))

    # status is set to default value
    #     in case of unexpected error in FacadeExecution.execute below
    execution_status.add_msg(msg)

    if len(arg_names) != len(arg_values):
        msg = 'Argument error in execalgo.run: incorrect arguments number)'
        execution_status.set_error_with_msg(IkatsInputError(msg), "RunAlgo: initial check failed")

    # CheckEngine status generated when check have been applied
    status = None
    try:
        if is_customized_algo:
            my_custom = CustomizedAlgoDao.find_business_elem_with_name(algo_name)[0]
            # ... may raise CustomizedAlgoDao.DoesNotExist
            my_implementation = my_custom.implementation

        else:
            my_custom = None
            my_implementation = ImplementationDao.find_business_elem_with_name(algo_name)[0]
            # ... may raise ImplementationDao.DoesNotExist

        my_script_name = my_script_name + " on " + my_implementation.name

        def_resource = __get_run_definition(implementation=my_implementation, customized_algo=my_custom)
        context = "Run algo with args {} on {}".format(json.dumps(__get_run_args(arg_names, arg_values)),
                                                       def_resource)
        checker = CheckEngine(checked_resource=def_resource, checked_value_context=context, check_status=None)

        completed_arg_names, completed_data_sources, output_names, receivers = __prepare_execution(
            algo_name,
            arg_names,
            arg_values,
            execution_status,
            my_implementation,
            my_custom,
            checker)

        if checker.has_errors():
            # ExecutableAlgo is not created, not executed
            raise CheckError(msg=context, status=checker.get_check_status())

        if asynchro is True:
            # asynchronous execution

            # creation of an executable algorithm DAO in order to get an id
            exec_algo = FacadeExecution.factory.build_exec_algo_without_custom_without_data_connectors(
                my_implementation)

            # business object is updated with db_id created by DAO
            exec_algo = ExecutableAlgoDao.create(exec_algo, False)
            execution_status.set_algo(exec_algo)

            exec_algo_db_id = exec_algo.get_process_id()

            # Create a thread for the algorithm execution itself
            run_msg = "Running asynchronous: {0} with implementation={1}".format(my_script_name, my_implementation.name)
            LOGGER.info(run_msg)

            execution_status.add_msg(run_msg)

            threading.Thread(target=FacadeExecution.execute_algo_without_custom,
                             args=(my_implementation,
                                   completed_arg_names,
                                   completed_data_sources,
                                   output_names,
                                   receivers,
                                   "" + exec_algo_db_id,
                                   run_debug,
                                   True)).start()
        else:
            # synchronous execution
            run_msg = "Running synchronous: {0} with implementation={1}".format(my_script_name, my_implementation.name)
            LOGGER.info(run_msg)

            execution_status.add_msg(run_msg)

            exec_algo, status = FacadeExecution.execute_algo_without_custom(
                implem=my_implementation,
                input_arg_names=completed_arg_names,
                input_data_sources=completed_data_sources,
                output_arg_names=output_names,
                output_data_receivers=receivers,
                exec_algo_db_id=None,
                run_debug=run_debug,
                dao_managed=True)

            execution_status.set_algo(exec_algo)
            # replace local internal status by the engine status: more interesting
            execution_status.set_internal_status(status)
            run_msg = "Ran synchronous: {0} with implementation={1}".format(my_script_name, my_implementation.name)
            execution_status.add_msg(run_msg)
            LOGGER.info(run_msg)

    except CustomizedAlgoDao.DoesNotExist as cerr:
        nf_msg = "Argument error in execalgo.run: unmatched CustomizedAlgo: err={}".format(cerr)
        nf_err = IkatsNotFoundError(nf_msg)
        execution_status.set_error_with_msg(nf_err, "RunAlgo: initial check failed")

    except ImplementationDao.DoesNotExist as ierr:
        nf_msg = "Argument error in execalgo.run: unmatched Implementation: err={}".format(ierr)
        nf_err = IkatsNotFoundError(nf_msg)
        execution_status.set_error_with_msg(nf_err, "RunAlgo: initial check failed")

    except (CheckError, IkatsInputError, IkatsNotFoundError, IkatsException) as exception:
        # interrupts the executions
        # => in that case: executable algo is not created ...
        raise exception

    except Exception as error:

        error_message = "Failure occurred running {0} with implementation={1}".format(
            my_script_name, algo_name)

        LOGGER.error(error_message)
        execution_status.add_msg(error_message)

        LOGGER.exception(error)

        if (status is None) or (not status.has_error()):
            # add error when not yet recorded ...
            msg = "Unexpected error occurred"
            execution_status.get_state().set_error_with_msg(added_error=error, added_msg=msg, raise_error=False)

        execution_status.get_state().debug = True
        # logged by calling code
    # Note that at this step: execution_status.has_error() may be true
    return execution_status


def __get_run_args(arg_names, arg_values):
    # Prepare dict of json inputs
    dict_inputs = dict()
    for my_name, my_value in zip(arg_names, arg_values):
        dict_inputs[my_name] = my_value
    return dict_inputs


def __get_run_definition(implementation, customized_algo):
    if customized_algo is not None:
        run_def = customized_algo
    else:
        run_def = implementation
    return run_def


def __get_init_context(implementation, customized_algo):
    glob_msg = "RunAlgo: initial check failed on inputs for the run of {}"
    glob_msg = glob_msg.format(__get_run_definition(implementation, customized_algo))
    return glob_msg


def __check_value(profile_item, value, checker):
    if isinstance(profile_item, Parameter):
        checker.check_type(profile_item, value)
        checker.check_domain(profile_item, value)


def __prepare_execution(algo_name,
                        arg_names,
                        arg_values,
                        execution_status,
                        implementation,
                        customized_algo,
                        checker):
    # Init if possible: customized_alp identifier
    customized_algo_id = None
    if customized_algo is not None:
        customized_algo_id = customized_algo.db_id

    # Prepare dict of json inputs
    dict_inputs = __get_run_args(arg_names, arg_values)

    current_epoch_time = "%s" % (time.time() * 1000000)
    running_prefix = "{}_{}_".format(current_epoch_time, algo_name)

    # Fulfill the argument lists with private arguments
    completed_arg_names = []
    completed_data_sources = []
    # input_profile from catalogue is ordered by order_index
    for cat_input in implementation.input_profile:
        name_cat_input = cat_input.name
        data_format_input = cat_input.data_format
        my_init = None
        if data_format_input in FactoryCatalogue.IKATS_PRIVATE_ARGTYPES:
            scope = "private"
            # private argument shall not be passed by the ikats client:
            #  => initialized by the server
            if name_cat_input in arg_names:
                msg = "Argument error in execalgo.run: the argument named {0} in implementation {1} (name={2}) \
                            is private and cannot be defined on the client side".format(name_cat_input,
                                                                                        implementation.name, algo_name)
                execution_status.set_error_with_msg(IkatsInputError(msg),
                                                    "RunAlgo: initial check failed: on input args")

            my_init = FactoryExecAlgo.init_private_arg_value(name_cat_input)

        else:
            scope = "public"

            # any non-private argument must be defined: according to evaluating policy:
            # 1: if possible: initialized from run arguments
            #     Note: specific case: argument is provided with null
            #          => managed since #151688
            #
            # 2: else: initialized from the optional customized value defined by customized_algo
            #          on same profile_item
            # 3: or else: initialized from the optional default value defined on the profile_item
            is_none_explicitly_defined = False
            if name_cat_input in dict_inputs:
                my_init = dict_inputs[name_cat_input]
                is_none_explicitly_defined = my_init is None

            if ((my_init is None) and (is_none_explicitly_defined is False) and
                    (customized_algo is not None) and
                    (customized_algo.has_custom_value(name_cat_input))):
                my_init = customized_algo.get_custom_param_value(name_cat_input, return_default_when_missing=False)
                # it is impossible that the value is missing
                # because customized_algo.has_custom_value(name_cat_input)
                is_none_explicitly_defined = my_init is None

            if (my_init is None) and (is_none_explicitly_defined is False):
                my_init = cat_input.default_value
                # when default value is None
                # => ikats interprets that there is no default value defined in DB
                # ... => keep: is_none_explicitly_defined is left to False

        if (my_init is None) and (is_none_explicitly_defined is False):

            msg = "Undefined {} input name={}: no value in the running context on implem={} custom_algo={}"
            msg = msg.format(scope, name_cat_input, implementation.db_id, customized_algo_id)

            execution_status.set_error_with_msg(IkatsInputError(msg),
                                                __get_init_context(implementation, customized_algo))
        else:
            __check_value(cat_input, my_init, checker)

        completed_arg_names.append(name_cat_input)

        if scope == "private":
            completed_data_sources.append(my_init)
        else:
            # required: transform the client value into the data_source
            #
            # specify a unique data receiver/source name
            my_data_source_ref = "in_" + running_prefix + name_cat_input

            # ... returns the value itself, simple case, or if required, a data source
            my_data_source = FactoryExecAlgo.get_data_source(implem=implementation,
                                                             input_def=cat_input,
                                                             client_value=my_init,
                                                             reference=my_data_source_ref)
            completed_data_sources.append(my_data_source)

    if checker.has_errors():
        # interrupts the execution with CheckError
        raise CheckError(msg=__get_init_context(implementation, customized_algo),
                         status=checker.get_check_status())

    # final check: no unexpected argument from the client inputs
    cat_input_names = [x.name for x in implementation.input_profile]
    for my_name in arg_names:
        if my_name not in cat_input_names:
            execution_status.set_error_with_msg(
                IkatsInputError(
                    "Argument error in execalgo.run: " +
                    "no such argument named {0} in implementation {1} (name={2}): execution is aborted.".format(
                        my_name, implementation.name, algo_name)), "RunAlgo: initial check failed: on input args")
            # process_id will be updated once ExecutableAlgo is saved in DB
    output_names = []
    receivers = []
    for cat_arg_output in implementation.output_profile:
        output_names.append(cat_arg_output.name)

        # If required: build the data receiver
        my_data_receiver_ref = cat_arg_output.name

        process_data_receiver = FactoryExecAlgo.get_data_receiver(implementation,
                                                                  cat_arg_output,
                                                                  my_data_receiver_ref)
        receivers.append(process_data_receiver)

    return completed_arg_names, completed_data_sources, output_names, receivers


def get_algo_db(process_id):
    """
    returns data stored in DB about any algorithm whose execution has been previously launched

    :param process_id: executable algorithm identifier
    :type process_id: str
    :return: executable algorithm from DB
    :rtype: apps.algo.execute.models.business.algo.ExecutableAlgo
    """
    my_algo = ExecutableAlgoDao.find_from_key(process_id)
    if my_algo is None:
        raise IkatsNotFoundError(
            "Resource not found in scripts.execalgo.get_algo_db: ExecutableAlgo with id=" + process_id)

    return my_algo
