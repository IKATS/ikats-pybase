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

from logging import StreamHandler
import logging
import sys
import unittest
from ikats_processing.core.resource_config import ResourceClientSingleton

LOGGER = logging.getLogger(__name__)

# Defines the log level to DEBUG
LOGGER.setLevel(logging.DEBUG)

# Create the handler to a file, append mode, 3 backups, max size = 1Mo
FILE_HANDLER = StreamHandler(sys.stdout)
FILE_HANDLER.setLevel(logging.DEBUG)
LOGGER.addHandler(FILE_HANDLER)


class Test(unittest.TestCase):
    """
    Tests the client of
    """
    IMPORTED_TSUIDS = ["00001F00000B000BFE", "00008300000B000BFF", "00008400000B000C08"]
    IMPORTED_FUNC_IDS = ["azerty_max", "azerty_max2", "azerty_funcid"]

    EXPECTED_FUNC_IDS = {"00001F00000B000BFE": "azerty_max",
                         "00008300000B000BFF": "azerty_max2",
                         "00008400000B000C08": "azerty_funcid"}

    EXPECTED_TSUIDS = {"azerty_max": "00001F00000B000BFE",
                       "azerty_max2": "00008300000B000BFF",
                       "azerty_funcid": "00008400000B000C08"}

    @unittest.skip("ignored TU on PIC [test_search_func_id] (could be useful for dev tests)")
    def test_search_func_id(self):
        LOGGER.info(ResourceClientSingleton.get_singleton())

        try:
            self.__get_functional_identifier_from_tsuid(self.IMPORTED_TSUIDS[0], self.IMPORTED_FUNC_IDS[0])

            # all tsuids are retrieved
            self.__get_fid_from_tsuids(self.IMPORTED_TSUIDS, self.IMPORTED_FUNC_IDS)

            # tsuids partially retrieved
            self.__get_fid_from_tsuids(
                [self.IMPORTED_TSUIDS[0], 'foto'], [self.IMPORTED_FUNC_IDS[0]])

        except Exception as error:
            LOGGER.info("TU failed with %s %s", type(error), error)
            LOGGER.error(error)
            self.fail("KO: unexpected error for nominal tests")

        try:
            self.__get_fid_from_tsuids(
                ['toto', 'foto'], ['', ''])
            self.fail("KO: degraded test not found: no error raised !")
        except ValueError as mismatched:
            LOGGER.info("OK: degraded test: nice error: %s", mismatched.__str__())
        except Exception as unexpected:
            LOGGER.info("TU failed with %s %s", type(unexpected), unexpected)
            LOGGER.error(unexpected)
            self.fail("KO: degraded test not found: wrong error")

    @unittest.skip("ignored TU on PIC [test_search_tsuid_from_funcid] (could be useful for dev tests)")
    def test_search_tsuid_from_funcid(self):
        """
        Comment @unittest.skip to activate this test:
        => launch test plugged with configured connection in ikats_processing.urls
        (temporary choice) => effective connection to the resource server

        !!!!PLEASE: REMOVE COMMENT BEFORE COMMITTING THIS SOURCE IN SVN => may disturb the PIC !!!!
        """

        LOGGER.info(ResourceClientSingleton.get_singleton())

        try:
            self.__get_fid_from_funcId(self.IMPORTED_FUNC_IDS[0], self.IMPORTED_TSUIDS[0])

            # all funcIds are retrieved
            self.__get_fid_from_funcIds(self.IMPORTED_FUNC_IDS, self.IMPORTED_TSUIDS)

            # funcIds partially retrieved
            self.__get_fid_from_funcIds(
                [self.IMPORTED_FUNC_IDS[0], 'toto'], [self.IMPORTED_TSUIDS[0]])

        except Exception as error:
            LOGGER.info("TU failed with %s %s", type(error), error)
            LOGGER.error(error)
            self.fail("KO: unexpected error for nominal tests")

        try:
            self.__get_fid_from_funcIds(
                ['toto', 'foto'], ['', ''])
            self.fail("KO: degraded test not found: no error raised !")
        except ValueError as mismatched:
            LOGGER.info("OK: degraded test: nice error: %s", mismatched.__str__())
        except Exception as unexpected:
            LOGGER.info("TU failed with %s %s", type(unexpected), unexpected)
            LOGGER.error(unexpected)
            self.fail("KO: degraded test not found: wrong error")

    def __get_fid_from_tsuids(self, tsuids, expected_functional_ids):

        LOGGER.info("__get_fid_from_tsuids: tsuid list= %s", tsuids.__str__())

        my_manager = ResourceClientSingleton.get_singleton().get_temporal_manager()
        res = my_manager.search_functional_identifiers("tsuids", tsuids)

        self.assertTrue(len(expected_functional_ids) == len(res))

        for res_item in res:
            res_tsuid = res_item['tsuid']
            res_funcid = res_item['funcId']
            self.assertEqual(res_funcid, self.EXPECTED_FUNC_IDS[res_tsuid])

        LOGGER.info("__get_fid_from_tsuids: res= %s", res.__str__())

    def __get_fid_from_funcIds(self, func_ids, expected_tsuids):

        LOGGER.info("__get_fid_from_funcIds: funcId list= %s", func_ids.__str__())

        my_manager = ResourceClientSingleton.get_singleton().get_temporal_manager()
        res = my_manager.search_functional_identifiers("func_ids", func_ids)

        self.assertTrue(len(expected_tsuids) == len(res))

        for res_item in res:
            res_tsuid = res_item['tsuid']
            res_funcid = res_item['funcId']
            self.assertEqual(res_tsuid, self.EXPECTED_TSUIDS[res_funcid])

        LOGGER.info("__get_fid_from_funcIds: res= %s", res.__str__())

    def __get_fid_from_funcId(self, func_id, expected_tsuid):

        my_manager = ResourceClientSingleton.get_singleton().get_temporal_manager()
        res = my_manager.get_tsuid_from_func_id(func_id)

        LOGGER.info("__get_fid_from_funcId=%s : %s", func_id, res.__str__())
        self.assertEqual(expected_tsuid, res)


if __name__ == "__main__":
    unittest.main()
