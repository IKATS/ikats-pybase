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
import os
from unittest import TestCase

import numpy as np
import requests

from ikats.core.config.ConfigReader import ConfigReader
from ikats.core.resource.opentsdb.HttpClient import HttpClient

LOGGER = HttpClient.LOGGER
LOGGER.setLevel(logging.DEBUG)
FORMATTER = logging.Formatter('%(asctime)s:%(levelname)s:%(funcName)s:%(message)s')
# Create another handler that will redirect log entries to STDOUT
STREAM_HANDLER = logging.StreamHandler()
STREAM_HANDLER.setLevel(logging.DEBUG)
STREAM_HANDLER.setFormatter(FORMATTER)
LOGGER.addHandler(STREAM_HANDLER)

# Configuration file
CONFIG_READER = ConfigReader()


def delete_ts(metric, **tags):
    """
    Delete the TS from OpenTSDB manually
    """

    tag_string = ','.join(['%s=%s' % (k, v) for k, v in tags.items()])

    # Address of the real server to use for tests
    test_opentsdb_host = CONFIG_READER.get('cluster', 'opentsdb.write.ip')
    test_opentsdb_port = int(CONFIG_READER.get('cluster', 'opentsdb.write.port'))
    direct_root_url = 'http://%s:%s//api/query?start=0&m=sum:%s{%s}&ms=true&delete=true' % (
        test_opentsdb_host, test_opentsdb_port, metric, tag_string)

    results = requests.post(direct_root_url)
    if results.status_code != 200:
        raise SystemError("Can't delete TS")


class TestHttpClient(TestCase):
    """
    This class tests the HTTP client to connect to OpenTSDB
    """

    def test_nominal(self):
        """
        Tests the import of TS by using telnet
        """

        size = 1000000
        values = np.linspace(0, 100, size)
        data = np.column_stack((np.arange(1000000000, 1000000000 + 1000 * len(values), 1000), values))

        metric = "toDelete"
        tags = {"t1": "42"}

        try:
            client = HttpClient()
            results = client.send_http(metric, tags, data_points=data, max_points_per_query=500000)
            LOGGER.info("Import speed : %.3f points/s", results.speed())
            LOGGER.info("Errors %s", results.errors)
            LOGGER.info("Failed %s", results.failed)
            LOGGER.info("Timeouts %s", results.timeouts)

            self.assertEqual(results.success, size, "Number of imported points is not the same")

        except Exception as exception:
            self.fail(exception)
        finally:
            # Cleanup TS database
            delete_ts(metric, **tags)

    def test_nominal_multi_threads(self):
        """
        Tests the import of TS by using telnet
        """

        size = 11000000
        values = np.linspace(0, 100, size)
        data = np.column_stack((np.arange(1000000000, 1000000000 + 1000 * len(values), 1000), values))

        metric = "toDelete"
        tags = {"t1": "42"}

        try:
            # Limit the parallelization to the half number of CPU on testing target (to not encounter freezing issues)
            client = HttpClient(threads_count=max(2, int(os.cpu_count() / 2)))
            results = client.send_http(metric, tags, data_points=data, max_points_per_query=500000)
            LOGGER.info("Import speed : %.3f points/s", results.speed())
            LOGGER.info("Errors %s", results.errors)
            LOGGER.info("failed %s", results.failed)
            LOGGER.info("timeouts %s", results.timeouts)

            self.assertEqual(results.success, size, "Number of imported points is not the same")

        finally:
            # Cleanup TS database
            delete_ts(metric, **tags)
