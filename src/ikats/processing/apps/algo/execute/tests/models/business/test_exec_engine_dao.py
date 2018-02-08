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
"""
import json
import logging
# from numbers import Number
import time

from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import RequestFactory

from apps.algo.catalogue.models.business.factory import FactoryCatalogue

from apps.algo.custom.models.business.check_engine import CheckEngine
from apps.algo.custom.models.ws.algo import CustomizedAlgoWs
from apps.algo.custom.tests.tu_commons import CommonsCustomTest

from apps.algo.execute.models.business.exec_engine import ExecStatus

from apps.algo.execute.models.business.python_local_exec_engine import PythonLocalExecEngine
from apps.algo.execute.tests.models.business.test_python_local_exec_engine import init_basic_exec_algo
from apps.algo.execute.views.algo import run as views_algo_run
from ikats.core.library.status import State as EnumState

from ikats.core.json_util.rest_utilities import LevelInfo
from ikats_processing.core.http import HttpResponseFactory
from ikats_processing.core.json import decode as json_io

LOGGER = logging.getLogger(__name__)


class TestExecEngineWithDao(TestCase):
    """
    Tests the Execution engine through the DAO
    """

    def test_execute_dao_cosinus(self):

        local_variable = 0.0

        my_exec_algo = init_basic_exec_algo(lib_path="math::cos",
                                            in_argnames_list=["angle"],
                                            input_arg_value_list=[local_variable],
                                            out_argnames_list=["res"])
        exec_engine = PythonLocalExecEngine(executable_algo=my_exec_algo, debug=True, dao_managed=True)

        self.assertListEqual(my_exec_algo.get_ordered_input_names(), ["angle"])
        self.assertListEqual(my_exec_algo.get_ordered_output_names(), ["res"])

        status = exec_engine.execute()

        self.assertIsInstance(status, ExecStatus, "Failed to retrieve status")

        try:
            self.assertTrue(exec_engine.get_executable_algo().state == EnumState.ALGO_OK)
        except Exception:
            LOGGER.error(status.error)
            LOGGER.exception(status.error)
            raise status.error

        # Command has results
        my_res = my_exec_algo.get_data_receiver("res").get_received_value()
        self.assertTrue((1.0 - my_res) < 0.1e-10, "cos(0.0) = 1.0")


class TestExecEngineWithCheckEngine(TestCase, CommonsCustomTest):
    """
    Tests the engine with its checker
    """

    @classmethod
    def setUpTestData(cls):
        super(TestExecEngineWithCheckEngine, cls).init_tu()
        cls.prepare_custom_database()
        CheckEngine.set_checking_rules(FactoryCatalogue.TYPE_CHECKING_FUNCTIONS)
        cls.request_factory = RequestFactory()

    @classmethod
    def tearDownClass(cls):
        cls.commons_tear_down_class()

        super(TestExecEngineWithCheckEngine, cls).tearDownClass()
        # It is important to call superclass

    def test_checked_exec_nominal_seq1(self):
        """
        Tests that the nominal execution on one CustomizedAlgo consistent with its Implementation:
          - is executed in nominal mode (no tests about Python execution: tested by another Test unit)
        Note: this unit test is testing the expected error code.
        TODO: complete this test: evaluate that response body is empty
        """
        angle = 1.58

        my_custom = self.init_resource_named("Custom for created at {}".format(time.time()),
                                             save_in_db=True)

        my_id = my_custom.db_id

        my_async = False
        my_opts = {'async': my_async, 'custo_algo': my_id, 'debug': True}

        my_args = {'angle': angle}

        my_data = {'opts': my_opts, 'args': my_args}

        # self.info("- Implem ={}".format( my_custom.implementation ) )
        self.info("- Custom ={}".format(CustomizedAlgoWs(my_custom).to_json(indent=2, level=LevelInfo.DETAIL)))
        self.info("- data ={}".format(json.dumps(obj=my_data, indent=2)))

        http_req = self.request_factory.post(path=reverse(viewname='algo_run', args=[my_id]),
                                             data=json.dumps(my_data),
                                             content_type="application/json")

        self.info("- data ={}".format(json.dumps(obj=my_data, indent=2)))
        http_response = views_algo_run(http_req, my_id)

        # Display the check result
        result = json_io.decode_json_from_http_response(http_response)

        self.info("response loaded={}".format(result))
        self.info("response status={}".format(http_response.status_code))

        self.assertTrue(http_response.status_code == HttpResponseFactory.OK_HTTP_STATUS)

    def test_checked_exec_errors_seq2(self):
        """
        Test run with
        - customized algo inconsistent with its implementation: 2 wrong specified values
        - run args: angle (no value overriding)
        => CheckEngine detects errors
        Note: this unit test is testing the expected error code.
        """
        angle = 1.58

        # Wrong type : string for factor
        #
        # Wrong value for phase: 5.0 is outside of the domain defined in
        # my_pseudo_impl_with_domain_from_db: [0, 1.1, 2 ]
        #
        # ... checking rule are not activated here:
        my_custom = self.init_resource_named("Custom for created at {}".format(time.time()),
                                             save_in_db=True,
                                             implem=self.my_pseudo_impl_with_domain_from_db,
                                             factor="3",
                                             phase=5.0)

        my_id = my_custom.db_id

        my_async = False
        my_opts = {'async': my_async, 'custo_algo': True, 'debug': True}

        # case where
        # => no parameter value is redefined
        # => only argument angle is specified
        my_args = {'angle': angle}

        my_data = {'opts': my_opts, 'args': my_args}

        # self.info("- Implem ={}".format( my_custom.implementation ) )
        self.info("- Custom ={}".format(CustomizedAlgoWs(my_custom).to_json(indent=2, level=LevelInfo.DETAIL)))
        self.info("- data ={}".format(json.dumps(obj=my_data, indent=2)))

        http_req = self.request_factory.post(path=reverse(viewname='algo_run', args=[my_id]),
                                             data=json.dumps(my_data),
                                             content_type="application/json")

        self.info("- data ={}".format(json.dumps(obj=my_data, indent=2)))
        http_response = views_algo_run(http_req, my_id)

        # Display the check result
        result = json_io.decode_json_from_http_response(http_response)

        self.info("response loaded={}".format(result))
        self.info("response status={}".format(http_response.status_code))

        self.assertTrue(http_response.status_code == HttpResponseFactory.BAD_REQUEST_HTTP_STATUS)

    def test_checked_exec_errors_seq3(self):
        """
        Test run with
        - implementation: see my_pseudo_impl_with_domain_from_db
        - run args: angle + inconsistent phase + inconsistent factor

        => CheckEngine detects errors
        Note: this unit test is testing the expected error code.
        """

        angle = 1.58

        # Outside of domain
        phase = 0.9
        # Wrong type
        factor = "1.4"

        # running case with Implementation:
        #
        my_id = self.my_pseudo_impl_with_domain_from_db.db_id

        my_async = False
        my_opts = {'async': my_async, 'custo_algo': False, 'debug': True}

        # run args: angle + inconsistent phase + inconsistent factor
        #
        my_args = {'angle': angle, 'phase': phase, 'factor': factor}

        my_data = {'opts': my_opts, 'args': my_args}

        self.info("- implem ={}".format(self.my_pseudo_impl_with_domain_from_db))
        self.info("- data ={}".format(json.dumps(obj=my_data, indent=2)))

        http_req = self.request_factory.post(path=reverse(viewname='algo_run', args=[my_id]),
                                             data=json.dumps(my_data),
                                             content_type="application/json")

        self.info("- data ={}".format(json.dumps(obj=my_data, indent=2)))
        http_response = views_algo_run(http_req, my_id)

        # Display the check result
        result = json_io.decode_json_from_http_response(http_response)

        self.info("response loaded={}".format(result))
        self.info("response status={}".format(http_response.status_code))

        self.assertEquals(http_response.status_code, HttpResponseFactory.BAD_REQUEST_HTTP_STATUS)

    def test_checked_exec_nominal_seq4(self):
        """
        Test run with
          - implementation: see my_pseudo_impl_with_domain_from_db
          - run args: angle + consistent phase + consistent factor

        Note: this unit test is testing the expected error code.
        TODO: complete this test: evaluate that response body is empty
        """
        angle = 1.58
        phase = 1.1
        factor = 1.4

        my_id = self.my_pseudo_impl_with_domain_from_db.db_id

        my_async = False
        my_opts = {'async': my_async, 'custo_algo': False, 'debug': True}

        my_args = {'angle': angle, 'phase': phase, 'factor': factor}

        my_data = {'opts': my_opts, 'args': my_args}

        self.info("- implem ={}".format(self.my_pseudo_impl_with_domain_from_db))
        self.info("- data ={}".format(json.dumps(obj=my_data, indent=2)))

        http_req = self.request_factory.post(path=reverse(viewname='algo_run', args=[my_id]),
                                             data=json.dumps(my_data),
                                             content_type="application/json")

        self.info("- data ={}".format(json.dumps(obj=my_data, indent=2)))
        http_response = views_algo_run(http_req, my_id)

        # Display the check result
        result = json_io.decode_json_from_http_response(http_response)

        self.info("response loaded={}".format(result))
        self.info("response status={}".format(http_response.status_code))

        self.assertTrue(http_response.status_code == HttpResponseFactory.OK_HTTP_STATUS)
