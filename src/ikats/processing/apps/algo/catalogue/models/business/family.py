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

from apps.algo.catalogue.models.business.element import Element


class FunctionalFamily(Element):
    """
    Business class associated to the ORM class FunctionalFamilyDao:

    One FunctionalFamily is an abstraction of a group of computing issues.

    It is designed in order to be able to classify different Algorithms into one set, their FunctionalFamily.

    """

    def __init__(self, name, description, db_id=None, label=None):
        """
        Constructor

        :param name:
        :type name:
        :param description:
        :type description:
        :param db_id: optional (default None): the DB identifier is the key of record in the table defined
                    for FunctionalFamilyDao
        :type db_id:
        :param label: optional (default None): the label optionally defined. When undefined: the label attribute
                is initialized with name argument
        :type label: str
        """
        super(FunctionalFamily, self).__init__(name, description, db_id, label)

    def __str__(self):
        return "FunctionalFamily %s" % super(FunctionalFamily, self).__str__()
