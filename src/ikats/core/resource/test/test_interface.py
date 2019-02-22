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
import sys
from unittest import TestCase

import numpy as np

from ikats.core.library.singleton import Singleton
from ikats.core.resource.client.non_temporal_data_mgr import NonTemporalDataMgr
from ikats.core.resource.client.temporal_data_mgr import TemporalDataMgr
from ikats.core.resource.interface import ResourceLocator

TS_SAMPLES = {'tsuid1': np.array([[1000.1, 5.5], [1010.5, 150], [1020, 100.7], [1030, 200]]),
              'tsuid2': np.array([[1000.1, 15.5], [1010.5, 1150], [1020, 1.3], [1030, 30]]),
              'tsuid3': np.array([[1000.1, -5.5], [1010.5, -150], [1020, 100.7], [1030, -200]])}


class TdmForTest(object):
    """
    A partial and specific implementation of tdm for the test
    """

    def __init__(self, *args, **kwargs):
        pass

    def get_ts(self, tsuid_list, sd=None, ed=None):
        """
        Get the content of a timeseries
        :param tsuid_list:
        :param sd:
        :param ed:
        :return:
        """
        res = []
        for tsuid in tsuid_list:
            ts = TS_SAMPLES.get(tsuid, None)
            if ts is None:
                raise Exception("Not found {}".format(tsuid))
            res.append(ts)
        return res


class TestResourceLocator(TestCase):
    """
    Tests the ResourceLocator class.
    """
    # tu logger
    log = logging.getLogger("TestResourceLocator")

    @classmethod
    def setUpClass(cls):
        cls.log.setLevel(logging.INFO)
        cls.log.addHandler(logging.StreamHandler(sys.stdout))

        if ResourceLocator in Singleton._instances:
            # remember to delete tested singleton !!!
            # => quite specific to unit-tests
            del Singleton._instances[ResourceLocator]

    def test_explicite_init(self):
        """
        Tests explicite initialization of ResourceLocator
        """

        # Not done here: see also specific TU on the Singleton metaclass:
        #
        #  ikats.core.library.tests.test_singleton

        tdm = TdmForTest()
        ResourceLocator(tdm=tdm, ntdm=None)

        my_ts = ResourceLocator().tdm.get_ts(['tsuid1'])

        self.assertListEqual(my_ts, [TS_SAMPLES['tsuid1']])
        self.log.info(type(ResourceLocator()))
        self.log.info(type(ResourceLocator().tdm))

        # remember to delete tested singleton !
        # => quite specific to unit-tests
        del Singleton._instances[ResourceLocator]

    def test_implicite_init(self):
        """
        Tests implicite initialization of ResourceLocator
        """
        ResourceLocator()

        self.log.info(ResourceLocator().tdm)
        self.log.info(ResourceLocator().ntdm)

        self.assertTrue(isinstance(ResourceLocator().tdm, TemporalDataMgr))
        self.assertTrue(isinstance(ResourceLocator().ntdm, NonTemporalDataMgr))

        # remember to delete tested singleton !!!
        # => quite specific to unit-tests
        del Singleton._instances[ResourceLocator]

    @classmethod
    def tearDownClass(cls):
        if ResourceLocator in Singleton._instances:
            # remember to delete tested singleton !!!
            # => quite specific to unit-tests
            del Singleton._instances[ResourceLocator]
