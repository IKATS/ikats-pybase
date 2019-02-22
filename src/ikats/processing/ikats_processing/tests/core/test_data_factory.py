"""
Copyright 2018-2019 CS Systèmes d'Information

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
from logging import StreamHandler
import logging
import sys
import unittest

from ikats.core.data.ts import TimestampedMonoVal
from ikats_processing.core.data.tsref import TsuidTsRef
from ikats_processing.core.data_factory import TsFactory, TsRefFactory
from ikats_processing.core.resource_config import ResourceClientSingleton

LOGGER = logging.getLogger(__name__)

# Defines the log level to DEBUG
LOGGER.setLevel(logging.DEBUG)

# Create the handler to a file, append mode, 3 backups, max size = 1Mo
FILE_HANDLER = StreamHandler(sys.stdout)
FILE_HANDLER.setLevel(logging.DEBUG)
LOGGER.addHandler(FILE_HANDLER)


class TestDataFactory(unittest.TestCase):
    """
    Test of the data factory
    """
    @unittest.skip("ignored TU on PIC [test_extract_import] (could be useful for dev tests)")
    def test_extract_import(self):
        LOGGER.info(ResourceClientSingleton.get_singleton())

        my_manager = ResourceClientSingleton.get_singleton().get_temporal_manager()

        ts_data_ref = TsuidTsRef(
            arg_tsuid="000074000009000B1E", arg_start_date=1450572606000, arg_end_date=1450709406000)

        ts_factory = TsFactory()

        data = ts_factory.read_ts_from_temporal_db(ts_ref=ts_data_ref,
                                                   timeseries_class=TimestampedMonoVal,
                                                   tmp_mgr=my_manager)
        LOGGER.info("Extracted data:")
        LOGGER.info(str(data.data))

        ts_ref_factory = TsRefFactory()

        data_ref, status = ts_ref_factory.write_ts_into_temporal_db(
            tmp_mgr=my_manager, ts=data,
            metric="TestDataFactory_import",
            output_func_id="TestDataFactory_import_output_func_id",
            tags_dict={"num_exec": "TestDataFactory_import_1"})

        LOGGER.info("Imported tsuid ref: %s", str(data_ref))
        LOGGER.info("Import status: %s", str(status))
