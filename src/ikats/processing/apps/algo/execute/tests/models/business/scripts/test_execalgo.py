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

from django.test import TestCase
import mock

from apps.algo.catalogue.models.orm.implem import ImplementationDao
from apps.algo.execute.models.business.scripts.execalgo import run
from ikats.core.config.ConfigReader import ConfigReader
from ikats.core.library.status import State
from ikats.core.resource.client.temporal_data_mgr import DTYPE
from ikats_processing.core.resource_config import ResourceClientSingleton
import numpy as np

LOGGER = logging.getLogger(__name__)

CONFIG_READER = ConfigReader()
HOST = CONFIG_READER.get('cluster', 'tdm.ip')
PORT = int(CONFIG_READER.get('cluster', 'tdm.port'))


# noinspection PyUnusedLocal
def get_fid_from_tsuid_mock(self, tsuid):
    """
    Mock of TemporalDataMgr.get_data_set method

    Same parameters and types as the original function

    """
    return {'funcId': 'funcId' + tsuid,
            'tsuid': tsuid}


# noinspection PyUnusedLocal,PyIncorrectDocstring
def get_ts_mock(self, tsuid_list, sd=None, ed=None):
    """
    Mock of TemporalDataMgr.get_ts method

    Same parameters and types as the original function
    """
    if tsuid_list == ['00001', '00002', '00003', '00004']:
        return [np.array([[1449755790000, 1], [1449755791000, 2], [1449755792000, 3]]),
                np.array(
                    [[1449755790000, 4], [1449755791000, 5], [1449755792000, 7]]),
                np.array(
                    [[1449755790000, 7], [1449755791000, 6], [1449755792000, 5]]),
                np.array([[1449755790000, 7], [1449755791000, 6], [1449755792000, 4]])]
    elif tsuid_list == ['TSUID1', 'TSUID2']:
        result = [[[np.int64(0), 5],
                   [np.int64(1000), 6],
                   [np.int64(2000), 8],
                   [np.int64(3000), -15],
                   [np.int64(4000), 2],
                   [np.int64(5000), 6],
                   [np.int64(6000), 3],
                   [np.int64(7000), 2],
                   [np.int64(8000), 42],
                   [np.int64(9000), 8]],
                  [[np.int64(0), 5],
                   [np.int64(10000), 6],
                   [np.int64(20000), 8],
                   [np.int64(30000), -100],
                   [np.int64(40000), 2],
                   # Hole
                   [np.int64(60000), 3],
                   [np.int64(70000), 40],
                   [np.int64(80000), 40.01],
                   [np.int64(90000), 8]]]
        return result


# noinspection PyUnusedLocal,PyIncorrectDocstring
def get_ts_by_tsuid_mock(self, tsuid, sd, ed=None, ag='avg', old_format=False):
    """
    Mock of TemporalDataMgr.get_ts_by_tsuid method

    Same parameters and types as the original function

    """
    if tsuid == '00001':
        return np.array([[1449755790000, 1], [1449755791000, 2], [1449755792000, 3]])

    if tsuid == '00002':
        return np.array([[1449755790000, 4], [1449755791000, 5], [1449755792000, 7]])

    if tsuid == '00003':
        return np.array([[1449755790000, 7], [1449755791000, 6], [1449755792000, 5]])

    if tsuid == '00004':
        return np.array([[1449755790000, 7], [1449755791000, 6], [1449755792000, 4]])


# noinspection PyUnusedLocal,PyIncorrectDocstring
def get_data_set_mock(self, data_set):
    """
    Mock of TemporalDataMgr.get_data_set method

    Same parameters and types as the original function

    """
    return {"description": "description of my data set",
            "ts_list": ['00001',
                        '00002',
                        '00003',
                        '00004']}


# noinspection PyUnusedLocal,PyIncorrectDocstring
def import_ts_data_mock(self, metric, data, fid, tags=None, data_set=None):
    """
    Mock of TemporalDataMgr.import_ts_data method

    Same parameters and types as the original function

    """

    return {
        'status': True,
        'errors': {},
        'numberOfSuccess': 20,
        'summary': 'test',
        'tsuid': 'TSUID_res_' + fid
    }


# noinspection PyUnusedLocal,PyIncorrectDocstring
def get_ts_meta_mock(self, tsuid):
    """
    Mock of TemporalDataMgr.get_ts_meta method

    Same parameters and types as the original function

    """

    return {
        'tsuid': tsuid,
        'funcId': 'funcId' + tsuid,
        'metric': 'metric' + tsuid,
        'tags': {'tag1': 'test'}
    }


# noinspection PyUnusedLocal,PyIncorrectDocstring
def add_data_mock(self, data, process_id, data_type=None, name=None):
    """
    Mock of NonTemporalDataMgr.add_data method

    Same parameters and types as the original function

    """
    return "1234567"


