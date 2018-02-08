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
    Maxime PERELMUTER <maxime.perelmuter@c-s.fr>
"""
import codecs
import json
import logging
import pickle

import numpy as np

from apps.algo.execute.models.business.data_receiver import AbstractDataReceiver
from ikats.core.library.exception import IkatsException, IkatsInputTypeError
from ikats.core.resource.api import IkatsApi
from ikats_processing.core.resource_config import ResourceClientSingleton

LOGGER = logging.getLogger(__name__)


class ProcessDataDbWriter(AbstractDataReceiver):
    """
    This receiver redefines class AbstractDataReceiver for a processed data:

    Once send_value() is called on this receiver, corresponding process data is stored in db.

    .. deprecated::
        obsolete, will be replaced by ProcessDataWriter.

    """

    def get_received_value(self):
        pass

    def get_received_progress_status(self):
        pass

    def __init__(self, output_name, process_id=None, data=None, data_type=None):
        """
        constructor
        :param output_name: name of the receiver (corresponding to the algorithm output name)
        :type output_name: str
        :param process_id:
        :type process_id: str
        :param data: data to be received by the data receiver
        :type data: depending on algorithm result (for the moment only "CSV" and "JSON" data types are considered)
        :param data_type: type of data (for the moment only "CSV" and "JSON" data types are considered)
        :type data_type: str
        """

        self.output_name = output_name
        self.process_id = process_id
        self.data = data
        self.data_type = data_type

    def get_output_name(self):
        return self.output_name

    def get_data_type(self):
        return self.data_type

    def get_process_id(self):
        return self.process_id

    def set_process_id(self, arg_process_id):
        self.process_id = arg_process_id

    def __str__(self):
        msg = "ProcessDataDbWriter: output_name=%s for process id=%s with data_type=%s"
        return msg % (self.output_name, self.process_id, self.data_type)

    def send_value(self, value, progress_status=None):
        """
        Triggers  the receiver action: import the processed data into the non
        temporal DB, with the defined process-id
        :param value: value to store
        :type value: depending on algorithm output data type
        :param progress_status: will be used to follow the execution progress
        :type progress_status: object
        """
        ntdm = ResourceClientSingleton.get_singleton().get_non_temporal_manager()

        assert self.process_id is not None, "Unexpected: process_id is None"

        try:
            data_to_store = None
            if self.data_type == 'JSON':
                # convert list to string
                data_to_store = json.dumps(value)
            elif self.data_type == 'CSV':

                # save result into csv file
                file_path = '/tmp/%s_%s.csv' % (self.output_name, self.process_id)

                # expecting array-like value
                np.savetxt(file_path, value, delimiter=';', fmt="%s")
                data_to_store = file_path

            # add result to non temporal database
            ntdm.add_data(
                data=data_to_store,
                process_id=self.process_id,
                data_type=self.data_type,
                name=self.output_name)

            LOGGER.debug("Processed data imported in DB.")

        except Exception as error:
            LOGGER.error("Import failure in data receiver: %s", str(self))
            LOGGER.error(error)
            raise error


class ProcessDataWriter(AbstractDataReceiver):
    """
    This receiver is the base class of process_data writers: this is new standard.

    Once send_value() is called on this receiver, corresponding process data is encoded into bytes
    and stored in db.
    """

    def __init__(self, catalog_output_name, writer_id=None):
        """
        Constructor
        :param catalog_output_name: name of the output in catalog,
               associated to the process_data written by send_value()
        :type catalog_output_name: str
        :param writer_id: optional default None: user defined reference of this writer.
               could refer to the implementation occurrence.
        :type writer_id: str
        """
        self.__output_name = catalog_output_name
        self.__execalgo_id = None
        self.__writer_id = writer_id
        self.__written_data_id = None

    def get_written_data_id(self):
        """
        Gets the written id updated by the last call to send_value().
        None: when nothing has been written.
        """
        return self.__written_data_id

    @staticmethod
    def get_received_value():
        """
        return None: value is not cached
        """
        return None

    @staticmethod
    def get_received_progress_status():
        """
        return None: progress status not handled in this receiver
        """
        return None

    def get_writer_id(self):
        return self.__writer_id

    def get_output_name(self):
        return self.__output_name

    def get_process_id(self):
        return self.__execalgo_id

    def set_process_id(self, arg_process_id):
        self.__execalgo_id = arg_process_id

    def __str__(self):
        msg = "{}: writing output named={}. Defined from execalgo_id={} with writer_id={}."
        return msg.format(self.__class__.__name__,
                          self.get_output_name(),
                          self.get_process_id(),
                          self.get_writer_id())

    @staticmethod
    def encode_content(value):
        """
        Encodes the value: returns the blob content: encoded bytes, written in the new row process_data.
        Here: the default implementation is to return the value as-is.

        This method shall be redefined by subclasses, from specific encodings.

        :param value: input value from send_value, not yet ready to be saved in the blob.
        :type value: any
        :return: encoded value is transformed from value argument: this encoded value is ready to be saved
                 in the blob
        :rtype: any
        """
        return value

    def send_value(self, value, progress_status=None):
        """
        Triggers  the receiver action: import the processed data into the non
        temporal DB, with the defined self attributes.
          - encodes the blob content with self.encode_content(value)
          - calls the API to send the blob
          - returns creates row ID

        :param value: value to store
        :type value: depending on algorithm output data type
        :param progress_status: optional default None: will be used to follow the execution progress
        :type progress_status: object
        :return: id of written processed data
        :rtype: str or int

        :raises IkatsException: error with its cause:
          - missing process_id: request is cancelled
          - http request failed
          - unexpected error
        """
        try:

            if self.get_process_id() is None:
                raise IkatsException("Unexpected: send_value() called with self.get_process_id()==None")

            encoded_value = self.encode_content(value)

            LOGGER.debug("Content is encoded, ready to be written. Context=%s", str(self))

            res = IkatsApi.pd.create(data=encoded_value,
                                     process_id=self.get_process_id(),
                                     name=self.get_output_name())

            if res['status']:
                self.__written_data_id = res['id']
                LOGGER.debug("Process-data imported in DB: returned id=%s. Context=%s", self.__written_data_id,
                             str(self))
            else:
                msg = "Failure: IkatsApi.pd.create returned error={}"
                raise IkatsException(msg.format(res))

            return self.__written_data_id

        except Exception:
            raise IkatsException("Writing failure in data receiver: %s" % str(self))


class ProcessDataPlainTextWriter(ProcessDataWriter):
    """
    This receiver redefines class ProcessDataDbWriter: used to directly write plain text into processdata blobs:
    it manages str values: once send_value() is called on this receiver,
    corresponding process data is stored in db as plain text.

    See equivalent reader: ProcessDataPlainTextReader.
    """

    def __init__(self, catalog_output_name, writer_id=None, char_encoding="utf-8"):
        """
        Constructor with char_encoding argument.
        :param catalog_output_name: see superclass
        :type catalog_output_name: see superclass
        :param writer_id: see superclass
        :type writer_id: see superclass
        :param char_encoding: optional default "utf-8": defines the character encoding.
               Value accepted by standard bytes type.
        :type char_encoding: str
        """
        super(ProcessDataPlainTextWriter, self).__init__(catalog_output_name, writer_id)
        self.__char_encoding = char_encoding

    def encode_content(self, value):
        """
        Encodes the str value into bytes, using self.__char_encoding initialized by the constructor.
        Note: bytes value is accepted, in that case it is directly returned.
        :param value: data to encode
        :type value: str or bytes
        :return: encoded bytes
        :rtype: bytes
        :raise IkatsInputTypeError: when value arg has an unexpected type
        """
        if type(value) is bytes:
            return value
        elif type(value) is str:
            return bytes(value, self.__char_encoding)
        else:
            msg = "Unexpected python type={}. Context={}"
            raise IkatsInputTypeError(msg.format(type(value, str(self))))


class ProcessDataPickleWriter(ProcessDataWriter):
    """
    This receiver redefines class ProcessDataWriter::encode_content
    in order to write the pickled object into process_data blob:
    it handles python objects which can be persisted in database in pickle format.

    See equivalent reader: ProcessDataPickleReader
    """

    def __init__(self, catalog_output_name, writer_id=None):
        """
        Constructor
        :param catalog_output_name: see superclass
        :type catalog_output_name: see superclass
        :param writer_id: see superclass
        :type writer_id: see superclass
        """
        super(ProcessDataPickleWriter, self).__init__(catalog_output_name, writer_id)

    def encode_content(self, value):
        """
        Encodes the binary data to pickle then to string

        :param value: data to encode
        :type value: any
        :return: encoded string
        :rtype: str
        """
        my_str_pickle = codecs.encode(pickle.dumps(value), "base64").decode()

        return my_str_pickle
