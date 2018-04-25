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
from django.test import TestCase
from apps.algo.catalogue.models.business.profile import ProfileItem, Parameter, Argument
from apps.algo.catalogue.models.business.implem import Implementation


class TestImplementation(TestCase):
    """
    Test file for the Implementation class
    """
    def test_init(self):
        """
        Tests the init method override
        """
        imp = Implementation('Name_of_my_implementation',
                             'description of my implementation',
                             'Execution_plugin_name',
                             'library/address/')

        self.assertEquals(imp.input_profile, [])
        self.assertEquals(imp.output_profile, [])

    def test_input_profile(self):
        """
        Tests the input_profile method cases
        """

        profile1 = Parameter(name="param",
                             description="description of the new param",
                             direction=Parameter.DIR.INPUT,
                             order_index=0,
                             data_format='String',
                             domain_of_values='*',
                             db_id=1)

        profile2 = Argument(name="arg",
                            description="description of the new arg",
                            direction=Argument.DIR.INPUT,
                            order_index=1,
                            data_format='Int',
                            domain_of_values='*',
                            db_id=1)

        try:
            imp = Implementation('Name_of_my_implementation',
                                 'description of my implementation',
                                 'Execution_plugin_name',
                                 'library/address/',
                                 input_profile=[profile1, profile2])
        except TypeError:
            self.fail("input_profile raised TypeError unexpectedly!")

        # Testing input_profile as a non-list
        with self.assertRaises(TypeError):
            imp.input_profile = "A list is expected here"

        # Trying to add Output in Input_profile list
        profile1.direction = Parameter.DIR.OUTPUT
        with self.assertRaises(ValueError):
            imp.input_profile = [profile1, profile2]

        # Trying another case for adding Output in Input_profile list
        profile1.direction = Parameter.DIR.INPUT
        profile2.direction = Parameter.DIR.OUTPUT
        with self.assertRaises(ValueError):
            imp.input_profile = [profile1, profile2]

        # Sorting
        profile2.direction = Parameter.DIR.INPUT
        imp.input_profile = [profile2, profile1]
        self.assertEquals(imp.input_profile, [profile1, profile2])

        # Finding inputs ...
        # ... among Arguments or Parameters
        item1 = imp.find_by_name_input_item("param")
        self.assertEquals(profile1, item1)
        item2 = imp.find_by_name_input_item("arg")
        self.assertEquals(profile2, item2)
        # ... only among Arguments
        item3 = imp.find_by_name_input_item("param", accepted_type=Argument)
        self.assertEquals(None, item3)
        item4 = imp.find_by_name_input_item("arg", accepted_type=Argument)
        self.assertEquals(profile2, item4)
        # ... only among Parameters
        item5 = imp.find_by_name_input_item("param", accepted_type=Parameter)
        self.assertEquals(profile1, item5)
        item6 = imp.find_by_name_input_item("arg", accepted_type=Parameter)
        self.assertEquals(None, item6)

        # ... mismatched name
        item7 = imp.find_by_name_input_item("mismatched_name")
        self.assertEquals(None, item7)

    def test_output_profile(self):
        """
        Tests the output_profile method
        """

        profile1 = Parameter(name="param",
                             description="description of the new param",
                             direction=Parameter.DIR.OUTPUT,
                             order_index=0,
                             data_format='String',
                             domain_of_values='*',
                             db_id=1)

        profile2 = Argument(name="arg",
                            description="description of the new arg",
                            direction=Argument.DIR.OUTPUT,
                            order_index=1,
                            data_format='Int',
                            domain_of_values='*',
                            db_id=1)

        try:
            imp = Implementation('Name_of_my_implementation',
                                 'description of my implementation',
                                 'Execution_plugin_name',
                                 'library/address/',
                                 output_profile=[profile1, profile2])
        except TypeError:
            self.fail("output_profile raised TypeError unexpectedly!")

        # Testing output_profile as a non-list
        with self.assertRaises(TypeError):
            imp.output_profile = "A list is expected here"

        # Trying to add Output in output_profile list
        profile1.direction = ProfileItem.DIR.INPUT
        with self.assertRaises(ValueError):
            imp.output_profile = [profile1, profile2]

        # Trying another case for adding Output in output_profile list
        profile1.direction = ProfileItem.DIR.OUTPUT
        profile2.direction = ProfileItem.DIR.INPUT
        with self.assertRaises(ValueError):
            imp.output_profile = [profile1, profile2]

        # Sorting
        profile2.direction = ProfileItem.DIR.OUTPUT
        imp.output_profile = [profile2, profile1]
        self.assertEquals(imp.output_profile, [profile1, profile2])
