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


def method_test1():
    """
    Test method that return a fixed value
    :return: a string
    """
    return "results of the testing method1"


def method_test2():
    """
    Test method that return a fixed value but prints something in STDOUT
    :return: a string
    """
    print("testing method2 with print inside")
    return "results of the testing method2"


def method_test3(val):
    """
    Test method that return the value provided in argument
    :param val: value (any type) to return
    :return: the string with val converted as string
    """
    return "results of the testing method3 : %s" % str(val)


def method_test4(ret):
    """
    returns the value given in arguments
    :param ret: parameter to return
    :return: the parameter as is
    """
    return ret


def method_test5(a, b, c):
    """
    Tested method: test that multiple results are correctly handled
    :param a:
    :type a:
    :param b:
    :type b:
    :param c:
    :type c:
    :return c, b, a
    """
    return c, b, a


def method_test6():
    raise Exception("Simulate error raised by method_test6()")
