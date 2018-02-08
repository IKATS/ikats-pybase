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
"""

from django.test import TestCase

from apps.algo.catalogue.models.business.profile import ProfileItem, Parameter, Argument
from apps.algo.catalogue.models.orm.profile import ProfileItemDao


class TestProfileItemDao(TestCase):
    """
    Test file for the abstract AlgorithmDao class
    """
    @classmethod
    def setUpTestData(cls):
        """
        Setup of the test (Fill the database)
        """

        ProfileItemDao.objects.create(name="my_param",
                                      desc="Description of this param",
                                      direction=ProfileItemDao.DIR.OUTPUT,
                                      dtype=ProfileItemDao.DTYPE.PARAM,
                                      order_index=1,
                                      data_format='string',
                                      domain_of_values='*')

        ProfileItemDao.objects.create(name="my_arg",
                                      desc="Description of this param",
                                      direction=ProfileItemDao.DIR.INPUT,
                                      dtype=ProfileItemDao.DTYPE.ARG,
                                      order_index=0,
                                      data_format='string',
                                      domain_of_values='*')

    def test_is_parameter(self):
        """
        Tests the is_parameter method
        """
        profile_1 = ProfileItemDao.objects.get(name__exact="my_param")
        self.assertEquals(profile_1.is_parameter(), True)
        profile_2 = ProfileItemDao.objects.get(name__exact="my_arg")
        self.assertEquals(profile_2.is_parameter(), False)

    def test_is_argument(self):
        """
        Tests the is_argument method
        """
        profile_1 = ProfileItemDao.objects.get(name__exact="my_param")
        self.assertEquals(profile_1.is_argument(), False)
        profile_2 = ProfileItemDao.objects.get(name__exact="my_arg")
        self.assertEquals(profile_2.is_argument(), True)

    def test_str(self):
        """
        Tests the str method override
        """
        profile_1 = ProfileItemDao.objects.get(name__exact="my_param")
        self.assertEquals(str(profile_1), "Output Parameter [1]")
        profile_2 = ProfileItemDao.objects.get(name__exact="my_arg")
        self.assertEquals(str(profile_2), "Input Argument [0]")

    def test_init_orm(self):
        """
        Tests the init_orm method
        """
        profile = Parameter(name="param",
                            description="description of the new param",
                            direction=Parameter.DIR.OUTPUT,
                            order_index=0,
                            data_format='String',
                            domain_of_values='*',
                            db_id=1)
        p_orm = ProfileItemDao.init_orm(profile)
        self.assertEquals(p_orm.name, profile.name)
        self.assertEquals(p_orm.desc, profile.description)
        self.assertEquals(p_orm.dtype, profile.dtype)
        self.assertEquals(p_orm.direction, profile.direction)
        self.assertEquals(p_orm.data_format, profile.data_format)
        self.assertEquals(p_orm.domain_of_values, profile.domain_of_values)
        self.assertEquals(p_orm.order_index, profile.order_index)

    def test_build_business(self):
        """
        tests the build_business method
        """

        # build an ORM object
        p_orm = ProfileItemDao(name="my_param",
                               desc="Description of this param",
                               direction=ProfileItemDao.DIR.OUTPUT,
                               dtype=ProfileItemDao.DTYPE.ARG,
                               order_index=1,
                               data_format='string',
                               domain_of_values='*')

        # Create the corresponding business object: Argument
        p_biz = p_orm.build_business()
        self.assertEquals(isinstance(p_biz, Parameter), False)
        self.assertEquals(isinstance(p_biz, Argument), True)

        # Change Argument to Parameter
        p_orm.dtype = ProfileItem.DTYPE.PARAM

        # Re create the corresponding object: Parameter
        p_biz = p_orm.build_business()
        self.assertEquals(isinstance(p_biz, Parameter), True)
        self.assertEquals(isinstance(p_biz, Argument), False)
