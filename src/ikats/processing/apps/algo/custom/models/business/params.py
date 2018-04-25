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

from apps.algo.catalogue.models.orm.profile import ProfileItemDao
from apps.algo.catalogue.models.business.profile import Parameter
from ikats.core.library.exception import IkatsException


class CustomizedParameter(object):
    """
    Business resource of one customized parameter:
     * edited value
     * associated business resource Parameter from catalogue (Parameter is a subclass of ProfileItem)
     * flag is_aliased:
      * When False: the edited value is the string encoding of the effective parameter value at runtime
      * When True: the value defines an alias i.e. a symbolic reference:
          | For dynamic assignment of values to parameter: the alias is
          | matching a namespace defining values shared by the processing
          | session.
    Note: the customized parameter is linked to one resource CustomizedAlgo: see available methods  in \
    class CustomizedAlgo

    .. todo in next stories, about workflows and sessions: is_aliased=True is not yet used at runtime execution of algo
    """

    def __init__(self, cat_parameter, value, db_id=None):
        """
        Constructor
        :param cat_parameter: either parameter business resource from catalogue or parameter database ID
        (business db_id)
        :type cat_parameter: either Parameter (business subclass of ProfileItem) or int
        :param value: edited value, json-friendly object (str, int, bool, list, dict, ...)
        :type value: object
        :param db_id: optional, default None: db_id of self, when self is already saved in DB
        :type db_id: str or None
        """
        if type(cat_parameter) is int:
            try:
                my_param = ProfileItemDao.find_business_elem_with_key(cat_parameter)
            except ProfileItemDao.DoesNotExist:
                my_msg = "Not found in catalogue: parameter with id={}"
                raise IkatsException(msg=my_msg.format(cat_parameter))

        elif not isinstance(cat_parameter, Parameter):
            my_msg = "Unexpected {} type read instead of Parameter: id={} type= {}"
            raise IkatsException(msg=my_msg.format("cat_parameter",
                                                   cat_parameter,
                                                   type(cat_parameter).__name__))
        else:
            my_param = cat_parameter

        self._parameter = my_param
        self._value = value

        # When resource is read from DB: db_id records the primary key
        self._db_id = db_id

    def get_db_id(self):
        """
        Gets the database id
        """
        return self._db_id

    def set_db_id(self, value):
        """
        Sets the database ID
        :param value: the database ID
        :type value: int
        """
        self._db_id = value

    def get_parameter(self):
        """
        Getter on the catalogue business Parameter associated to self
        """
        return self._parameter
    # no setter on parameter: it is assumed to be read-only from self

    def get_value(self):
        return self._value

    def set_value(self, value):
        self._value = value

    # no setter on parameter: it is assumed to be read-only from self
    parameter = property(get_parameter, None, None, "")
    # Value getter+setter
    value = property(get_value, set_value, None, "")

    def __eq__(self, other):
        """
        Implements the '==' operator on CustomizedParameter

        Note: self.db_id and other.db_id are not compared.
        :param other:
        :type other: CustomizedParameter
        :return: True if self and other represent the same business content
        :rtype: bool
        """
        if not isinstance(other, CustomizedParameter):
            return False

        if (self.parameter.db_id is None) and (other.parameter.db_id is None):
            msg = "Forbidden: both compared parameter.db_id are None with \n{} and \n{}".format(self, other)
            raise IkatsException(msg)

        return (
            self.parameter.db_id == other.parameter.db_id
        ) and (
            self.value == other.value
        )

    def __str__(self):

        my_info = "CustomizedParameter name={} id={} value={} ref_profile_item={}"

        return my_info.format(self.parameter.name,
                              self.db_id,
                              self.value,
                              self.parameter.db_id)

    db_id = property(get_db_id, set_db_id, None, "")
