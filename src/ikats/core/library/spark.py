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
import numpy as np

from ikats.core.library.exception import IkatsException
from ikats.core.resource.api import IkatsApi
from ikats.core.resource.client import TemporalDataMgr
from ikats.core.resource.client.non_temporal_data_mgr import NonTemporalDataMgr
from ikats.core.resource.interface import ResourceLocator

from pyspark import SparkContext
from pyspark.sql import SparkSession
from pyspark.accumulators import AccumulatorParam
from pyspark.conf import SparkConf

from ikats.core.config.ConfigReader import ConfigReader


class SSessionManager(object):
    """
    Spark Session manager
    Used to manage spark session creation and closure.
    Note that a Spark Session includes a Spark Context.
    Introduced for usage of spark DataFrame.
    """

    log = logging.getLogger("SSessionManager")

    # Number of current algorithms needing the spark context
    ikats_users = 0

    # Spark session: for DataFrame creation
    spark_session = None

    @staticmethod
    def get_ts_by_chunks_as_df(tsuid, sd, ed, period, nb_points_by_chunk=50000, overlap=None):
        """
        Read current TS (`tsuid`), chunked with spark.
        For now, it's the optimal way to read TS with Spark DataFrame.

        Action performed:
            * get chunks intervals (id, start, end) (`get_chunks_def`)
            * read current TS (`tsuid`) chunked with spark (RDD)
            * transform resulting rdd into Spark DataFrame (DF)

        :param tsuid: TS to get values from
        :type tsuid: str

        :param sd: The meta data corresponding to the ts start date
        :type sd: int

        :param ed: The meta data corresponding to the ts end date
        :type ed: int

        :param period: The meta data corresponding to the ts period
        :type period: int

        :param nb_points_by_chunk: size of chunks in number of points (assuming timeserie is periodic and without holes)
        :type nb_points_by_chunk: int

        :return: DataFrame containing all data from current TS (["Index", "Timestamp", "Value"])
        :rtype: pyspark.sql.dataframe.DataFrame
        """

        # Review#495: (FTA) what is overlap ?


        # retrieve spark context
        sc = SSessionManager.get_context()

        # 1/ Get the chunks, and read TS chunked
        # ----------------------------------------------------------------------
        # Get the chunks, and distribute them with Spark
        # Format: [(tsuid, chunk_id, start_date, end_date), ...]
        chunks = SparkUtils.get_chunks_def(tsuid=tsuid, sd=sd, ed=ed, period=period,
                                           nb_points_by_chunk=nb_points_by_chunk, overlap=overlap)

        rdd_ts_info = sc.parallelize(chunks, len(chunks))

        # DESCRIPTION : Get the points within chunk range and suppress empty chunks
        # INPUT  : [(tsuid, chunk_id, start_date, end_date), ...]
        # OUTPUT : The dataset flat [[time1, value1], ...]
        rdd_chunk_data = rdd_ts_info \
            .flatMap(lambda x: [(x[1], y[0], y[1]) for y in IkatsApi.ts.read(tsuid_list=x[0],
                                                                             sd=int(x[2]),
                                                                             ed=int(x[3]))[0].tolist()])
        # Note that result has to be list (if np.array, difficult to convert into Spark DF)

        # 2/ Put result into a Spark DataFrame
        # ----------------------------------------------------------------------
        # Init a DataFrame for one single ts_data
        # DESCRIPTION : Get the points within chunk range and suppress empty chunks
        # INPUT  : [[time1, value1], ...]
        # OUTPUT : DataFrame containing dataset (columns [Index, Timestamp, Value])
        df = rdd_chunk_data.toDF(["Index", "Timestamp", "Value"])

        return df, len(chunks)

    @staticmethod
    def create():
        """
        Create a new spark session from an existing spark context.
        :param spark_context: A SparkContext (ex: ScManager.spark_context)
        :type spark_context: SparkContext

        :return: The spark Session
        :rtype: SparkSession
        """

        if not SSessionManager.spark_session:
            # Init a Spark Session for using spark Dataframes:
            master = ConfigReader().get('cluster', 'spark.url')
            SSessionManager.spark_session = SparkSession.builder \
                .master(master) \
                .appName('Ikats') \
                .getOrCreate()

        return SSessionManager.spark_session

    @staticmethod
    def get():
        """
        Get a spark session if exists or create a new one.

        :return: The spark session
        :rtype: SparkSession
        """
        SSessionManager.ikats_users += 1

        # Get or Create is yet implemented in `create` method.
        if not SSessionManager.spark_session:
            SSessionManager.create()

        return SSessionManager.spark_session

    @staticmethod
    def get_context():
        """
        Get a spark context from a spark session if exists or create a new one.

        :return: The spark context
        :rtype: SparkContext
        """

        if not SSessionManager.spark_session:
            SSessionManager.create()

        return SSessionManager.spark_session.sparkContext

    @staticmethod
    def stop():
        """
        Request to stop session.
        The Spark session will continue to run if other algo needs it
        :return: True if the spark session was actually stopped
        :rtype: bool
        """
        actually_stopped = False
        if SSessionManager.ikats_users > 0:
            SSessionManager.ikats_users -= 1
            SSessionManager.log.info("SSessionManager: stopping SparkSession: users count decreased to %s",
                                     SSessionManager.ikats_users)
        else:
            SSessionManager.log.warning("SSessionManager: stopping SparkSession: users count is already zero")

        if SSessionManager.ikats_users == 0:
            if SSessionManager.spark_session is None:
                ScManager.log.error("SSessionManager: stopping SparkSession: unexpected error: undefined SparkSession")
                raise SystemError('Trying to close an already closed Spark session')
            SSessionManager.spark_session.stop()
            SSessionManager.log.info("SSessionManager: stopping SparkSession without user left: SSessionManager.sc is "
                                     "stopped and set to None.")

            actually_stopped = True
            SSessionManager.spark_session = None

        return actually_stopped

    @staticmethod
    def stop_all():
        """
        Forces the stop of the defined SparkSession: SSessionManager.sc
          - sets  SSessionManager.ikats_users to 0
          - calls SSessionManager.sc.stop()
          - sets SSessionManager.sc to None

        Beware: do not use this method in operational mode: method to be used in TU only.
        """
        SSessionManager.ikats_users = 0
        if SSessionManager.spark_session is not None:
            SSessionManager.spark_session.stop()
            SSessionManager.spark_session = None


