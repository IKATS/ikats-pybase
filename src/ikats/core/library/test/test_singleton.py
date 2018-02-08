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
from unittest import TestCase
from ikats.core.library.singleton import Singleton


class TestSingleton(TestCase):
    """
    Test of the singleton
    """

    class MySingletonClass(object, metaclass=Singleton):
        """
        Testing class using Singleton
        """

        def __init__(self, *args, **kwargs):
            """
            Initialize the singleton object: to be called once only !

            Just an example of init requiring at least one arg or kwarg
            Otherwise: raises an error => initialization is incorrect
            """

            if (len(args) == 0) and (len(kwargs) == 0):
                raise Exception("Unexpected build")
            self._args = args
            self._kwargs = kwargs

        def get_args(self):
            """
            Returns args
            """
            return self._args

        def get_kwargs(self):
            """
            Returns kwargs
            """
            return self._kwargs

        @classmethod
        def get_singleton(cls):
            """
            Should raise error if constructor not yet called with arguments,
            otherwise should return the singleton
            :param cls:
            :type cls:
            """
            return cls()

    def test_singleton(self):
        """
        Tests nominal use of the singleton
        """

        # Firstly: test that when not initialized with arg/kwarg => raises error
        with self.assertRaises(Exception):
            TestSingleton.MySingletonClass.get_singleton().get_args()

        # first call to singleton: initialize ...
        obj1 = TestSingleton.MySingletonClass(1, 2, 3, toto=4)

        # very weird use for testing: should not pass arguments the second time
        # => will return the original singleton
        obj2 = TestSingleton.MySingletonClass(3, 4, 5)

        # usual get:
        obj3 = TestSingleton.MySingletonClass.get_singleton()
        print(TestSingleton.MySingletonClass.get_singleton().get_args())
        print(TestSingleton.MySingletonClass.get_singleton().get_kwargs())
        self.assertTrue(obj1 == obj2)
        self.assertTrue(obj1 == obj3)
        self.assertTrue(obj1.get_args() == obj2.get_args())
        self.assertTrue(obj3.get_kwargs() == obj2.get_kwargs())
