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
    Maxime PERELMUTER <maxime.perelmuter@c-s.fr>
"""
import sys
import traceback

from apps.algo.catalogue.models.business.algorithm import Algorithm
from apps.algo.catalogue.models.business.factory import FactoryCatalogue
from apps.algo.catalogue.models.business.family import FunctionalFamily
from apps.algo.catalogue.models.business.implem import Implementation
from apps.algo.catalogue.models.business.profile import Argument, Parameter, ProfileItem
from apps.algo.catalogue.models.orm.algorithm import AlgorithmDao
from apps.algo.catalogue.models.orm.family import FunctionalFamilyDao
from apps.algo.catalogue.models.orm.implem import ImplementationDao


def create_algo_catalogue():
    """
    This Data migration is the effective catalogue based upon the algorithms used by DEMO JUNE 2016
    Initially these algorithms were stubs

    scope: tested functions:
        cosinus,

    Changes:
    1/ links managed now: at business + ws levels:
      implementation -> algo
      algo -> family

    2/ created attribute label at levels orm + business + ws for each Element

    """

    try:

        factory_cat = FactoryCatalogue()
        my_report = []

        stats_correlation_family = FunctionalFamily(
            name="Stats__TS_Correlation_Computation",
            description="Set of correlation functions, applied on Time series",
            db_id=None,
            label="Stats/TS Correlation computation")
        stats_correlation_family = FunctionalFamilyDao.create(stats_correlation_family)

        prepro_transform_family = FunctionalFamily(
            name="Preprocessing_TS__Transforming",
            description="Set of pre-processing functions which are transforming the Time series: not classified "
                        "as cleaning, or reduction functions.",
            db_id=None,
            label="Pre-processing on TS/transforming")
        prepro_transform_family = FunctionalFamilyDao.create(prepro_transform_family)

        pearson_correlation_algo = Algorithm(
            name="Pearson_correlation",
            description="Pearson correlation applied on Time Series.",
            db_id=None,
            label="Pearson correlation", family=stats_correlation_family)
        pearson_correlation_algo = AlgorithmDao.create(pearson_correlation_algo)

        resampling_period_min_algo = Algorithm(
            name="Resampling_to_period_min",
            description="Resamples the TS for the specified period between 2 points.",
            db_id=None,
            label="Resampling to period min", family=prepro_transform_family)
        resampling_period_min_algo = AlgorithmDao.create(resampling_period_min_algo)

        # Factory is just adding some checks on initialized implementations
        #
        factory_cat.build_implem(_get_pearson_correl_matrix_impl(pearson_correlation_algo),
                                 check_report=my_report)
        factory_cat.build_implem(_get_resampling_dataset_impl(resampling_period_min_algo),
                                 check_report=my_report)

        my_fam = FunctionalFamily(name="tested_family_custom", description="a family for ikats tests of custom",
                                  db_id=None,
                                  label="tested family for custom")
        my_algo = Algorithm(name="tested algo1 custom",
                            description="an abstract algo for ikats tests of custom",
                            db_id=None,
                            label="tested algo1 custom",
                            family=my_fam)
        arg_one = Argument("angle", "angle (rad)", ProfileItem.DIR.INPUT, 0)
        param_factor = Parameter("factor", "factor on angle", ProfileItem.DIR.INPUT, 1,
                                 data_format="float",
                                 domain_of_values="[0, 0.5, 1, 2.7, 0.885 ]",
                                 label="phase",
                                 default_value="0")
        param_phase = Parameter(name="phase", description="added phase constant",
                                direction=ProfileItem.DIR.INPUT, order_index=2,
                                db_id=None,
                                data_format="number",
                                domain_of_values="toto",
                                label="phase",
                                default_value="0")

        res_four = Argument("result", "tan(factor*angle+phase)", ProfileItem.DIR.OUTPUT, 0)

        my_pseudo_impl = Implementation(
            "test_impl1_custom", "Python tan from math::my_tan",
            "apps.algo.execute.models.business.python_local_exec_engine::PythonLocalExecEngine",
            "math::my_tan", [arg_one, param_factor, param_phase], [res_four], algo=my_algo,
            label="test impl1 for custom")

        # Implementation created in DB => this one will be tested
        #
        ImplementationDao.create(my_pseudo_impl)

    except Exception:
        traceback.print_exc(file=sys.stdout)
        raise Exception("Failed data migration: init_db_V2::create_catalogue_ikats")


def _get_pearson_correl_matrix_impl(pearson_correlation_algo):
    factory_cat = FactoryCatalogue()
    pearson_correl_matrix_impl = Implementation(
        name="pearson_correl_matrix_impl",
        description="Implementation of pearson correlation on a set of TS: this version is not distributed.",
        execution_plugin="apps.algo.execute.models.business.python_local_exec_engine::PythonLocalExecEngine",
        library_address="ikats.algo.core.correlation::pearson_correlation_matrix",
        input_profile=(factory_cat.build_temp_data_manager_arg(),
                       Argument(
                           name="ts_selection",
                           label="TS selection",
                           description="The selection of several TS on which is computed the correlation matrix",
                           direction=ProfileItem.DIR.INPUT,
                           order_index=1,
                           db_id=None,
                           data_format=FactoryCatalogue.TS_SELECTION_ARGTYPE,
                           domain_of_values=None),),
        output_profile=(Argument(
            name="result",
            label="result",
            description="The pearson correlation matrix: recorded as CSV.",
            direction=ProfileItem.DIR.OUTPUT,
            order_index=0,
            db_id=None,
            data_format=FactoryCatalogue.CORRELATION_MATRIX_ARGTYPE,
            domain_of_values=None),),  # default
        db_id=None,
        label="Pearson correlation local",
        algo=pearson_correlation_algo)
    return pearson_correl_matrix_impl


def _get_resampling_dataset_impl(resampling_period_min_algo):
    factory_cat = FactoryCatalogue()
    resampling_dataset_impl = Implementation(
        name="resampling_dataset_impl",
        description="Resamples, with the selected period, each Time series from the selected dataset",
        execution_plugin="apps.algo.execute.models.business.python_local_exec_engine::PythonLocalExecEngine",
        library_address="ikats.algo.core.resampling::resampling",
        input_profile=(factory_cat.build_temp_data_manager_arg(),
                       Argument(
                           name="ts_selection",
                           label="TS selection",
                           description="The selection of several TS",
                           direction=ProfileItem.DIR.INPUT,
                           order_index=1,
                           db_id=None,
                           data_format=FactoryCatalogue.TS_SELECTION_ARGTYPE,
                           domain_of_values=None),
                       Parameter(
                           name="period",
                           description="Optional number: the value defining the resampling period. If not defined: "
                                       "the minimal period over the TS selection is retained.",
                           direction=ProfileItem.DIR.INPUT,
                           order_index=2,
                           db_id=None,
                           data_format=FactoryCatalogue.NUMBER_ARGTYPE,
                           domain_of_values=None),),
        output_profile=(Argument(
            name="result",
            label="result",
            description="The list of TSUIDs referencing the resampled Time series.",
            direction=ProfileItem.DIR.OUTPUT,
            order_index=0,
            db_id=None,
            data_format=FactoryCatalogue.TSUID_LIST_ARGTYPE,
            domain_of_values=None),),  # default
        db_id=None,
        label="Resampling TS selection",
        algo=resampling_period_min_algo)

    return resampling_dataset_impl