class ScManager(object):
    """
    Spark Context manager
    Used to manage the spark context creation and closure

    NB : DEPRECATED since we use SparkSession instead
    """

    log = logging.getLogger("ScManager")
    log.warning("ScManager is deprecated, use SparkSession instead")

    # Review#495: you should not include "TEST" instrumentation in the prod code
    APPNAME_UNIT_TEST_IKATS = "UNIT_TEST_IKATS"

    # Spark context
    spark_context = None

    # Broadcast variables: shared content
    sc_tdm = None
    sc_ntdm = None

    @staticmethod
    def create():
        """
        Get or create a spark context from a spark session
        :return: The spark Context
        :rtype: SparkContext
        """
        # Review#495: There is a getOrCreate function, why not using it ?
        return SSessionManager.get_context()

    @staticmethod
    def get():
        """
        Get a spark context from current session if exists or create a new one
        :return: The spark Context
        :rtype: SparkContext
        """
        # Review#495: There is a getOrCreate function, why not using it ?
        return SSessionManager.get_context()

    @staticmethod
    def stop():
        """
        Request to stop session (and then context)
        The Spark session will continue to run if other algo needs it
        :return: True if the spark session was actually stopped
        :rtype: bool
        """
        return SSessionManager.stop()

    @staticmethod
    def get_ts_by_chunks(tsuid, sd, ed, period, nb_points_by_chunk=50000):
        """
        Read current TS (`tsuid`), chunked with spark.

        Action performed:
            * get chunks intervals (id, start, end) (`get_chunks_def`)
            * read current TS (`tsuid`) chunked with spark (RDD)

        :param tsuid: TS to get values from
        :type tsuid: str

        :param md: The meta data corresponding to the current tsuid
        :type md: dict

        :return: RDD containing all data from current TS
        :rtype: pyspark.rdd.RDD
        """

        # Init or retrieve spark context
        sc = ScManager.get()

        # 1/ Get the chunks
        # ----------------------------------------------------------------------
        # Get the chunks, and distribute them with Spark
        # Format: [(tsuid, chunk_id, start_date, end_date), ...]
        chunks = ScManager.get_chunks(tsuid=tsuid, sd=sd, ed=ed, period=period,
                                      nb_points_by_chunk=nb_points_by_chunk)

        rdd_ts_info = sc.parallelize(chunks, len(chunks))

        # 2/ Read TS chunked
        # DESCRIPTION : Get the points within chunk range and suppress empty chunks
        # INPUT  : [(tsuid, chunk_id, start_date, end_date), ...]
        # OUTPUT : The dataset flat [[time1, value1], ...]
        rdd_chunk_data = rdd_ts_info \
            .map(lambda x: IkatsApi.ts.read(tsuid_list=tsuid,
                                            sd=int(x[2]),
                                            ed=int(x[3])))

        return rdd_chunk_data

    @staticmethod
    def only_shared_tdm():
        """
        This function filters the defined TDM in ResourceLocator
          - returns TDM if it can be shared between driver and executors
          - returns None otherwise

        The aim is to share the mocked providers in the context of spark unit-test.

        """
        tdm_filtered = ResourceLocator().tdm
        if tdm_filtered is None:
            return None

        elif ScManager.spark_context and ScManager.spark_context.getLocalProperty(
                'spark.app.name') == ScManager.APPNAME_UNIT_TEST_IKATS:
            if type(tdm_filtered) in [TemporalDataMgr, NonTemporalDataMgr]:
                # Even in unittest context: never broadcast exact types like TemporalDataMgr or NonTemporalDataMgr
                # => in that case the implicit initialization ResourceLocator() on each executor will be processed,
                #
                # None returned: resource is not shared, and will be re-evaluated locally
                tdm_filtered = None
                # else:
                # ... tdm_filtered is assumed to be mocked when not TemporalDataMgr or NonTemporalDataMgr
                # In unittest context: we assume that these services are mocked
                # => in that case: we can broadcast the mocked tdm_filtered (read-only)
        else:
            # In operational context: never share the resource tdm_filtered
            #   initializations may be different between
            #     - driver
            #     - executor 1
            #     - executor 2 ...
            return None

        if tdm_filtered is None:
            ScManager.log.info("tdm: real mode activated: no broadcast")
        else:
            name = tdm_filtered.__class__.__name__
            ScManager.log.info("tdm: mocked mode in unit-test: broadcast possible with %s", name)
        return tdm_filtered

    @staticmethod
    def get_tu_spark_context():
        """
        Gets the spark context in specific context of Unit-Test.

        :return: The spark Context
        :rtype: SparkContext
        """
        # if stop_before:
        #     ScManager.__stop_all()
        ScManager.stop_all()
        if ScManager.spark_context is None:
            ScManager.create_tu_spark_context(ScManager.APPNAME_UNIT_TEST_IKATS)
        else:
            raise Exception("Unexpected case: get_tu_spark_context() :" +
                            " a spark_context already exists ! {}".format(str(ScManager.spark_context)))
        return ScManager.spark_context

    @staticmethod
    def create_tu_spark_context(tu_appli_name):
        """
        Used by get_tu_spark_context in order to create the specific context for current Unit-test.

        :param tu_appli_name:
        :type tu_appli_name:
        """

        if not SparkContext._active_spark_context:
            spark_conf = SparkConf(False).setMaster('local[4]').setAppName(tu_appli_name)
            my_context = SparkContext(conf=spark_conf)
            my_context.setLocalProperty('spark.app.name', tu_appli_name)
            ScManager.spark_context = my_context
            ScManager.sc_tdm = ResourceLocator().tdm
        else:
            raise Exception("Unexpected call to create_tu_spark_context():  SparkContext._active_spark_context == True")
        return ScManager.spark_context

    @staticmethod
    def stop_all():
        """
        Forces the stop of the defined SparkContext: SSessionManager.SparkContext
          - calls SSessionManager.stop()

        """
        SSessionManager.ikats_users = 0
        if SSessionManager.spark_session is not None:
            SSessionManager.stop()
            SSessionManager.spark_session = None


