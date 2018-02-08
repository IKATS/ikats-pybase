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
import numpy


def ms_to_timestamp(date_ms):
    """
    Convert to internal timestamp : numpy.int64
    :param date_ms: date in milliseconds
    :type date_ms: float or int or float64 or int64
    :return: conversion
    :rtype: numpy.int64
    """
    if isinstance(date_ms, float) or isinstance(date_ms, numpy.float64):
        return numpy.int64(round(date_ms))
    else:
        # int or int64
        return numpy.int64(date_ms)


def timestamp_to_ms(internal_timestamp):
    """
    Convert internal timestamp to int number in millisecond.
    :param internal_timestamp: timestamp in internal format, assuming that it is in milliseconds
    :type internal_timestamp: numpy int64
    :return: conversion
    :rtype: int
    """
    return int(internal_timestamp)


def ts_mono_to_np(array, only_if_needed=True):
    """
    Convert array defining a TS mono-valued to standard numpy array used by resource client

    Note: values are converted to float64

    :param array:array to be converted
        required:  shape equivalent of ( nb_points, 2) AND nb_points > 0
    :type array: an array (python or numpy ...)
    :param only_if_needed: when true: no conversion is made if first date is already converted, and array is returned
    :type only_if_needed: bool
    :return: conversion
    :rtype: conversion to numpy array whose timestamps are converted to int64 / float64
    """
    assert (len(array) > 0), "Empty Timeseries"
    if only_if_needed:
        if type(array[0][0]) == numpy.float64 or type(array[0][0]) == numpy.int64:
            return array

    return numpy.array([[ms_to_timestamp(point[0]),
                         value_to_float_resource_client(point[1])] for point in array])


def value_to_float_resource_client(value):
    """
    Convert a point value to the resource client format
    :param value: input to be converted
    :type value: float
    :return: converted value
    :rtype: numpy.float64
    """
    return numpy.float64(value)


def to_timestamps_resource_client(array, only_if_needed=True):
    """

    :param array:
    :type array:
    :param only_if_needed: if True: lazy conversion
    :type only_if_needed: bool
    :return: converted timestamps
    :rtype: numpy array of numpy.int64
    """

    if only_if_needed:
        if isinstance(array[0], numpy.int64):
            return array

    return numpy.array([ms_to_timestamp(date) for date in array])


def get_std_float(internal_value):
    """
    Convert internal value: from any type to standard float.
    Note: useful for specific values provided by resource client: boolean, or ...

    :param internal_value:
    :type internal_value: numpy number ...
    :return: converted std value
    :rtype: float
    """
    if isinstance(internal_value, numpy.float64):
        return float(internal_value)

    elif isinstance(internal_value, numpy.number):
        # may be useful : if values are something else: intXX or boolean
        return float(numpy.float64(internal_value))
    else:
        #
        return float(internal_value)


def get_std_millisec(internal_timestamp):
    """

    :param internal_timestamp:
    :type internal_timestamp: see resource client type for timestamps
    :return: converted std timestamp in milliseconds
    :rtype: int
    """

    if isinstance(internal_timestamp, numpy.datetime64):
        return int(internal_timestamp.view(numpy.int64))

    elif isinstance(internal_timestamp, numpy.number):
        return int(numpy.int64(internal_timestamp))

    else:
        return int(internal_timestamp)
