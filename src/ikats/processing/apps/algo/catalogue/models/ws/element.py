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
import json

from apps.algo.catalogue.models.business.element import Element
from ikats.core.json_util.rest_utilities import LevelInfo


class ElementWs(object):
    """
    WS resource: ElementWs wraps the Element business object

    Not directly returned: this abstraction is derived by ImplementationWs etc.
    """

    def __init__(self, business_obj):
        """
        Constructor...
        """
        assert (isinstance(business_obj, Element)), \
            "Expects Element type for argument business_obj in ElementWs constructor"

        self.__model_biz = business_obj

    @property
    def model_business(self):
        """
        Getter of the business resource wrapped behind this web service resource
        """
        return self.__model_biz

    def add_element_properties_to_dict(self, completed_impl_dict, element=None, level=LevelInfo.NORMAL):
        """
        Complete completed_impl_dict with business Element information (name, label, description, ...)
        :param completed_impl_dict: initialized dict, that is completed with element information: None forbidden
        :type completed_impl_dict: dict
        :param element: optional business resource Element (default None). When None: self.model_business is used
        :type element: Element
        :param level: enum value for the level of details added in completed_impl_dict: optional, default is NORMAL
        :type level: enum ikats.core.json.rest_utilities.LevelInfo
        :return: completed dict (same instance than completed_impl_dict)
        :rtype:dict
        """

        if element is None:
            my_element = self.model_business
        else:
            my_element = element

        completed_impl_dict['id'] = my_element.db_id
        completed_impl_dict['name'] = my_element.name
        completed_impl_dict['label'] = my_element.label
        completed_impl_dict['description'] = my_element.description

        return completed_impl_dict

    def to_dict(self, level=LevelInfo.NORMAL):
        """
        Return the json-friendly dictionary associated to self.
        :param level: level of details, optional, default is NORMAL
        :type level: enum value ikats.core.json.rest_utilities.LevelInfo
        :return: a dictionary Json-serializable resource ElementWs
        :rtype: dict
        """
        my_dict = {}
        return self.add_element_properties_to_dict(my_dict, element=self.model_business, level=level)

    def to_json(self, indent=2, level=LevelInfo.NORMAL):
        """
        Returns the json string associated to self: encoded from self.to_dict()
        :param indent: indent arg passed to json.dumps
        :type indent: int
        :param level: LevelInfo of produced json: see enum values.
        :type level: LevelInfo
        :return the json content
        :rtype: str
        """
        my_dict = self.to_dict(level)
        return json.dumps(obj=my_dict, indent=indent)
