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
from django.test import TestCase

from apps.algo.catalogue.models.business.profile import ProfileItem


class TestProfileItem(TestCase):
    """
    Test file for the abstract ProfileItem class
    """

    def test_str(self):
        """
        Testing the __str__ override
        """
        profile_item = ProfileItem(name="param",
                                   description="description of the new param",
                                   dtype=ProfileItem.DTYPE.PARAM,
                                   direction=ProfileItem.DIR.INPUT,
                                   order_index=0,
                                   data_format='String',
                                   domain_of_values='*',
                                   db_id=1)
        self.assertEquals(str(profile_item), "param (id=1, dir Input, at position[0], format=String, domain=*)")

    def test_get_type_name(self):
        """
        Testing the get_type_name method
        """
        profile_item = ProfileItem(name="param",
                                   description="description of the new param",
                                   dtype=ProfileItem.DTYPE.PARAM,
                                   direction=ProfileItem.DIR.INPUT,
                                   order_index=0,
                                   data_format='String',
                                   domain_of_values='*',
                                   db_id=1)
        self.assertEquals(profile_item.get_type_name(), (0, "Parameter"))

        profile_item_2 = ProfileItem(name="arg",
                                     description="description of the new arg",
                                     dtype=ProfileItem.DTYPE.ARG,
                                     direction=ProfileItem.DIR.INPUT,
                                     order_index=0,
                                     data_format='String',
                                     domain_of_values='*',
                                     db_id=1)
        self.assertEquals(profile_item_2.get_type_name(), (1, "Argument"))

    def test_is_input(self):
        """
        Testing the is_input method
        """
        profile_item = ProfileItem(name="param",
                                   description="description of the new param",
                                   dtype=ProfileItem.DTYPE.PARAM,
                                   direction=ProfileItem.DIR.INPUT,
                                   order_index=0,
                                   data_format='String',
                                   domain_of_values='*',
                                   db_id=1)
        self.assertEquals(profile_item.is_input(), True)
        profile_item.direction = ProfileItem.DIR.OUTPUT
        self.assertEquals(profile_item.is_input(), False)

    def test_is_output(self):
        """
        Testing the is_output method
        """
        profile_item = ProfileItem(name="param",
                                   description="description of the new param",
                                   dtype=ProfileItem.DTYPE.PARAM,
                                   direction=ProfileItem.DIR.OUTPUT,
                                   order_index=0,
                                   data_format='String',
                                   domain_of_values='*',
                                   db_id=1)
        self.assertEquals(profile_item.is_output(), True)
        profile_item.direction = ProfileItem.DIR.INPUT
        self.assertEquals(profile_item.is_output(), False)
