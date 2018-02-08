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
    Pierre BONHOURE <pierre.bonhoure@c-s.fr>
"""

from apps.algo.catalogue.models.business.algorithm import Algorithm
from apps.algo.catalogue.models.business.family import FunctionalFamily
from apps.algo.catalogue.models.business.implem import Implementation
from apps.algo.catalogue.models.business.profile import Argument, ProfileItem, Parameter
from apps.algo.catalogue.models.orm.implem import ImplementationDao
from apps.algo.custom.models.business.check_engine import CheckEngine
from ikats_processing.tests.commons_unittest import CommonsUnittest


class CommonsCatalogueTests(CommonsUnittest):
    """
    Common services used by several tests on Catalogue part
      - extends the CommonsUnittest:
      - init_tu(): to be called in setUpClass()
      - commons_tearDownClass(): to be called in each tearDownClass()
      - prepare_catalogue_data() available for different Tests
        * class variables are initialized
        * TODO ? explicit getters on these cls vars would improve readability
    """

    @classmethod
    def init_tu(cls):
        """
        To be called in the setUpClass of each test:
          - init the logger
          - empties the checking rules:  CheckEngine.set_checking_rules({})
        :param cls:
        :type cls:
        """
        cls.cat_initialized = False
        cls.init_logger()
        # for each test: the checking rules are emptied: default behaviour
        # which may be modified in each setUpClass method
        CheckEngine.set_checking_rules({})

    @classmethod
    def commons_tear_down_class(cls):

        super(CommonsCatalogueTests, cls).commons_tear_down_class()
        CheckEngine.set_checking_rules({})

    @classmethod
    def prepare_catalogue_data(cls):
        """
        this setup is made once for several tests_ methods

        operational database is not impacted by the Django unittests
        """
        cls.init_logger()
        if cls.cat_initialized is False:
            cls.cat_initialized = True
            cls.info("Start: prepareCatalogueData on {}".format(cls.__name__))
            t_name = cls.__name__
            try:

                my_fam = FunctionalFamily(name=t_name + " tested family", description="", db_id=None,
                                          label="lab family")
                my_algo = Algorithm(name=t_name + "my algo", description=" desc", db_id=None, label="lab",
                                    family=my_fam)

                cls.arg_one = Argument("angle", "angle (rad)", ProfileItem.DIR.INPUT, 0)
                cls.param_factor = Parameter("factor", "factor on angle", ProfileItem.DIR.INPUT, 1)
                cls.param_factor.data_format = "number"

                cls.param_phase = Parameter(name="phase", description="added phase constant",
                                            direction=ProfileItem.DIR.INPUT, order_index=2,
                                            db_id=None,
                                            data_format="number",
                                            domain_of_values=None,
                                            label="phase",
                                            default_value=0)

                cls.param_phase_with_domain = Parameter(name="phase", description="added phase constant",
                                                        direction=ProfileItem.DIR.INPUT, order_index=2,
                                                        db_id=None,
                                                        data_format="number",
                                                        domain_of_values="[0, 1.1, 2 ]",
                                                        label="phase with constraint",
                                                        default_value=0)

                cls.res_one = Argument("result", "cos(angle)", ProfileItem.DIR.OUTPUT, 0)
                cls.res_two = Argument("result", "sin(angle)", ProfileItem.DIR.OUTPUT, 0)
                cls.res_three = Argument("result", "tan(angle)", ProfileItem.DIR.OUTPUT, 0)

                cls.res_four = Argument("result", "tan(factor*angle+phase)", ProfileItem.DIR.OUTPUT, 0)

                cls.my_cosinus = Implementation(
                    t_name + " ORM Python Standard cosinus", "Python cosinus from math::cos",
                    "apps.algo.execute.models.business.python_local_exec_engine::PythonLocalExecEngine",
                    "math::cos", [cls.arg_one], [cls.res_one])

                cls.my_sinus = Implementation(
                    t_name + " ORM Python Standard sinus", "Python sinus from math::sin",
                    "apps.algo.execute.models.business.python_local_exec_engine::PythonLocalExecEngine",
                    "math::sin", [cls.arg_one], [cls.res_two])

                cls.my_tan = Implementation(
                    t_name + " ORM Python Standard tan", "Python tan from math::tan",
                    "apps.algo.execute.models.business.python_local_exec_engine::PythonLocalExecEngine",
                    "math::tan", [cls.arg_one], [cls.res_three])

                cls.my_pseudo_impl = Implementation(
                    t_name + " ORM impl for CustomizedAlgo", "Python tan from math::my_tan",
                    "apps.algo.execute.models.business.python_local_exec_engine::PythonLocalExecEngine",
                    "ikats.processing.ikats_processing.tests.test_contrib::my_tan",
                    [cls.arg_one, cls.param_factor, cls.param_phase],
                    [cls.res_four],
                    algo=my_algo)

                cls.my_pseudo_impl_with_domain = Implementation(
                    t_name + " ORM impl2 for CustomizedAlgo", "Python tan from math::my_tan_bis",
                    "apps.algo.execute.models.business.python_local_exec_engine::PythonLocalExecEngine",
                    "ikats.processing.ikats_processing.tests.test_contrib::my_tan_bis",
                    [cls.arg_one, cls.param_factor, cls.param_phase_with_domain],
                    [cls.res_four],
                    algo=my_algo)

                # Implementation created in DB => this one will be tested
                #
                cls.my_pseudo_impl_from_db = ImplementationDao.create(cls.my_pseudo_impl)
                cls.my_arg_one = cls.my_pseudo_impl_from_db.find_by_name_input_item("angle")
                cls.my_param_factor = cls.my_pseudo_impl_from_db.find_by_name_input_item("factor")
                cls.my_param_phase = cls.my_pseudo_impl_from_db.find_by_name_input_item("phase")

                cls.info("prepare_catalogue_data initialized implem= {}".format(cls.my_pseudo_impl_from_db))
                cls.info("prepare_catalogue_data initialized arg_one= {}".format(cls.my_arg_one))
                cls.info("prepare_catalogue_data initialized param_factor= {}".format(cls.my_param_factor))
                cls.info("prepare_catalogue_data initialized param_phase= {}".format(cls.my_param_phase))

                cls.my_pseudo_impl_with_domain_from_db = ImplementationDao.create(cls.my_pseudo_impl_with_domain)
                cls.my_arg_one_bis = cls.my_pseudo_impl_with_domain_from_db.find_by_name_input_item("angle")
                cls.my_param_factor_bis = cls.my_pseudo_impl_with_domain_from_db.find_by_name_input_item("factor")
                cls.my_param_phase_bis = cls.my_pseudo_impl_with_domain_from_db.find_by_name_input_item("phase")

                cls.info("prepare_catalogue_data my_pseudo_impl_with_domain_from_db= {}".format(
                    cls.my_pseudo_impl_with_domain_from_db))
                cls.info("prepare_catalogue_data my_arg_one_bis= {}".format(cls.my_arg_one_bis))
                cls.info("prepare_catalogue_data my_param_factor_bis= {}".format(cls.my_param_factor_bis))
                cls.info("prepare_catalogue_data my_param_phase_bis= {}".format(cls.my_param_phase_bis))

                cls.info("End: prepare_catalogue_data on {}".format(cls.__name__))

            except Exception as err:
                cls.logger().exception("got exception type=" + type(err).__name__)
                cls.logger().exception("exception as str=" + str(err))
                cls.error("... ended prepare_catalogue_data {}: Failed".format(cls.__name__))
