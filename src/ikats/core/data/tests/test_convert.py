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
from logging import StreamHandler
import logging
import sys
import unittest

import numpy

import ikats.core.data.convert as tmod

REF_CONVERT_DATE = numpy.int64(100)
REF_DATE_INT = 100
REF_DATE_FLOAT = 100.1
REF_DATE_NINT = numpy.int64(100)
REF_DATE_NFLOAT = numpy.float64(100.1)

SAMPLE_UNFORMATED_TS_1 = [[100, 0.0],
                          [120, 1.0],
                          [140, 2.0],
                          [180, 1.0],
                          [200, -1.0]]

SAMPLE_UNFORMATED_TS_2 = [[100.0, 0.0],
                          [120.4, 1.0],
                          [140, 2.0],
                          [179.6, 1.0],
                          [200, -1.0]]

SAMPLE_UNFORMATED_TS_3 = numpy.array([[100.0, 0.0],
                                      [120.4, 1.0],
                                      [140, 2.0],
                                      [179.6, 1.0],
                                      [200, -1.0]])

SAMPLE_UNFORMATED_TS_4 = numpy.array([[100, 0.0],
                                      [120, 1.0],
                                      [140, 2.0],
                                      [180, 1.0],
                                      [200, -1.0]])

SAMPLE_TIMESTAMPS_1 = [100, 120, 140, 180, 200]
SAMPLE_TIMESTAMPS_2 = [100.1, 119.7, 140.0, 180.0, 200.0]

REF_CONVERTED = numpy.array([[numpy.int64(100), 0.0],
                             [numpy.int64(120), 1.0],
                             [numpy.int64(140), 2.0],
                             [numpy.int64(180), 1.0],
                             [numpy.int64(200), -1.0]])

REF_CONVERTED_FLOAT = numpy.array([[numpy.float64(100), 0.0],
                                   [numpy.float64(120.4), 1.0],
                                   [numpy.float64(140), 2.0],
                                   [numpy.float64(179.6), 1.0],
                                   [numpy.float64(200), -1.0]])

REF_TIMESTAMPS = numpy.array([numpy.int64(100),
                              numpy.int64(120),
                              numpy.int64(140),
                              numpy.int64(180),
                              numpy.int64(200)])

LOGGER = logging.getLogger(tmod.__name__)
LOGGER.setLevel(logging.DEBUG)
LOGGER.addHandler(StreamHandler(sys.stdout))


