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

from django.test import TestCase

from apps.algo.catalogue.models.business.implem import Implementation
from apps.algo.catalogue.models.business.profile import Argument, ProfileItem, Parameter
from apps.algo.catalogue.models.orm.implem import ImplementationDao
from apps.algo.custom.models.business.params import CustomizedParameter
from apps.algo.custom.models.orm.algo import CustomizedAlgo, CustomizedAlgoDao
from apps.algo.custom.tests.tu_commons import CommonsCustomTest
from ikats.core.library.exception import IkatsException
from ikats.processing.apps.algo.catalogue.tests.tu_commons import CommonsCatalogueTests


class TestCustomizedAlgoDao(TestCase, CommonsCatalogueTests):
    """
    Test file for the classes CustomizedAlgo and CustomizedParameterDao
    """

    @classmethod
    def setUpTestData(cls):
        super(TestCustomizedAlgoDao, cls).init_tu()
        cls.prepare_catalogue_data()
        # activates the info level: just change to logging.INFO to have a more verbose log in dev environment
        # here: logging.ERROR is default level: useless command provided as an example:
        cls.set_verbose(logging.ERROR)

    @classmethod
    def tearDownClass(cls):
        # Keep the tearDownClass name from the django.test
        cls.commons_tear_down_class()

        super(TestCustomizedAlgoDao, cls).tearDownClass()
        # It is important to call superclass

    def test_seq1_create(self):
        """
        TU testing a scenario of the creation of CustomizedAlgo
          - error 1: bad argument
          - error 2: business resource has unexpected defined ID
          - error 3: missing customized parameter values
          - ok : finally created the CustomizedAlgo
        """
        my_custom_algo = CustomizedAlgo(arg_implementation=TestCustomizedAlgoDao.my_pseudo_impl_from_db,
                                        custom_params=None,
                                        name="Custo1 of my_pseudo_impl_from_db",
                                        label="Custo1",
                                        db_id=1,
                                        description="Custo1 created with test_seq1_create")

        with self.assertRaises(IkatsException):
            CustomizedAlgoDao.create("Bad type: str")

        # db_id defined => error
        with self.assertRaises(IkatsException):
            CustomizedAlgoDao.create(my_custom_algo)

        my_custom_algo.db_id = None

        # No customized params => error
        with self.assertRaises(IkatsException):
            CustomizedAlgoDao.create(my_custom_algo)

        my_custo_param_factor = CustomizedParameter(cat_parameter=TestCustomizedAlgoDao.my_param_factor,
                                                    value="0.5")
        my_custom_algo.add_custom_param(my_custo_param_factor)

        # Simpler
        #    the best is to use: my_custom_algo.add_custom_value(...) instead of add_custom_param(...)
        my_custom_algo.add_custom_value(param_name=TestCustomizedAlgoDao.my_param_phase.name,
                                        value="1.5")

        my_custom_algo_in_db = CustomizedAlgoDao.create(my_custom_algo)

        self.info("CREATED by TU: " + str(my_custom_algo_in_db))

    def test_seq2_update(self):
        """
        TU testing a scenario of the update of CustomizedAlgo
          - error 1: bad argument
          - error 2: business resource has unexpected defined ID
          - error 3: missing customized parameter values
          - ok : finally created the CustomizedAlgo
        """
        my_custom_algo = CustomizedAlgo(arg_implementation=TestCustomizedAlgoDao.my_pseudo_impl_from_db,
                                        custom_params=None,
                                        name="Custo1 of my_pseudo_impl_from_db",
                                        label="Custo1",
                                        db_id=None,
                                        description="Custo1 created with test_seq2_update")

        my_custo_param_factor = CustomizedParameter(cat_parameter=TestCustomizedAlgoDao.my_param_factor,
                                                    value="0.5")
        my_custo_param_phase = CustomizedParameter(cat_parameter=TestCustomizedAlgoDao.my_param_phase,
                                                   value="1.5")

        my_custom_algo.add_custom_param(my_custo_param_factor)
        my_custom_algo.add_custom_param(my_custo_param_phase)

        created_custom_algo_in_db = CustomizedAlgoDao.create(my_custom_algo)

        self.info("   - prepared data: " + str(created_custom_algo_in_db))
        initial_count_custo = CustomizedAlgoDao.objects.count()
        self.info("prepared data: CustomizedAlgoDao initial count={}".format(initial_count_custo))

        self.info("step1: test update with updated values and deleted CustomizedParameter")

        initial_name = created_custom_algo_in_db.name
        initial_label = created_custom_algo_in_db.label
        initial_description = created_custom_algo_in_db.description
        updated_param_name = "phase"
        param_to_update = created_custom_algo_in_db.custom_params[updated_param_name]
        initial_param_value = param_to_update.value

        created_custom_algo_in_db.name = "updated " + initial_name
        created_custom_algo_in_db.label = "updated " + initial_label
        created_custom_algo_in_db.description = "updated " + initial_description
        param_to_update.value = "updated " + initial_param_value

        param_name_to_delete = "factor"
        del created_custom_algo_in_db.custom_params[param_name_to_delete]

        my_updated_custom_algo_in_db = CustomizedAlgoDao.update(created_custom_algo_in_db)

        step1_count_custo = CustomizedAlgoDao.objects.count()
        self.info("... step1: CustomizedAlgoDao count={}".format(step1_count_custo))

        self.info("... step1: before update CustomizedAlgoDao ={}".format(created_custom_algo_in_db))
        self.info("... step1:  after update CustomizedAlgoDao ={}".format(my_updated_custom_algo_in_db))

        self.assertEqual(initial_count_custo, step1_count_custo, msg="initial_count_custo == step1_count_custo")

        self.assertEqual("updated " + initial_name, my_updated_custom_algo_in_db.name,
                         "updated name")
        self.assertEqual("updated " + initial_label, my_updated_custom_algo_in_db.label,
                         "updated label")
        self.assertEqual("updated " + initial_description, my_updated_custom_algo_in_db.description,
                         "updated description")
        # CustomizedParameter
        updated_param = my_updated_custom_algo_in_db.custom_params[updated_param_name]
        self.assertEqual("updated " + initial_param_value, updated_param.value,
                         "updated value for input name={}".format(updated_param.parameter.name))

        self.info("step1 updated resource: {}".format(
            my_updated_custom_algo_in_db))

        self.info(" ... step1: test update with added CustomizedParameter")
        step2_initial_content = str(my_updated_custom_algo_in_db)
        # Add previously deleted customized parameter ...
        # ... test persistence of aliased flag ... even if not yet used ...
        my_added_custom_param = CustomizedParameter(
            cat_parameter=TestCustomizedAlgoDao.my_param_factor,
            value="reference_factor")

        my_updated_custom_algo_in_db.custom_params[param_name_to_delete] = my_added_custom_param

        step2_updated_custom_algo_in_db = CustomizedAlgoDao.update(my_updated_custom_algo_in_db)

        step2_count_custo = CustomizedAlgoDao.objects.count()
        self.info(" ... step2: CustomizedAlgoDao count={}".format(step2_count_custo))

        self.info(" ... step2: before update CustomizedAlgoDao ={}".format(step2_initial_content))
        self.info(" ... step2:  after update CustomizedAlgoDao ={}".format(step2_updated_custom_algo_in_db))

        self.assertEqual(initial_count_custo, step2_count_custo, msg="initial_count_custo == step2_count_custo")

        self.info(" step2 updated resource: {}".format(step2_updated_custom_algo_in_db))

        my_updated_added_param = step2_updated_custom_algo_in_db.custom_params[param_name_to_delete]

        self.assertIsNotNone(my_updated_added_param.db_id,
                             msg="defined db_id on updated CustomizedParameter")

        self.assertTrue(my_added_custom_param == my_updated_added_param, "Test DB content: add custom param")

    def test_seq3_delete(self):
        """
        test the deletion
        :return:
        """

        list_custom_algo = []
        initial_count_custo = CustomizedAlgoDao.objects.count()
        self.info(" ... zero created: CustomizedAlgoDao initial count={}".format(initial_count_custo))

        for num_custo in ["1", "2"]:
            my_custom_algo = CustomizedAlgo(arg_implementation=TestCustomizedAlgoDao.my_pseudo_impl_from_db,
                                            custom_params=None,
                                            name="Custo{} of my_pseudo_impl_from_db".format(num_custo),
                                            label="Custo" + num_custo,
                                            db_id=None,
                                            description="Custo{} created with test_seq3_delete".format(num_custo))

            my_custo_param_factor = CustomizedParameter(cat_parameter=TestCustomizedAlgoDao.my_param_factor,
                                                        value="0.5" + num_custo)
            my_custo_param_phase = CustomizedParameter(cat_parameter=TestCustomizedAlgoDao.my_param_phase,
                                                       value="1.5" + num_custo)

            my_custom_algo.add_custom_param(my_custo_param_factor)
            my_custom_algo.add_custom_param(my_custo_param_phase)

            my_custom_algo_in_db = CustomizedAlgoDao.create(my_custom_algo)
            list_custom_algo.append(my_custom_algo_in_db)

            self.info("  - prepared data ={}".format(my_custom_algo_in_db))

        prepared_count_custo = CustomizedAlgoDao.objects.count()
        self.info(" ... once created: CustomizedAlgoDao count={}".format(prepared_count_custo))

        alt = True
        for custom_from_db in list_custom_algo:
            if alt:
                CustomizedAlgoDao.delete_resource(custom_from_db)
                self.info("  - deleted data ={}".format(custom_from_db))
            else:
                CustomizedAlgoDao.delete_resource_with_id(custom_from_db.db_id)
                self.info("  - deleted by id data ={}".format(custom_from_db))
            alt = not alt

        final_count_custo = CustomizedAlgoDao.objects.count()
        self.info(" ... once deleted: CustomizedAlgoDao count={}".format(final_count_custo))

        self.assertEqual(initial_count_custo, final_count_custo, msg="delete all the created custom algo")

    def test_seq4_find_from_implem_id(self):

        list_custom_algo = []
        initial_count_custo = CustomizedAlgoDao.objects.count()
        self.info("zero created: CustomizedAlgoDao initial count={}".format(initial_count_custo))

        list_num = ["3", "4", "5"]
        for num_custo in list_num:
            my_custom_algo = CustomizedAlgo(arg_implementation=TestCustomizedAlgoDao.my_pseudo_impl_from_db,
                                            custom_params=None,
                                            name="Custo{} of my_pseudo_impl_from_db".format(num_custo),
                                            label="Custo" + num_custo,
                                            db_id=None,
                                            description="Custo{} created with test_seq4_find_from_implem_id".format(
                                                num_custo))

            my_custo_param_factor = CustomizedParameter(cat_parameter=TestCustomizedAlgoDao.my_param_factor,
                                                        value="0.5" + num_custo)
            my_custo_param_phase = CustomizedParameter(cat_parameter=TestCustomizedAlgoDao.my_param_phase,
                                                       value="1.5" + num_custo)

            my_custom_algo.add_custom_param(my_custo_param_factor)
            my_custom_algo.add_custom_param(my_custo_param_phase)

            my_custom_algo_in_db = CustomizedAlgoDao.create(my_custom_algo)
            list_custom_algo.append(my_custom_algo_in_db)

            self.info("  - prepared data ={}".format(my_custom_algo_in_db))

        implem_id = TestCustomizedAlgoDao.my_pseudo_impl_from_db.db_id
        search = CustomizedAlgoDao.find_from_implementation_id(implem_id)
        for found in search:
            self.info("  - found result ={}".format(found))

        self.assertEqual(len(search), len(list_num), msg="search finds expected number of customized algo")

        search = CustomizedAlgoDao.find_from_implementation_id(1111111111111)
        self.assertEqual(len(search), 0, msg="empty search result is []")


