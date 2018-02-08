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
import logging
import sys
from unittest.case import TestCase

import numpy as np

from ikats.core.library.spark import ScManager
from ikats.core.resource.interface import ResourceLocator
from ikats.core.resource.test.test_interface import TdmForTest


def tested_spark_algo():
    """
    This is a working example of spark algo:
      - no assumption about the tdm services : they are provided by the ResourceLocator singleton
      - the ScManager.only_shared_tdm() detects if the tdm is mocked in unit-test
        - if mocked in unit-test: the tdm is a defined param of function algo_map:
          it is automatically broadcasted.
        - else: real mode: tdm is not defined at the beginning of algo_map, so that it is finally
          initialized by ResourceLocator().tdm
    """
    spark_context = ScManager.get()

    #
    def algo_map(tsuid, tdm=ScManager.only_shared_tdm()):
        """
        tdm param is defined only when it is mocked: its value is broadcasted
        :param tsuid:
        :param tdm:
        :return:
        """

        if tdm is None:
            tdm = ResourceLocator().tdm

        return tsuid + "_algo", tdm.get_ts([tsuid])

    local_ts = ResourceLocator().tdm.get_ts(['tsuid1'])

    rdd = spark_context.parallelize(['tsuid2', 'tsuid3'])

    rdd = rdd.map(algo_map)

    res = rdd.collect()

    res.append(local_ts)
    return res


class TestScManager(TestCase):
    """
    Tests the ikats spark context manager: class ScManager used in unit-test context
    """

    @classmethod
    def setUpClass(cls):
        """
        Setup the logger
        """
        ScManager.log.setLevel(logging.INFO)
        ScManager.log.addHandler(logging.StreamHandler(sys.stdout))

    def test_get_tu_spark_context(self):
        """
        Tests the specific mode get_tu_spark_context():
         => tests that the ResourceLocator is providing the mock TdmForTest to the tasks
        """
        ScManager.stop_all()
        tdm = TdmForTest(port=80, host='dev')
        ResourceLocator(tdm=tdm, ntdm=None)

        local_ts = ResourceLocator().tdm.get_ts(['tsuid1'])

        spark_context = ScManager.get_tu_spark_context()

        sc2 = ScManager.get()

        self.assertEqual(spark_context, sc2, "TU context should be retrieved")

        rdd = spark_context.parallelize(['tsuid1', 'tsuid2', 'tsuid3'])

        rdd = rdd.map(lambda data_points: (data_points, ResourceLocator(tdm=tdm, ntdm=None).tdm.get_ts([data_points])))

        rdd = rdd.map(lambda data_points: (data_points[0] + "_two", ResourceLocator().tdm.get_ts([data_points[0]])))
        res = rdd.collect()

        collected_tsuid1 = [x[1] for x in res if x[0] == 'tsuid1_two'][0]

        self.assertTrue(np.equal(local_ts, collected_tsuid1).all())

        ScManager.stop_all()
