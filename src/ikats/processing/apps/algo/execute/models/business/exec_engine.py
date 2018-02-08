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
from abc import ABCMeta, abstractmethod
import logging
import sys
import traceback

from apps.algo.execute.models.business.algo import ExecutableAlgo
from apps.algo.execute.models.orm.algo import ExecutableAlgoDao
from ikats.core.library.exception import IkatsException
from ikats.core.library.status import State as EnumState

LOGGER = logging.getLogger(__name__)


class EngineException(IkatsException):
    """
    Exception declaration for an Engine error
    """
    def __init__(self, msg, cause=None):
        super(EngineException, self).__init__(msg, cause)


class AlgoException(IkatsException):
    """
    Exception declaration for an Algorithm error
    """
    def __init__(self, msg, cause=None):
        super(AlgoException, self).__init__(msg, cause)


class ExecStatus(object):
    """
    Status of the execution
    """
    def __init__(self, debug, error=None, msg=None):
        """
        :param debug: True if debug is demanded, optional : False is default value
        :type debug: bool
        :param error: error caught at runtime, cause of failure (default None)
        :type error:Exception
        :param msg: Initial message: optional, default: None
        :type msg: list of str or objects with readable __str__()
        """
        self.__debug = debug
        self.__error = error
        self.__msg = []
        if msg is not None:
            self.__msg.append(msg)

    def get_error(self):
        return self.__error

    def get_msg_list(self):
        """
        Gets the list of messages
        :return: the list
        :rtype:  list of str
        """
        return self.__msg

    def set_error(self, value):
        self.__error = value

    def add_msg(self, info):
        self.__msg.append(info)

    def has_error(self):
        return self.__error is not None

    def set_error_with_msg(self, added_error, added_msg, raise_error=True):
        """
        Complete this status with error, and according to raiseError: raises the error
        :param added_error: error set on self.__error
        :type added_error: Exception
        :param added_msg: message associated to the error, summarizing of the context:
                        it will be completed with str(error)
        :type added_msg: str
        :param raise_error:
        :type raise_error:
        """
        self.__error = added_error
        self.__msg.append("Error added with [msg=%s] : %s" % (added_msg, str(added_error)))

        if raise_error is True:
            raise self.__error

    error = property(get_error, set_error, None, "")

    def __str__(self):
        if self.__error:
            return "ExecStatus: msg[%s] with error[%s]" % (str(self.__msg), str(self.__error))

        return "ExecStatus: msg[%s]" % (str(self.__msg))


class ExecEngine(object):
    """
    Abstract class allowing the execution of algorithms

    """

    __metaclass__ = ABCMeta

    def __init__(self, executable_algo, debug=False, dao_managed=False):

        assert (isinstance(executable_algo, ExecutableAlgo))

        if executable_algo.state != EnumState.INIT:
            raise ValueError("Unexpected: executable algo must be in state INIT")

        self.__dao_managed = dao_managed

        # create exec algo in database, if required
        #
        self.__executable_algo = executable_algo
        if dao_managed:

            if executable_algo.process_id is None:
                # Not yet save !
                self.__executable_algo = ExecutableAlgoDao.create(
                    original_business_obj=executable_algo, merge_with_unsaved_data=True)

        self.__status = ExecStatus(debug=debug)

    def get_executable_algo(self):
        return self.__executable_algo

    def get_status(self):
        return self.__status

    def add_msg(self, info):
        self.__status.add_msg(info)

    def execute(self):
        """
        This method is published as the entry point of execution for the client:
        it internally call run_command and updates finally the returned self.status
        :return: self.status
        """
        try:
            LOGGER.info("ExecEngine::execute update process_id on each data sources and data receivers")
            self.__status.add_msg("update process_id on each data sources and data receivers")
            self.__executable_algo.update_connectors_with_pid()

            LOGGER.info("ExecEngine::execute started: %s", self.__executable_algo.as_detailed_string())

            self.__status.add_msg("update executable algo: trigger start date + RUN")

            self.__executable_algo.trigger_start_execution_date()
            self.__executable_algo.state = EnumState.RUN

            if self.__dao_managed:
                self.__executable_algo = ExecutableAlgoDao.update(self.__executable_algo,
                                                                  merge_with_unsaved_data=True)

            LOGGER.debug("ExecEngine::run_command() ... ")
            self.__status.add_msg("run_command ...")
            self.run_command()
            LOGGER.debug("... run_command() finished without exception")

            self.__status.add_msg("sets on exec algo: state=OK")

            self.__executable_algo.state = EnumState.ALGO_OK

            if self.__dao_managed:
                self.__executable_algo = ExecutableAlgoDao.update(self.__executable_algo,
                                                                  merge_with_unsaved_data=True)

        except AlgoException as err_alg:
            trace_back = sys.exc_info()[2]
            stack_list = traceback.format_tb(trace_back, limit=None)

            LOGGER.error("Caught AlgoException: ")
            LOGGER.exception(err_alg)

            self.status.error = err_alg
            self.status.add_msg("Got error raised by algorithm => ExecutableAlgo.state == ALGO_KO")
            self.status.add_msg(str(err_alg))
            if stack_list and (len(stack_list) > 0):
                for line_error in stack_list:
                    self.status.add_msg(line_error)

            self.__executable_algo.state = EnumState.ALGO_KO

        except EngineException as err_engine:
            LOGGER.error("EngineException: ")
            LOGGER.exception(err_engine)

            self.status.error = err_engine
            self.status.add_msg("Got error raised by engine => ExecutableAlgo.state == ENGINE_KO")

            self.__executable_algo.state = EnumState.ENGINE_KO

        except Exception as e:
            LOGGER.error("Exception: ")
            LOGGER.exception(e)

        finally:
            self.__executable_algo.trigger_end_execution_date()
            if (not ((self.__executable_algo.end_execution_date is None) or
                     (self.__executable_algo.start_execution_date is None))):
                LOGGER.info("- execute() handled in  %s sec.",
                            self.__executable_algo.end_execution_date - self.__executable_algo.start_execution_date)

            LOGGER.info("ExecEngine::execute ... ended: %s", self.__executable_algo.as_detailed_string())

            if self.__dao_managed:
                try:
                    self.__executable_algo = ExecutableAlgoDao.update(self.__executable_algo,
                                                                      merge_with_unsaved_data=True)
                except Exception as save_err:
                    LOGGER.error("EngineException: saving the ExecutableAlgo in DB")
                    LOGGER.exception(save_err)

                    if self.__executable_algo.state == EnumState.RUN:
                        my_msg = "Algo has been run with success, producing results; \
                                but the ExecutableAlgoDao.update(...) failed. Please contact administrator."
                        self.status.add_msg(my_msg)
                        LOGGER.error(my_msg)
                        self.status.error = save_err
                        self.__executable_algo.state = EnumState.ENGINE_KO

        return self.status

    @abstractmethod
    def run_command(self):
        """
        abstract void method: contract is the following:
           pre-required: data sources and receivers are all set as expected on self.executable_algo
           - run the algo defined by self.executable_algo
           - consumes inputs from defined data sources
           - produces results into defined data receivers
           - updates the engine.status.msg with additional msg(s) (optional)
           - throws EngineException for any error generated by engine itself
           - throws AlgoException for any error raised by algorithm itself
        """
        raise NotImplementedError("Please Implement this method")

    executable_algo = property(get_executable_algo, None, None, "")
    status = property(get_status, None, None, "")
