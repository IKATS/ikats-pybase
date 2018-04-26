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
from math import tan, pi
"""
This module groups the functions executed during unit tests
See also the tested Implementations defined by class CommonsCatalogueTest,
and used by CommonsCustomTest
"""


def my_tan(angle, factor, phase):
    """
    Function used by the TU: it is not very important to understand the tested formula.
      - returns tan(factor * angle + phase)
    :param angle: the angle value
    :type angle: number
    :param factor: the factor value
    :type factor: number
    :param phase: the phase value
    :type phase: number
    :return: tan(factor * angle + phase)
    :rtype: float
    """
    return tan(factor * angle + phase)


def my_tan_bis(angle, factor, phase):
    """
    Another function used by the TU: it is not very important to understand the tested formula.
      - returns my_tan(angle * 180.0 / pi, factor, phase * 180 / pi)
    :param angle: the angle value
    :type angle: number
    :param factor: the factor value
    :type factor: number
    :param phase: the phase value
    :type phase: number
    :return:  my_tan(angle * 180.0 / pi, factor, phase * 180 / pi)
    :rtype: float
    """
    return my_tan(angle * 180.0 / pi, factor, phase * 180 / pi)
