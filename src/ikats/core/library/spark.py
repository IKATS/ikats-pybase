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

from ikats.core.resource.api import IkatsApi
from ikats.core.resource.client import TemporalDataMgr
from ikats.core.resource.client.non_temporal_data_mgr import NonTemporalDataMgr
from ikats.core.resource.interface import ResourceLocator
from pyspark import SparkContext
from pyspark.sql import SparkSession
from pyspark.accumulators import AccumulatorParam
from pyspark.conf import SparkConf

from ikats.core.resource.interface import ResourceLocator
from ikats.core.resource.client.non_temporal_data_mgr import NonTemporalDataMgr
from ikats.core.config.ConfigReader import ConfigReader

class Connector(object):
    """
    Standard actions to perform with map/reduce
    """

    @staticmethod
    def get_ts(tsuid, sd=None, ed=None):
        """
        Encapsulation of get_ts to be used by maps chain

        :param tsuid: TSUID to get data from
        :param sd: start date
        :param ed: end date
        :return: the ts_data corresponding to the TSUID
        """

        tdm = TemporalDataMgr()
        return tdm.get_ts(tsuid_list=[tsuid], sd=sd, ed=ed)[0]

    @staticmethod
    def import_ts(func_id, data, generate_metadata=True, *args, **kwargs):
        """
        Encapsulation of IkatsApi.ts.create
        Import TS data points in database or update an existing TS with new points

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
        return IkatsApi.ts.create(func_id, data, generate_metadata, *args, **kwargs)


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

    # Spark session
    spark_session = None

    # Broadcast variables: shared content
    sc_tdm = None
    sc_ntdm = None

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
