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
from apps.algo.catalogue.models.business.profile import Parameter
from apps.algo.catalogue.models.orm.implem import ImplementationDao
from apps.algo.catalogue.models.ws.implem import ImplementationWs
from apps.algo.custom.models.business.algo import CustomizedAlgo
from apps.algo.custom.models.business.params import CustomizedParameter
from apps.algo.custom.models.orm.algo import CustomizedAlgoDao
from ikats.core.library.exception import IkatsException, IkatsNotFoundError, IkatsInputError


class CustomizedAlgoWs(ImplementationWs):
    """
    From the End-User Rest API: this resource is encoding a CustomizedAlgo
    Usage:
      - CustomizedAlgoWs.load_from_dict(...) generates the object CustomizedAlgoWs from the json-parsed dictionary
      - obj.to_dict(...) generates the json-friendly dictionary (see superclass ImplementationWs)
      - obj.to_json(...) generates the json (see super-super class ElementWs)
      - CustomizedAlgoWs( custom_algo ): builds the  object CustomizedAlgoWs from business resource CustomizedAlgo

    .. note::  The catalogue is read-only for End-User Rest API
        so there are
          - one READ-ONLY part: the catalogue content part inherited from ImplementationWs:
                - Implementation defined under 'parent',
                - and its profile items Argument, Parameter (all profile definitions
                  under properties 'inputs' or'outputs' or 'parameters',  except 'values' properties)
          - one WRITEABLE part:
                - the CustomizedAlgo general info (name, label, description).
                  id must refer to existing CustomizedAlgo in database
                - the edited properties 'value' matching the business defined CustomizedParameter items

    Json content, with level: **INFO_LEVEL.SUMMARY**::

        {
          "id": 3,
          "name": "Custo2 of my_pseudo_impl_from_db",
          "label": "Custo2",
          "is_customized": true,
          "family": "tested family",
          "algo": "my algo",
          "description": "Custo2 description",
          "parent": {
            "label": "TU ORM impl for CustomizedAlgo",
            "description": "Python tan from math::my_tan",
            "name": "TU ORM impl for CustomizedAlgo",
            "id": 1
          }
        }

    Json content, with level: **INFO_LEVEL.NORMAL**::

        {
          "id": 2,
          "name": "Custo1 of my_pseudo_impl_from_db",
          "label": "Custo1",
          "description": "Custo1 description",
          "is_customized": true,
          "family": "tested family",
          "algo": "my algo",
          "parent": {
            "label": "TU ORM impl for CustomizedAlgo",
            "description": "Python tan from math::my_tan",
            "name": "TU ORM impl for CustomizedAlgo",
            "id": 1
          },
          "inputs": [
            {
              "label": "angle",
              "type": null,
              "description": "angle (rad)",
              "order_index": 0,
              "name": "angle"
            }
          ],
          "parameters": [
            {
              "type": null,
              "order_index": 1,
              "default_value": null,
              "domain": null,
              "label": "factor",
              "description": "factor on angle",
              "value": "0.5",
              "name": "factor"
            },
            {
              "type": "number",
              "order_index": 2,
              "default_value": null,
              "domain": null,
              "label": "phase",
              "description": "added phase constant",
              "value": "1.5",
              "name": "phase"
            }
          ],
          "outputs": [
            {
              "label": "result",
              "type": null,
              "description": "tan(factor*angle+phase)",
              "order_index": 0,
              "name": "result"
            }
          ]

        }

    Json content, with level: **INFO_LEVEL.DETAIL**::

        {
            "id": 3,
            "is_customized": true,
            "name": "Custo2 of my_pseudo_impl_from_db",
            "label": "Custo2",
            "family": "tested family",
            "description": "Custo2 description",
            "algo": "my algo",
            "library_address": "math::my_tan",
            "execution_plugin": "apps.algo.execute.models.business.python_local_exec_engine::PythonLocalExecEngine",
            "parent": {
             "label": "TU ORM impl for CustomizedAlgo",
             "description": "Python tan from math::my_tan",
             "name": "TU ORM impl for CustomizedAlgo",
             "id": 1
            },
            "parameters": [
              {
                "type": null,
                "order_index": 1,
                "default_value": null,
                "domain": null,
                "label": "factor",
                "description": "factor on angle",
                "value": "0.885",
                "name": "factor"
              },
              {
                "type": "number",
                "order_index": 2,
                "default_value": null,
                "domain": null,
                "label": "phase",
                "description": "added phase constant",
                "value": "0.33",
                "name": "phase"
              }
            ],
            "inputs": [
              {
                "label": "angle",
                "type": null,
                "description": "angle (rad)",
                "order_index": 0,
                "name": "angle"
              }
            ],
            "outputs": [
              {
                "label": "result",
                "type": null,
                "description": "tan(factor*angle+phase)",
                "order_index": 0,
                "name": "result"
              }
            ]
        }

    """

    def __init__(self, business_custom_algo):
        """
        Constructor
        :param business_custom_algo: the customized algo
        :type business_custom_algo: CustomizedAlgo
        """
        super(CustomizedAlgoWs, self).__init__(business_custom_algo.implementation)
        self._custom_algo = business_custom_algo

    def compute_implem_dict(self, implem, level):
        """
        Builds the root dict associated to the customized-algorithm
        :param implem: business implementation
        :type implem: Implementation
        :param level: the level defining how the content is viewed: see LevelInfo
        :type level: LevelInfo
        """

        # Computes following properties according to the level:
        #
        #    {
        #       id: "", // Functional key : custom-algo identifier (unique)
        #       name: "", // Functional key : custom-algo name (unique)
        #       label: "", // Label to use for display
        #       description: "", // Description of the custom-algo to use for display
        #       family: "", // Functional key reference : family name
        #       algo: "" // Functional key reference : algo name
        #       execution_plugin: ... // for detailed level
        #       library_address: ... // for detailed level
        #       is_customized: True // indicates that this resource is a custom-algo, not an implementation
        #       parent: { 'id': ..., 'name': ..., 'label': ..., 'description': ... } // (according to level ...)
        #    },
        #

        # Step 1: reuse super init:
        #  - ok: family, algo, execution_plugin, library_address
        dictionary = super(CustomizedAlgoWs, self).compute_implem_dict(implem, level)

        # Step2: redefines properties:
        #    id, name, label, description,
        dictionary = self.add_element_properties_to_dict(dictionary, self._custom_algo, level)

        # Note: could be simplified later:
        #  is_customized field is useless since the Endpoint already define this is a custom_algo.
        #  Moreover, the parent != None indicates this is a custom

        #    is_customized,
        dictionary['is_customized'] = True

        # Step3: creates parent property: implementation information
        dict_parent = {}
        dict_parent = self.add_element_properties_to_dict(dict_parent, implem, level)
        dictionary['parent'] = dict_parent

        return dictionary

    def compute_parameter_to_dict(self, business_arg, level):
        """
        Computes the customized parameter view: merges the catalogue configuration part with the edited value
        :param business_arg: the customized parameter
        :type business_arg: ProfileItem
        :param level: the level defining how the content is viewed: see LevelInfo
        :type level: LevelInfo
        """
        # Initialized from catalogue
        my_dict = super(CustomizedAlgoWs, self).compute_parameter_to_dict(business_arg, level)
        if self._custom_algo.has_custom_value(business_arg.name):
            my_dict['value'] = self._custom_algo.get_custom_param_value(business_arg.name)
        return my_dict

    def get_implementation(self):
        """
        Gets the business Implementation referred by this CustomizedAlgoWs
        """
        return self._custom_algo.implementation

    def get_customized_algo(self):
        """
        Gets the business CustomizedAlgo wrapped by this CustomizedAlgoWs
        """
        return self._custom_algo

    @classmethod
    def raise_load_error(cls, err_type, diag_msg):
        """
        Raises error
        :param err_type: type of error raised
        :type err_type: subclass of IkatsException
        :param diag_msg: diagnostic gives the error detailed information
        :type diag_msg: str
        """
        msg = "Error in CustomizedAlgoWs::load_from_dict(): {}".format(diag_msg)
        raise err_type(msg)

    @classmethod
    def load_from_dict(cls, ws_dict):
        """
        Reload the resource CustomizedAlgoWs from the json-friendly dictionary ws_dict.
        This service checks the consistency against the catalogue+custom database definitions:
          - the ws_dict must match one Implementation in the catalogue database,
          identified by ws_dict['parent']['id']
          - when the  ws_dict['id'] is not None: it matches one CustomizedAlgo in the custom database
          - the customized values of parameters must match existing parameter definition in the target
          implementation.

        :param cls:
        :type cls:
        :param ws_dict: the json-friendly dictionary
        :type ws_dict: dict
        """
        # my_parent_id, my_custo_id are string, independent of DAO choices (numbers handled by postgres)
        # When defined: my_parent_id is the ID of Implementation being customized
        my_parent_id = ""
        # When defined: my_custo_id is ID of customized algo in custom database
        my_custo_id = ""
        my_parent = ws_dict.get('parent', None)
        try:
            if my_parent is None:
                cls.raise_load_error(IkatsInputError,
                                     "missing definition of ws_dict['parent'] => unknown Implementation")
            else:
                my_parent_id = my_parent.get('id', None)
                if my_parent_id is None:
                    cls.raise_load_error(IkatsInputError,
                                         "missing definition of ws_dict['parent']['id'] => unknown Implementation")

                my_implementation = ImplementationDao.find_business_elem_with_key(primary_key=my_parent_id)

                my_custo_id = ws_dict.get('id', None)

                # Get customized parameters
                my_custom_params = []
                my_parameters_list = ws_dict.get('parameters', [])
                for param_dict in my_parameters_list:
                    name = param_dict.get('name', None)
                    if name is None:
                        cls.raise_load_error(IkatsInputError, "Missing name on parameter: {}".format(param_dict))

                    if 'value' in param_dict.keys():
                        # Checks that referenced parameter is defined in catalogue
                        cat_param = my_implementation.find_by_name_input_item(name, Parameter)
                        if cat_param is None:
                            msg = "Unmatched parameter name={} for implementation id={}"
                            cls.raise_load_error(IkatsInputError,
                                                 msg.format(name, my_parent_id))

                        parsed_val = param_dict['value']
                        custo_param = CustomizedParameter(cat_param, parsed_val)
                        my_custom_params.append(custo_param)

                if len(my_custom_params) == 0:
                    cls.raise_load_error(IkatsInputError, "CustomizedAlgo must have at least one customized value")

                if my_custo_id is not None:
                    # We just check that the defined id is matching one resource in the database
                    # - if missing => raises CustomizedAlgoDao.DoesNotExist
                    CustomizedAlgoDao.find_business_elem_with_key(primary_key=my_custo_id)

                my_name = ws_dict.get('name', None)
                my_label = ws_dict.get('label', my_name)
                my_desc = ws_dict.get('description', None)

                business_custo_algo = CustomizedAlgo(arg_implementation=my_implementation,
                                                     custom_params=my_custom_params,
                                                     name=my_name,
                                                     label=my_label,
                                                     db_id=my_custo_id,
                                                     description=my_desc)

                return CustomizedAlgoWs(business_custo_algo)

        except ImplementationDao.DoesNotExist:
            cls.raise_load_error(IkatsNotFoundError, "Not found: Implementation with id={}".format(my_parent_id))
        except CustomizedAlgoDao.DoesNotExist:
            cls.raise_load_error(IkatsNotFoundError, "Not found: CustomizedAlgo with id={}".format(my_custo_id))
        except IkatsException as e:
            raise e
        except Exception as err:
            cls.raise_load_error(IkatsException, str(err))
