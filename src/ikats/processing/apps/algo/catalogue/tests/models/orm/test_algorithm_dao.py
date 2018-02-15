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

from apps.algo.catalogue.models.orm.algorithm import AlgorithmDao, FunctionalFamilyDao


class TestAlgorithmDao(TestCase):
    """
    Test file for the abstract AlgorithmDao class
    """

    @classmethod
    def setUpTestData(cls):
        """
        Setup of the test (Fill the database)
        """
        FunctionalFamilyDao.objects.create(name="Reduction", desc="This is another test family")
        f_record = FunctionalFamilyDao.objects.create(name="Clustering", desc="This is a test family")
        AlgorithmDao.objects.create(name="my_Algo", desc="Description of my awesome algo", family=f_record)

    def test_algorithm_nominal(self):
        """
        Tests the nominal query
        """

        a_record = AlgorithmDao.objects.get(name="my_Algo")

        self.assertEquals(a_record.name, "my_Algo")
        self.assertEquals(a_record.desc, "Description of my awesome algo")
        self.assertEquals(a_record.family.name, "Clustering")
        self.assertEquals(a_record.family.desc, "This is a test family")

    def test_algorithm_nominal2(self):
        """
        Tests Family change for an algo
        """
        a_record = AlgorithmDao.objects.get(name="my_Algo")
        f_record = FunctionalFamilyDao.objects.get(name="Reduction")
        a_record.family = f_record
        a_record.save()

        self.assertEquals(a_record.name, "my_Algo")
        self.assertEquals(a_record.desc, "Description of my awesome algo")
        self.assertEquals(a_record.family.name, "Reduction")
        self.assertEquals(a_record.family.desc, "This is another test family")

    def test_algorithm_nominal3(self):
        """
        Tests Family change for an algo
        """
        a_record = AlgorithmDao.objects.get(name="my_Algo")
        f_record = FunctionalFamilyDao.objects.get(name="Reduction")
        a_record.family = f_record
        a_record.family.name = "NewName"
        a_record.save()

        self.assertEquals(a_record.name, "my_Algo")
        self.assertEquals(a_record.desc, "Description of my awesome algo")
        self.assertEquals(a_record.family.name, "NewName")
        self.assertEquals(a_record.family.desc, "This is another test family")
