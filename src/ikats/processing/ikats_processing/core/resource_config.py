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

from ikats.core.resource.client import NonTemporalDataMgr
from ikats.core.resource.client import TemporalDataMgr

LOGGER = logging.getLogger(__name__)


class ResourceClientSingleton(object):
    """
    Manage TDM Singleton
    """
    __singleton = None

    @classmethod
    def has_singleton(cls):
        """
        returns True is a singleton already exist
        """
        return ResourceClientSingleton.__singleton is not None

    @classmethod
    def singleton_init(cls, host, port):
        """

        :param cls: ResourceClientSingleton class
        :type cls: ResourceClientSingleton
        :param host: configured host on the singleton
        :type host: string
        :param port: configured port on the singleton
        :type port: int
        """
        if cls.__singleton is None:
            LOGGER.info("Initializing ResourceClientSingleton [ host=%s, port=%s]", host, port)
            cls.__singleton = ResourceClientSingleton(host, port)
        else:
            LOGGER.warning("Ignored Initialization: ResourceClientSingleton [ host=%s, port=%s]", host, port)
            LOGGER.warning("Already Initialized: ResourceClientSingleton [ host=%s, port=%s]",
                           cls.__singleton.host, cls.__singleton.port)

    def __str__(self):
        return "ResourceClientSingleton(host=%s, port=%s)" % (self.host, self.port)

    @classmethod
    def get_singleton(cls):
        """
        Returns the singleton if it exists
        :return:
        """
        assert cls.__singleton, \
            "Unconfigured singleton: it is required to run ResourceClientSingleton::singleton_init before."
        return cls.__singleton

    def __init__(self, host, port):
        """
        Called once by singleton_init !
        :param host:
        :type host:
        :param port:
        :type port:
        """
        self.host = host
        self.port = port

    def get_temporal_manager(self):
        """
        Gets the temporal manager from the singleton configuration
        Note: new instance is created each time this method is called
        """
        return TemporalDataMgr(self.host, self.port)

    def get_non_temporal_manager(self):
        """
        Gets the non temporal manager from the singleton configuration
        Note: new instance is created each time this method is called
        """
        return NonTemporalDataMgr(self.host, self.port)
