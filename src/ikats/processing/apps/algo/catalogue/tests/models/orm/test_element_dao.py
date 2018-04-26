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
from unittest import TestCase

from apps.algo.catalogue.models.orm.element import ElementDao


class TestElementDao(TestCase):
    """
    Test file for the abstract ElementDao class
    """
    def test_label_nominal(self):
        """
        Testing label field access
        """
        element = ElementDao()
        self.assertEquals(element.label, '')
        element.label = "my label"
        self.assertEquals(element.label, "my label")
        self.assertEquals(str(element), element.label)

    def test_desc_nominal(self):
        """
        Testing desc field access
        """
        element = ElementDao()
        self.assertEquals(element.desc, None)
        element.desc = "my desc"
        self.assertEquals(element.desc, "my desc")

    def test_str_robustness(self):
        """
        Testing undefined name return when printing the object
        """
        element = ElementDao()
        self.assertEquals(str(element), "UndefinedLabel")
