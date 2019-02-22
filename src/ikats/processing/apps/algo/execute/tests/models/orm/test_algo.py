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
import logging
import time

from django.test import TestCase as DjTestCase

from apps.algo.catalogue.models.business.implem import Implementation
from apps.algo.custom.models.business.algo import CustomizedAlgo
from apps.algo.execute.models.business.algo import ExecutableAlgo
from apps.algo.execute.models.orm.algo import ExecutableAlgoDao
from ikats.core.library.status import State as EnumState

LOGGER = logging.getLogger(__name__)


class TestExecutableAlgoDaoCRUD(DjTestCase):
    """
    Tests the CRUD of Algorithm execution engine
    """

    @classmethod
    def setUpTestData(cls):
        """
        setUpClass: this setup is made once for several tests_ methods

        operational database is not impacted by the Django unittests
        """
        cls.main_name = "TestExecutableAlgoDaoCRUD"

    def test_seq1_create(self):
        """
        Tests the creation of Algorithm execution
        """
        # even if unused: create stub data for Implementation
        my_impl_fake = Implementation(name="TU Fake Impl", description="TU fake",
                                      execution_plugin="TU fake",
                                      library_address="TU Fake",
                                      input_profile=None,
                                      output_profile=None,
                                      db_id=None)

        # even if unused: create stub data for CustomizedAlgo
        my_custom_algo_fake = CustomizedAlgo(arg_implementation=my_impl_fake, custom_params=None)

        current_date = time.time()
        LOGGER.info("Current date %s", current_date)
        my_exec_algo = ExecutableAlgo(
            custom_algo=my_custom_algo_fake, dict_data_sources={}, dict_data_receivers={}, arg_process_id=None)

        string_algo_before = my_exec_algo.as_detailed_string()

        LOGGER.info("creation date= %s", my_exec_algo.creation_date)

        nb_init = ExecutableAlgoDao.objects.count()
        LOGGER.info("After test_seq1_create: ImplementationDao count = %s", nb_init)

        my_exec_algo_created = ExecutableAlgoDao.create(my_exec_algo, merge_with_unsaved_data=True)

        string_algo_after = my_exec_algo_created.as_detailed_string()

        LOGGER.info("Before creation: %s", string_algo_before)
        LOGGER.info("After  creation: %s", string_algo_after)

        my_exec_algo_created.trigger_start_execution_date()
        LOGGER.info("Triggered start: %s", my_exec_algo_created.as_detailed_string())

        my_exec_algo_created.trigger_end_execution_date()
        LOGGER.info("Triggered end  : %s", my_exec_algo_created.as_detailed_string())

        my_exec_algo_created.state = EnumState.ALGO_KO

        string_algo_state_updated = my_exec_algo_created.as_detailed_string()
        LOGGER.info("State updated  : %s", string_algo_state_updated)

        nb_after = ExecutableAlgoDao.objects.count()

        self.assertEqual(nb_init + 1, nb_after, "count in DB: expected: nb_init + 1 == nb_after")

    @staticmethod
    def test_seq2_update():
        """
        Tests the update of Algorithm execution
        """
        # even if unused: create stub data for Implementation
        my_impl_fake = Implementation(name="TU Fake Impl", description="TU fake",
                                      execution_plugin="TU fake",
                                      library_address="TU Fake",
                                      input_profile=None,
                                      output_profile=None,
                                      db_id=None)

        # even if unused: create stub data for CustomizedAlgo
        my_custom_algo_fake = CustomizedAlgo(arg_implementation=my_impl_fake, custom_params=None)

        current_date = time.time()
        LOGGER.info("Current date %s", current_date)
        my_exec_algo = ExecutableAlgo(
            custom_algo=my_custom_algo_fake, dict_data_sources={}, dict_data_receivers={}, arg_process_id=None)

        # ignore unsaved data here : we test the update in database
        my_exec_algo_created = ExecutableAlgoDao.create(my_exec_algo, merge_with_unsaved_data=False)

        string_algo_before = my_exec_algo_created.as_detailed_string()

        LOGGER.info("DB Before update: %s", string_algo_before)

        my_exec_algo_created.trigger_start_execution_date()
        my_exec_algo_created.trigger_end_execution_date()
        my_exec_algo_created.state = EnumState.ALGO_OK

        string_algo_business_updated = my_exec_algo_created.as_detailed_string()
        LOGGER.info("Business updated: %s", string_algo_business_updated)

        my_exec_algo_updated = ExecutableAlgoDao.update(my_exec_algo_created, merge_with_unsaved_data=False)
        string__db_updated = my_exec_algo_updated.as_detailed_string()

        LOGGER.info("DB updated      : %s", string__db_updated)

    @staticmethod
    def test_seq3_read():
        """
        Tests the read of Algorithm execution status
        """
        # even if unused: create stub data for Implementation
        my_impl_fake = Implementation(name="TU Fake Impl", description="TU fake",
                                      execution_plugin="TU fake",
                                      library_address="TU Fake",
                                      input_profile=None,
                                      output_profile=None,
                                      db_id=None)

        # even if unused: create stub data for CustomizedAlgo
        my_custom_algo_fake = CustomizedAlgo(arg_implementation=my_impl_fake, custom_params=None)

        current_date = time.time()
        LOGGER.info("Current date %s", current_date)
        my_exec_algo = ExecutableAlgo(
            custom_algo=my_custom_algo_fake, dict_data_sources={}, dict_data_receivers={}, arg_process_id=None)

        my_exec_algo.trigger_start_execution_date()
        my_exec_algo.trigger_end_execution_date()
        my_exec_algo.state = EnumState.ALGO_OK

        # ignore unsaved data here : we test the update in database
        my_exec_algo_created = ExecutableAlgoDao.create(my_exec_algo, merge_with_unsaved_data=False)
        string_algo_before = my_exec_algo_created.as_detailed_string()
        LOGGER.info("DB Before read  : %s", string_algo_before)

        my_exec_algo_read = ExecutableAlgoDao.find_from_key(my_exec_algo_created.process_id)
        string_db_read = my_exec_algo_read.as_detailed_string()

        LOGGER.info("DB after read   : %s", string_db_read)
