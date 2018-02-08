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
    Pierre BONHOURE <pierre.bonhoure@c-s.fr>
"""
import logging
import re
from unittest import TestCase

import httpretty
import mock
import numpy as np

from ikats.core.config.ConfigReader import ConfigReader
from ikats.core.resource.api import IkatsApi
from ikats.core.resource.client.temporal_data_mgr import DTYPE
from ikats.core.resource.opentsdb.HttpClient import HttpClient
from ikats.core.resource.opentsdb.wrapper import Wrapper

USE_REAL_SERVER = False

# Configuration file
CONFIG_READER = ConfigReader()

# Address of the real server to use for tests
TEST_HOST = CONFIG_READER.get('cluster', 'tdm.ip')
TEST_PORT = int(CONFIG_READER.get('cluster', 'tdm.port'))

TEST_OPENTSDB_HOST = CONFIG_READER.get('cluster', 'opentsdb.read.ip')
TEST_OPENTSDB_PORT = int(CONFIG_READER.get('cluster', 'opentsdb.read.port'))
ROOT_URL = 'http://%s:%s/TemporalDataManagerWebApp/webapi' % (TEST_HOST, TEST_PORT)
DIRECT_ROOT_URL = 'http://%s:%s/api' % (TEST_OPENTSDB_HOST, TEST_OPENTSDB_PORT)


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


# noinspection PyUnusedLocal
def import_meta_data_mock(self, tsuid, name, value, data_type=DTYPE.string, force_update=False):
    """
    Mock of the import of meta data function to verify the imported meta data
    :param self:
    :param tsuid:
    :param name:
    :param value:
    :param data_type:
    :param force_update:
    :return:
    """
    if tsuid not in META_DATA_LIST:
        META_DATA_LIST[tsuid] = {}

    if name not in META_DATA_LIST[tsuid] or force_update:

        # Update ikats start/end date with new value if lesser/greater than old value
        if name == "ikats_start_date" and name in META_DATA_LIST[tsuid]:
            META_DATA_LIST[tsuid][name] = min(int(META_DATA_LIST[tsuid][name]), int(value))
            print("Overwriting Metadata %s=%s for TSUID=%s" % (name, value, tsuid))
        elif name == "ikats_end_date" and name in META_DATA_LIST[tsuid]:
            META_DATA_LIST[tsuid][name] = max(int(META_DATA_LIST[tsuid][name]), int(value))
            print("Overwriting Metadata %s=%s for TSUID=%s" % (name, value, tsuid))
        else:
            META_DATA_LIST[tsuid][name] = value
            print("Writing Metadata %s=%s for TSUID=%s" % (name, value, tsuid))
        return True
    return False


# noinspection PyUnusedLocal,PyUnusedLocal
def get_meta_data_mock(self, ts_list):
    """
    :param ts_list:
    :param self:
    """
    return META_DATA_LIST


FID_DATABASE = {}


# noinspection PyUnusedLocal,PyUnusedLocal
def import_fid_mock(self, tsuid, fid):
    """
    Mock of the FID import
    :param self:
    :param tsuid:
    :param fid:
    :return:
    """
    if tsuid in FID_DATABASE:
        raise IndexError
    FID_DATABASE[tsuid] = fid


# noinspection PyUnusedLocal,PyUnusedLocal
def get_fid_mock(_, tsuid):
    """
    Mock of the FID import
    :param self:
    :param tsuid:
    :return:
    """
    if tsuid not in FID_DATABASE:
        raise ValueError
    return FID_DATABASE[tsuid]


# noinspection PyUnusedLocal,PyUnusedLocal
def get_tsuid_from_func_id_mock(_, func_id):
    """
    Mock of get_tsuid_from_func_id_mock
    :param self:
    :param func_id:
    :return:
    """
    for tsuid in FID_DATABASE:
        if FID_DATABASE[tsuid] == func_id:
            return tsuid
    raise ValueError


def fake_server(func):
    """
    Decorator used to activate (or not) the fake server
    It depends on ``use_real_server`` boolean global variable

    :param func: decorated function
    :return: the function decorated or not with fake server activation
    """
    if not USE_REAL_SERVER:
        return httpretty.activate(func)
    else:
        return func


class TestIkatsApi(TestCase):
    """
    Tests the Ikats API
    """

    @fake_server
    def test_fid_create(self):
        """
        Tests the import of a functional identifier
        """

        # Fake answer definition
        httpretty.register_uri(
            httpretty.POST,
            '%s/metadata/funcId/test_TSUID/test_FID' % ROOT_URL,
            body='OK',
            status=200
        )

        # Implicit data type
        IkatsApi.fid.create(
            tsuid='test_TSUID',
            fid='test_FID')
        # If something wrong happens, an assert will be raised by import_fid

    @fake_server
    def test_fid_read(self):
        """
        Tests the deletion of a functional identifier
        """

        # Fake answer definition
        httpretty.register_uri(
            httpretty.GET,
            '%s/metadata/funcId/test_TSUID' % ROOT_URL,
            body="""
                {
                    "tsuid":"test_TSUID",
                    "funcId":"MyFID"
                }""",
            status=200,
            content_type='text/json'
        )

        # Implicit data type
        fid = IkatsApi.fid.read(tsuid='test_TSUID')
        self.assertEqual(fid, "MyFID")

    @fake_server
    def test_fid_delete(self):
        """
        Tests the deletion of a functional identifier
        """

        # Fake answer definition
        httpretty.register_uri(
            httpretty.DELETE,
            '%s/metadata/funcId/test_TSUID' % ROOT_URL,
            body='OK',
            status=200
        )

        # Implicit data type
        IkatsApi.fid.delete(tsuid='test_TSUID')
        # If something wrong happens, an assert will be raised by delete_fid

    @fake_server
    def test_md_create(self):
        """
        Tests the import of meta data (nominal)
        """

        # Fake answer definition
        httpretty.register_uri(
            httpretty.POST,
            '%s/metadata/import/TSUID/test_meta_data/value_of_meta_data' % ROOT_URL,
            body='OK',
            status=200
        )

        # Fake answer definition
        httpretty.register_uri(
            httpretty.POST,
            '%s/metadata/import/TSUID/test_meta_data_typed/value_of_meta_data?dtype=string' % ROOT_URL,
            body='OK',
            status=200
        )

        # Fake answer definition
        httpretty.register_uri(
            httpretty.POST,
            '%s/metadata/import/TSUID/test_meta_data_number/3?dtype=number' % ROOT_URL,
            body='OK',
            status=200
        )

        # Fake answer definition
        httpretty.register_uri(
            httpretty.POST,
            '%s/metadata/import/TSUID/test_meta_data_date/1234567890123?dtype=date' % ROOT_URL,
            body='OK',
            status=200
        )

        # Fake answer definition
        httpretty.register_uri(
            httpretty.POST,
            '%s/metadata/import/TSUID/test_meta_data_complex/{key:value}?dtype=complex' % ROOT_URL,
            body='OK',
            status=200
        )

        # Implicit data type
        results = IkatsApi.md.create(
            tsuid='TSUID',
            name='test_meta_data',
            value='value_of_meta_data')
        self.assertTrue(results)

        # Explicitly specify the data type string
        results = IkatsApi.md.create(
            tsuid='TSUID',
            name='test_meta_data',
            value='value_of_meta_data',
            data_type=DTYPE.string)
        self.assertTrue(results)

        # Explicitly specify the data type number
        results = IkatsApi.md.create(
            tsuid='TSUID',
            name='test_meta_data_number',
            value='3',
            data_type=DTYPE.number)
        self.assertTrue(results)

        # Explicitly specify the data type date
        results = IkatsApi.md.create(
            tsuid='TSUID',
            name='test_meta_data_date',
            value='1234567890123',
            data_type=DTYPE.date)
        self.assertTrue(results)

        # Explicitly specify the data type complex
        results = IkatsApi.md.create(
            tsuid='TSUID',
            name='test_meta_data_complex',
            value='{key:value}',
            data_type=DTYPE.complex)
        self.assertTrue(results)

    @fake_server
    def test_md_create_not_created(self):
        """
        Tests the import of meta data not created
        """

        # Fake answer definition
        httpretty.register_uri(
            httpretty.POST,
            '%s/metadata/import/TSUID/test_meta_data/value_of_meta_data' % ROOT_URL,
            body='OK',
            status=204
        )

        results = IkatsApi.md.create(tsuid='TSUID', name='test_meta_data', value='value_of_meta_data')
        self.assertFalse(results)

    def test_md_create_wrong_data_type(self):
        """
        Tests the import of meta data with a wrong data type
        """

        with self.assertRaises(TypeError):
            IkatsApi.md.create(tsuid='TSUID',
                               name='test_meta_data',
                               value='value_of_meta_data',
                               data_type="unknown")

    @fake_server
    def test_md_create_not_exist(self):
        """
        Tests the import of meta data which doesn't exists
        """

        # Fake answer definition
        httpretty.register_uri(
            httpretty.POST,
            '%s/metadata/import/TSUID/test_meta_data/value_of_meta_data' % ROOT_URL,
            body='OK',
            status=404
        )

        results = IkatsApi.md.create(tsuid='TSUID', name='test_meta_data', value='value_of_meta_data')
        self.assertFalse(results)

    @fake_server
    def test_md_create_force_update(self):
        """
        Tests the creation of meta data which doesn't exists but force update require to create it
        """

        # Fake answer definition
        httpretty.register_uri(
            httpretty.POST,
            '%s/metadata/import/TSUID/test_meta_data/value_of_meta_data' % ROOT_URL,
            body='',
            status=404
        )

        # Fake answer definition
        httpretty.register_uri(
            httpretty.PUT,
            '%s/metadata/TSUID/test_meta_data/value_of_meta_data' % ROOT_URL,
            body='',
            status=200
        )

        results = IkatsApi.md.create(tsuid='TSUID', name='test_meta_data', value='value_of_meta_data',
                                     force_update=True)
        self.assertFalse(results)

    @fake_server
    def test_md_read_typed(self):
        """
        Requests for the meta data associated to a TS with its associated type
        """

        # Fake answer definition
        httpretty.register_uri(
            httpretty.GET,
            '%s/metadata/list/json' % ROOT_URL,
            body="""[{"id":12,"tsuid":"TS1","name":"MD1","value":"my_string", "dtype":"string"},
                 {"id":13,"tsuid":"TS1","name":"MD2","value":"42", "dtype":"number"},
                 {"id":14,"tsuid":"TS1","name":"MD3","value":"1234567890123", "dtype":"date"},
                 {"id":15,"tsuid":"TS1","name":"MD4","value":"{key1:value1}", "dtype":"complex"}]""",
            status=200,
            content_type='text/json'
        )

        results = IkatsApi.md.read('TS1', with_type=True)
        self.assertDictEqual(results, {'TS1': {
            'MD1': {'value': 'my_string', 'type': 'string'},
            'MD2': {'value': '42', 'type': 'number'},
            'MD3': {'value': '1234567890123', 'type': 'date'},
            'MD4': {'value': '{key1:value1}', 'type': 'complex'},
        }})

    @fake_server
    def test_md_read(self):
        """
        Requests for the meta data associated to a TS
        """

        # Fake answer definition
        httpretty.register_uri(
            httpretty.GET,
            '%s/metadata/list/json' % ROOT_URL,
            body="""[{"id":12,"tsuid":"MAM3","name":"cycle","value":"takeoff"},
                 {"id":13,"tsuid":"MAM3","name":"flight","value":"AF2042"},
                 {"id":14,"tsuid":"MAM3","name":"units","value":"meters"}]""",
            status=200,
            content_type='text/json'
        )

        results = IkatsApi.md.read('MAM3')
        self.assertDictEqual(results, {'MAM3': {'cycle': 'takeoff', 'flight': 'AF2042', 'units': 'meters'}})

    @fake_server
    def test_md_read_multi(self):
        """
        Requests for the meta data associated to a TS
        """

        # Fake answer definition
        httpretty.register_uri(
            httpretty.GET,
            '%s/metadata/list/json' % ROOT_URL,
            body="""[{"id":12,"tsuid":"MAM3","name":"cycle","value":"takeoff"},
                 {"id":13,"tsuid":"MAM3","name":"flight","value":"AF2042"},
                 {"id":14,"tsuid":"MAM3","name":"units","value":"meters"},
                 {"id":15,"tsuid":"MAM4","name":"cycle","value":"landing"}]""",
            status=200,
            content_type='text/json'
        )

        results = IkatsApi.md.read(['MAM3', 'MAM4'])

        self.assertDictEqual(results, {
            'MAM3': {
                'cycle': 'takeoff',
                'flight': 'AF2042',
                'units': 'meters'
            },
            'MAM4': {
                'cycle': 'landing'
            },

        })

    @fake_server
    def test_md_read_unknown(self):
        """
        Requests for the meta data associated to an unknown TS
        """

        # Fake answer definition
        httpretty.register_uri(
            httpretty.GET,
            '%s/metadata/list/json' % ROOT_URL,
            body='[]',
            status=200,
            content_type='text/json'
        )

        results = IkatsApi.md.read('unknown_TS')

        self.assertDictEqual(results, {'unknown_TS': {}})

    @fake_server
    def test_md_read_multi_mixed(self):
        """
        Requests for the meta data associated to several TS having unknown TS
        """

        # Fake answer definition
        httpretty.register_uri(
            httpretty.GET,
            '%s/metadata/list/json' % ROOT_URL,
            body="""[{"id":12,"tsuid":"MAM3","name":"cycle","value":"takeoff"},
                 {"id":13,"tsuid":"MAM3","name":"flight","value":"AF2042"},
                 {"id":14,"tsuid":"MAM3","name":"units","value":"meters"}]""",
            status=200,
            content_type='text/json'
        )

        results = IkatsApi.md.read(['MAM3', 'unknown'])

        self.assertDictEqual(results, {
            'MAM3': {
                'cycle': 'takeoff',
                'flight': 'AF2042',
                'units': 'meters'
            },
            'unknown': {},
        })

    @fake_server
    def test_md_update(self):
        """
        Tests the update of meta data (nominal)
        """

        # Fake answer definition
        httpretty.register_uri(
            httpretty.PUT,
            '%s/metadata/TSUID/test_meta_data/value_of_meta_data' % ROOT_URL,
            body='',
            status=200
        )

        results = IkatsApi.md.update(
            tsuid='TSUID',
            name='test_meta_data',
            value='value_of_meta_data')

        self.assertTrue(results)

    @fake_server
    def test_md_update_not_created(self):
        """
        Tests the update of meta data not created
        """

        # Fake answer definition
        httpretty.register_uri(
            httpretty.PUT,
            '%s/metadata/TSUID/test_meta_data/value_of_meta_data' % ROOT_URL,
            body='',
            status=204
        )

        results = IkatsApi.md.update(tsuid='TSUID', name='test_meta_data', value='value_of_meta_data')
        self.assertFalse(results)

    @fake_server
    def test_md_update_not_exist(self):
        """
        Tests the update of meta data which doesn't exists
        """

        # Fake answer definition
        httpretty.register_uri(
            httpretty.PUT,
            '%s/metadata/TSUID/test_meta_data/value_of_meta_data' % ROOT_URL,
            body='',
            status=404
        )

        results = IkatsApi.md.update(tsuid='TSUID', name='test_meta_data', value='value_of_meta_data')
        self.assertFalse(results)

    @fake_server
    def test_md_update_force_create(self):
        """
        Tests the update of meta data which doesn't exists but force create require to create it
        """

        # Fake answer definition
        httpretty.register_uri(
            httpretty.PUT,
            '%s/metadata/TSUID/test_meta_data/value_of_meta_data' % ROOT_URL,
            body='',
            status=404
        )
        # Fake answer definition
        httpretty.register_uri(
            httpretty.POST,
            '%s/metadata/import/TSUID/test_meta_data/value_of_meta_data' % ROOT_URL,
            body='',
            status=200
        )

        results = IkatsApi.md.update(tsuid='TSUID', name='test_meta_data', value='value_of_meta_data',
                                     force_create=True)
        self.assertTrue(results)

    @fake_server
    def test_ds_list(self):
        """
        Get the dataset list
        """

        # Fake answer definition
        httpretty.register_uri(
            httpretty.GET,
            '%s/dataset' % ROOT_URL,
            body="""[{"name":"dataset_MAM1","description":"1st test dataset"},
                 {"name":"datasetMAM1","description":"1st test dataset"},
                 {"name":"test_data_PHC","description":"test dataset"}]""",
            status=200,
            content_type='text/json'
        )

        results = IkatsApi.ds.list()

        self.assertEqual(len(results), 3)

    @fake_server
    def test_ds_list_empty(self):
        """
        Get a TS from valid meta data
        """

        # Fake answer definition
        httpretty.register_uri(
            httpretty.GET,
            '%s/dataset' % ROOT_URL,
            body='[]',
            status=200,
            content_type='text/json'
        )

        results = IkatsApi.ds.list()

        self.assertEqual(len(results), 0)

    @fake_server
    def test_ds_create(self):
        """
        Tests the import of a data set (nominal)
        """

        # Fake answer definition
        httpretty.register_uri(
            httpretty.POST,
            '%s/dataset/import/id_of_data_set' % ROOT_URL,
            body='OK',
            status=200
        )

        results = IkatsApi.ds.create('id_of_data_set', 'description of my data set', ['TSUID1', 'TSUID2', 'TSUID3'])

        self.assertTrue(results)

    @fake_server
    def test_ds_read_nominal(self):
        """
        Request for a data set which exists in Ikats
        """

        # Fake answer definition
        httpretty.register_uri(
            httpretty.GET,
            '%s/dataset/id_of_data_set' % ROOT_URL,
            body="""{"name":"id_of_data_set","description":"description of my data set","tsuids":
                 [{"tsuid":"TSUID1"},{"tsuid":"TSUID2"},{"tsuid":"TSUID3"}],
                 "tsuidsAsString":["TSUID1","TSUID2","TSUID3"]}""",
            status=200,
            content_type='text/json'
        )

        dataset = IkatsApi.ds.read('id_of_data_set')
        self.assertEqual(dataset['ts_list'], ['TSUID1', 'TSUID2', 'TSUID3'])
        self.assertEqual(dataset['description'], 'description of my data set')

    @fake_server
    def test_ds_read_unknown(self):
        """
        Request for a data set which doesn't exist in Ikats
        """

        # Fake answer definition
        httpretty.register_uri(
            httpretty.GET,
            '%s/dataset/unknown_data_set' % ROOT_URL,
            body='dataset with id : unknown_data_set not found on server',
            status=404
        )

        dataset = IkatsApi.ds.read('unknown_data_set')

        self.assertEqual(dataset['ts_list'], [])
        self.assertEqual(dataset['description'], None)

    @fake_server
    def test_ds_delete(self):
        """
        Request to remove an existing data set
        """

        # Fake answer definition
        httpretty.register_uri(
            httpretty.DELETE,
            '%s/dataset/id_of_data_set' % ROOT_URL,
            body='Deletion of dataSet id_of_data_set OK',
            status=200
        )

        status = IkatsApi.ds.delete('id_of_data_set')
        self.assertTrue(status)

    @fake_server
    def test_ds_delete_unknown(self):
        """
        Trying to remove an unknown data set
        No difference with removing an existing data set
        """

        # Fake answer definition
        httpretty.register_uri(
            httpretty.DELETE,
            '%s/dataset/unknown data set' % ROOT_URL,
            body='Deletion of dataSet unknown data set OK',
            # Even if the data_set is unknown, the deletion operation is a success
            status=200
        )
        status = IkatsApi.ds.delete('unknown data set')

        self.assertTrue(status)

    @mock.patch('ikats.core.resource.client.TemporalDataMgr.get_tsuid_from_func_id', get_tsuid_from_func_id_mock)
    @mock.patch('ikats.core.resource.client.TemporalDataMgr.get_fid', get_fid_mock)
    @mock.patch('ikats.core.resource.client.TemporalDataMgr.import_meta_data', import_meta_data_mock)
    @mock.patch('ikats.core.resource.client.TemporalDataMgr.get_meta_data', get_meta_data_mock)
    def test_ts_create(self):
        """
        Tests the creation of a TS via Ikats API
        """
        fid = "test_fid"
        data = np.array([
            [1450772111000, 1.0],
            [1450772112000, 2.0],
            [1450772113000, 3.0],
            [1450772114000, 5.0],
            [1450772115000, 8.0],
            [1450772116000, 13.0]
        ])
        results = None
        try:
            results = IkatsApi.ts.create(fid=fid, data=data)
            self.assertEqual(len(data), results['numberOfSuccess'])
        finally:
            # Delete the TS to cleanup the database
            if results is not None:
                IkatsApi.ts.delete(results['tsuid'], no_exception=True)

    @mock.patch('ikats.core.resource.client.TemporalDataMgr.get_tsuid_from_func_id', get_tsuid_from_func_id_mock)
    @mock.patch('ikats.core.resource.client.TemporalDataMgr.import_meta_data', import_meta_data_mock)
    @mock.patch('ikats.core.resource.client.TemporalDataMgr.get_meta_data', get_meta_data_mock)
    def test_ts_create_inheritance(self):
        """
        Tests the creation of a TS via Ikats API with inheritance of original metadata
        """
        fid = "test_ts_create_inheritance_fid"
        parent_tsuid = "test_ts_create_inheritance_parent"
        data = np.array([
            [1450772111000, 1.0],
            [1450772112000, 2.0],
            [1450772113000, 3.0],
            [1450772114000, 5.0],
            [1450772115000, 8.0],
            [1450772116000, 13.0]
        ])

        # Fill mocked parent meta data
        IkatsApi.md.create(tsuid=parent_tsuid, name='ATA', value=32, force_update=True)
        IkatsApi.md.create(tsuid=parent_tsuid, name='FlightId', value=12345, force_update=True)
        IkatsApi.md.create(tsuid=parent_tsuid, name='ikats_start_date', value='1234567890000', force_update=True)
        IkatsApi.md.create(tsuid=parent_tsuid, name='metric', value='sensor1', force_update=True)
        IkatsApi.md.create(tsuid=parent_tsuid, name='qual_nb_points', value=500, force_update=True)

        results = None
        try:
            results = IkatsApi.ts.create(fid=fid, data=data, parent=parent_tsuid)

            # Check that the funcId has not been overriden by parent inheritance
            self.assertEqual(fid, results['funcId'])
            # Check that the new ts is filled with inherited properties
            metadata = IkatsApi.md.read(fid)
            self.assertEqual(32, metadata[results['tsuid']]['ATA'])
            self.assertEqual(12345, metadata[results['tsuid']]['FlightId'])
            self.assertEqual('sensor1', metadata[results['tsuid']]['metric'])
            # Check that the new ts has not inherited of non-inheritable properties
            self.assertNotEqual('1234567890000', metadata[results['tsuid']]['ikats_start_date'])
            self.assertNotEqual(32, metadata[results['tsuid']]['qual_nb_points'])
        finally:
            # Delete the TS to cleanup the database
            IkatsApi.ts.delete(results['tsuid'], no_exception=True)

    @mock.patch('ikats.core.resource.client.TemporalDataMgr.get_tsuid_from_func_id', get_tsuid_from_func_id_mock)
    @mock.patch('ikats.core.resource.client.TemporalDataMgr.import_meta_data', import_meta_data_mock)
    @mock.patch('ikats.core.resource.client.TemporalDataMgr.get_meta_data', get_meta_data_mock)
    def test_properties_inheritance(self):
        """
        Tests the inheritance of original TSUID
        """

        fid = "test_properties_inheritance_fid"
        parent_tsuid = "test_properties_inheritance_parent"

        data = np.array([
            [1450772111000, 1.0],
            [1450772112000, 2.0],
            [1450772113000, 3.0],
            [1450772114000, 5.0],
            [1450772115000, 8.0],
            [1450772116000, 13.0]
        ])

        # Fill mocked parent meta data
        IkatsApi.md.create(tsuid=parent_tsuid, name='ATA', value=32, force_update=True)
        IkatsApi.md.create(tsuid=parent_tsuid, name='FlightId', value=12345, force_update=True)
        IkatsApi.md.create(tsuid=parent_tsuid, name='ikats_start_date', value='1234567890000', force_update=True)
        IkatsApi.md.create(tsuid=parent_tsuid, name='metric', value='sensor1', force_update=True)
        IkatsApi.md.create(tsuid=parent_tsuid, name='qual_nb_points', value=500, force_update=True)

        results = None
        try:
            results = IkatsApi.ts.create(fid=fid, data=data)

            IkatsApi.ts.inherit(results['tsuid'], parent_tsuid)

            # Check that properties are now well inherited
            metadata = IkatsApi.md.read(fid)
            self.assertEqual(32, metadata[results['tsuid']]['ATA'])
            self.assertEqual(12345, metadata[results['tsuid']]['FlightId'])
            self.assertEqual('sensor1', metadata[results['tsuid']]['metric'])
            # Check that the new ts has not inherited of non-inheritable properties
            self.assertNotEqual('1234567890000', metadata[results['tsuid']]['ikats_start_date'])
            self.assertNotEqual(32, metadata[results['tsuid']]['qual_nb_points'])

        finally:
            # Delete the TS to cleanup the database
            if results is not None:
                IkatsApi.ts.delete(results['tsuid'], no_exception=True)

    @fake_server
    def test_ts_delete(self):
        """
        Request to remove an existing timeseries
        """

        # Fake answer definition
        httpretty.register_uri(
            httpretty.DELETE,
            '%s/ts/tsuid' % ROOT_URL,
            body='Deletion of timeseries tsuid OK',
            status=204
        )

        IkatsApi.ts.delete('tsuid')

    @fake_server
    def test_ts_read(self):
        """
        Tests the extraction of metric data points without knowing the start date and end date (but meta data contain
        these dates)
        """

        META_DATA_LIST.clear()

        # Fake answer definition
        httpretty.register_uri(
            httpretty.GET,
            '%s/metadata/list/json?tsuid=00001600000300077D0000040003F1' % ROOT_URL,
            body="""[{"id":12,"tsuid":"00001600000300077D0000040003F1","name":"ikats_start_date","value":"10000"},
                 {"id":13,"tsuid":"00001600000300077D0000040003F1","name":"flight","value":"AF2042"},
                 {"id":14,"tsuid":"00001600000300077D0000040003F1","name":"ikats_end_date","value":"50000"}]""",
            status=200,
            content_type='text/json'
        )

        # Fake answer definition
        httpretty.register_uri(
            httpretty.POST,
            re.compile(".*TemporalDataManagerWebApp/webapi/metadata/import/.*"),
            body='',
            status=200,
        )
        # Fake answer definition
        httpretty.register_uri(
            httpretty.POST,
            '%s/metadata/import/00001600000300077D0000040003F1/ikats_end_date/*' % ROOT_URL,
            body='',
            status=200,
        )

        # Fake answer definition
        httpretty.register_uri(
            httpretty.GET,
            re.compile('%s/query' % DIRECT_ROOT_URL),
            body="""[{"tsuid":"00001600000300077D0000040003F1","tags":{"aircraftIdentifier":"A320001"},
                 "aggregateTags":["flightIdentifier"],"dps":{"10000":8.164285714285715,"20000":0.0}}]""",
            status=200,
            content_type='text/json'
        )

        results = IkatsApi.ts.read(tsuid_list=["00001600000300077D0000040003F1"])

        # The previous request shall return points
        self.assertGreater(len(results), 0)

        # No new meta data stored
        self.assertEqual(META_DATA_LIST, {})

    @fake_server
    def test_ts_find_from_meta_empty(self):
        """
        Get a TS from empty meta data
        """

        # Fake answer definition
        httpretty.register_uri(
            httpretty.GET,
            '%s/metadata/tsmatch' % ROOT_URL,
            body='["TS1", "TS2", "TS3"]',
            # Even if the data_set is unknown, the operation is a success
            status=200,
            content_type='application/json'
        )

        results = IkatsApi.ts.find_from_meta()

        self.assertGreater(len(results), 0)

    @fake_server
    def test_ts_find_with_param(self):
        """
        Get a TS from valid meta data
        """

        # Fake answer definition
        httpretty.register_uri(
            httpretty.GET,
            '%s/metadata/tsmatch' % ROOT_URL,
            body='["TS1","TS2","TS3"]',
            # Even if the data_set is unknown, the operation is a success
            status=200,
            content_type='text/json'
        )

        results = IkatsApi.ts.find_from_meta({'cycle': ['takeoff', 'landing']})

        self.assertGreater(len(results), 0)

    @fake_server
    def test_ts_find_no_results(self):
        """
        Get a TS from valid meta data
        """

        # Fake answer definition
        httpretty.register_uri(
            httpretty.GET,
            '%s/metadata/tsmatch' % ROOT_URL,
            body='[]',
            # Even if the data_set is unknown, the operation is a success
            status=200,
            content_type='text/json'
        )

        results = IkatsApi.ts.find_from_meta({'unknown_meta': '42'})

        self.assertEqual(len(results), 0)

    @fake_server
    def test_ts_list(self):
        """
        Get a TS from valid meta data
        """

        # Fake answer definition
        httpretty.register_uri(
            httpretty.GET,
            '%s/ts/tsuid' % ROOT_URL,
            body="""[{"tsuid":"poc.sinusoide.outliers","metric":"000001000001000001000002000002"},
                 {"tsuid":"poc.sinusoide.outliers","metric":"000001000001000001000002000003"},
                 {"tsuid":"poc.sinusoide.outliers","metric":"000001000001000001000002000004"},
                 {"tsuid":"poc.sinusoide.outliers","metric":"000001000001000001000002000005"},
                 {"tsuid":"poc.sinusoide.outliers","metric":"000001000001000001000002000006"},
                 {"tsuid":"poc.sinusoide.outliers","metric":"000001000001000001000002000007"},
                 {"tsuid":"poc.sinusoide.outliers","metric":"000001000001000001000002000008"}]""",
            status=200,
            content_type='text/json'
        )

        results = IkatsApi.ts.list()

        self.assertEqual(len(results), 7)

    @fake_server
    def test_ts_list_empty(self):
        """
        Get a TS from valid meta data
        """

        # Fake answer definition
        httpretty.register_uri(
            httpretty.GET,
            '%s/ts/tsuid' % ROOT_URL,
            body='[]',
            status=200,
            content_type='text/json'
        )

        results = IkatsApi.ts.list()

        self.assertEqual(len(results), 0)
