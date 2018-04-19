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
from apps.algo.catalogue.models.business.element import Element
from apps.algo.catalogue.models.business.profile import ProfileItem


class Implementation(Element):
    """
    Implementation from business layer
    """

    def __init__(self, name, description,
                 execution_plugin,
                 library_address,
                 input_profile=(),
                 output_profile=(),
                 db_id=None,
                 label=None,
                 algo=None,
                 visibility=True):
        """
        :param name:
        :type name:
        :param description:
        :type description:
        :param execution_plugin:
        :type execution_plugin:
        :param library_address: address of function, or any executable
        :type library_address: str, CharField
        :param input_profile: ordered list of definitions of parameters and arguments
        :type input_profile: list of objects - either business.Parameter or business.Argument -
        :param output_profile:
        :type output_profile: list or tuple
        :param db_id:
        :type db_id:
        :param label: optional (default None): the label optionally defined. When undefined: the label attribute is
                      initialized with name argument
        :type label: str
        :param algo: optional (default None): the algo optionally defined.
        :type algo: Algorithm
        :param visibility: optional (default True): indicate if implementation can be picked up in operators list
                                                    if set to True.
        :type visibility: boolean
        """
        super(Implementation, self).__init__(name, description, db_id, label)

        self._algo = algo

        self._execution_plugin = execution_plugin
        self._library_address = library_address

        self._visibility = visibility

        self._input_profile = []
        # Calling explicitly the setter to sort the list
        # input_profile is provided as a tuple to have non-mutable parameter
        if input_profile is not None:
            self.input_profile = list(input_profile)

        self._output_profile = []
        # Calling explicitly the setter to sort the list
        # output_profile is provided as a tuple to have non-mutable parameter
        if output_profile is not None:
            self.output_profile = list(output_profile)

    @property
    def algo(self):
        """
        Getter for self._execution_plugin
        """
        return self._algo

    @algo.setter
    def algo(self, value):
        """
        Setter for self._algo
        """
        self._algo = value

    @property
    def execution_plugin(self):
        """
        Getter for self._execution_plugin
        """
        return self._execution_plugin

    @execution_plugin.setter
    def execution_plugin(self, value):
        """
        Setter for self._execution_plugin
        """
        self._execution_plugin = value

    @property
    def library_address(self):
        """
        Getter for self._library_address
        """
        return self._library_address

    @library_address.setter
    def library_address(self, value):
        """
        Setter for self._library_address
        """
        self._library_address = value

    @property
    def visibility(self):
        """
        Getter for self._visibility
        """
        return self._visibility

    @visibility.setter
    def visibility(self, value):
        """
        Setter for self._visibility
        """
        self._visibility = value

    @property
    def input_profile(self):
        """
        Getter for self._input_profile
        returns the list of ProfileItem configuring the inputs
        """
        return self._input_profile

    @input_profile.setter
    def input_profile(self, value=None):
        """
        Setter for self._input_profile
        """
        if not value:
            # Trick to not have not-mutable value as input if no data is
            # provided
            value = []
        if type(value) is not list:
            raise TypeError("input_profile must be a list")

        # Check that there is no error on direction
        for i in value:
            if i.direction != ProfileItem.DIR.INPUT:
                raise ValueError(
                    "Item [%s] provided in 'input_profile' is defined as OUTPUT" % i.name)

        # Sort values using order_index
        value.sort(key=lambda p: p.order_index)
        self._input_profile = value

    @property
    def output_profile(self):
        """
        Getter for self._output_profile
        returns the list of ProfileItem configuring the outputs
        """
        return self._output_profile

    @output_profile.setter
    def output_profile(self, value=None):
        """
        Setter for self._output_profile
        """
        if not value:
            # Trick to not have not-mutable value as input if no data is
            # provided
            value = []
        if type(value) is not list:
            raise TypeError("output_profile must be a list")

        # Check that there is no error on direction
        for i in value:
            if i.direction != ProfileItem.DIR.OUTPUT:
                raise ValueError(
                    "Item [%s] provided in 'output_profile' is defined as INPUT" % i.name)

        # Sort values using order_index
        value.sort(key=lambda p: p.order_index)
        self._output_profile = value

    def find_by_name_input_item(self, name, accepted_type=ProfileItem):
        """
        Finds the input item having specified name, specified class or superclass
        :param name: the searched name
        :type name: str
        :param accepted_type: optional, default is ProfileItem, for no specific restriction:
               the specified class or superclass which restricts the finding. Note:
               ProfileItem is superclass of Argument and Parameter.
        :type accepted_type: ProfileItem or Argument or Parameter.
        :return: the good item with specified name and accepted type. None when no result is found.
        :rtype: ProfileItem
        """
        for item in self.input_profile:
            if isinstance(item, accepted_type):
                if item.name == name:
                    return item
        return None

    def as_text(self):
        """
        Return the implementation as a text
        """

        str_input_profile = []
        if self.input_profile is not None:
            for item in self.input_profile:
                str_input_profile.append(str(item))

        str_output_profile = []
        if self.output_profile is not None:
            for item in self.output_profile:
                str_output_profile.append(str(item))

        return str({"implem": self.__str__(),
                    "input-profile": str_input_profile,
                    "output-profile": str_output_profile})

    def __eq__(self, other):

        if isinstance(other, Implementation):
            res = (self.db_id == other.db_id)
            res = res and (self.name == other.name)
            res = res and (self.label == other.label)
            res = res and (self.description == other.description)
            res = res and (self.library_address == other.library_address)
            res = res and (self.execution_plugin == other.execution_plugin)

            res = res and (len(self.input_profile) == len(other.input_profile))
            if res:
                # input lists are ordered
                for my_input, other_input in zip(self.input_profile, other.input_profile):
                    res = res and (my_input == other_input)

            res = res and (len(self.output_profile) == len(other.output_profile))
            if res:
                # output lists are ordered
                for my_output, other_output in zip(self.output_profile, other.output_profile):
                    res = res and (my_output == other_output)

            # note: here we do not compare parent algo: it is a context, not the resource itself
            return res
        else:
            return False

    def __str__(self):

        if self.algo is not None:
            return "Implementation %s, execution_plugin=%s, library_address=%s algo=%s" % (
                super(Implementation, self).__str__(),
                self.execution_plugin,
                self.library_address,
                str(self.algo))
        else:
            return "Implementation %s, execution_plugin=%s, library_address=%s algo=None" % (
                super(Implementation, self).__str__(),
                self.execution_plugin,
                self.library_address)
