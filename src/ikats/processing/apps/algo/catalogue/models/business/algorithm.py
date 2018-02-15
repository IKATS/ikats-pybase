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
"""
from apps.algo.catalogue.models.business.element import Element


class Algorithm(Element):
    """
    Business class associated to the ORM class AlgorithmDao:

    One Algorithm is an abstraction of a computing issue, which may be supported by several Implementations.

    """

    def __init__(self, name, description, db_id=None, label=None, family=None):
        """
        Constructor

        :param name:
        :type name:
        :param description:
        :type description:
        :param db_id: optional (default None): the DB identifier is the key of the record in the table defined for
                      AlgorithmDao
        :type db_id:
        :param label: optional (default None): the label optionally defined. When undefined: the label attribute is
                      initialized with name argument
        :type label: str
        :param family: optional (default None): the family optionally defined. When undefined: may be defined later
                       by setter
        :type family: FunctionalFamily
        """
        super(Algorithm, self).__init__(name, description, db_id, label)
        self._family = family

    @property
    def family(self):
        """
        Getter for self._family
        """
        return self._family

    @family.setter
    def family(self, value):
        """
        Setter for self._family
        """
        self._family = value

    def __str__(self):

        if self._family is not None:
            return "Algorithm %s, family=%s" % (super(Algorithm, self).__str__(), str(self._family))
        else:
            return "Algorithm %s, family=None" % super(Algorithm, self).__str__()
