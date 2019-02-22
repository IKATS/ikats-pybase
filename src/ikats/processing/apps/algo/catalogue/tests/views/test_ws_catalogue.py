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

from django.test import TestCase

from apps.algo.catalogue.models.business.implem import Implementation
from apps.algo.catalogue.models.business.profile import ProfileItem, Argument
from apps.algo.catalogue.models.orm.implem import ImplementationDao
from apps.algo.catalogue.models.ws.implem import ImplementationWs
from apps.algo.catalogue.tests.tu_commons import CommonsCatalogueTests


class TestWsCatalogue(TestCase, CommonsCatalogueTests):
    """
    TU with
        Django pseudo-Http-Client tool for test units on catalogue
    """

    @classmethod
    def setUpTestData(cls):
        """
        setUpClass: this setup is made once for several tests_ methods

        operational database is not impacted by the Django unittests
        """
        cls.init_tu()
        arg_one = Argument("angle", "angle (rad)", ProfileItem.DIR.INPUT, 0)
        res_one = Argument("result", "cos(angle)", ProfileItem.DIR.OUTPUT, 0)

        cls.my_cosinus = Implementation(
            "TU WS Python Standard cosinus", "Python cosinus from math::cos",
            "apps.algo.execute.models.business.python_local_exec_engine::PythonLocalExecEngine",
            "math::cos", [arg_one], [res_one])

    @classmethod
    def tearDownClass(cls):
        cls.commons_tear_down_class()

        super(TestWsCatalogue, cls).tearDownClass()
        # It is important to call superclass

    def test_to_dict(self):
        """
        Tests the json-friendly python dict produced by to_dict() method on ImplementationWs instance:
          - Test made with TestWsCatalogue.my_cosinus
        """

        bizz_impl = ImplementationDao.create(TestWsCatalogue.my_cosinus)

        ws_impl = ImplementationWs(bizz_impl)

        my_dict = ws_impl.to_dict()

        self.info(json.dumps(obj=my_dict, indent=2))

        # reference hard-coded: id may be different
        ref_dict = {
            "is_customized": False,
            "outputs": [
                {
                    "type": None,
                    "name": "result",
                    "order_index": 0,
                    "domain": None,
                    "label": "result",
                    "description": "cos(angle)"
                }
            ],
            "parameters": [],
            "algo": None,
            "name": "TU WS Python Standard cosinus",
            "label": "TU WS Python Standard cosinus",
            "description": "Python cosinus from math::cos",
            "id": 11,
            "inputs": [
                {
                    "type": None,
                    "name": "angle",
                    "order_index": 0,
                    "domain": None,
                    "label": "angle",
                    "description": "angle (rad)"
                }
            ],
            "family": None,
            "visibility": True
        }
        self.assertTrue(type(my_dict) is dict)
        self.assertEqual(my_dict['id'], bizz_impl.db_id)
        self.assertEqual(my_dict['is_customized'], False)

        # correct ID before comparing ref_dict with my_dict
        ref_dict['id'] = my_dict['id']
        self.assertDictEqual(my_dict, ref_dict, "my_dict differs from expected ref_dict")

    def test_from_dict(self):
        """
        Tests that ImplementationWs object is correctly loaded from a json-friendly dict
        """

        # Prepare data ...
        bizz_impl = ImplementationDao.create(TestWsCatalogue.my_cosinus)

        ws_impl = ImplementationWs(bizz_impl)
        my_dict = ws_impl.to_dict()

        # ... apply load_from_dict
        loaded_ws_impl = ImplementationWs.load_from_dict(my_dict)

        # ... assert that loaded business is the same than bizz_impl
        loaded_bizz_impl = loaded_ws_impl.model_business

        self.assertTrue(loaded_bizz_impl == bizz_impl)