class TestCustomizedAlgo(TestCase, CommonsCustomTest):
    # Init objects, not the custom DB
    custom_initialized = False

    @classmethod
    def setUpTestData(cls):
        cls.init_tu()
        cls.prepare_catalogue_data()

    def test_seq1_init_custo_params(self):
        # Should raise error: Argument instead of Parameter
        with self.assertRaises(IkatsException):
            CustomizedParameter(cat_parameter=self.my_arg_one,
                                value="0.5")
        # Constructor from id : raised error: unknown ID
        with self.assertRaises(IkatsException):
            CustomizedParameter(cat_parameter=111111111111,
                                value="0.5")

        my_init_from_id = CustomizedParameter(cat_parameter=self.my_param_factor.db_id,
                                              value=0.5)

        my_init_from_orm_obj = CustomizedParameter(cat_parameter=self.my_param_factor,
                                                   value=0.5)

        self.assertEqual(my_init_from_id.parameter.db_id,
                         my_init_from_orm_obj.parameter.db_id,
                         "my_init_from_id.parameter.id == my_init_from_orm_obj.parameter.db_id")


class TestCustomizedParameter(TestCase, CommonsCatalogueTests):
    """
    Tests on CustomizedParameter
    """

    @classmethod
    def setUpTestData(cls):
        """
        setUpClass: this setup is made once for several tests_ methods

        operational database is not impacted by the Django unittests
        """
        cls.init_logger()
        cls.info("Start: setUpTestData on TestCustomizedParameter")
        try:
            arg_one = Argument("angle", "angle (rad)", ProfileItem.DIR.INPUT, 0)
            param_factor = Parameter("factor", "factor on angle", ProfileItem.DIR.INPUT, 1)
            param_phase = Parameter(name="phase", description="added phase constant",
                                    direction=ProfileItem.DIR.INPUT, order_index=2,
                                    db_id=None,
                                    data_format="number",
                                    domain_of_values=None,
                                    label="phase",
                                    default_value="0")

            cls.res_one = Argument("result", "cos(angle)", ProfileItem.DIR.OUTPUT, 0)
            cls.res_two = Argument("result", "sin(angle)", ProfileItem.DIR.OUTPUT, 0)
            cls.res_three = Argument("result", "tan(angle)", ProfileItem.DIR.OUTPUT, 0)

            res_four = Argument("result", "tan(factor*angle+phase)", ProfileItem.DIR.OUTPUT, 0)

            cls.my_pseudo_impl = Implementation(
                "TU ORM impl for CustomizedAlgo", "Python tan from math::my_tan",
                "apps.algo.execute.models.business.python_local_exec_engine::PythonLocalExecEngine",
                "math::my_tan_tri", [arg_one, param_factor, param_phase], [res_four])

            # Implementation created in DB => this one will be tested
            #
            cls.my_pseudo_impl_from_db = ImplementationDao.create(cls.my_pseudo_impl)
            cls.my_arg_one = cls.my_pseudo_impl_from_db.find_by_name_input_item("angle")
            cls.my_param_factor = cls.my_pseudo_impl_from_db.find_by_name_input_item("factor")
            cls.my_param_phase = cls.my_pseudo_impl_from_db.find_by_name_input_item("phase")

            cls.info("setUpTestData initialized implem= {}".format(cls.my_pseudo_impl_from_db))
            cls.info("setUpTestData initialized arg_one= {}".format(cls.my_arg_one))
            cls.info("setUpTestData initialized param_factor= {}".format(cls.my_param_factor))
            cls.info("setUpTestData initialized param_phase= {}".format(cls.my_param_phase))

        except Exception as err:
            cls.logger().exception("got exception type=" + type(err).__name__)
            cls.logger().exception("exception as str=" + str(err))
            cls.error("... ended setUpTestData TestCustomizedParameter: Failed: %s")

        cls.info("End: setUpTestData on TestCustomizedParameter")

    def test_seq1_equals(self):

        my_custom_param_1 = CustomizedParameter(
            cat_parameter=TestCustomizedParameter.my_param_phase,
            value="reference_phase")

        my_custom_param_2 = CustomizedParameter(
            cat_parameter=TestCustomizedParameter.my_param_phase,
            value="5.2")

        my_custom_param_3 = CustomizedParameter(
            cat_parameter=TestCustomizedParameter.my_param_phase,
            value="5.2")

        my_custom_param_4 = CustomizedParameter(
            cat_parameter=TestCustomizedParameter.my_param_phase,
            value="75")

        my_custom_param_5 = CustomizedParameter(
            cat_parameter=TestCustomizedParameter.my_param_factor,
            value="75")

        self.assertTrue(my_custom_param_1 != my_custom_param_2)
        self.assertTrue(my_custom_param_2 == my_custom_param_3)
        self.assertTrue(my_custom_param_3 != my_custom_param_4)
        self.assertTrue(my_custom_param_4 != my_custom_param_5)
