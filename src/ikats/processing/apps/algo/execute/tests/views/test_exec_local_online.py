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
"""
import logging
import unittest

import numpy
from django.test import Client
from django.test import TestCase as DjTestCase

LOGGER = logging.getLogger(__name__)


class TestExecLocalOnline(unittest.TestCase):
    def get_ts_by_tsuid_mock_lo(self, tsuid, sd=None, ed=None):
        """
        Mock for ikats.core.resource.client.TemporalDataMgr.get_ts_by_tsuid
        :param tsuid:
        :type tsuid:
        :param sd:
        :type sd:
        :param ed:
        :type ed:
        """

        LOGGER.info("TU MOCK: get_ts_by_tsuid_mock_lo: [tsuid=%s] [sd=%s] [ed=%s]", tsuid, sd, ed)

        stub_arr = numpy.array([[1449755790000, 5],
                                [1449755791000, 6],
                                [1449755792000, 8],
                                [1449755793000, 5],
                                [1449755794000, 2],
                                [1449755795000, 6],
                                [1449755796000, 3],
                                [1449755797000, 2],
                                [1449755798000, 5],
                                [1449755799000, 8]])

        return stub_arr

    def import_ts_data_mock_lo(self, metric, data, fid, tags=None, data_set=None):
        """
        Mock for ikats.core.resource.client.TemporalDataMgr.import_ts_data
        :param metric:
        :type metric:
        :param data:
        :type data:
        :param fid:
        :type fid:
        :param tags:
        :type tags:
        :param data_set:
        :type data_set:
        """
        LOGGER.info("TU MOCK: import_ts_data_mock_lo: metric=%s fid=%s tags=%s", metric, fid, str(tags))
        LOGGER.info("TU MOCK: import_ts_data_mock_lo: data=%s", data)
        return {'status': True,
                'tsuid': "mockTsuidImport",
                'numberOfSuccess': 1}

    def get_func_id_from_tsuid_mock_lo(self, tsuid):
        """
        Mock for ikats.core.resource.client.TemporalDataMgr.get_func_id_from_tsuid
        :param tsuid:
        :type tsuid:
        """
        LOGGER.info("TU MOCK: get_func_id_from_tsuid_mock_lo: tsuid=%s", tsuid)
        return "stub_funcId_%s" % tsuid


class TestExecLocalOnlineWithCatalogue(DjTestCase):
    def test_ws_run_algo_ok(self):
        client_test = Client()

        response = client_test.get('/ikats/algo/execute/runalgo/',
                                   {
                                       "output_metric": "WS1",
                                       "path": "apps.algo.execute.tests.util.online",
                                       "function": "replace_missing_values",
                                       "tsref_input": "stubtsuid_ref"
                                   })

        LOGGER.info(response.status_code)
        LOGGER.info(response.content)
