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
import json

from django.test.testcases import TestCase

from apps.algo.custom.models.ws.algo import CustomizedAlgoWs
from apps.algo.custom.tests.tu_commons import CommonsCustomTest
from ikats.core.json_util.rest_utilities import LevelInfo


class TestCustomizedAlgoWs(TestCase, CommonsCustomTest):
    """
    Tests the web service of the customized algo
    """
    @classmethod
    def setUpTestData(cls):
        """
        Sets up database globally for the class
        :param cls:
        :type cls:
        """
        super(TestCustomizedAlgoWs, cls).init_tu()
        cls.prepare_custom_database()

    @classmethod
    def tearDownClass(cls):
        """
        Calls the final processing on the class, once all tests are executed
        :param cls:
        :type cls:
        """
        cls.commons_tear_down_class()

        super(TestCustomizedAlgoWs, cls).tearDownClass()
        # It is important to call superclass

    def test_to_dict_normal_seq1(self):
        """
        Tests the building of Normal-leveled json view of CustomizedAlgoWs
        """

        my_custom_ws = CustomizedAlgoWs(self.my_custom_algo_in_DB)

        self.info("- Evaluating my_custom_ws => to_dict(level=LevelInfo.NORMAL): ")
        normal_dict = my_custom_ws.to_dict(level=LevelInfo.NORMAL)
        my_dict_str = json.dumps(obj=normal_dict, indent=2)
        self.info(my_dict_str)

        # Hard-defined reference: a bit long
        # --> start definition of ref_normal_dict ...
        ref_normal_dict = {
            "is_customized": True,
            "name": "Custo1 of my_pseudo_impl_from_db",
            "description": "Custo1 description",
            "inputs": [
                {
                    "domain": None,
                    "name": "angle",
                    "description": "angle (rad)",
                    "type": None,
                    "label": "angle",
                    "order_index": 0
                }
            ],
            "parameters": [
                {
                    "domain": None,
                    "name": "factor",
                    "description": "factor on angle",
                    "default_value": None,
                    "type": "number",
                    "label": "factor",
                    "value": 0.5,
                    "order_index": 1
                },
                {
                    "domain": None,
                    "name": "phase",
                    "description": "added phase constant",
                    "default_value": 0,
                    "type": "number",
                    "label": "phase",
                    "value": 1.5,
                    "order_index": 2
                }
            ],
            "label": "Custo1",
            "family": "TestCustomizedAlgoWs tested family",
            "parent": {
                "label": "TestCustomizedAlgoWs ORM impl for CustomizedAlgo",
                "name": "TestCustomizedAlgoWs ORM impl for CustomizedAlgo",
                "description": "Python tan from math::my_tan",
                "id": 11
            },
            "outputs": [
                {
                    "domain": None,
                    "name": "result",
                    "description": "tan(factor*angle+phase)",
                    "type": None,
                    "label": "result",
                    "order_index": 0
                }
            ],
            "algo": "TestCustomizedAlgoWsmy algo",
            "id": 4,
            "visibility": True
        }
        # ... end definition of ref_normal_dict

        self.assertEqual(normal_dict['parent']['id'],
                         self.my_custom_algo_in_DB.implementation.db_id)

        self.assertEqual(normal_dict['id'],
                         self.my_custom_algo_in_DB.db_id)

        # Needed before comparing dict:
        #    change hard-coded ID values: hard-coded values may be different from IDs from prepared DB
        #
        ref_normal_dict['parent']['id'] = normal_dict['parent']['id']
        ref_normal_dict['id'] = normal_dict['id']
        self.assertDictEqual(ref_normal_dict, normal_dict)

    def test_to_dict_detailed_seq2(self):
        """
        Tests the building of DETAIL-leveled json view
        """

        my_custom_ws = CustomizedAlgoWs(self.my_custom_algo_2_in_DB)

        self.info("- Evaluating my_custom_algo_2_in_DB => to_dict(level=LevelInfo.DETAIL): ")
        detailed_dict = my_custom_ws.to_dict(level=LevelInfo.DETAIL)

        my_dict_str = json.dumps(obj=detailed_dict, indent=2)
        self.info(my_dict_str)

        # Hard-defined reference: a bit long
        # --> start definition of ref_dict ...
        ref_dict = {
            "is_customized": True,
            "execution_plugin": "apps.algo.execute.models.business.python_local_exec_engine::PythonLocalExecEngine",
            "outputs": [
                {
                    "label": "result",
                    "domain": None,
                    "type": None,
                    "name": "result",
                    "order_index": 0,
                    "description": "tan(factor*angle+phase)"
                }
            ],
            "family": "TestCustomizedAlgoWs tested family",
            "label": "Custo2",
            "library_address": "ikats.processing.ikats_processing.tests.test_contrib::my_tan",
            "name": "TestCustomizedAlgoWs Custo2 of my_pseudo_impl_from_db",
            "algo": "TestCustomizedAlgoWsmy algo",
            "inputs": [
                {
                    "label": "angle",
                    "domain": None,
                    "type": None,
                    "name": "angle",
                    "order_index": 0,
                    "description": "angle (rad)"
                }
            ],
            "parameters": [
                {
                    "label": "factor",
                    "value": 0.885,
                    "default_value": None,
                    "domain": None,
                    "type": "number",
                    "name": "factor",
                    "order_index": 1,
                    "description": "factor on angle"
                },
                {
                    "label": "phase",
                    "value": 0.33,
                    "default_value": 0,
                    "domain": None,
                    "type": "number",
                    "name": "phase",
                    "order_index": 2,
                    "description": "added phase constant"
                }
            ],
            "id": 5,
            "description": "Custo2 description",
            "visibility": True,
            "parent": {
                "id": 11,
                "label": "TestCustomizedAlgoWs ORM impl for CustomizedAlgo",
                "name": "TestCustomizedAlgoWs ORM impl for CustomizedAlgo",
                "description": "Python tan from math::my_tan"
            }
        }
        # ... end definition of ref_dict

        self.assertEqual(detailed_dict['parent']['id'],
                         self.my_custom_algo_2_in_DB.implementation.db_id)

        self.assertEqual(detailed_dict['id'],
                         self.my_custom_algo_2_in_DB.db_id)

        # Needed before comparing dict:
        #    change hard-coded ID values:
        #      hard-coded IDS can be different from IDs from prepared DB
        #
        ref_dict['parent']['id'] = detailed_dict['parent']['id']
        ref_dict['id'] = detailed_dict['id']
        self.assertDictEqual(ref_dict, detailed_dict)

    def test_to_dict_summary_seq3(self):
        """
        Tests the building of SUMMARY-leveled json view
        """

        my_custom_ws = CustomizedAlgoWs(self.my_custom_algo_2_in_DB)

        self.info("- Evaluating my_custom_algo_2_in_DB => to_dict(level=LevelInfo.SUMMARY): ")
        summary_dict = my_custom_ws.to_dict(level=LevelInfo.SUMMARY)

        ref_summary_dict = {
            "description": "Custo2 description",
            "label": "Custo2",
            "parent": {
                "description": "Python tan from math::my_tan",
                "label": "TestCustomizedAlgoWs ORM impl for CustomizedAlgo",
                "id": 11,
                "name": "TestCustomizedAlgoWs ORM impl for CustomizedAlgo"
            },
            "name": "TestCustomizedAlgoWs Custo2 of my_pseudo_impl_from_db",
            "family": "TestCustomizedAlgoWs tested family",
            "is_customized": True,
            "id": 5,
            "algo": "TestCustomizedAlgoWsmy algo",
            "visibility": True
        }

        self.info(json.dumps(obj=summary_dict, indent=2))

        self.assertEqual(summary_dict['parent']['id'],
                         self.my_custom_algo_2_in_DB.implementation.db_id)

        self.assertEqual(summary_dict['id'],
                         self.my_custom_algo_2_in_DB.db_id)

        # Needed before comparing dict:
        #    change hard-coded ID values:
        #      hard-coded IDS can be different from IDs from prepared DB
        #
        ref_summary_dict['parent']['id'] = summary_dict['parent']['id']
        ref_summary_dict['id'] = summary_dict['id']

        self.assertDictEqual(ref_summary_dict, summary_dict)

    def test_load_from_dict_seq4(self):
        """
        Nominal test of load_from_dict()
        """

        my_custom_ws = CustomizedAlgoWs(self.my_custom_algo_in_DB)
        normal_dict = my_custom_ws.to_dict(level=LevelInfo.NORMAL)

        self.info("- Evaluating my_custom_algo_in_DB => CustomizedAlgoWs.load_from_dict(...)")
        loaded_ws_resource = CustomizedAlgoWs.load_from_dict(normal_dict)

        my_business_custo = loaded_ws_resource.get_customized_algo()
        self.info(" - uploaded custom_algo={}".format(my_business_custo))

        self.assertTrue(my_business_custo == self.my_custom_algo_in_DB)
