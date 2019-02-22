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

import numbers
from apps.algo.catalogue.models.business.algorithm import Algorithm
from apps.algo.catalogue.models.business.family import FunctionalFamily
from apps.algo.catalogue.models.business.implem import Implementation
from apps.algo.catalogue.models.business.profile import Argument, ProfileItem
from apps.algo.catalogue.models.orm.algorithm import AlgorithmDao
from apps.algo.catalogue.models.orm.implem import ImplementationDao
from ikats_processing.core.resource_config import ResourceClientSingleton
from ikats.core.data.ts import AbstractTs
from numpy import array as nparray

LOGGER = logging.getLogger(__name__)


def init_temporal_manager():
    """
    Initialize the singleton for TDM
    """
    return ResourceClientSingleton.get_singleton().get_temporal_manager()


def init_non_temporal_manager():
    """
    Initialize the singleton for NTDM
    """
    return ResourceClientSingleton.get_singleton().get_non_temporal_manager()


def is_list_of_tsuid_fid_pairs(value):
    """
    Functional type checking function
    :param value:
    :type value:
    """
    if not isinstance(value, list):
        return False
    else:
        for item in value:
            if not (checktype_is_tsuid_fid_pair(item)):
                return False
    return True


def checktype_is_tsuid_fid_pair(value):
    """
    Functional type checking function
    :param value:
    :type value:
    """
    return (isinstance(value, dict)) and ('tsuid' in value) and ('funcId' in value)


def checktype_is_list_of_str(value):
    """
    Functional type checking function
    :param value:
    :type value:
    """
    if not isinstance(value, list):
        return False
    else:
        for item in value:
            if not isinstance(item, str):
                return False
    return True


def checktype_ts_selection(value):
    """
    Functional type checking function
    :param value:
    :type value:
    """
    if isinstance(value, str):
        # dataset name
        return True
    elif checktype_is_list_of_str(value):
        # list of tsuids
        return True
    elif is_list_of_tsuid_fid_pairs(value):
        # list of tsuid/funcId pairs
        return True
    else:
        return False


