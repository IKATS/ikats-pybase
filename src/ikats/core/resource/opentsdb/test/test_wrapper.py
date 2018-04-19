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
import multiprocessing
from unittest import TestCase

import httpretty
import numpy as np

from ikats.core.resource.api import IkatsApi
from ikats.core.resource.client.temporal_data_mgr import DTYPE, TemporalDataMgr
from ikats.core.resource.opentsdb.HttpClient import HttpClient
from ikats.core.resource.opentsdb.wrapper import Wrapper

USE_REAL_SERVER = False


def log_to_stdout(logger_to_use):
    """
    Allow to print some loggers to stdout
    :param logger_to_use: the logger object to redirect to stdout
    """

    logger_to_use.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(funcName)s:%(message)s')
    # Create another handler that will redirect log entries to STDOUT
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)
    stream_handler.setFormatter(formatter)
    logger_to_use.addHandler(stream_handler)


# Prints everything from these loggers
log_to_stdout(Wrapper.logger)
log_to_stdout(HttpClient.LOGGER)

META_DATA_LIST = {}
FID_DATABASE = {}

# Disable real connection depending on the usage of real or fake server
httpretty.HTTPretty.allow_net_connect = USE_REAL_SERVER

ROOT_URL = 'TemporalDataManagerWebApp/webapi'


class TestWrapperOpenTSDB(TestCase):
    """
    Tests the wrapper methods to OpenTSDB
    """

    def setUp(self):
        META_DATA_LIST.clear()
        FID_DATABASE.clear()

    def test_nominal_upload(self):
        """
        Tests the import of TS by using telnet
        """

        tdm = TemporalDataMgr()

        data_to_send = [
            [1000000000000, 42],
            [1000000000001, 43],
            [1000000000002, 44],
            [1000000000003, 45],
            [1000000000004, 46],
            [1000000000005, 47],
            [1000000000006, 48],
        ]

        fid = "FID_TEST"

        results = Wrapper.import_ts(data=data_to_send, fid=fid)
        tsuid = results['tsuid']

        # Check content are equals
        data_points = tdm.get_ts([tsuid])
        self.assertListEqual(data_points[0].tolist(), data_to_send)

        # Delete the TS to cleanup the database
        IkatsApi.ts.delete(tsuid, no_exception=True)

    def test_multi_part_upload(self):
        """
        Tests the import of TS with multipart
        """

        tdm = TemporalDataMgr()
        global_fid = "FID_test_multi_part_upload"

        global_data = [
            [1000000000000, 42],
            [1000000000001, 43],
            [1000000000002, 44],
            [1000000000003, 45],
            [1000000000004, 46],
            [1000000000005, 47],
            [1000000000006, 48],
        ]

        def thr_upload(data_to_send, fid):
            """
            Threaded action
            :param data_to_send:
            :param fid:
            :return:
            """
            Wrapper.import_ts(data=data_to_send, fid=fid, generate_metadata=False)

        # Firstly creating ref in database
        tsuid = IkatsApi.ts.create_ref(fid=global_fid)

        # First thread handling a part of the data
        thr1 = multiprocessing.Process(
            target=thr_upload,
            args=(global_data[0:], global_fid))
        thr1.start()

        # Second thread handling another part of the data
        thr2 = multiprocessing.Process(
            target=thr_upload,
            args=(global_data[4:], global_fid,))
        thr2.start()

        try:
            # Update metadata manually because of the multiprocessing
            tdm.update_meta_data(tsuid, 'ikats_start_date', global_data[0][0], data_type=DTYPE.date, force_create=True)
            tdm.update_meta_data(tsuid, 'ikats_end_date', global_data[-1][0], data_type=DTYPE.date, force_create=True)
            tdm.update_meta_data(tsuid, 'qual_nb_points', len(global_data), data_type=DTYPE.date, force_create=True)

            # Cleanup
            thr1.join()
            thr2.join()

            # Checks
            data_points = tdm.get_ts([tsuid])
            self.assertListEqual(data_points[0].tolist(), global_data)
        finally:
            # Delete the TS to cleanup the database
            if tsuid:
                IkatsApi.ts.delete(tsuid, no_exception=True)

    def test_create_tsuid(self):
        """
        Tests the creation of a timeseries reference in opentsdb (tsuid)
        """
        fid = 'Timeseries_for_testing_tsuid_creation'

        data_write = np.array([[1449759331500, 125.0],
                               [1449759332000, 661.27],
                               [1449759332500, 1064.45],
                               [1449759333000, 1467.63]])

        tsuid = None
        try:
            # creation of a timeseries reference in temporal database
            tsuid = IkatsApi.ts.create_ref(fid=fid)

            # Write data to timeseries defined by fid
            IkatsApi.ts.create(fid=fid, data=data_write)

            # Because of the short size of data, even if the import to OpenTSDB is made synchronously, it seems it
            # answers before the points are effectively available for use is some cases (depending on platform)
            data_read = IkatsApi.ts.read([tsuid])[0]
            retry_count = 0
            while len(data_read) == 0:
                retry_count += 1
                Wrapper.logger.error("Data not available. Retrying ! (try %s)", retry_count)
                data_read = IkatsApi.ts.read([tsuid])[0]

            # check data read by tsuid is the same as data written by fid
            self.assertTrue(np.allclose(
                np.array(data_write, dtype=np.float64),
                np.array(data_read, dtype=np.float64),
                atol=1e-3))

        finally:
            # cleaning data
            if tsuid:
                IkatsApi.ts.delete(tsuid, no_exception=True)
