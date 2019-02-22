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
from ikats.core.library.exception import IkatsInputTypeError, IkatsInputContentError


def check_defined_type(field_name, field_value_type, dictionary, is_optional=False):
    """
    Check json syntax with the mapping dictionary:
    check the data exists, not null, and has expected type.
    :param field_name: name of json data
    :type field_name: str
    :param field_value_type: expected type of value of json data (ex: list, dict, str ...)
    :type field_value_type: a type
    :param dictionary: the object mapping the json
    :type dictionary: dict
    :return: checked value for the defined field.
    :raise exception:  raised in case of check failure:
         IkatsInputTypeError or IkatsInputContentError (both are subclasses of IkatsInputError)
    """
    if not isinstance(dictionary, dict):
        raise IkatsInputTypeError("Bad json mapping dict: suspicious content")

    if field_name not in dictionary.keys():
        if not is_optional:

            raise IkatsInputContentError("Bad json: missing data name: '%s'" % field_name)
        else:
            return None
    value = dictionary[field_name]

    if value is None:
        raise IkatsInputContentError("Bad json: null value")

    if not isinstance(value, field_value_type):
        raise IkatsInputTypeError("Bad json: bad type %s instead of %s" % (type(value), field_value_type))

    return value


def check_defined_list(field_name, dictionary):
    """
    Check json syntax with the mapping dictionary:
    check the data exists, is a list and is not empty list
    :param field_name: data name of the checked field
    :type field_name: str
    :param dictionary: object mapping the json structure
    :type dictionary: dict
    :return: checked list when success
    :rtype: list
    :raise exception: raised in case of check failure:
       IkatsInputTypeError or IkatsInputContentError (both are subclasses of IkatsInputError)
    """
    if not isinstance(dictionary, dict):
        raise IkatsInputTypeError("Bad json mapping dict: suspicious content")

    if field_name not in dictionary.keys():
        raise IkatsInputContentError("Bad json: missing data name: '%s'" % field_name)

    my_list = dictionary[field_name]
    if isinstance(my_list, list):
        if len(my_list) == 0:
            raise IkatsInputContentError(
                "Bad Json: no element defined in data value list for data name: '%s'" % field_name)
        return my_list
    else:
        raise IkatsInputTypeError("Bad json: unexpected data value type for data name: '%s'" % field_name)
