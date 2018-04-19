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


class Element(object):
    """
    Abstraction of catalogued elements from business view: common properties
    """

    def __init__(self, name, description, db_id=None, label=None):
        """

        :param name: readable name of element
        :type name: str
        :param description: user-friendly description of element
        :type description: str
        :param db_id: representation of primary key of element, if defined (default is None)
        :type db_id: str representation of primary key
        :param label: optional (default None): the label optionally defined. When undefined: the label attribute is
                    initialized with name argument
        :type label: str
        """
        self._db_id = db_id
        self._name = name
        self._description = description

        if label is not None:
            self._label = label
        else:
            self._label = name

    @property
    def db_id(self):
        """
        Getter for _db_id
        :param self: current instance
        """
        return self._db_id

    @db_id.setter
    def db_id(self, value):
        """
        Setter for _db_id
        :param value: value to set
        :param self: current instance
        """
        self._db_id = value

    @property
    def label(self):
        """
        Getter for _label
        :param self: current instance
        """
        return self._label

    @label.setter
    def label(self, value):
        """
        Setter for _label
        :param value: value to set
        :param self: current instance
        """
        self._label = value

    @property
    def name(self):
        """
        Getter for _name
        :param self: current instance
        """
        return self._name

    @name.setter
    def name(self, value):
        """
        Setter for _name
        :param self: current instance
        :param value: value to set
        """
        self._name = value

    @property
    def description(self):
        """
        Getter for _description
        :param self: current instance
        """
        return self._description

    @description.setter
    def description(self, value):
        """
        Setter for _description
        :param self: current instance
        :param value: value to set
        """
        self._description = value

    def is_db_id_defined(self):
        """
        Returns if the db_id is defined
        :return: True if defined, False otherwise
        """
        return self._db_id is not None

    def __str__(self):
        if self.is_db_id_defined():
            return "%s [label=%s] [id=%s]" % (self.name, self.label, self.db_id)
        else:
            return "%s [label=%s]" % (self.name, self.label)