class SparkUtils:

    @staticmethod
    def check_spark_usage(tsuid_list, meta_list=None, nb_ts_criteria=100, nb_points_by_chunk=50000):
        """
        Function for checking Spark usage utility, function of the amount of available data.

        :param tsuid_list: A list of TS identifier ("tsuid")
        :type tsuid_list: list

        :param meta_list: The list of meta data (not mandatory). If None, request IKATS for meta-data
        type meta_list: dict (key is TS identifier, value is list of metadata with its associated data type)
                    | {
                    |     'TS1': {'param1':{'value':'value1', 'type': 'dtype'}, 'param2':{'value':'value2', 'type': 'dtype'}},
                    |     'TS2': {'param1':{'value':'value1', 'type': 'dtype'}, 'param2':{'value':'value2', 'type': 'dtype'}}
                    | }

        :param nb_ts_criteria: The minimal number of TS to consider for considering Spark is
        necessary
        :type nb_ts_criteria: int

        :param nb_points_by_chunk: number of points per chunk
        :type nb_points_by_chunk: int

        :return spark_usage: Bool indicating if (case True) spark should be used, according
        to the available amount of data.
        :rtype spark_usage: bool

        Criterion: if one of these criteria is true -> use spark
            * number of TS > `nb_ts_criteria`
            * nb_point of one of the TS not available
            * nb_point of one of the TS > 2 * `nb_points_by_chunk`
        """
        ScManager.log.info("Check criterion for Spark usage.")

        # 0/ Check inputs
        # ---------------------------------------------------
        # Types
        if type(tsuid_list) is not list:
            raise TypeError("Input `tsuid_list` is {}, list expected.".format(type(tsuid_list)))
        if type(meta_list) is not dict and meta_list is not None:
            raise TypeError("Input `meta_list` is {}, dict expected.".format(type(meta_list)))
        if type(nb_ts_criteria) is not int:
            raise TypeError("Input `nb_ts_criteria` is {}, int expected.".format(type(nb_ts_criteria)))
        if type(nb_points_by_chunk) is not int:
            raise TypeError("Input `nb_points_by_chunk` is {}, int expected.".format(type(nb_points_by_chunk)))

        # Value
        if nb_ts_criteria <= 0:
            raise ValueError('`nb_ts_criteria` is {}, expected to be strictly greater than 0')

        if nb_points_by_chunk <= 0:
            raise ValueError('`nb_points_by_chunk` is {}, expected to be strictly greater than 0')

        # 1/ Start check
        # ---------------------------------------------------
        if meta_list is None:
            # Checking metadata availability before starting cutting
            meta_list = IkatsApi.md.read(tsuid_list)

        # Applying criterion on dataset total number of points
        if len(tsuid_list) > nb_ts_criteria:
            spark_usage = True
        else:
            # Collecting nb points to decide to use spark or not
            spark_usage = False

            for tsuid in tsuid_list:
                # Checking metadata existence
                if 'qual_nb_points' not in meta_list[tsuid]:
                    # Metadata not found
                    ScManager.log.error(
                        "Metadata 'qual_nb_points' for time series %s not found in base, using Spark by default",
                        tsuid)
                    spark_usage = True
                    break

                # Retrieving tme series number of points from metadata
                nb_points_ts = int(meta_list[tsuid]['qual_nb_points'])
                # Applying criterion on each time series number of points
                if nb_points_ts > 2 * nb_points_by_chunk:
                    spark_usage = True
                    break

        ScManager.log.info("Spark usage set to {}.".format(spark_usage))

        return spark_usage

    @staticmethod
    def get_chunks_def(tsuid, sd, ed, period, nb_points_by_chunk=50000, overlap=None):
        """
        Split a TS into chunks according to it's number of points.
        Build np.array containing (([tsuid, chunk_index, start_date, end_date],...).

        Necessary for extracting a TS in Spark.

        :param tsuid: TS to get values from
        :type tsuid: str

        :param sd: start date of data
        :type sd: int

        :param ed: end date of data
        :type ed: int

        :param period: period of data
        :type period: int

        :param nb_points_by_chunk: size of chunks in number of points (assuming timeserie is periodic and without holes)
        :type nb_points_by_chunk: int

        :return: list containing chunks definition ([tsuid, chunk_index, start_date, end_date],...)
        :rtype: list
        """

        # Review#495: (FTA) overlap ? explain

        # Review#495: (FTA) Function is wrong/needs clarification for the following call:
        #                   SparkUtils.get_chunks_def("123TS", 1000, 10000, 1000, nb_points_by_chunk=2, overlap=None)
        #                   end date=10000 but the last chunk (#4) has range between [90000,10001]

        # Init result
        data_to_compute = []

        # 1/ Chunk intervals computation
        # ----------------------------------------------------------------------
        # Prepare data to compute by defining intervals of final size nb_points_by_chunk

        # Number of periods for one chunk
        data_chunk_size = int(nb_points_by_chunk * period)
        # ex: data_chunk_size = 10

        if overlap is None or overlap == 0:
            coef = 1
            overlap = None
        else:
            coef = 2
            overlap_time = overlap * period

        # Computing intervals for chunk definition (limits are TIMESTAMPS)
        interval_limits = np.hstack(np.arange(sd, ed, data_chunk_size, dtype=np.int64))
        # ex: intervals = [ 10, 20, 30, 40 ], if sd=10, ed=40

        # 2/ Define chunk of data to compute from intervals created
        # ----------------------------------------------------------------------
        # 2.1/ Defining chunks excluding last point of data within every chunk
        data_to_compute.extend([(tsuid,
                                 coef * i,
                                 interval_limits[i],
                                 interval_limits[i + 1] - 1) for i in range(len(interval_limits) - 1)])
        # ex: intervals = [ 10, 20, 30, 40 ] => 2 chunks [10, 19] and [20, 29]
        # (last chunk added in step 2)

        # 2.2/ Add the last interval, including last point of data
        data_to_compute.append((tsuid,
                                coef * (len(interval_limits) - 1),
                                interval_limits[-1],
                                ed + 1))
        # ex: data_to_compute => 4 chunks  [[10, 19], [20, 29], [30, 40]]

        # 2.3/ add inter chunks definition with overlap
        if overlap is not None:
            data_to_compute.extend([(tsuid,
                                     2 * i + 1,
                                     interval_limits[i + 1] - overlap_time,
                                     interval_limits[i + 1] + overlap_time - 1) for i in
                                    range(len(interval_limits) - 1)])

        return sorted(data_to_compute, key=lambda tup: tup[1])

    @staticmethod
    def save_data(fid, data):
        """
        Saves a data corresponding to time series points to database by providing functional identifier.

        :param fid: functional identifier for the new time series
        :param data: data to save

        :type fid: str
        :type data: np.array

        :return: the TSUID
        :rtype: str

        :raises IkatsException: if TS couldn't be created
        """

        results = IkatsApi.ts.create(fid=fid, data=data, generate_metadata=False, sparkified=True)
        if results['status']:
            return results['tsuid']
        else:
            raise IkatsException("TS %s couldn't be created" % fid)


class ListAccumulatorParam(AccumulatorParam):
    """
    Accumulator of internal type dict
    inherited from Spark, justify the PEP8 errors
    """

    def zero(self, initial_value):
        """
        Init the internal variable. initial_value is ignored here
           :param initial_value:
           :type initial_value: any
        """
        return dict()

    def addInPlace(self, v1, v2):
        """
            Add two values of the accumulator's data type,
            returning a new value
            add v2 to v1

            :param v1: parameter 1 to use for addition
            :param v2: parameter 2 to use for addition
        """
        v1.update(v2)
        return v1
