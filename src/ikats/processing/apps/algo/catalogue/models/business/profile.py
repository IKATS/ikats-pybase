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

import logging
from enum import IntEnum

from apps.algo.catalogue.models.business.element import Element

LOGGER = logging.getLogger(__name__)


class ProfileItem(Element):
    """
    Business class defining a profile
    """

    class DIR(IntEnum):
        """
        Enumerate defining the available direction for a profile
        """
        INPUT = 0
        OUTPUT = 1

    DIR_DESC = [(DIR.INPUT, 'Input'), (DIR.OUTPUT, 'Output')]

    class DTYPE(IntEnum):
        """
        Enumerate defining the available type for a profile
        """
        PARAM = 0
        ARG = 1

    TYPE_DESC = [(DTYPE.PARAM, 'Parameter'), (DTYPE.ARG, 'Argument')]

    def __init__(self, name, description, dtype, direction, order_index, data_format,
                 domain_of_values, db_id, label=None, default_value=None):
        """

        :param name: see superclass __init__ : formal name of profile item
        :type name: str
        :param description: see superclass __init__ : short description of profile item
        :type description: str
        :param dtype: internal argument PARAM_TYPE|ARG_TYPE
        :type dtype: DTYPE
        :param direction: 'IN', or 'OUT'
        :type direction: DIR
        :param order_index: rank of item in input profile or output profile, according to item's direction
        :type order_index: int
        :param data_format: data format (for checking rules...), default value: None
        :type data_format: object (TBC)
        :param domain_of_values: data domain (for checking rules...), default value: None
        :type domain_of_values: object (TBC)
        :param db_id:  key matching the corresponding database record, default value: None
        :type db_id: (see DAO type)
        :param label: optional (default None): the label optionally defined. When undefined: the label attribute
                      is initialized with name argument
        :type label: str
        :param default_value: optional (default None): the default value, string encoded, optionally defined.
        :type default_value: str
        """
        super(ProfileItem, self).__init__(name, description, db_id, label)
        self._dtype = int(dtype)
        self._direction = int(direction)
        self._order_index = order_index

        # zero or one data_format
        self._data_format = data_format
        # zero or one domain_of_values
        self._domain_of_values = domain_of_values

        # optional
        self._default_value = default_value

    @property
    def default_value(self):
        """
        Getter for the default value
        :return:
        """
        return self._default_value

    @default_value.setter
    def default_value(self, value):
        """
        Setter for the default value
        :param value:
        :return:
        """
        self._default_value = value

    @property
    def dtype(self):
        """
        Getter for self._dtype
        """
        return self._dtype

    @dtype.setter
    def dtype(self, value):
        """
        Setter for self._dtype
        """
        self._dtype = value

    @property
    def direction(self):
        """
        Getter for self._direction
        """
        return self._direction

    @direction.setter
    def direction(self, value):
        """
        Setter for self._direction
        """
        self._direction = value

    @property
    def order_index(self):
        """
        Getter for self._order_index
        """
        return self._order_index

    @order_index.setter
    def order_index(self, value):
        """
        Setter for self._order_index
        """
        self._order_index = value

    @property
    def data_format(self):
        """
        Getter for self._data_format
        """
        return self._data_format

    @data_format.setter
    def data_format(self, value):
        """
        Setter for self._data_format
        """
        self._data_format = value

    @property
    def domain_of_values(self):
        """
        Getter for self._domain_of_values
        """
        return self._domain_of_values

    @domain_of_values.setter
    def domain_of_values(self, value):
        """
        Setter for self._domain_of_values
        """
        self._domain_of_values = value

    def get_type_name(self):
        """
        returns 'Argument' or 'Parameter' depending on the type of the data
        :return: string containing 'Argument' or 'Parameter'
        """
        if int(self._dtype) in range(0, len(ProfileItem.TYPE_DESC)):
            return ProfileItem.TYPE_DESC[self._dtype]
        else:
            msg = "type is unknown: %s" % self._dtype
            LOGGER.error(msg)
            raise ValueError(msg)

    def is_input(self):
        """
        indicates if the direction is input
        :return: True if input, False otherwise
        """
        return self.direction == ProfileItem.DIR.INPUT

    def is_output(self):
        """
        indicates if the direction is output
        :return: True if output, False otherwise
        """
        return self.direction == ProfileItem.DIR.OUTPUT

    def __str__(self):
        msg = "%s (id=%s, dir %s, at position[%s], format=%s, domain=%s)"
        return msg % (self.name, self.db_id,
                      ProfileItem.DIR_DESC[int(self.direction)][1],
                      self.order_index,
                      str(self.data_format),
                      str(self.domain_of_values))

    def __eq__(self, other):
        # dynamic test on the class: because subclass instances are managed:
        #   and  Argument != Parameter
        if isinstance(other, self.__class__):
            res = (self.db_id == other.db_id)
            res = res and (self.name == other.name)
            res = res and (self.label == other.label)
            res = res and (self.description == other.description)
            res = res and (self.order_index == other.order_index)
            res = res and (self.direction == other.direction)
            res = res and (self.data_format == other.data_format)
            res = res and (self.domain_of_values == other.domain_of_values)
            res = res and (self.default_value == other.default_value)
            return res
        else:
            return False


class Parameter(ProfileItem):
    """
    Parameter specific profile
    """

    def __init__(self, name, description, direction, order_index, db_id=None, data_format=None, domain_of_values=None,
                 label=None, default_value=None):
        super(Parameter, self).__init__(name=name,
                                        description=description,
                                        dtype=ProfileItem.DTYPE.PARAM,
                                        direction=direction,
                                        order_index=order_index,
                                        db_id=db_id,
                                        data_format=data_format,
                                        domain_of_values=domain_of_values, label=label,
                                        default_value=default_value)

    def __str__(self):
        return "Parameter %s" % super(Parameter, self).__str__()


class Argument(ProfileItem):
    """
    Argument specific profile
    """

    def __init__(self, name, description, direction, order_index, db_id=None,
                 data_format=None, domain_of_values=None, label=None):
        super(Argument, self).__init__(name=name, description=description,
                                       dtype=ProfileItem.DTYPE.ARG,
                                       direction=direction,
                                       order_index=order_index,
                                       db_id=db_id,
                                       data_format=data_format,
                                       domain_of_values=domain_of_values, label=label)

    def __str__(self):
        return "Argument %s" % super(Argument, self).__str__()
