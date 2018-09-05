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

from ikats.core.resource.api import IkatsApi
from ikats.core.resource.client import TemporalDataMgr
from ikats.core.resource.client.non_temporal_data_mgr import NonTemporalDataMgr
from ikats.core.resource.interface import ResourceLocator

from pyspark import SparkContext
from pyspark.sql import SparkSession
from pyspark.accumulators import AccumulatorParam
from pyspark.conf import SparkConf

from ikats.core.config.ConfigReader import ConfigReader

from ikats.core.library.exception import IkatsException


class Connector(object):
    """
    Standard actions to perform with map/reduce
    """
    log = logging.getLogger("Connector")

    @staticmethod
    def read_ts(tsuid, start_date=None, end_date=None):
        """
        Return the points of a TS

        :param tsuid: TS to get values from
        :type tsuid: str

        :param start_date: start date (ms since EPOCH)
        :type start_date: int or NoneType

        :param end_date: end date (ms since EPOCH)
        :type end_date: int or NoneType

        :return: the values of the Timeseries
        :rtype: np.array
        """
        return IkatsApi.ts.read(tsuid_list=[tsuid], sd=start_date, ed=end_date)[0]

    @staticmethod
    def import_ts(func_id, data, generate_metadata=True, *args, **kwargs):
        """
        Import TS data points in database or update an existing TS with new points
        Encapsulation of IkatsApi.ts.create.

        :param data: array of points where first column is timestamp (EPOCH ms) and second is value (float compatible)
        :param func_id: Functional Identifier of the TS in Ikats
        :param generate_metadata: flag indicating the need of generating Metadata (True default)
        :param args: Other arguments
        :param kwargs: Other keyword arguments

        :type data: ndarray or list
        :type func_id: str
        :type generate_metadata: bool
        :type args: tuple
        :type kwargs: dict

        :return: an object containing several information about the import
        :rtype: dict containing information :
           | {
           |     'status' : True if import successful, False otherwise,
           |     'errors' : *dict of errors*,
           |     'numberOfSuccess': *Number of successful imported entries*,
           |     'summary': *summary of import status*,
           |     'tsuid': *tsuid if created*
           |     'funcId': *functional identifier if created*
           |     'responseStatus': *status of response*
           | }
        """
        results = IkatsApi.ts.create(fid=func_id,
                                     data=data,
                                     generate_metadata=generate_metadata,
                                     *args, **kwargs)
        if results['status']:
            return results
        else:
            raise IkatsException("TS %s couldn't be created" % func_id)

    @staticmethod
    def save_metadata(tsuid, md_name, md_value, data_type, force_update):
        """
        Saves metadata to Ikats database and log potential errors

        :param tsuid: TSUID to link metadata with
        :param md_name: name of the metadata to save
        :param md_value: value of the metadata
        :param data_type: type of the metadata
        :param force_update: overwrite metadata value if exists (if True)

        :type tsuid: str
        :type md_name: str
        :type md_value: str or int or float
        :type data_type: DTYPE
        :type force_update: bool
        """
        if not IkatsApi.md.create(
                tsuid=tsuid,
                name=md_name,
                value=md_value,
                data_type=data_type,
                force_update=force_update):
            Connector.log.error("Metadata '%s' couldn't be saved for TS %s", md_name, tsuid)


