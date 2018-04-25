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
import codecs
import pickle

from apps.algo.catalogue.models.business.factory import FactoryCatalogue
from apps.algo.catalogue.models.business.profile import ProfileItem
from apps.algo.custom.models.business.algo import CustomizedAlgo
from apps.algo.execute.models.business.algo import ExecutableAlgo
from apps.algo.execute.models.business.data_receiver import SimpleDataReceiver
from apps.algo.execute.models.business.data_source import AbstractDataSource
from apps.algo.execute.models.business.dataflow.process_data_receiver import \
    ProcessDataDbWriter, ProcessDataPickleWriter, ProcessDataPlainTextWriter
from apps.algo.execute.models.business.dataflow.process_data_sources import ProcessDataPlainTextReader


class FactoryExecAlgo(object):
    """
    This class provides different ways to instantiate one ExecutableAlgorithm
    - services follow the naming syntax get[_customized][_persistent]_algo[_xxx](...)
       where name parts have a specific meaning
       - "Customized" involves implementations with editable parameters
       - "Persistent" involves implementations defined in the catalogue database
    """

    @staticmethod
    def build_exec_algo_without_custom(implementation, input_names, input_values_or_sources,
                                       output_names, output_receivers):
        """
        build an executable algorithm from a given implementation
        :param implementation: instance of Implementation defined in catalogue
        :type implementation: apps.algo.catalogue.business.implem.Implementation
        :param input_names: list of algo input names
        :type input_names: list
        :param input_values_or_sources:
        :type input_values_or_sources
        :param output_names: list of algo output names
        :type output_names: list
        :param output_receivers: list of algo output receivers
        :type output_receivers: list
        """
        buzz_custom = CustomizedAlgo(implementation)
        buzz_exec = ExecutableAlgo(buzz_custom)

        # Optional dict assigning data sources
        if input_names:
            if len(input_names) != len(input_values_or_sources):
                raise Exception(
                    "Unexpected error: build_exec_algo_without_custom called with \
                    len( input_names) != len(input_values_or_sources)")

            for (arg, value) in zip(input_names, input_values_or_sources):
                if isinstance(value, AbstractDataSource):
                    # value not yet evaluated: AbstractDataSource::getValue() is called during execution
                    # example: a data source may be a reader of OpenTSDB, reading
                    # one TS
                    buzz_exec.set_data_source(arg, value)
                else:
                    # evaluated value directly passed
                    buzz_exec.set_input_value(arg, value)
        if output_names:
            if len(output_names) != len(output_receivers):
                raise Exception(
                    "Unexpected error: build_exec_algo_without_custom called with \
                    len( output_names) != len(output_receivers)")

            for (out_arg_name, out_receiver) in zip(output_names, output_receivers):
                if out_receiver is None:
                    buzz_exec.set_data_receiver(out_arg_name, SimpleDataReceiver())
                else:
                    buzz_exec.set_data_receiver(out_arg_name, out_receiver)

        return buzz_exec

    @staticmethod
    def build_exec_algo_without_custom_without_data_connectors(implementation):
        buzz_custom = CustomizedAlgo(implementation)
        buzz_exec = ExecutableAlgo(buzz_custom)
        return buzz_exec

    @classmethod
    def init_private_arg_value(cls, dtype):
        """
        Initializes the value of a private argument, hidden to client, but required by the server execution.
        Examples: the temporal data manager
        :param dtype: the data_format of the argument specifically initialized on the server side
        :type dtype: str
        :return: the value initialized by the configured function in FactoryCatalogue
        :rtype: type depending on the data_format:
        """
        if dtype in FactoryCatalogue.IKATS_PRIVATE_ARGTYPES:
            my_initializer = FactoryCatalogue.IKATS_PRIVATE_ARG_INITIALIZERS[dtype]
            return my_initializer()
        else:
            raise Exception("Error in FactoryExecAlgo: private type with name=%s has no initializer defined." % dtype)

    @classmethod
    def get_data_source(cls, implem, input_def, client_value, reference):
        """
        :param implem: the catalogue definition of the implementation : business object
        :type implem: Implementation
        :param input_def: the catalogue definition of the input: business object
        :type input_def: ProfileItem (Parameter or Argument)
        :param client_value: input value provided by the client.
        :type client_value: any type
        :param reference is a value used to build unique identifier of the data source
        :type reference: str
        :return: built data source if conversion (or iteration, ...) is required, otherwise,
                the argument client_value is returned.
        :rtype: DataSource or type of client_value
        """

        # Prepare the reader identifier <=> implementation name + input name
        reader_id = "input.{}.{}".format(implem.name, input_def.name)

        # Here: client provides the ID of process_data row for data types compatible with
        # plain-text:
        if input_def.data_format in [FactoryCatalogue.DOT_ARGTYPE]:
            # Default encoding is 'utf-8'

            return ProcessDataPlainTextReader(identifier=client_value,
                                              catalog_input_name=input_def.name,
                                              reader_id=reader_id)

        # Here: client provides the pickled model formatted as a string.
        elif input_def.data_format in [FactoryCatalogue.SK_MODEL_ARGTYPE]:
            return pickle.loads(codecs.decode(client_value.encode(), 'base64'))

        # else: any other values are explicitly defined...
        else:
            # - client_value is an effective value
            #
            # - or client_value is a database reference provided by the front client
            #   => the executed algorithm is responsible of the data reading from database
            #
            #   In the future, IKATS will integrate new smart connectors *Reader
            #   from ikats_django module (process_data_sources):
            #   theses will read data before transmitting to the executed script
            #   from ikats_algo
            #   => this will avoid big http traffic between front/back.
            #   => this will reduce the work of contributors
            return client_value

    @classmethod
    def get_data_receiver(cls, implem, output_profile_item, reference):
        """
        Builds the data receiver according to the output definition in the catalogue

        :param implem: the catalogue definition of the implementation : business object
        :type implem: Implementation
        :param output_profile_item: the catalogue definition of the output: business object
        :type output_profile_item: Argument
        :param reference: is a value used to build unique identifier of the data receiver
        :type reference: str
        :return: the built data receiver
        :rtype: DataReceiver subclass
        """

        assert isinstance(output_profile_item, ProfileItem) and (output_profile_item is not None), \
            "Unexpected param FactoryCatalogue.get_data_receiver : ProfileItem type required, and None is forbidden"

        # Note1: process_id attribute will be updated once ExecutableAlgo is saved in DB
        #
        # Note2: at the moment: output_name and reference are equal in the context of ExecutableAlgo
        #
        output_type = output_profile_item.data_format
        output_name = output_profile_item.name

        # Here: deprecated use: for CSV written data types
        if output_type in [FactoryCatalogue.CORRELATION_MATRIX_ARGTYPE,
                           FactoryCatalogue.MODEL_ARGTYPE]:
            # Deprecated use ... presently kept
            return ProcessDataDbWriter(output_name=reference,
                                       process_id=None,
                                       data_type="CSV")

        # Here: plain-text written data types
        elif output_type in [FactoryCatalogue.DOT_ARGTYPE]:
            # see default args: encoding is utf-8
            return ProcessDataPlainTextWriter(catalog_output_name=output_name,
                                              writer_id=reference)

        # Here: data types written with pickle library
        elif output_type in [FactoryCatalogue.SK_MODEL_ARGTYPE]:
            return ProcessDataPickleWriter(catalog_output_name=output_name,
                                           writer_id=reference)
        # ... else JSON written data types
        else:
            # Deprecated use of ProcessDataDbWriter
            return ProcessDataDbWriter(output_name=reference,
                                       process_id=None,
                                       data_type="JSON")
