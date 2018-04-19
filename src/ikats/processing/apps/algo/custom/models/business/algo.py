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
from apps.algo.catalogue.models.business.implem import Implementation
from apps.algo.catalogue.models.business.element import Element
from ikats.core.library.exception import IkatsException
from apps.algo.custom.models.business.params import CustomizedParameter
from apps.algo.catalogue.models.business.profile import Parameter


class CustomizedAlgo(Element):
    PREFIX_CHECK = "Consistency error detected in check_param_in_catalogue:"
    """
    The business resource CustomizedAlgo defines values edited by the end-user (customer),
    for specific parameters of one Implementation defined in the catalogue.
    """

    def __init__(self, arg_implementation, custom_params=None, name=None, label=None, db_id=None,
                 description=None):
        """
        Constructor of one customized algorithm is defined with
         * one Implementation from catalogue
         * a set of values for the parameters defined by custom_params
         * optional information referencing the customized algorithm in the database:
          * name
          * label
          * db_id
          * description


        If specified custom_params is not None: consistency checks are applied, regarding \
        the arg_implementation and each customized parameter: see method check_param_in_catalogue().

        .. WARNING:: A CustomizedAlgo may have **None** values for **name**, **label**: \
                     this is
                      * **ok for any usage disconnected from DB**, typically in runalgo,
                      * **but will cause failure on CREATE/UPDATE** in database \
                        (see CustomizedAlgoDao class methods create() update())

        .. WARNING:: A CustomizedAlgo may have **None** value for **description**: \
                     this is
                      * **ok for any usage disconnected from DB**, typically in runalgo,
                      * and also **ok saving the resource in the database**, \
                        but the drawback is that the user will forget the purpose of customizing !

        .. WARNING:: A CustomizedAlgo may have **None** value for **db_id**: \
                     this is
                      * **ok for any usage disconnected from DB**, typically in runalgo,
                      * and also **ok creating a new resource** in the database, assuming that \
                        there is no conflict with existing CustomizedAlgo in custom DB

        .. todo [story session management] later: could add one session/user ID:
           session/user holding this customized algo (for processing session management)


        :param arg_implementation: instance of the catalogued Implementation being customized by self
        :type arg_implementation: apps.algo.catalogue.business.implem.Implementation
        :param custom_params: optional, default None: customized parameter values defined by user.
                              Default value None defines an empty set of customized parameters.
                              It is also possible to complete the customized parameters set
                              with the method add_custom_param.
        :type custom_params: list of CustomizedParameter
        :param name: optional, default None: the name of the CustomizedAlgo in custom DB
        :type name: str
        :param label: optional, default None: the readable name of the CustomizedAlgo in custom DB:
        value visible in HMI
        :type label: str or None
        :param db_id: optional, default None: the database identifier of a CustomizedAlgo which is already saved
        :type db_id: str or None
        :param description: optional, default None: the description of the CustomizedAlgo
        :type description: str or None
        """
        super(CustomizedAlgo, self).__init__(name=name, description=description, db_id=db_id, label=label)

        if (arg_implementation is None) or (not isinstance(arg_implementation, Implementation)):
            raise IkatsException("Constructor error: CustomizedAlgo expects arg_implementation " +
                                 "as a defined Implementation")
        self._implementation = arg_implementation

        if custom_params is not None:
            if type(custom_params) is not list:
                my_mess = "Constructor error: CustomizedAlgo expects defined custom_params as a list:" + \
                          " got instead type="
                raise IkatsException(my_mess + type(custom_params).__name__)

            self._custom_params = dict()
            for custo_param in custom_params:
                self.check_param_in_catalogue(buz_custom_param=custo_param)
                self._custom_params[custo_param.parameter.name] = custo_param
        else:
            self._custom_params = dict()

    @property
    def implementation(self):
        """
        Gets the Implementation business resource being customized
        """
        return self._implementation

    @property
    def custom_params(self):
        """
        Gets the dict holding the customized parameters:
         * each key: the name of CustomizedParameter
         * each associated value: the CustomizedParameter
        """
        return self._custom_params

    def get_custom_param_value(self, param_name, return_default_when_missing=True):
        """
        For the specified parameter name,
        returns
         * the customized value for one parameter when customized
         * or if (return_default_when_missing is True): the default parameter value from self.implementation,
         * or else: None

        :param param_name: name of the parameter defined in the self.implementation
        :type param_name: str
        :param return_default_when_missing: optional,default is True: flag True when default value
                is read from catalogue, when there is no customized value
        :type return_default_when_missing: bool
        :return: the available value either customized value by self.custom_params or default value
                 from self.implementation inputs.
        :rtype: str for defined value or None when unavailable
        :raise IkatsException: error when there is no input parameter named param_name in self.implementation
        """
        cat_input_param = self.implementation.find_by_name_input_item(name=param_name,
                                                                      accepted_type=Parameter)
        if cat_input_param is None:
            raise IkatsException("Unexpected: no input parameter named {} in {}".format(param_name,
                                                                                        self.implementation))
        if param_name in self.custom_params.keys():
            return self.custom_params[param_name].value
        elif return_default_when_missing:
            return cat_input_param.default_value

    def has_custom_value(self, param_name):
        """
        Checks if the specified parameter has a configured value under self CustomizedAlgo
        :param param_name: specified name of the parameter
        :type param_name: str
        :return: True if the specified parameter has a configured value under self CustomizedAlgo
        :rtype: bool
        """
        return self.has_custom_explicit_value(param_name) or self.has_custom_aliased_value(param_name)

    def has_custom_explicit_value(self, param_name):
        """
        Same than has_custom_value: presently only explicit values are managed
        :param param_name: specified name of the parameter
        :type param_name: str
        :return: True if the specified parameter has a configured and explicit value
        under self CustomizedAlgo
        :rtype: bool
        """
        return param_name in self.custom_params.keys()

    def has_custom_aliased_value(self, param_name):
        """
        Checks if the specified parameter has a configured and alias under self CustomizedAlgo
        Not yet implemented: False is returned
        :param param_name:
        :type param_name:
        :return: False
        """
        #         if param_name in self.custom_params.keys():
        #                 return self.custom_params[param_name].is_aliased
        #         return False
        return False

    def add_custom_value(self, param_name, value):
        """
        Add the specific customized value to current CustomizedAlgo, for specified input.

        :param param_name: input name of Parameter defined from self.implementation
        :type param_name:
        :param value: value must be string encoded
        :type value: str
        :return: the CustomizedParameter added to self
        :rtype: CustomizedParameter
        :raise IkatsException: consistency error detected
        """
        cat_param_from_impl = self._implementation.find_by_name_input_item(param_name, accepted_type=Parameter)
        added = CustomizedParameter(cat_parameter=cat_param_from_impl, value=value, db_id=None)
        self.add_custom_param(added)

    def clear_custom_params(self):
        """
        This method clears all customized parameters

        Note: you can also delete one parameter, using: syntax:
          - del self.custom_params[deleted_param_name]

        :return: deleted dict
        :rtype: dict
        """
        deleted_dict = self._custom_params
        self._custom_params = dict()
        return deleted_dict

    def add_custom_param(self, buz_custom_param):
        """
        !!! Deprecated: inconsistency risks: use add_custom_value() instead !!!

        Add the specific CustomizedParameter to current CustomizedAlgo, overriding previous settings

        .. note:: It is deprecated to use this method: it will become private

        :param buz_custom_param: the new/updated value of customized parameter resource
        :type buz_custom_param:  CustomizedParameter
        """
        self.check_param_in_catalogue(buz_custom_param)
        param_name = buz_custom_param.parameter.name
        self._custom_params[param_name] = buz_custom_param

    def check_param_in_catalogue(self, buz_custom_param):
        """
        Checks the consistency of a new CustomizedParameter to be added to self, regarding self.implementation
         * the buz_custom_param.parameter.name is matching one input Parameter of self.implementation
         * if the self.implementation is defined in the catalogue - i.e. has defined db_id - :
          * buz_custom_param.parameter.db_id is defined and is equal to the db_id \
            of the matched self.implementation input
         * if the self.implementation is not defined in the catalogue:
          * buz_custom_param.parameter.db_id is None
          * matched self.implementation input Parameter has also a db_id == None

        .. Note:: already checked by CustomizedParameter constructor: the referenced catalogue
                  type is Parameter

        :param buz_custom_param:
        :type buz_custom_param:
        """
        # Check1: check with named parameter inputs
        new_param_name = buz_custom_param.parameter.name
        cat_param_from_impl = self._implementation.find_by_name_input_item(new_param_name, accepted_type=Parameter)
        if cat_param_from_impl is not None:
            # OK: check1
            cat_param_id_from_impl = cat_param_from_impl.db_id
            new_referenced_param_id = buz_custom_param.parameter.db_id
            if self._implementation.is_db_id_defined():
                # Check 2: case when Implementation is saved in DB:
                # --------------------------------------------------

                # Check 2.1: defined ID of Parameter on Implementation side
                if cat_param_id_from_impl is None:
                    my_error = "{} unexpected: undefined db_id in Parameter {} defined by saved Implementation {}"
                    raise IkatsException(msg=my_error.format(self.PREFIX_CHECK,
                                                             cat_param_from_impl,
                                                             self.implementation))

                # Check 2.2: defined ID of Parameter referenced by buz_custom_param
                if new_referenced_param_id is None:
                    my_error = "{} unexpected undefined db_id of Parameter {} defined by CustomizedParameter {}"
                    raise IkatsException(msg=my_error.format(self.PREFIX_CHECK,
                                                             new_referenced_param_id,
                                                             buz_custom_param))

                # Check 2.3: respective IDs must be equal
                if cat_param_id_from_impl != new_referenced_param_id:
                    my_error = "{} unexpected: catalogue input ID != customized input ID: {} != {} : added={}"
                    raise IkatsException(msg=my_error.format(self.PREFIX_CHECK,
                                                             cat_param_id_from_impl,
                                                             new_referenced_param_id,
                                                             buz_custom_param))
            else:
                # Check 2: case when Implementation is not saved in DB
                # -----------------------------------------------------
                # Check 2.4: requires undefined db_id for the matched Parameter in self.implementation
                if cat_param_from_impl.is_db_id_defined():
                    my_error = "{} unexpected: for unsaved Implementation: defined db_id on matched input {}"
                    raise IkatsException(msg=my_error.format(self.PREFIX_CHECK,
                                                             cat_param_from_impl))
                # Check 2.5: requires undefined db_id for Parameter defined by buz_custom_param
                if buz_custom_param.parameter.is_db_id_defined():
                    my_error = "{} unexpected: for unsaved Implementation: customized Parameter with db_id: {}"
                    raise IkatsException(msg=my_error.format(self.PREFIX_CHECK,
                                                             buz_custom_param.parameter))
        else:
            # KO check 1
            my_error = "{} missing input Parameter name={} from {}"
            raise IkatsException(msg=my_error.format(self.PREFIX_CHECK,
                                                     new_param_name,
                                                     self.implementation))

    def __eq__(self, other):

        if isinstance(other, CustomizedAlgo):
            res = (self.db_id == other.db_id)
            res = res and (self.name == other.name)
            res = res and (self.label == other.label)
            res = res and (self.description == other.description)
            res = res and (self.implementation.db_id == other.implementation.db_id)
            if res:
                for name, custom_param in self.custom_params.items():
                    res = res and other.has_custom_value(name)
                    res = res and (custom_param.value == other.get_custom_param_value(name))

            return res
        else:
            return False

    def __str__(self):
        """
        Gets the str for resource CustomizedAlgo.
        """

        self_element_info = super(CustomizedAlgo, self).__str__()

        if len(self._custom_params) > 0:
            info_params = dict()
            for key, val in sorted(self._custom_params.items()):
                info_params[key] = str(val)
            return "CustomizedAlgo[{}] on implementation=[{}] with custo_params=[{}]".format(self_element_info,
                                                                                             self._implementation,
                                                                                             info_params)
        else:
            return "CustomizedAlgo[{}] on implementation=[{}]".format(self_element_info,
                                                                      self._implementation)
