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
import pickle
from apps.algo.execute.models.business.data_source import AbstractDataSource
from ikats.core.library.exception import IkatsException

from ikats.core.resource.api import IkatsApi

LOG_PROCESS_DATA_READER = logging.getLogger(__name__)


class ProcessDataReader(AbstractDataSource):
    """
    Base class of the data sources reading the process_data blobs.
    """

    def __init__(self, identifier, catalog_input_name, reader_id):
        """
        constructor
        :param identifier: the process_data reference is the ID of the row in database
        :type identifier: str
        :param catalog_input_name: name of the input in catalog, associated to the process_data
        :type catalog_input_name: str
        :param reader_id: identifier of this data source ProcessDataReader
        :type reader_id: str
        """
        self.__id = identifier
        self.__input_name = catalog_input_name
        self.__reader_id = reader_id
        self.__execalgo_id = None

    def get_value(self):
        """
        Reads the value as the BLOB content in the process_data row identified by self.id.

        The decoding process is made by decode() method, which may be overridden.

        :raises IkatsException: error with its cause:
          - missing process_id: request is cancelled
          - read failed (http request failed)
          - unexpected error
        """

        try:
            if self.get_process_id() is None:
                raise IkatsException("Unexpected: process_id is None")

            content = IkatsApi.pd.read(process_data_id=self.__id)

            LOG_PROCESS_DATA_READER.debug("Content has been read. Context=%s", str(self))

            decoded_content = self.decode_content(content)

            LOG_PROCESS_DATA_READER.debug("Content has been decoded. Context=%s", str(self))

            return decoded_content

        except Exception:
            raise IkatsException("Read failure in data source ProcessDataReader: %s" % str(self))

    def get_process_id(self):
        """
        Gets the ID of the executed algorithm: None before the running time
        """
        return self.__execalgo_id

    def set_process_id(self, process_id):
        """
        Sets the ID of the executed algorithm: this can be done at running time,
        see ExecutableAlgo::update_connectors_with_pid().

        :param process_id: process_id value to be assigned
        :type process_id: int or str
        """
        self.__execalgo_id = process_id

    @property
    def identifier(self):
        """
        Gets the ID key pointing to the process_data which will be read
        """
        return self.__id

    @property
    def input_name(self):
        """
        Gets the name on the input defined in the catalog, associated to the process_data
        """
        return self.__input_name

    @property
    def reader_id(self):
        """
        Get the ProcessDataReader unique identifier
        """
        return self.__reader_id

    @staticmethod
    def decode_content(raw_content):
        """
        Decodes the raw content.
        By default this method simply returns raw_content, as is.
        This method ought to be overridden by subclass in order to have specific decoding process.

        :param raw_content: the raw content directly loaded from the blob of process_data
        :type raw_content: bytes
        :return: the decoded content
        :rtype: any
        """
        return raw_content

    def __str__(self):
        msg = "{}: reading input named={} from data id={}. Defined from execalgo_id={} with reader_id={}."
        return msg.format(self.__class__.__name__,
                          self.input_name,
                          self.id,
                          self.get_process_id(),
                          self.reader_id)


class ProcessDataPlainTextReader(ProcessDataReader):
    """
    The reader of plain text encoded in the process_data blob.
    """

    def __init__(self, identifier, catalog_input_name, reader_id, char_encoding="utf-8"):
        """
        constructor
        :param identifier: the process_data reference is the ID of the row in database
        :type identifier: str
        :param catalog_input_name: name of the input in catalog, associated to the process_data
        :type catalog_input_name: str
        :param reader_id: identifier of this data source ProcessDataReader
        :type reader_id: str
        """
        super(ProcessDataPlainTextReader, self).__init__(identifier, catalog_input_name, reader_id)
        self.__char_encoding = char_encoding

    def decode_content(self, raw_content):
        """
        Decodes the raw_content as a plain text: converted into a str, using self.__char_encoding
        :param raw_content: the raw content
        :type raw_content: bytes or str
        :return: the decoded content
        :rtype: str
        :raises IkatsException: unexpected raw_content type
        """

        # You could have kept type(...) is ...
        if isinstance(raw_content, str):
            return raw_content
        elif isinstance(raw_content, bytes):
            return str(raw_content, self.__char_encoding)
        else:
            msg = "Unhandled raw content type={} instead of bytes or str. Context={}"
            raise IkatsException(msg.format(type(raw_content), str(self)))


class ProcessDataPickleReader(ProcessDataReader):
    """
    The reader of python object picked in the process_data blob:
    case when the pickle library has been used to persist object in the blob.
    """

    def __init__(self, identifier, catalog_input_name, reader_id):
        """
        Constructor
        :param identifier: the process_data reference is the ID of the row in database
        :type identifier: str
        :param catalog_input_name: name of the input in catalog, associated to the process_data
        :type catalog_input_name: str
        :param reader_id: identifier of this data source ProcessDataPickleReader
        :type reader_id: str
        """
        super(ProcessDataPickleReader, self).__init__(identifier, catalog_input_name, reader_id)

    def decode_content(self, raw_content):
        """
        Decodes the raw_content as a python object, unpicking the raw content.
        :param raw_content: the raw content
        :type raw_content: pickle bytes
        :return: the unpicked object
        :rtype: any
        :raises IkatsException: error occurred while loading the object from the pickled content
        """
        try:
            obj = pickle.loads(raw_content)
            return obj
        except Exception:
            raise IkatsException("Failed to load picked object. Context={}".format(str(self)))