# Local meta data database for testing purposes
META_DATA_BASE = {}


# noinspection PyUnusedLocal,PyIncorrectDocstring
def import_meta_data_mock(self, tsuid, name, value, data_type=DTYPE.string, force_update=False):
    """
    Mock of the import method ikats.core.resource.client.TemporalDataMgr.import_meta_data
    """
    if tsuid not in META_DATA_BASE:
        META_DATA_BASE[tsuid] = {}

    META_DATA_BASE[tsuid][name] = value
    return True


# noinspection PyUnusedLocal,PyIncorrectDocstring
def get_meta_data_mock(self, ts_list):
    """
    Mock of the import method ikats.core.resource.client.TemporalDataMgr.get_meta_data
    """

    md = {}
    for ts in ts_list:
        md[ts] = {}
        if ts in META_DATA_BASE:
            md[ts] = META_DATA_BASE[ts]

    return META_DATA_BASE


class TestRunAlgo(TestCase):
    """
    Tests the RunAlgo
    """
    def assert_status_is_without_error(self, algo_status, tu_context="TODO_UNDEFINED_TU_CONTEXT"):
        """
        Tests the algo status is defined
        """
        self.assertTrue(algo_status is not None)
        LOGGER.info(str(algo_status))
        if algo_status.get_error() is not None:
            msg = "Failure ExecutableAlgo::status.get_error() in {0}: {1}".format(tu_context,
                                                                                  str(algo_status.get_error()))

            LOGGER.error(msg)
            self.assertIsNone(algo_status.get_error(), msg)

    def get_impl_id(self, name):
        """
        Tests the implementation id returned
        """
        my_resampling_impl = ImplementationDao.find_business_elem_with_name(name)
        self.assertIsNotNone(my_resampling_impl, "Not None: find Implementations list with name=" + name)
        self.assertEqual(len(my_resampling_impl), 1, "Unique Implementation with name=" + name)
        self.assertIsNotNone(my_resampling_impl[0].db_id, "ID of implementation with name=" + name)
        str_algo_id = str(my_resampling_impl[0].db_id)
        return str_algo_id

    @mock.patch('ikats.core.resource.client.TemporalDataMgr.get_data_set', get_data_set_mock)
    @mock.patch('ikats.core.resource.client.TemporalDataMgr.get_ts_by_tsuid', get_ts_by_tsuid_mock)
    @mock.patch('ikats.core.resource.client.TemporalDataMgr.import_ts_data', import_ts_data_mock)
    @mock.patch('ikats.core.resource.client.TemporalDataMgr.import_meta_data', import_meta_data_mock)
    @mock.patch('ikats.core.resource.client.TemporalDataMgr.get_ts_meta', get_ts_meta_mock)
    @mock.patch('ikats.core.resource.client.TemporalDataMgr.get_meta_data', get_meta_data_mock)
    @mock.patch('ikats.core.resource.client.NonTemporalDataMgr.add_data', add_data_mock)
    @mock.patch('ikats.core.resource.client.TemporalDataMgr.get_ts', get_ts_mock)
    def test_exec_async(self):
        """
        Tests the resampling and correlation algorithm call asynchronously through Algorithm Manager
        """
        ResourceClientSingleton.singleton_init(host=HOST, port=PORT)
        tdm = ResourceClientSingleton.get_singleton().get_temporal_manager()

        resampling_tested_impl_name = "resampling_dataset_impl"
        resampling_impl_id = self.get_impl_id(resampling_tested_impl_name)

        tdm.import_meta_data("00001", "qual_nb_points", 3)
        tdm.import_meta_data("00002", "qual_nb_points", 3)
        tdm.import_meta_data("00003", "qual_nb_points", 3)
        tdm.import_meta_data("00004", "qual_nb_points", 3)

        status_algo1 = run(resampling_impl_id, ["ts_selection", "period"], ["PORTFOLIO", 500], asynchro=True)

        process_id_algo1 = status_algo1.get_process_id()
        state_algo1 = status_algo1.get_state()

        self.assertTrue(process_id_algo1 is not None)
        self.assertTrue(state_algo1 == State.INIT)
        self.assert_status_is_without_error(
            status_algo1, "test_exec_async: step1 algo resampling")

        tested_impl_name = "pearson_correl_matrix_impl"
        impl_id = self.get_impl_id(tested_impl_name)

        status_algo2 = run(impl_id, ["ts_selection"], [['00001', '00002', '00003', '00004']], asynchro=True)

        process_id_algo2 = status_algo2.get_process_id()
        state_algo2 = status_algo2.get_state()

        self.assertTrue(process_id_algo2 is not None)
        self.assert_status_is_without_error(
            status_algo2,
            "test_exec_async: step2 algo pearson correlation matrix")
        self.assertTrue(state_algo2 == State.INIT)
