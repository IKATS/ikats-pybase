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
import decimal

from apps.algo.custom.models.business.algo import CustomizedAlgo
from apps.algo.execute.models.business.data_receiver import AbstractDataReceiver
from apps.algo.execute.models.business.data_source import AbstractDataSource, SimpleValueDataSource
from ikats.core.library.status import State as EnumState
from ikats_processing.core.time import time_utils


class ExecutableAlgo(object):
    """
    classdocs
    """

    def __init__(
            self,
            custom_algo,
            dict_data_sources=None,
            dict_data_receivers=None,
            arg_process_id=None,
    ):
        """
        Init of Executable algorithm supposes that self.__state is INIT at present time, with undefined (ie None)
        self.__start_execution_date and self.__end_execution_date.
        You can use afterwards setters to update these attributes  ...

        :param custom_algo: required: customized algo wrapped by this executable algo
        :type custom_algo: apps.algo.custom.models.business.algo.CustomizedAlgo
        :param dict_data_sources:
        :type dict_data_sources:
        :param dict_data_receivers:
        :type dict_data_receivers:
        :param arg_process_id:
        :type arg_process_id: str if defined, or None
        """
        if custom_algo is not None:
            assert (isinstance(custom_algo, CustomizedAlgo))
        self.__custom_algo = custom_algo

        if dict_data_sources:
            assert (type(dict_data_sources) is dict)
            self.__data_sources = dict_data_sources
        else:
            self.__data_sources = dict()

        if dict_data_receivers:
            assert (type(dict_data_receivers) is dict)
            self.__data_receivers = dict_data_receivers
        else:
            self.__data_receivers = dict()

        self.__process_id = None
        if arg_process_id is not None:
            self.set_process_id(arg_process_id)

        # note: by default current date is the creation date
        # but this can be changed after ...
        # time in seconds (floating point if system is able to...), since EPOCH
        self.set_creation_date(time_utils.get_current_time_second_as_float())

        # by default current state is INIT
        # but this can be changed after ...
        self.set_state(EnumState.INIT)

        # by default: undefined start/end dates
        self.__start_execution_date = None
        self.__end_execution_date = None

    def get_state(self):
        return self.__state

    def set_state(self, value):
        if type(value) is int:
            self.__state = EnumState.parse(value)
        else:
            assert (isinstance(value, EnumState))
            self.__state = value

    def get_creation_date(self):
        """
        Note: if float is expected:  use float( algo.get_creation_date() )
        :return: creation date
        :rtype: decimal.Decimal (!!!)
        """
        return self.__creation_date

    def get_start_execution_date(self):
        """
        Note: if float is expected:  use float( algo.get_start_execution_date() )
        :return: creation date
        :rtype: decimal.Decimal (!!!)
        """
        return self.__start_execution_date

    def get_end_execution_date(self):
        """
        Note: if float is expected:  use float( algo.get_end_execution_date() )
        :return: end execution date
        :rtype: decimal.Decimal (!!!)
        """
        return self.__end_execution_date

    def set_creation_date(self, value):
        """
        Sets the creation date.
        :param value: value of decimal number in seconds since EPOCH
        :type value: float or string or Decimal
        """
        self.__creation_date = decimal.Decimal(value)

    def set_start_execution_date(self, value):
        """
        Sets the start execution date.
        :param value: value of decimal number in seconds since EPOCH
        :type value: float or string or Decimal
        """
        if value is None:
            self.__start_execution_date = None
        else:
            self.__start_execution_date = decimal.Decimal(value)

    def trigger_start_execution_date(self):
        """
        Just update the start_execution_date with the current date, using
        time_utils.get_current_time_second_as_float
        """
        self.__start_execution_date = decimal.Decimal(time_utils.get_current_time_second_as_float())

    def set_end_execution_date(self, value):
        """
        Sets the end execution date.
        :param value: value of decimal number in seconds since EPOCH
        :type value: float or string or Decimal
        """
        if value is None:
            self.__end_execution_date = None
        else:
            self.__end_execution_date = decimal.Decimal(value)

    def trigger_end_execution_date(self):
        """
        Just update the end_execution_date with the current date, using
        time_utils.get_current_time_second_as_float
        """
        self.__end_execution_date = decimal.Decimal(time_utils.get_current_time_second_as_float())

    def get_process_id(self):
        return self.__process_id

    def set_process_id(self, value):
        """
        Sets the process ID
        :param value: the process ID value
        :type value: str if defined or None
        """
        if value is not None:
            assert (type(value) is str)

        self.__process_id = value

    def is_db_id_defined(self):
        return self.__process_id is not None

    def as_detailed_string(self):

        msg = ("Executable algo\n"
               "  PID:%s\n"
               "  Creation Date:%s\n"
               "  start_date:%s\n"
               "  end_date:%s\n"
               "  state:%s\n"
               "  custom:%s\n"
               "  sources:%s\n"
               "  receivers:%s\n")

        sources = ""
        for source in self.__data_sources:
            # Limit the data to the first 3000 characters to not overload the log
            if len(str(self.__data_sources[source])) > 3000:
                data = str(self.__data_sources[source])[:3000] + " ...(truncated)"
            else:
                data = self.__data_sources[source]
            sources += "    %s = %s\n" % (source, data)
        receivers = ""
        for source in self.__data_receivers:
            # Limit the data to the first 3000 characters to not overload the log
            if len(str(self.__data_receivers[source])) > 3000:
                data = str(self.__data_receivers[source])[:3000] + " ...(truncated)"
            else:
                data = self.__data_receivers[source]
            receivers += "    %s = %s\n" % (source, data)

        return msg % (self.__process_id,
                      str(self.__creation_date),
                      str(self.__start_execution_date),
                      str(self.__end_execution_date),
                      self.__state,
                      self.custom_algo,
                      sources,
                      receivers)

    def __str__(self):
        msg = "Executable algo process_id=%s, custom=%s"
        return msg % (self.__process_id, self.custom_algo)

    def get_custom_algo(self):
        return self.__custom_algo

    def set_custom_algo(self, custom_algo):
        """
        CustomizedAlgo setter: needed by DAO.
        :param custom_algo: instance of CustomizedAlgo.
        :type custom_algo: CustomizedAlgo. None is also accepted
        """
        if custom_algo is not None:
            assert (isinstance(custom_algo, CustomizedAlgo))
        self.__custom_algo = custom_algo

    def get_execution_plugin(self):
        return self.__custom_algo.implementation.execution_plugin

    def get_lib_path(self):
        return self.__custom_algo.implementation.library_address

    def get_ordered_input_names(self):
        """
        Returns list of names for input arguments: ordered according to self.custom_algo.implementation.input_profile
        """
        names = None
        try:
            names = [
                x.name for x in self.custom_algo.implementation.input_profile]
        except Exception:
            raise Exception(
                "Failed: ExecutableAlgorithm::get_ordered_input_names for algo [%s]" % self.__str__())
        return names

    def get_ordered_output_names(self):
        """
        Returns list of names for output arguments: ordered according to self.custom_algo.implementation.output_profile
        """
        names = None
        try:
            names = [
                x.name for x in self.custom_algo.implementation.output_profile]
        except Exception:
            raise Exception(
                "Failed: ExecutableAlgorithm::get_ordered_output_names for algo [%s]" % self.__str__())
        return names

    def get_data_sources(self):
        return self.__data_sources

    def set_data_sources(self, dict_sources):
        """
        Setter of data sources: defining inputs of the executed algo
        :param dict_sources: structure coding the set of ( argname, source )
        :type dict_sources: dict of sources:
            - each key is a string: the argument name configured in the catalogue
            - each dict value is source of data: a subclass of AbstractDataSource
              (ex: use SimpleDataSource wrapper for explicit values)
        """
        self.__data_sources = dict_sources

    def get_data_receivers(self):
        return self.__data_receivers

    def set_data_receivers(self, dict_receivers):
        """
        Setter of data receivers: defines consumers of results produced by executed algo
        Note: algo can produce several results, each configured in catalogue as named output arguments
        :param dict_receivers: structure coding the set of ( argname, receiver )
        :type dict_receivers: dict of receivers:
            - each key is a string: the output argument name, configured in the catalogue
            - each dict value is receiver of data, always a subclass of AbstractDataReceiver
        """
        self.__data_receivers = dict_receivers

    def get_data_source(self, arg_name):
        if arg_name in self.__data_sources.keys():
            return self.__data_sources[arg_name]
        else:
            raise Exception(
                "Undefined data source for argument name=%s" % arg_name)

    def set_data_source(self, arg_name, data_source):
        """
        Defining ExecutableAlgo before Runtime: assign a data source to an argument of algorithm.
        :param arg_name: name matching argument from   self.custom_algo.implementation
        :type arg_name: str
        :param data_source: the data source instance
        :type data_source: subclass of AbstractDataSource
        """
        assert (isinstance(data_source, AbstractDataSource))

        self.__data_sources[arg_name] = data_source

    def set_input_value(self, arg_name, value):
        """
        Defining ExecutableAlgo before Runtime: with a simple value, fully predefined:
        this method is equivalent to:
        self. setDataSource(self, arg_name, SimpleValueDataSource(value))

        Note: this method may lead to memory troubles: it is recommended to use setDataSource with more appropriate
        subclasses of AbstractDataSource when handling
          - large datasets better handled by external cache
          - value by reference  (implying DB connections, big external files ...)
          - generators, iterators ...

        :param arg_name: name matching argument from   self.custom_algo.implementation
        :type arg_name: str
        :param value:
        :type value:
        """
        self.set_data_source(arg_name, SimpleValueDataSource(value))

    def get_data_receiver(self, arg_name):
        if arg_name in self.data_receivers.keys():
            return self.__data_receivers[arg_name]
        else:
            raise Exception(
                "Undefined data receiver for argument name=%s" % arg_name)

    def set_data_receiver(self, arg_name, data_receiver):
        assert (isinstance(data_receiver, AbstractDataReceiver))

        self.__data_receivers[arg_name] = data_receiver

    def consume_value(self, arg_name):
        """
        At runtime: consume retrieve the input value for the algo from
        - either the self.custom_algo if arg_name is matching a parameter (first attempt)
        - or from the the data_source associated to the argument named arg_name (second attempt)
        :param arg_name: name specifying one argument/parameter from   self.custom_algo.implementation
        :type arg_name: str
        :return: value returned either from a parameter (value in self.custom_algo), or from an argument
            (value in associated data source)
        """
        if arg_name in self.custom_algo.custom_params.keys():
            my_val = self.custom_algo.custom_params[arg_name]
        else:
            my_data_source = self.get_data_source(arg_name)
            if my_data_source:
                my_val = my_data_source.get_value()
            else:
                raise Exception(
                    "Unconfigured data source for [%s] in algo (%s)" % (arg_name, str(self)))

        return my_val

    def update_connectors_with_pid(self):
        """
        Update the process id on
          - each data source
          - each data receiver
        Note: this method shall be called once
          - 1: every data sources are set
          - 2: every data receivers are set
          - 3: this algo has at least a defined process_id: case with
        """
        for source in self.__data_sources.values():
            source.set_process_id(self.__process_id)
        for receiver in self.__data_receivers.values():
            receiver.set_process_id(self.__process_id)

    def produce_value(self, arg_name, value, progress_status=None):
        """
        At runtime: send a new couple (value, status) to the data receiver of one specific output argument
        TODO [story barre progression] finaliser usage de status
        :param arg_name: name specifying one argument from   self.custom_algo.implementation
        :type arg_name: str
        :param value: produced value
        :type value: object
        :param progress_status: optional information about running status / progress information
        :type progress_status: object  TODO [story barre progression]  classe specifique a definir
            (differente de ExecStatus ...)
        """
        my_receiver = self.get_data_receiver(arg_name)
        my_receiver.send_value(value, progress_status)

    # custom_algo: instance of CustomizedAlgo set by constructor
    custom_algo = property(get_custom_algo, set_custom_algo, None, "")

    # data_sources is dict with key: arg/param name and value: instance of
    # DataSource
    data_sources = property(get_data_sources, set_data_sources, None, "")

    # data_receivers is dict with key: arg/param name and value: instance of
    # DataReceiver
    data_receivers = property(get_data_receivers, set_data_receivers, None, "")
    process_id = property(get_process_id, set_process_id, None, "")
    creation_date = property(get_creation_date, set_creation_date, None, "")
    start_execution_date = property(get_start_execution_date, set_start_execution_date, None, "")
    end_execution_date = property(get_end_execution_date, set_end_execution_date, None, "")
    state = property(get_state, set_state, None, "")
