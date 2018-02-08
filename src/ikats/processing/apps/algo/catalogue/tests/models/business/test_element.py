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

from apps.algo.catalogue.models.business.profile import Element


class TestElement(TestCase):
    """
    Test file for the Business Element class
    """
    def test_is_db_id_defined(self):
        """
        Tests the method is_db_id_defined
        """
        obj = Element(name="MyElement", description="Description of MyElement")
        self.assertEquals(obj.is_db_id_defined(), False)
        obj.db_id = 1
        self.assertEquals(obj.is_db_id_defined(), True)