class FactoryCatalogue(object):
    """
    This Factory helps to build Implementations/ Algorithms/ FunctionalFamily
    which are consistent with Ikats integration constraints: database, ...
    """
    # -------------------------------------------------------------------
    # SPECIFIC FAMILIES
    # -------------------------------------------------------------------

    # private family: not published on standard Rest API
    INTERNAL_TEST_IKATS_FAMILY = "Internal_Test_IKATS"

    IKATS_PRIVATE_FAMILIES = [INTERNAL_TEST_IKATS_FAMILY]

    # -----------------------------------------------------------------------------
    #  ARGTYPES
    # -----------------------------------------------------------------------------

    # private data_format in implementations: not published on standard Rest API
    TEMPORAL_DATA_MANAGER_ARGTYPE = 'temporal_data_manager'
    NTDM_ARGTYPE = 'non_temporal_data_manager'

    DATASET_NAME_ARGTYPE = 'ds_name'

    # TS_LIST_ARGTYPE is a list of types  TSUID_FID_PAIR_ARGTYPE:
    #     [  { 'tsuid' : ..., 'funcId' : ... }, ...,  { 'tsuid' : ..., 'funcId' : ... }]
    TS_LIST_ARGTYPE = 'ts_list'

    # TSUID_LIST_ARGTYPE means flat list of string: the tsuids
    #
    TSUID_LIST_ARGTYPE = 'tsuid_list'

    CORRELATION_MATRIX_ARGTYPE = 'correlation_matrix'
    DICT_CORRELATION_MATRIX_ARGTYPE = 'dict_correlation_matrix'
    TS_DATA_ARGTYPE = 'ts_data'
    TS_METADATA_ARGTYPE = 'ts_metadata'

    # TS_SELECTION_ARGTYPE means: DATASET_NAME_ARGTYPE | TSUID_LIST_ARGTYPE | TS_LIST_ARGTYPE
    #
    TS_SELECTION_ARGTYPE = 'ts_selection'
    STATS_DEFINITIONS_V0_ARGTYPE = 'stats_definitions_v0'

    # TSUID_FID_PAIR_ARGTYPE means dict in that shape:
    #    { 'tsuid' : ..., 'funcId' : ... }
    TSUID_FID_PAIR_ARGTYPE = 'tsuid_funcid_pair'

    BOOL_ARGTYPE = 'bool'
    NUMBER_ARGTYPE = 'number'
    STRING_ARGTYPE = 'str'
    FLOAT_ARGTYPE = 'float'
    INTEGER_ARGTYPE = 'int'
    LIST_ARGTYPE = 'list'
    TUPLE_ARGTYPE = 'tuple'
    DICT_ARGTYPE = 'dict'
    NUMPY_ARRAY = 'numpy_array'
    MODEL_ARGTYPE = 'model'
    SK_MODEL_ARGTYPE = "sk_model"
    DOT_ARGTYPE = "dot"

    IKATS_FUNCTIONAL_ARGTYPES = [DATASET_NAME_ARGTYPE,
                                 TS_LIST_ARGTYPE,
                                 TSUID_LIST_ARGTYPE,
                                 CORRELATION_MATRIX_ARGTYPE,
                                 DICT_CORRELATION_MATRIX_ARGTYPE,
                                 TS_DATA_ARGTYPE,
                                 TS_METADATA_ARGTYPE,
                                 TS_SELECTION_ARGTYPE,
                                 STATS_DEFINITIONS_V0_ARGTYPE,
                                 TSUID_FID_PAIR_ARGTYPE,
                                 SK_MODEL_ARGTYPE,
                                 DOT_ARGTYPE]

    IKATS_BASIC_TYPES = [BOOL_ARGTYPE, NUMBER_ARGTYPE, STRING_ARGTYPE, FLOAT_ARGTYPE,
                         INTEGER_ARGTYPE, LIST_ARGTYPE, TUPLE_ARGTYPE, DICT_ARGTYPE, NUMPY_ARRAY]

    # Complete the configuration of TYPE_CHECKING_FUNCTIONS with new functional types
    # (its entries are optional: only defined when a check is desired)
    # -------------------------------------------------------------------------------
    # Presently: type-checking functions TYPE_CHECKING_FUNCTIONS
    # - are deactivated in operational mode
    # - are only used in test units, because get_checking_rules returns {}
    #    => see in CheckEngine unittest setups how can be used
    #       with CheckEngine.set_checking_rules(FactoryCatalogue.TYPE_CHECKING_FUNCTIONS )
    #
    #
    TYPE_CHECKING_FUNCTIONS = {
        BOOL_ARGTYPE: lambda x: isinstance(x, bool),
        NUMBER_ARGTYPE: lambda x: isinstance(x, numbers.Number),
        STRING_ARGTYPE: lambda x: isinstance(x, str),
        FLOAT_ARGTYPE: lambda x: isinstance(x, float),
        LIST_ARGTYPE: lambda x: isinstance(x, list),
        TUPLE_ARGTYPE: lambda x: isinstance(x, tuple),
        DICT_ARGTYPE: lambda x: isinstance(x, dict),
        NUMPY_ARRAY: lambda x: isinstance(x, nparray),
        DATASET_NAME_ARGTYPE: lambda x: isinstance(x, str),
        TS_LIST_ARGTYPE: is_list_of_tsuid_fid_pairs,
        TSUID_LIST_ARGTYPE: checktype_is_list_of_str,
        CORRELATION_MATRIX_ARGTYPE: lambda x: isinstance(x, nparray),
        TS_DATA_ARGTYPE: lambda x: isinstance(x, AbstractTs),
        TS_METADATA_ARGTYPE: lambda x: isinstance(x, dict),
        TS_SELECTION_ARGTYPE: checktype_ts_selection,
        DOT_ARGTYPE: lambda x: isinstance(x, str)
    }

    IKATS_PRIVATE_ARGTYPES = [TEMPORAL_DATA_MANAGER_ARGTYPE,
                              NTDM_ARGTYPE]

    IKATS_PRIVATE_ARG_INITIALIZERS = {TEMPORAL_DATA_MANAGER_ARGTYPE: init_temporal_manager,
                                      NTDM_ARGTYPE: init_non_temporal_manager}

    @staticmethod
    def get_checking_rules_per_types():
        """
        Returns the rules checking the values assigned to CustomizedAlgo or ExecutableAlgo
        :return: dict whose keys are configured functional types; and values are python functions (including lambda)
        :rtype: dict with str keys and function values
        """
        # To be completed: checks in operational mode
        return {}

    @staticmethod
    def get_log():
        """
        Gets the logger for the FactoryCatalogue
        """
        return LOGGER

    @classmethod
    def is_private(cls, item):
        """
        in normal use: Rest API will not publish private resources.

        :param item:
        :type item: any subclass of apps.algo.catalogue.models.business.element::Element
        :return: True if specified element is private
        :rtype: boolean
        """
        if isinstance(item, ProfileItem):
            return (item.data_format is not None) and (item.data_format in FactoryCatalogue.IKATS_PRIVATE_ARGTYPES)

        elif isinstance(item, FunctionalFamily):
            return item.name in FactoryCatalogue.IKATS_PRIVATE_FAMILIES

        elif isinstance(item, Algorithm):
            return (item.family is not None) and (item.family.name in FactoryCatalogue.IKATS_PRIVATE_FAMILIES)
        else:
            return False

    def build_algo(self, the_algo, the_parent_family=None, check_report=None, save=True):
        """
        Complete algorithm definition with parent family.
        Perform checks on consistency.
        Save algo in db on demand.
        :param the_algo: algo to update
        :type the_algo: Algorithm
        :param the_parent_family: optional, default None: attached to the algo when not None
        :type the_parent_family: FunctionalFamily
        :param check_report: list of errors
        :type check_report: list
        :param save: boolean to save in db or not
        :type save: boolean
        :return: updated algorithm
        :rtype: Algorithm
        """
        if the_parent_family is not None:
            the_algo.family = the_parent_family

        if check_report is not None:
            self.__is_algo_consistent(the_algo, check_report)
            self.__check_point(check_report)

        # Beware !!! risk to save without checking the consistency !!!
        if save is True:
            return AlgorithmDao.create(the_algo)
        else:
            return the_algo

    def build_implem(self, the_implem, the_parent_algo=None, check_report=None, save=True):
        """
        Complete implementation definition with parent algorithm.
        Perform checks on consistency.
        create a DAO record for given implementation on demand.
        :param the_implem: implementation to update
        :type the_implem: Implementation
        :param the_parent_algo: the parent algorithm, optional, default None
        :type the_parent_algo: Algorithm
        :param check_report: list of errors
        :type check_report: list
        :param save: boolean to save in db or not
        :type save: boolean
        :return: updated implementation
        :rtype: Implementation
        """
        if the_parent_algo is not None:
            the_implem.algo = the_parent_algo

        if check_report is not None:
            self.__is_implementation_consistent(the_implem, check_report)
            self.__check_point(check_report)

        # Beware !!! risk to save without checking the consistency !!!
        if save is True:
            return ImplementationDao.create(the_implem)
        else:
            return the_implem

    @staticmethod
    def build_temp_data_manager_arg():
        """
        Build the private argument typed TEMPORAL_DATA_MANAGER_ARGTYPE

        HYP: always the first argument
        """

        return Argument(name=FactoryCatalogue.TEMPORAL_DATA_MANAGER_ARGTYPE,
                        description="temporal_data_manager is a singleton initialized on server side",
                        direction=ProfileItem.DIR.INPUT,
                        order_index=0, db_id=None,
                        data_format=FactoryCatalogue.TEMPORAL_DATA_MANAGER_ARGTYPE,
                        domain_of_values=None)

    def __is_implementation_consistent(self, the_implementation, check_report):
        """
        Check database compatibility for an Implementation
        """
        check = (isinstance(the_implementation, Implementation)) or self.__add_error(
            "Implementation type required for the_implementation", check_report)

        check = check and ((self.__is_element_consistent(the_implementation, check_report)) or
                           self.__add_error("Implementation is not consistent as Element", check_report))

        check = check and ((the_implementation.algo is not None) or
                           self.__add_error("Implementation with undefined Algorithm", check_report))

        in_index = 0
        for profile_item in the_implementation.input_profile:
            # input_profile getter is sorting items by index,
            # => test that indexes are contiguous, and starting from zero
            profile_index = profile_item.order_index

            if in_index != profile_index:
                self.__add_error("Bad ProfileItem::order_index for Implementation with name={3}: \
                                    expects {0} instead of {1} for input with name={2}"
                                 .format(in_index, profile_index, profile_item.name, the_implementation.name),
                                 check_report)
                check = False

            in_index += 1

        my_output_profile = the_implementation.output_profile

        if my_output_profile and (len(my_output_profile) > 0):

            out_index = 0

            for profile_item in my_output_profile:
                # input_profile getter is sorting items by index,
                # => test that indexes are contiguous, and starting from zero
                profile_index = profile_item.order_index

                if out_index != profile_index:
                    self.__add_error("Bad ProfileItem::order_index for Implementation with name={3}: \
                                        expects {0} instead of {1} for output with name={2}"
                                     .format(out_index, profile_index, profile_item.name, the_implementation.name),
                                     check_report)
                    check = False

                out_index += 1

        return check and ((self.__is_algo_consistent(the_implementation.algo, check_report)) or
                          self.__add_error("Implementation with an Algorithm not consistent", check_report))

    def __is_algo_consistent(self, the_algorithm, check_report):
        """
        Check database compatibility for a FunctionalFamily
        """
        check = not (not (isinstance(the_algorithm, Algorithm)) and
                     not self.__add_error("Algorithm type required for the_algorithm", check_report))

        check = check and ((self.__is_element_consistent(the_algorithm, check_report)) or
                           self.__add_error("Algorithm is not consistent as Element", check_report))

        check = check and ((the_algorithm.family is not None) or
                           self.__add_error("Algorithm with undefined FunctionalFamily", check_report))

        return check and ((self.__is_family_consistent(the_algorithm.family, check_report)) or
                          self.__add_error("Algorithm with a FunctionalFamily not consistent", check_report))

    def __is_family_consistent(self, the_family, check_report):
        """
        Check database compatibility for a FunctionalFamily
        """
        check = (isinstance(the_family, FunctionalFamily)) or self.__add_error(
            "FunctionalFamily type required for the_family", check_report)

        check = check and ((self.__is_element_consistent(the_family, check_report)) or
                           self.__add_error("FunctionalFamily is not consistent as Element", check_report))

        return check

    @staticmethod
    def __is_str_defined(the_value, max_chars=None, min_chars=None):
        check = isinstance(the_value, str)

        if min_chars is None:
            check = check and (len(the_value) > 0)
        else:
            check = check and (len(the_value) > min_chars)

        if max_chars is not None:
            check = check and (len(the_value) < max_chars)

        return check

    def __is_element_consistent(self, the_element, check_report):
        """
        Check database compatibility for an Element: common rules for business subclasses of Element
        """
        check = self.__is_str_defined(the_element.name, 60) or self.__add_error("Bad string length for Element.name",
                                                                                check_report)
        check = check and ((" " not in the_element.name) or
                           self.__add_error("Element.name must not contain spaces", check_report))

        return check and (self.__is_str_defined(the_element.label, 60) or
                          self.__add_error("Bad string length for Element.label", check_report))

    def __add_error(self, msg, check_report):
        if check_report is not None:
            assert isinstance(check_report, list), "Error: expecting list type for check_report"
            check_report.append(msg)

        self.get_log().error(msg)

    @staticmethod
    def __check_point(check_report):
        if check_report and len(check_report) > 0:
            raise Exception("Check failure raised by FactoryCatalogue: %s" % (str(check_report)))
