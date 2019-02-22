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
from apps.algo.custom.models.business.algo import CustomizedAlgo
from apps.algo.custom.models.business.params import CustomizedParameter
from apps.algo.custom.models.orm.algo import CustomizedAlgoDao
from apps.algo.catalogue.tests.tu_commons import CommonsCatalogueTests


class CommonsCustomTest(CommonsCatalogueTests):
    """
    Common services used by tests on Custom part
      - extends the CommonsCatalogueTests:
        * extends init_tu
      - prepare_custom_database() available for different Tests: to be called in setUpClass()
        * class variables are initialized
        * TODO ? explicit getters on these cls vars would improve readability
      - services creating resources on the fly:
        * init_resource_...()
    """

    @classmethod
    def init_tu(cls):
        """
        Unit test initialization
        """
        super(CommonsCustomTest, cls).init_tu()

        # flag managed by classmethod prepare_custom_database:
        cls.custom_db_initialized = False

    @classmethod
    def prepare_custom_database(cls):
        """
        Prepare resources:
          - cls.my_custom_algo : unsaved in DB
          - cls.my_custom_algo_in_DB : loaded from DB
          - cls.my_custom_algo_2_in_DB
        :param cls:
        :type cls:
        """

        # prepares: cls.my_pseudo_impl_from_db
        cls.prepare_catalogue_data()
        t_name = cls.__name__
        if not cls.custom_db_initialized:
            cls.custom_db_initialized = True
            try:
                cls.info("Start: prepare_custom_database on {}".format(cls.__name__))

                cls.my_custom_algo = CustomizedAlgo(arg_implementation=cls.my_pseudo_impl_from_db,
                                                    custom_params=None,
                                                    name="Custo1 of my_pseudo_impl_from_db",
                                                    label="Custo1",
                                                    db_id=None,
                                                    description="Custo1 description")

                cls.my_custo_param_factor = CustomizedParameter(cat_parameter=cls.my_param_factor,
                                                                value=0.5)
                cls.my_custom_algo.add_custom_param(cls.my_custo_param_factor)

                cls.my_custom_algo.add_custom_value(param_name=cls.my_param_phase.name,
                                                    value=1.5)

                cls.my_custom_algo_in_DB = CustomizedAlgoDao.create(cls.my_custom_algo)

                my_custom_algo_2 = CustomizedAlgo(arg_implementation=cls.my_pseudo_impl_from_db,
                                                  custom_params=None,
                                                  name=t_name + " Custo2 of my_pseudo_impl_from_db",
                                                  label="Custo2",
                                                  db_id=None,
                                                  description="Custo2 description")

                my_custo_param_factor_2 = CustomizedParameter(cat_parameter=cls.my_param_factor,
                                                              value=0.885)
                my_custom_algo_2.add_custom_param(my_custo_param_factor_2)

                my_custom_algo_2.add_custom_value(param_name=cls.my_param_phase.name,
                                                  value=0.33)

                cls.my_custom_algo_in_DB = CustomizedAlgoDao.create(cls.my_custom_algo)
                cls.my_custom_algo_2_in_DB = CustomizedAlgoDao.create(my_custom_algo_2)

                cls.info("End: prepare_custom_database on {}".format(cls.__name__))

            except Exception as err:
                cls.tu_logger.exception("got exception type=" + type(err).__name__)
                cls.tu_logger.exception("exception as str=" + str(err))
                cls.error("... ended prepare_custom_database {}: Failed".format(cls.__name__))

    def init_rsrc_outside_domain(self):
        """
        Initialize tested resource CustomizedAlgo with
          - 1 check type error
          - 1 check domain error
        """
        custom_algo_outside_domain = CustomizedAlgo(arg_implementation=self.my_pseudo_impl_with_domain_from_db,
                                                    custom_params=None,
                                                    name="CustoW generating check errors by TU",
                                                    label="CustoW",
                                                    db_id=None,
                                                    description="CustoW description")

        # note: deprecated code:
        # my_custo_param_factor_bad_type=CustomizedParameter(cat_parameter=self.my_param_factor_bis,
        #                                          value=0.885)
        #
        # custom_algo_outside_domain.add_custom_param( my_custo_param_factor_bad_type )
        #
        # ... replaced by:

        # check type error
        custom_algo_outside_domain.add_custom_value(param_name=self.my_param_factor_bis.name, value="0.885")

        # type is correct but value is outside of domain defined in my_pseudo_impl_with_domain_from_db
        custom_algo_outside_domain.add_custom_value(param_name=self.my_param_phase_bis.name,
                                                    value=0.33)

        return custom_algo_outside_domain

    def init_resource_named(self, name, save_in_db, implem=None, factor=0.885, phase=0.33):
        """
        Initializes for the TU: one new CustomizedAlgo on the Implementation defined from implem,
        and values of arguments factor and phase.

        Note: it is more convenient for TU that the creation is made without any tests by the Checkengine:
        inconsistent/consistent data can be tested, in second step of the test, calling the Checkengine.

        :param name: name of CustomizedAlgo
        :type name: str
        :param save_in_db: boolean flag defines if a save in database is demanded
        :type save_in_db: boolean
        :param implem: optional, default None: the implementation.
                       None is replaced by TestCustomizedParameter.my_pseudo_impl_from_db
        :type implem: Implementation or None
        :param factor: optional, default is 0.885 (consistent with default
        TestCustomizedParameter.my_pseudo_impl_from_db)
        :type factor: value for the tested parameter factor
        :param phase:  optional, default is 0.33 (consistent with default
        TestCustomizedParameter.my_pseudo_impl_from_db)
        :type phase: number or object
        """
        my_implem = implem
        if implem is None:
            my_implem = self.my_pseudo_impl_from_db

        my_custom_algo_named = CustomizedAlgo(arg_implementation=my_implem,
                                              custom_params=None,
                                              name=name,
                                              label="CustoW named=" + name,
                                              db_id=None,
                                              description="CustoW description")

        my_custom_algo_named.add_custom_value(param_name=self.my_param_factor.name,
                                              value=factor)

        my_custom_algo_named.add_custom_value(param_name=self.my_param_phase.name,
                                              value=phase)
        if save_in_db:
            my_custom_algo_named = CustomizedAlgoDao.create(my_custom_algo_named)

        return my_custom_algo_named