class TestConvert(unittest.TestCase):
    """
    Tests the timeseries converters
    """

    def test_timestamps_conversions(self):
        """
        Tests the basic conversion of timestamps
        """
        try:
            LOGGER.info("test_basic_timestamps_conversions")
            self.assertEqual(tmod.ms_to_timestamp(
                REF_DATE_INT), REF_CONVERT_DATE, "ms_to_timestamp with int")

            self.assertEqual(tmod.ms_to_timestamp(
                REF_DATE_FLOAT), REF_CONVERT_DATE, "ms_to_timestamp with float")

            self.assertEqual(tmod.ms_to_timestamp(
                REF_DATE_NINT), REF_CONVERT_DATE, "ms_to_timestamp with numpy.int64")

            self.assertEqual(tmod.ms_to_timestamp(
                REF_DATE_NFLOAT), REF_CONVERT_DATE, "ms_to_timestamp with numpy.float64")
        except Exception as err:
            LOGGER.error("Failed : test_basic_timestamps_conversions")
            raise err

    def test_ts_mono_to_np(self):
        """
        Tests the conversion of a timeseries mono valuated to numpy array
        """

        try:
            LOGGER.info("test_ts_mono_to_ndarray_resource_client")
            t_converted = tmod.ts_mono_to_np(SAMPLE_UNFORMATED_TS_1)
            self.check_numpy_array_equals(t_converted, REF_CONVERTED, "from Python array int:float")

            t_converted = tmod.ts_mono_to_np(SAMPLE_UNFORMATED_TS_2)
            self.check_numpy_array_equals(t_converted, REF_CONVERTED, "from Python array float:float")

            t_converted = tmod.ts_mono_to_np(SAMPLE_UNFORMATED_TS_3)
            self.check_numpy_array_equals(t_converted, REF_CONVERTED_FLOAT, "from numpy array float64:float64")

            t_converted = tmod.ts_mono_to_np(SAMPLE_UNFORMATED_TS_4)
            self.check_numpy_array_equals(t_converted, REF_CONVERTED, "from numpy array int64:float64")

            t_converted = tmod.ts_mono_to_np(REF_CONVERTED)
            self.check_numpy_array_equals(t_converted, REF_CONVERTED, "from already formatted numpy array")

        except Exception as err:
            LOGGER.error("Failed : test_ts_mono_to_ndarray_resource_client")
            LOGGER.error(err)
            LOGGER.exception(err)
            raise err

    def test_to_timestamps(self):
        """
        Tests the conversion of a timeseries to numpy array
        """

        try:
            LOGGER.info("test_to_timestamps_resource_client")

            dates_convert = tmod.to_timestamps_resource_client(SAMPLE_TIMESTAMPS_1)
            self.check_timestamps_equals(dates_convert, REF_TIMESTAMPS, "timestamps from int array")

            dates_convert = tmod.to_timestamps_resource_client(SAMPLE_TIMESTAMPS_2)
            self.check_timestamps_equals(dates_convert, REF_TIMESTAMPS, "timestamps from float array")

            dates_convert = tmod.to_timestamps_resource_client(SAMPLE_UNFORMATED_TS_4[:, 0])
            self.check_timestamps_equals(dates_convert, REF_TIMESTAMPS, "timestamps from numpy array int64")

            dates_convert = tmod.to_timestamps_resource_client(SAMPLE_UNFORMATED_TS_3[:, 0])
            self.check_timestamps_equals(dates_convert, REF_TIMESTAMPS, "timestamps from numpy array float64")

        except Exception as err:
            LOGGER.error("Failed : test_to_timestamps_resource_client")
            LOGGER.error(err)
            LOGGER.exception(err)
            raise err

    def check_numpy_array_equals(self, result_numpy_array, expected_numpy_array, test_info=""):
        """
        Checks both numpy arrays containing timeseries data are equal
        """
        shape_cond = None
        try:
            shape_cond = (result_numpy_array.shape[0] == expected_numpy_array.shape[0])
            if not shape_cond:
                self.fail("different shapes")

            index = 0
            while index < result_numpy_array.shape[0]:
                assert (result_numpy_array[index][0] == expected_numpy_array[index][0]), "equality of timestamps"
                assert (result_numpy_array[index][1] == expected_numpy_array[index][1]), "equality of values"
                index += 1

        except Exception as err:
            LOGGER.debug(err)
            LOGGER.debug("Unexpected check_numpy_array_equals failure: %s ", test_info)
            if shape_cond is not None:
                LOGGER.debug("- different lengths: res=%s REF=%s", result_numpy_array.shape,
                             expected_numpy_array.shape)
            LOGGER.debug("- result           : %s", str(result_numpy_array))
            LOGGER.debug("- expected by test : %s", str(expected_numpy_array))
            raise err

    def check_timestamps_equals(self, result_numpy_array, expected_numpy_array, test_info=""):
        """
        Method that checks the timestamps are equal between result and expected numpy arrays
        :param result_numpy_array:
        :param expected_numpy_array:
        :param test_info:
        :return:
        """
        shape_cond = None
        try:
            shape_cond = (result_numpy_array.shape[0] == expected_numpy_array.shape[0])
            if not shape_cond:
                self.fail("different shapes")

            index = 0
            while index < result_numpy_array.shape[0]:
                if result_numpy_array[index] != expected_numpy_array[index]:
                    self.fail("equality of timestamps")
                index += 1

        except Exception as err:
            LOGGER.debug(err)
            LOGGER.debug("Unexpected check_timestamps_equals failure: %s ", test_info)
            if shape_cond is not None:
                LOGGER.debug("- different lengths: res=%s REF=%s", result_numpy_array.shape, expected_numpy_array.shape)
            LOGGER.debug("- result           : %s", str(result_numpy_array))
            LOGGER.debug("- expected by test : %s", str(expected_numpy_array))
            raise err


if __name__ == "__main__":
    unittest.main()
