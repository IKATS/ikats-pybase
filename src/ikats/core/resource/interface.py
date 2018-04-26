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
import logging
from logging.handlers import RotatingFileHandler

from ikats.core.library.singleton import Singleton
from ikats.core.resource.client.non_temporal_data_mgr import NonTemporalDataMgr
from ikats.core.resource.client.temporal_data_mgr import TemporalDataMgr


class ResourceLocator(object, metaclass=Singleton):
    """
    This class is hosting the implementations of read/write services dealing with resources
      - time-series
      - meta-data
      - process-data
      - ...
    Presently these services have standard implementations
      - by TemporalDataManager (tdm), defining an interface -list of methods and their profile-
      - by NonTemporalDataManager (ntdm), defining an interface -list of methods and their profile-
    Later: mocked, or optimized implementations of these 2 will be developed, following the standard interfaces

    These services ought to be executed in spark context (map/reduce) by executors.

    How to initialize the ResourceLocator services ?
      - this class is a singleton: initialization is run once per process
        - default call: ResourceLocator()
          - ResourceLocator() will read standard deployment configuration file, calling internal __load_from_file__()
            - Assumed: configuration file(s) are deployed on the cluster to enable load_config()
        - explicit initialization ResourceLocator(tdm=..., ntdm=..., ... ) ought to be reserved to mocked tests,
            - specific implementations of tdm/ntdm ought to be used in that case
            - presently: syntax requires kwargs arguments for names tdm and ntdm.
              This could be extended later to new resource managers

    How to call a service from ResourceLocator ?
      - example: a service from tdm interface:
        - ResourceLocator().tdm.get_ts(...) is equivalent to:
          RessourceLocator.get_singleton().get_tdm().get_ts(...)
            - get_ts(...) has the same profile as the method on TemporalDataManager method get_ts()

      - it is the same for other services on TemporalDataManager
        -  ResourceLocator().tdm.<service>(...)
      - and the same for all services on NonTemporalDataManager
        -  ResourceLocator().ntdm.<service>(...)

    """

    def __init__(self, tdm=None, ntdm=None):
        """
        ResourceLocator singleton constructor is called once:
          - ResourceLocator(): implicite initialization using __load_from_file__() initializing the standard tdm, ntdm
          - or ResourceLocator(...) explicite initialization of tdm and ntdm

        :param tdm: optional, default None: specific implementation for tdm
        :type tdm: class implementing TemporalDataManager services
        :param ntdm: optional, default None: specific implementation for tdm.
        :type ntdm: class implementing TemporalDataManageer services
        """
        if tdm is None and ntdm is None:
            # the implicit initialization
            self.__load_from_file__()
        else:
            # the explicit initialization (for instance for mocked resources)
            self.__tdm = tdm
            self.__ntdm = ntdm

        self.__logs = dict()

    def __load_from_file__(self):
        """
        Load the service implementations of tdm, and ntdm from the deployed configuration file:
          - each node could have a local configuration

        Note: this method is called once, inside the singleton constructor of ResourceLocator
        """
        self.__tdm = TemporalDataMgr()
        self.__ntdm = NonTemporalDataMgr()

    @classmethod
    def get_singleton(cls):
        """
        Getter on the singleton: is equivalent to ResourceLocator()

        Note: object-oriented people would prefer this class method

        Assumed: the singleton is already initialized or it will be with implicite initialization
        as described in class header.
        :param cls:
        :type cls:
        :return: the singleton
        :rtype: ResourceLocator
        """
        return ResourceLocator()

    def get_logger(self, log_name):
        """
        Gets the logger specified with logname: it is stocked and handled by the ResourceLocator.
        This service ought to be good for using Spark logs.

        Note beta version:
          - logs under /tmp/ResourceLocator.log
          - RotatingFileHandler limited to 1500000 bytes, with 1 backup
        :param log_name: short name giving the log context:
          - visible in each logged line
          - used as a key by the ResourceLocator
        :type log_name: str
        :return: the logger managed
        :rtype: logging.logger
        """
        stocked_log = self.__logs.get(log_name, None)

        if stocked_log is None:
            stocked_log = logging.getLogger(log_name)
            # Log format
            formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(funcName)s:%(message)s')

            # Create the handler to a file, append mode, 3 backups, max size = 500kbytes
            file_handler = RotatingFileHandler("/tmp/ResourceLocator_{}.log".format(log_name), 'a', 500000, 1)
            # file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)

            stocked_log.addHandler(file_handler)
            # default level is info
            stocked_log.setLevel(logging.INFO)
            self.__logs[log_name] = stocked_log

        return stocked_log

    def get_tdm(self):
        """
        Return the Temporal Data Manager instance
        :return:
        """
        return self.__tdm

    def get_ntdm(self):
        """
        Return the Non Temporal Data Manager instance
        :return:
        """
        return self.__ntdm

    tdm = property(get_tdm, None, None, "")
    ntdm = property(get_ntdm, None, None, "")
