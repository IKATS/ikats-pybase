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
from ikats.core.library.spark import *
from unittest import TestCase
import logging
from ikats.core.resource.api import IkatsApi

LOGGER = logging.getLogger()


def gen_ts(ts_id):
    """
    Generate a TS in database used for test bench where id is defined. For now, just
    return portfolio tsuid_list.

    :param ts_id: Identifier of the TS to generate (see content below for the structure)
    :type ts_id: int

    :return: list of tsuid
    :rtype: list
    """

    ds_name = "Portfolio"

    if ts_id == 1:
        # Read Portfolio, and return the TS_list

        return IkatsApi.ds.read(ds_name=ds_name)['ts_list']
    else:
        raise NotImplementedError


class TestSpark(TestCase):
    """
    Test of the ikats.core.library.spark module
    """

    def test_SSessionManager_init(self):
        """
        Tests SSessionManager init
        """
        # Init Spark session with SSessionManager wrapper
        spark_session = SSessionManager.get()

        # Check spark_session is not None
        self.assertIsNotNone(spark_session, msg="`spark_session is None.")

        # Check spark_context is not None
        self.assertIsNotNone(SSessionManager.get_context(), msg="`spark_context is None.")

    def test_SparkUtils_get_chunk_def(self):
        """
        Test case for method SparkUtils get chunk
        """

        # generate TS
        ts_list = gen_ts(1)

        # Get the first ts
        tsuid = ts_list[0]

        # Get meta data of TS
        md = IkatsApi.md.read(ts_list)[tsuid]
        sd = int(md['ikats_start_date'])
        ed = int(md['ikats_end_date'])
        period = int(float(md['qual_ref_period']))

        # Get chunks
        result = SparkUtils.get_chunks_def(tsuid=tsuid, sd=sd, ed=ed, period=period, nb_points_by_chunk=4)

        # Check values
        # --------------

        # Check nb result (should be one, because size of TS << SSessionManager.CHUNK_SIZE)
        msg = "SparkUtils.get_chunks_def, get {} chunks, expected 1".format(len(result))
        self.assertEqual(12, len(result), msg=msg)

        # get the inner of the list
        first_chunk = result[0]
        last_chunk = result[11]

        # Check first value (tsuid)
        msg = "SparkUtils.get_chunks_def, first value (tsuid) is {}, expected {}".format(first_chunk[0], tsuid)
        self.assertEqual(tsuid, first_chunk[0], msg=msg)

        # Check second value (chunk index, 0: one single chunk !)
        msg = "SparkUtils.get_chunks_def, second value (chunk_index) is {}, expected 0".format(first_chunk[1])
        self.assertEqual(0, first_chunk[1], msg=msg)

        # Check third value (start date)
        msg = "SparkUtils.get_chunks_def, third value (start date) is {}, expected {}".format(
            str(first_chunk[2]), md['ikats_start_date'])
        self.assertEqual(md['ikats_start_date'], str(first_chunk[2]), msg=msg)

        # Check 4'th value (end date - 1)
        msg = "SparkUtils.get_chunks_def, 4'th value (end date) is {}, expected {}".format(
            str(last_chunk[3] - 1), md['ikats_end_date'])
        self.assertEqual(md['ikats_end_date'], str(last_chunk[3]), msg=msg)

    def test_SSessionManager_check_spark_usage(self):
        """
        Test case for method SsessionManager check_spark_usage
        """
        # retrieve ts list
        ts_list = gen_ts(1)

        # Get meta data of ts
        md = IkatsApi.md.read(ts_list)

        use_spark_true = SparkUtils.check_spark_usage(tsuid_list=ts_list, meta_list=md, nb_ts_criteria=10,
                                                      nb_points_by_chunk=5)
        self.assertEqual(use_spark_true, True)

        use_spark_false = SparkUtils.check_spark_usage(tsuid_list=ts_list, meta_list=md, nb_ts_criteria=100,
                                                       nb_points_by_chunk=50)
        self.assertEqual(use_spark_false, False)

    def test_SSessionManager_get_ts_by_chunks_as_df(self):
        """
        Test case for method SsessionManager get_ts_by_chunks_as_df
        """
        # generate TS
        ts_list = gen_ts(1)

        # Get the first ts
        tsuid = ts_list[0]

        # Get the TS data
        data = IkatsApi.ts.read([tsuid])[0].tolist()
        # List, [[time1, value1], ...]

        # Get meta data of first TS
        md = IkatsApi.md.read(ts_list)[tsuid]
        sd = int(md['ikats_start_date'])
        ed = int(md['ikats_end_date'])
        period = int(float(md['qual_ref_period']))

        # Import data into dataframe (["Timestamp", "Value"])

        df, size = SSessionManager.get_ts_by_chunks_as_df(tsuid=tsuid, sd=sd, ed=ed, period=period,
                                                          nb_points_by_chunk=3)

        # Test values
        # ---------------
        # Collect values of `df`
        df_as_list = df.select('Timestamp', 'Value').rdd.map(list).collect()
        # list [[time1, value1], ...]

        msg = "SSessionManager.get_ts_by_chunks_as_df, result is not correct."
        self.assertEqual(data, df_as_list, msg=msg)
