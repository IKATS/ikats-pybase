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

from django.test import TestCase as DjTestCase

from apps.algo.catalogue.models.business.implem import Implementation
from apps.algo.catalogue.models.business.profile import ProfileItem, Argument
from apps.algo.catalogue.models.orm.implem import ImplementationDao
from apps.algo.catalogue.models.orm.profile import ProfileItemDao
from apps.algo.catalogue.models.business.family import FunctionalFamily
from apps.algo.catalogue.models.orm.family import FunctionalFamilyDao
from apps.algo.catalogue.models.orm.algorithm import AlgorithmDao
from apps.algo.catalogue.models.business.algorithm import Algorithm
from ikats_processing.tests.commons_unittest import CommonsUnittest


class TestImplementationDaoCRUD(DjTestCase, CommonsUnittest):
    """
    TU testing ImplementationDao: static methods: CRUD services

    """

    @classmethod
    def setUpTestData(cls):
        """
        setUpClass: this setup is made once for several tests_ methods

        operational database is not impacted by the Django unittests
        """
        # init logger with CommonsUnittest service
        cls.init_logger()

        cls.arg_one = Argument("angle", "angle (rad)", ProfileItem.DIR.INPUT, 0)
        cls.res_one = Argument("result", "cos(angle)", ProfileItem.DIR.OUTPUT, 0)
        cls.res_two = Argument("result", "sin(angle)", ProfileItem.DIR.OUTPUT, 0)
        cls.res_three = Argument("result", "tan(angle)", ProfileItem.DIR.OUTPUT, 0)

        cls.my_cosinus = Implementation(
            "TU ORM Python Standard cosinus", "Python cosinus from math::cos",
            "apps.algo.execute.models.business.python_local_exec_engine::PythonLocalExecEngine",
            "math::cos", [cls.arg_one], [cls.res_one])

        cls.my_sinus = Implementation(
            "TU ORM Python Standard sinus", "Python sinus from math::sin",
            "apps.algo.execute.models.business.python_local_exec_engine::PythonLocalExecEngine",
            "math::sin", [cls.arg_one], [cls.res_two])

        cls.my_tan = Implementation(
            "TU ORM Python Standard tan", "Python tan from math::tan",
            "apps.algo.execute.models.business.python_local_exec_engine::PythonLocalExecEngine",
            "math::tan", [cls.arg_one], [cls.res_three])

    @classmethod
    def tearDownClass(cls):
        """
        Ends the class tests:
          - redefines the classmethod from unittest framework

        :param cls:
        :type cls:
        """

        # writes the test summary
        cls.commons_tear_down_class()
        # Note: it is important to call the django tearDownClass:
        #   django.test.TestCase rely on setUpClass() and tearDownClass()
        #   to perform some class-wide initialization (e.g. overriding settings).
        #    => If you need to override those methods, don't forget to call the super implementation:
        super(TestImplementationDaoCRUD, cls).tearDownClass()

    def test_seq1_create(self):
        self.info("TestImplementationDaoCRUD::test_seq1_create")
        created_sinus = ImplementationDao.create(TestImplementationDaoCRUD.my_sinus)
        TestImplementationDaoCRUD.my_created_sinus = created_sinus
        self.info("After test_seq1_create: ImplementationDao count = %s" % ImplementationDao.objects.count())

        self.info("Original %s" % str(TestImplementationDaoCRUD.my_sinus))
        self.info("Created %s" % str(created_sinus))

    def test_seq2_find(self):
        self.info("TestImplementationDaoCRUD::test_seq2_find")
        created_cosinus = ImplementationDao.create(TestImplementationDaoCRUD.my_cosinus)
        TestImplementationDaoCRUD.my_created_cosinus = created_cosinus
        self.info("After test_seq2_find: step 1 CREATE cos: ImplementationDao count = %s" %
                  ImplementationDao.objects.count())

        self.info("Original %s" % str(TestImplementationDaoCRUD.my_cosinus))
        self.info("Created %s" % str(created_cosinus))

        self.info("test_seq2_find_from_key [%s]: step 2 FIND by id: " %
                  TestImplementationDaoCRUD.my_created_cosinus.db_id)
        self.info("Before test_seq2_find_from_key: ImplementationDao count = %s" %
                  ImplementationDao.objects.count())

        res = ImplementationDao.find_from_key(TestImplementationDaoCRUD.my_created_cosinus.db_id)

        self.assertIsNotNone(res, "Failed find_by_key [%s]" % TestImplementationDaoCRUD.my_created_cosinus.db_id)

        self.info("Found %s" % str(res))

        self.info(
            "test_seq2_find: step 3 FIND by values:  [%s][%s][%s]" %
            (TestImplementationDaoCRUD.my_cosinus.name,
             TestImplementationDaoCRUD.my_cosinus.execution_plugin,
             TestImplementationDaoCRUD.my_cosinus.library_address))

        res2 = ImplementationDao.find_from_definition(TestImplementationDaoCRUD.my_cosinus.name,
                                                      TestImplementationDaoCRUD.my_cosinus.execution_plugin,
                                                      TestImplementationDaoCRUD.my_cosinus.library_address)

        self.assertTrue(len(res2) == 1, "ImplementationDao.find_from_definition returns unique result")
        self.assertTrue(str(res) == str(res2[0]), "find_from_key <=> find_from_definition on same object")

        self.info("Found %s" % str(res2[0]))

        self.info("test_seq2_find [%s][%s][%s]" % (TestImplementationDaoCRUD.my_cosinus.name,
                                                   TestImplementationDaoCRUD.my_cosinus.execution_plugin,
                                                   TestImplementationDaoCRUD.my_cosinus.library_address))

    def test_seq3_update(self):
        created_tan = ImplementationDao.create(TestImplementationDaoCRUD.my_tan)

        self.info("After test_seq3_update: step 1 CREATE tan: ImplementationDao count = %s" %
                  ImplementationDao.objects.count())

        self.info("Original: %s" % created_tan.as_text())

        created_tan.name = "TU ORM Python Standard tan"
        created_tan.output_profile = [TestImplementationDaoCRUD.res_three]

        updated_tan = ImplementationDao.update(created_tan)

        self.info("Updated: %s" % updated_tan.as_text())

    def test_seq4_delete(self):
        step = "------ step 1: create tan ------"
        self.info(step)

        count_implem_init = ImplementationDao.objects.count()
        count_profile_item_init = ProfileItemDao.objects.count()

        self.info("Before created: ImplementationDao count = %s" % count_implem_init)
        self.info("Before created: ProfileItemDao count = %s" % count_profile_item_init)

        created_tan = ImplementationDao.create(TestImplementationDaoCRUD.my_tan)

        self.info("  - Original tan oper: %s" % str(TestImplementationDaoCRUD.my_tan))
        self.info("  - Created tan oper: %s" % str(created_tan))

        step = "------ step 2: simple case of delete ------"
        self.info(step)

        ImplementationDao.delete_resource(created_tan)

        count_implem_post = ImplementationDao.objects.count()
        count_profile_item_post = ProfileItemDao.objects.count()

        self.info("Once deleted: ImplementationDao count = %s" % count_implem_post)
        self.info("Once deleted: ProfileItemDao count = %s" % count_profile_item_post)

        self.assertEqual(count_implem_init, count_implem_post)
        self.assertEqual(count_profile_item_init, count_profile_item_post)

    def test_seq5_delete(self):
        impl_count_before = ImplementationDao.objects.count()
        prof_count_before = ProfileItemDao.objects.count()

        self.info("Pre-condition: ImplementationDao count = %s" % impl_count_before)
        self.info("Pre-condition: ProfileItemDao count = %s" % prof_count_before)

        step = "------ step 1: create tan + tan Bis ------"
        self.info(step)

        created_tan = ImplementationDao.create(TestImplementationDaoCRUD.my_tan)

        impl_count_step1_1 = ImplementationDao.objects.count()
        prof_count_step1_1 = ProfileItemDao.objects.count()

        self.info("Once tan created: ImplementationDao count = %s" % impl_count_step1_1)
        self.info("Once tan created: ProfileItemDao count = %s" % prof_count_step1_1)
        self.info("  created input: " + str(created_tan.input_profile[0]))
        self.info(" created output: " + str(created_tan.output_profile[0]))

        tan_bis = Implementation(
            "TU ORM Python Standard tan BIS", "Python tan BIS from math::tan",
            "apps.algo.execute.models.business.python_local_exec_engine::PythonLocalExecEngine",
            "math::tan", [created_tan.input_profile[0]], [created_tan.output_profile[0]])

        created_tan_bis = ImplementationDao.create(tan_bis)

        impl_count_step1_2 = ImplementationDao.objects.count()
        prof_count_step1_2 = ProfileItemDao.objects.count()

        self.info("Once tan Bis created: ImplementationDao count = %s" % impl_count_step1_2)
        self.info("Once tan Bis created: ProfileItemDao count = %s" % prof_count_step1_2)

        self.info("  - Original tan oper: %s" % str(TestImplementationDaoCRUD.my_tan))
        self.info("  - Created tan oper: %s" % str(created_tan))
        self.info("  - Created tan BIS oper: %s" % str(created_tan_bis))

        step = "------ step 2:  delete oper tan with shared Profile_Items ------"
        self.info(step)

        ImplementationDao.delete_resource(created_tan)

        impl_count_step2 = ImplementationDao.objects.count()
        prof_count_step2 = ProfileItemDao.objects.count()

        self.info("Once tan deleted: ImplementationDao count = %s" % impl_count_step2)
        self.info("Once tan deleted: ProfileItemDao count = %s" % prof_count_step2)

        self.assertEqual(impl_count_step1_2, impl_count_step2 + 1,
                         "After first delete: impl_count_step2 == impl_count_step2 +1")
        self.assertEqual(prof_count_step1_2, prof_count_step2,
                         "After first delete: no orphan profile_item: prof_count_step1_2 == prof_count_step2")

        step = "------ step 3:  delete oper tan BIS with no more shared Profile_Items ------"
        self.info(step)

        ImplementationDao.delete_resource(created_tan_bis)

        impl_count_step3 = ImplementationDao.objects.count()
        prof_count_step3 = ProfileItemDao.objects.count()

        self.info("Once tan Bis deleted: ImplementationDao count = %s" % impl_count_step3)
        self.info("Once tan Bis deleted: ProfileItemDao count = %s" % prof_count_step3)

        self.assertEqual(impl_count_step3, impl_count_before,
                         "After second delete: impl_count_step3 == impl_count_before")
        self.assertEqual(prof_count_step3, prof_count_before,
                         "After second delete: prof_count_step3 == prof_count_before")

    def test_seq6_delete(self):
        fam_count_before = FunctionalFamilyDao.objects.count()
        algo_count_before = AlgorithmDao.objects.count()
        impl_count_before = ImplementationDao.objects.count()
        prof_count_before = ProfileItemDao.objects.count()

        self.info("Pre-condition: FunctionalFamilyDao count = %s" % fam_count_before)
        self.info("Pre-condition: AlgorithmDao count = %s" % algo_count_before)
        self.info("Pre-condition: ImplementationDao count = %s" % impl_count_before)
        self.info("Pre-condition: ProfileItemDao count = %s" % prof_count_before)

        step = "------ step 1: create tan Tri ------"
        self.info(step)

        family = FunctionalFamilyDao.create(FunctionalFamily(name="TU family", description="TU family for tan Tri"))
        algo = AlgorithmDao.create(Algorithm(name="TU algo",
                                             description="desc TU algo",
                                             label="label",
                                             family=family))

        self.info("  - family: %s" % str(family))
        self.info("  - algo: %s" % str(algo))

        fam_count_step1 = FunctionalFamilyDao.objects.count()
        algo_count_step1 = AlgorithmDao.objects.count()
        self.info("Parent family created: FunctionalFamilyDao count = %s" % fam_count_step1)
        self.info("Parent algo created: AlgorithmDao count = %s" % algo_count_step1)

        tan_tri = Implementation(
            "TU ORM Python Standard tan TRI", "Python tan TRI from math::tan",
            "apps.algo.execute.models.business.python_local_exec_engine::PythonLocalExecEngine",
            "math::tan", [TestImplementationDaoCRUD.arg_one], [TestImplementationDaoCRUD.res_three])

        tan_tri.algo = algo

        created_tan = ImplementationDao.create(tan_tri)

        impl_count_step1 = ImplementationDao.objects.count()
        prof_count_step1 = ProfileItemDao.objects.count()

        self.info("Once tan Tri created: ImplementationDao count = %s" % impl_count_step1)
        self.info("Once tan Tri created: ProfileItemDao count = %s" % prof_count_step1)

        self.info("  - Original tan Tri oper: %s" % str(tan_tri))
        self.info("  - Created tan Tri oper: %s" % str(created_tan))

        step = "------ step 2:  delete oper tan Tri with parent algo ------"
        self.info(step)

        ImplementationDao.delete_resource(created_tan)

        fam_count_step2 = FunctionalFamilyDao.objects.count()
        algo_count_step2 = AlgorithmDao.objects.count()
        impl_count_step2 = ImplementationDao.objects.count()
        prof_count_step2 = ProfileItemDao.objects.count()

        self.info("Step2: once tan Tri deleted: FunctionalFamilyDao count = %s" % fam_count_step2)
        self.info("Step2: once tan Tri deleted: AlgorithmDao count = %s" % algo_count_step2)
        self.info("Step2: once tan Tri deleted: ImplementationDao count = %s" % impl_count_step2)
        self.info("Step2: once tan Tri deleted: ProfileItemDao count = %s" % prof_count_step2)

        self.assertEqual(fam_count_step2, fam_count_step1,
                         "After  delete: family count unchanged: fam_count_step2 == fam_count_step1")
        self.assertEqual(algo_count_step2, algo_count_step1,
                         "After delete: algo count unchanged: algo_count_step2 == algo_count_step1")
        self.assertEqual(impl_count_step2, impl_count_before,
                         "After  delete: impl_count_step2 == impl_count_before")
        self.assertEqual(prof_count_step2, prof_count_before,
                         "After second delete: prof_count_step2 == prof_count_before")

        self.assertTrue(impl_count_step2 < impl_count_step1)
        self.assertTrue(prof_count_step2 < prof_count_step1)
