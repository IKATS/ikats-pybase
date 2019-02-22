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
from apps.algo.execute.models.business.exec_engine import ExecStatus

LOGGER = logging.getLogger(__name__)


class ExecutionStatus(object):
    """
    Sums the result of ExecutableAlgo executed by ExecutionEngine.


    Note: TODO refactoring: this class will soon replace completely the ExecStatus: ExecStatus will be removed
    """

    def __init__(self, algo, internal_status):
        """
        Constructor
        """
        if algo is not None:
            assert (isinstance(algo, ExecutableAlgo)), \
                "Error in ExecutionStatus::__init__(): Expecting algo.ExecutableAlgo class for arg algo"
            self.set_algo(algo)
        if internal_status is not None:
            assert (isinstance(internal_status, ExecStatus)), \
                "Error in ExecutionStatus::__init__(): Expecting exec_engine.ExecStatus class for arg internal_status"
            self.set_internal_status(internal_status)

    def get_process_id(self):
        """
        Get the process id of this execution
        :return:
        """
        if self.__algo is None:
            return None
        else:
            return self.__algo.get_process_id()

    def get_algo(self):
        """
        Get the algorithm of this execution
        :return:
        """
        if self.__algo is None:
            return None
        else:
            return self.__algo

    def get_msg_list(self):
        """
        Gets the internal messages list
        """
        if self.__internal_status is None:
            return None
        else:
            return self.__internal_status.get_msg_list()

    def add_msg(self, msg):
        """
        Adds a new message to the internal status
        :param msg: the added message
        :type msg: str
        """
        if self.__internal_status is None:
            raise Exception(
                "Forbidden use: ExecutionStatus::add_msg called with undefined __internal_status: called with arg msg="
                + msg)
        else:
            self.__internal_status.add_msg(msg)

    def has_error(self):
        """
        Checks it internal status exists and has an error already recorded
        :return:  True only if error exists within self.__internal_status
        """
        if self.__internal_status is not None:
            return self.__internal_status.has_error()
        else:
            return False

    def set_error_with_msg(self, added_error, added_msg=None, raise_error=True):
        """
        Complete this status with error, and according to raiseError: raises the error
        :param added_error: error set on self.__error
        :type added_error: Exception
        :param added_msg: message associated to the error, summarizing of the context
        :type added_msg: str
        :param raise_error:
        :type raise_error:
        """
        if self.__internal_status is None:
            # unexpected case !!!!
            LOGGER.error(
                "Forbidden use: ExecutionStatus::set_error_with_msg called with undefined __internal_status => "
                "please correct the calling code")
            if added_msg is not None:
                LOGGER.error(added_msg)

            # the main error is still added_error ...
            LOGGER.exception(added_error)
            raise added_error
        else:
            # usual case
            self.__internal_status.set_error_with_msg(added_error, added_msg, raise_error)

    def get_error(self):
        """
        return all errors encountered for this execution
        :return:
        """
        if self.__internal_status is None:
            return None
        else:
            return self.__internal_status.get_error()

    def get_state(self):
        """
        Get the current execution state
        :return:
        """
        if self.__algo is None:
            return None
        else:
            return self.__algo.get_state()

    def set_algo(self, value):
        """
        Set the algorithm to use for this execution
        :param value:
        :return:
        """
        if value is not None:
            assert (isinstance(value, ExecutableAlgo))
            self.__algo = value

    def set_internal_status(self, value):
        """
        Set the insternal status of the execution
        :param value:
        :return:
        """
        if value is not None:
            assert (isinstance(value, ExecStatus))
            self.__internal_status = value

    def __str__(self):
        tmpl_msg = "ExecutionStatus:\n  -with status=%s\n -with algo=%s"
        algo = "None"
        if self.__algo is not None:
            algo = self.__algo.__str__()
        status = "None"
        if self.__internal_status is not None:
            status = self.__internal_status.__str__()

        return tmpl_msg % (status, algo)