class SSessionManager(object):
    """
    Spark Session manager
    Used to manage spark session creation and closure. Note that a Spark Session is composed
    by some info from a Spark Context.
    Introduced for usage of spark DataFrame.
    """

    log = logging.getLogger("SSessionManager")

    APPNAME_UNIT_TEST_IKATS = "UNIT_TEST_IKATS"

    # Number of current algorithms needing the spark context
    ikats_users = 0

    # Spark session: for DataFrame creation
    spark_session = None
    # Spark context: For init a spark Session, or for RDD creation
    spark_context = None

    # Number of point by chunk
    CHUNK_SIZE = 50000

    @staticmethod
    def get_chunks(tsuid, md):
        """
        Cut a TS into chunks according to it's number of points.
        Build np.array containing (([chunk_index, start_date, end_date],...).

        Necessary for extracting a TS in Spark.

        :param tsuid: TS to get values from
        :type tsuid: str

        :param md: The meta data corresponding to the current tsuid
        :type md: dict

        :return: RDD containing ([chunk_index, start_date, end_date],...)
        :rtype: RDD
        """
        # Init result
        data_to_compute = []

        # 1/ Retrieve meta-data (start, end, nb_points)
        # ----------------------------------------------------------------------
        # Original time series information retrieved from metadata
        sd = int(md['ikats_start_date'])
        ed = int(md['ikats_end_date'])
        ref_period = int(float(md['qual_ref_period']))
        # qual_nb_points

        # 2/ Chunk intervals computation
        # ----------------------------------------------------------------------
        # Prepare data to compute by defining intervals of final size CHUNK_SIZE

        # Number of periods for one chunk
        data_chunk_size = int(SSessionManager.CHUNK_SIZE * ref_period)
        # ex: data_chunk_size = 10

        # Computing intervals for chunk definition (limits are TIMESTAMPS)
        interval_limits = np.hstack(np.arange(sd, ed, data_chunk_size, dtype=np.int64))
        # ex: intervals = [ 10, 20, 30, 40 ], if sd=10, ed=40

        # 3/ Define chunk of data to compute from intervals created
        # ----------------------------------------------------------------------
        # 3.1/ Defining chunks excluding last point of data within every chunk
        data_to_compute.extend([(tsuid,
                                 i,
                                 interval_limits[i],
                                 interval_limits[i + 1] - 1) for i in range(len(interval_limits) - 1)])
        # ex: intervals = [ 10, 20, 30, 40 ] => 2 chunks [10, 19] and [20, 29]
        # (last chunk added in step 2)

        # 3.2/ Add the last interval, including last point of data
        data_to_compute.append((tsuid,
                                len(interval_limits) - 1,
                                interval_limits[-1],
                                ed + 1))
        # ex: data_to_compute =  [[10, 19], [20, 29], [30, 40]]

        return data_to_compute

    @staticmethod
    def get_ts_by_chunks(tsuid, md):
        """
        Read current TS (`tsuid`), chunked with spark.
        For now, it's the optimal way to read TS with Spark DataFrame.

        Action performed:
            * get chunks intervals (id, start, end) (`get_chunks`)
            * read current TS (`tsuid`) chunked with spark (RDD)
            * transform resulting rdd into Spark DataFrame (DF)

        :param tsuid: TS to get values from
        :type tsuid: str

        :param md: The meta data corresponding to the current tsuid
        :type md: dict

        :return: DataFrame containing all data from current TS
        :rtype: pyspark.sql.dataframe.DataFrame
        """
        # 0/ Input check
        # ----------------------------------------------------------------------
        # Need a spark context to init an RDD
        if SSessionManager.spark_context is None:
            SSessionManager.log.error("SSessionManager: Trying to get TS by chunk with no spark_context."
                                      " Please, launch `get` or `create` method with proper arg. ")
            ValueError("No spark context.")

        # 1/ Get the chunks, and read TS chunked
        # ----------------------------------------------------------------------
        # Get the chunks, and distribute them with Spark
        rdd_ts_info = SSessionManager.spark_context.parallelize(SSessionManager.get_chunks(tsuid=tsuid,
                                                                                           md=md))

        # DESCRIPTION : Get the points within chunk range and suppress empty chunks
        # INPUT  : ([chunk_index, start_date, end_date],...)
        # OUTPUT : ([chunk_index, ts_data_points], ...)
        rdd_chunk_data = rdd_ts_info \
            .map(lambda x: (x[0],
                            Connector.read_ts(tsuid=tsuid,
                                              start_date=int(x[1]),
                                              end_date=int(x[2])))) \
            .filter(lambda x: len(x[1]) > 0)

        # 2/ Put result into a Spark DataFrame
        # ----------------------------------------------------------------------
        # Init a DataFrame for one single ts_data
        df = SSessionManager.spark_session.createDataFrame(
            rdd_chunk_data, ["Timestamp", "Value"])

        return df

    @staticmethod
    def create(spark_context):
        """
        Create a new spark session from an existing spark context.
        :param spark_context: A SparkContext (ex: ScManager.spark_context)
        :type spark_context: SparkContext

        :return: The spark Session
        :rtype: SparkSession
        """
        SSessionManager.spark_context = spark_context

        if not SSessionManager.spark_session:
            # Init a Spark Session for using spark Dataframes:
            # - use conf from a `SparkContext`
            SSessionManager.spark_session = SparkSession.builder\
                .config(conf=SSessionManager.spark_context.getConf())\
                .getOrCreate()

        return SSessionManager.spark_session

    @staticmethod
    def get(spark_context):
        """
        Get a spark session if exists or create a new one.
        :param spark_context: A SparkContext (ex: ScManager.spark_context)
        :type spark_context: SparkContext

        :return: The spark session
        :rtype: SparkSession
        """
        SSessionManager.ikats_users += 1

        # Get or Create is yet implemented in `create` method.
        return SSessionManager.create(spark_context)

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
            SSessionManager.log.info("SSessionManager: stopping SparkSession: users count decreased to %s", SSessionManager.ikats_users)
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
    """

    log = logging.getLogger("ScManager")

    APPNAME_UNIT_TEST_IKATS = "UNIT_TEST_IKATS"

    # Number of current algorithms needing the spark context
    ikats_users = 0

    # Spark context
    spark_context = None

    # Broadcast variables: shared content
    sc_tdm = None
    sc_ntdm = None

    @staticmethod
    def create():
        """
        Create a new spark context
        :return: The spark Context
        :rtype: SparkContext
        """
        if not ScManager.spark_context:
            # noinspection PyProtectedMember
            if not SparkContext._active_spark_context:
                master = ConfigReader().get('cluster', 'spark.url')
                ScManager.spark_context = SparkContext(
                    appName='Ikats',
                    master=master
                )
        return ScManager.spark_context

    @staticmethod
    def get():
        """
        Get a spark context if exists or create a new one
        :return: The spark Context
        :rtype: SparkContext
        """
        ScManager.ikats_users += 1
        if not ScManager.spark_context:
            return ScManager.create()
        else:
            return ScManager.spark_context

    @staticmethod
    def stop():
        """
        Request to stop context
        The Spark context will continue to run if other algo needs it
        :return: True if the spark context was actually stopped
        :rtype: bool
        """
        actually_stopped = False
        if ScManager.ikats_users > 0:
            ScManager.ikats_users -= 1
            ScManager.log.info("ScManager: stopping SparkContext: users count decreased to %s", ScManager.ikats_users)
        else:
            ScManager.log.warning("ScManager: stopping SparkContext: users count is already zero")

        if ScManager.ikats_users == 0:
            if ScManager.spark_context is None:
                ScManager.log.error("ScManager: stopping SparkContext: unexpected error: undefined SparkContext")
                raise SystemError('Trying to close an already closed Spark context')
            ScManager.spark_context.stop()
            ScManager.log.info(
                "ScManager: stopping SparkContext without user left: ScManager.sc is stopped and set to None.")

            actually_stopped = True
            ScManager.spark_context = None

        return actually_stopped

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

            # at most one user: the unit-test
            ScManager.ikats_users += 1
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
        Forces the stop of the defined SparkContext: ScManager.sc
          - sets  ScManager.ikats_users to 0
          - calls ScManager.sc.stop()
          - sets ScManager.sc to None

        Beware: do not use this method in operational mode: method to be used in TU only.
        """
        ScManager.ikats_users = 0
        if ScManager.spark_context is not None:
            ScManager.spark_context.stop()
            ScManager.spark_context = None

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

        Criterion: if one of these criterion is true -> use spark
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
        if type(meta_list) is not dict:
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
