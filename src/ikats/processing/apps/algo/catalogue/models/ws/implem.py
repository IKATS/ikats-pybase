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
    Maxime PERELMUTER <maxime.perelmuter@c-s.fr>
"""
from apps.algo.catalogue.models.business.factory import FactoryCatalogue
from apps.algo.catalogue.models.business.implem import Implementation
from apps.algo.catalogue.models.business.profile import Argument, Parameter
from apps.algo.catalogue.models.orm.implem import ImplementationDao
from apps.algo.catalogue.models.ws.element import ElementWs
from ikats.core.json_util.rest_utilities import LevelInfo
from ikats.core.library.exception import IkatsException


class ImplementationWs(ElementWs):
    """
    WS resource: ImplementationWs wraps the Implementation business object

    This WS resource is the model for Web services about Implementation,
    masking some internal information of business model Implementation.
    ImplementationWs is also used by the templates generating HTML views on Implementation
    """

    def __init__(self, business_obj):
        """
        Constructor...
        """
        super(ImplementationWs, self).__init__(business_obj)

        assert (isinstance(business_obj, Implementation)), \
            "Expects Implementation type for argument business_obj in ImplementationWs constructor"

    @property
    def execution_plugin(self):
        """
        Getter of execution_plugin from business model view
        """
        return self.model_business.execution_plugin

    @property
    def library_address(self):
        """
        Getter of library_address from business model view
        """
        return self.model_business.library_address

    def input_profile(self, cls, level=LevelInfo.NORMAL):
        """
        Getter of input_profile from business model view
        returns the list of dict initialized from Argument or Parameter configuring the inputs
        :param cls: the type of profile items: Argument or Parameter or both with ProfileItem
        :type cls: class
        :param level:
        :type level:
        :return: list of dict
        :rtype: list
        """

        return self.__profile_to_dict(self.model_business.input_profile, cls, level)

    def output_profile(self, cls, level=LevelInfo.NORMAL):
        """
        Getter for self._output_profile
        returns the list of dict initialized from configuring the outputs
        :param cls: the type of profile items: Argument is the only class expected at the moment
        :type cls: class
        :param level:
        :type level:
        :return: list of dict
        :rtype: list
        """
        return self.__profile_to_dict(self.model_business.output_profile,
                                      Argument, level)

    def __profile_to_dict(self, the_list, subclass, level):
        my_profile = []
        assert (type(the_list) is list), "Expects list type for the_list"
        for biz_profile_item in the_list:
            if isinstance(biz_profile_item, subclass):
                if subclass == Argument:
                    my_profile_item = self.compute_argument_to_dict(biz_profile_item, level)

                elif subclass == Parameter:
                    my_profile_item = self.compute_parameter_to_dict(biz_profile_item, level)

                if (level == LevelInfo.DETAIL) or not FactoryCatalogue.is_private(biz_profile_item):
                    my_profile.append(my_profile_item)

        return my_profile

    def compute_implem_dict(self, implem, level):
        """
        Builds the root dict associated to the business implementation
        :param implem: business implementation
        :type implem: Implementation
        :param level:
        :type level:
        """

        # At least : level >= SUMMARY :
        #
        # GET /catalog/implementations
        # [
        #    {
        #       id: "", // Functional key : implementation identifier (unique)
        #       name: "", // Functional key : implementation name (unique)
        #       label: "", // Label to use for display
        #       description: "", // Description of the implementation to use for display
        #       family: "", // Functional key reference : family name
        #       algo: "" // Functional key reference : algo name
        #    },
        #    ...
        # ]

        my_algo = None
        my_family = None
        if implem.algo:
            my_algo = implem.algo.name

            if implem.algo.family:
                my_family = implem.algo.family.name

        dictionary = {"id": implem.db_id,
                      "family": my_family,
                      "algo": my_algo,
                      "visibility": implem.visibility}

        dictionary = self.add_element_properties_to_dict(dictionary, None, level)

        if level == LevelInfo.DETAIL:
            dictionary['execution_plugin'] = self.execution_plugin
            dictionary['library_address'] = self.library_address

        dictionary['is_customized'] = False

        return dictionary

    @staticmethod
    def compute_profile_item_to_dict(business_profile, level=LevelInfo.SUMMARY):
        # V1: SUMMARY <=> NORMAL
        my_profile_item_dict = {"name": business_profile.name,
                                "label": business_profile.label,
                                "description": business_profile.description}

        if level >= LevelInfo.NORMAL:
            my_profile_item_dict["order_index"] = business_profile.order_index
            my_profile_item_dict["domain"] = business_profile.domain_of_values
            my_profile_item_dict["type"] = business_profile.data_format

        return my_profile_item_dict

    def compute_argument_to_dict(self, business_arg, level=LevelInfo.SUMMARY):
        my_argument_dict = self.compute_profile_item_to_dict(business_arg, level)
        # my_argument_dict["domain"] = business_arg.domain_of_values
        return my_argument_dict

    def compute_parameter_to_dict(self, business_arg, level=LevelInfo.SUMMARY):
        my_param_dict = self.compute_profile_item_to_dict(business_arg, level)

        #  - default_value ...
        if level >= LevelInfo.NORMAL:
            # Since FT [#150518]
            #  force False value when
            #  - data_format is 'bool'
            #  - default_value is None
            if (business_arg.data_format == 'bool') and (business_arg.default_value is None):
                my_param_dict["default_value"] = False
            else:
                my_param_dict["default_value"] = business_arg.default_value

        return my_param_dict

    def to_dict(self, level=LevelInfo.NORMAL):
        """

        :param level: level of details, optional, default is NORMAL
        :type level: enum value ikats.core.json_util.rest_utilities.LevelInfo
        :return: a dictionary Json-serializable resource ImplementationWs
        :rtype: dict
        """

        # further details: level > SUMMARY
        #
        #  GET /catalog/implementations/{implementation_name}
        #
        # {
        #    id: "", // Functional key : implementation identifier (unique)
        #    name: "", // Functional key : implementation name (unique)
        #    label: "", // Label to use for display
        #    description: "", // Description of the implementation to use for display
        #    family: "", // Functional key reference : family name
        #    algo: "", // Functional key reference : algo name
        #    inputs: [
        #       {
        #          name: "", // Functional key : input name (unique)
        #          label: "", // Label to use for display
        #          description: "", // Description of the input to use for display
        #          type: "", // Input type (see below)
        #       },
        #       ...
        #    ],
        #    parameters: [
        #       {
        #          name: "",// Functional key : parameter name (unique)
        #          label: "", // Label to use for display
        #          description: "", // Description of the parameter to use for display
        #          type: "", // Parameter type (see below)
        #          domain: [] // Depends on type (array for "list" typed parameters)
        #       },
        #       ...
        #    ],
        #    outputs: [
        #       {
        #          name: "",// Functional key : output name (unique)
        #          label: "", // Label to use for display
        #          description: "", // Description of the output to use for display
        #          type: "" // Output type (see below)
        #       },
        #       ...
        #    ],
        # }
        dictionary = self.compute_implem_dict(self.model_business, level)

        if level != LevelInfo.SUMMARY:
            dictionary['inputs'] = self.input_profile(Argument, level)
            dictionary['parameters'] = self.input_profile(Parameter, level)
            dictionary['outputs'] = self.output_profile(Argument, level)

        return dictionary

    @classmethod
    def load_from_dict(cls, ws_dict):
        """
        Reload the resource ImplementationWs with internal model:
        the 'id' key is required: points to existing Implementation from the catalogue DB.

        Restriction [#139805]: any other key of ws_dict is ignored, as the model is a read-only
        catalogue resource via ImplementationWs.

        :param cls:
        :type cls:
        :param ws_dict:
        :type ws_dict:
        """
        my_implem_id = ws_dict.get('id', None)
        if my_implem_id is not None:
            business_implem = ImplementationDao.find_business_elem_with_key(primary_key=my_implem_id)
        else:
            raise IkatsException("Unexpected: missing Implementation reference from json ImplementationWs")

        return ImplementationWs(business_implem)
