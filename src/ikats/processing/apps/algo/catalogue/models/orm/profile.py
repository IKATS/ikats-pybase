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
import json
from enum import IntEnum

from django.db import models as djmodels

from apps.algo.catalogue.models.business.profile import Parameter, Argument
from apps.algo.catalogue.models.orm.element import ElementDao


class ProfileItemDao(ElementDao):
    """
    ProfileItemDao from ORM layer:

    One instance of ProfileItemDao is mapping the database information for one specific input/output configured on
    one ImplementationDao.
      - build_business() returns new instance of associated business.Argument or business.Parameter

    The ProfileItemDao provides CRUD services with class methods:
      - find(criteria) returns business.Argument or business.Parameter according to retrieved ProfileItemDao
      - create(business.Argument or business.Parameter) creates record in database
      - update(business.Argument or business.Parameter) updates record in database
      - delete(business.Argument or business.Parameter) delete record in database

    """

    name = djmodels.CharField(max_length=60, null=False, blank=False, help_text='readable name')

    class DIR(IntEnum):
        """
        Enumerate defining the available direction for a profile
        """
        INPUT = 0
        OUTPUT = 1

    DIRECTIONS = [(DIR.INPUT, 'Input'), (DIR.OUTPUT, 'Output')]

    class DTYPE(IntEnum):
        """
        Enumerate defining the available type for a profile
        """
        PARAM = 0
        ARG = 1

    ITEM_DB_TYPES = [(DTYPE.PARAM, 'Parameter'), (DTYPE.ARG, 'Argument')]

    direction = djmodels.PositiveSmallIntegerField(choices=DIRECTIONS)

    # dtype: field defining the DTYPE enum for the ProfileItemDao: PARAM or ARG
    #
    # Note: currently published on HMI side: before story [#146979]
    #      ARG   => not edited by the user in viztool, but passed by the workflow, and possibly read by the viztool
    #      PARAM => edited by the user in viztool, and passed by the workflow
    #
    dtype = djmodels.PositiveSmallIntegerField(null=False, blank=False, choices=ITEM_DB_TYPES)

    # order_index:
    #
    # One ordering index is needed to encode input arguments/parameters (from zero to ...)
    # It is also needed to decode output arguments in case of multiple return
    #
    # For output items: index is restarting from zero

    order_index = djmodels.PositiveSmallIntegerField(null=False, blank=False, default=0)

    # data_format:
    #
    # The value of the functional type of the instance of ProfileItemDao

    data_format = djmodels.TextField('expected data format', null=True)

    # domain_of_values:
    #
    # Defines the possible values for that ProfileItemDao: constraint to be defined
    # (interval, function, enumerate, ...)

    domain_of_values = djmodels.TextField('domain of values', null=True)

    # default_value:
    #
    # Optional: string encoding the default value defined in the catalogue
    #
    # Note: when undefined: NULL in database
    #
    # Note: the real value is computed by the system from the data_format and the default_value
    #
    default_value = djmodels.TextField('default value', null=True,
                                       help_text='optional: string encoding the default value defined in the catalogue')

    def is_parameter(self):
        """
        tests if the profile is a parameter
        :return: True if it is a parameter, False otherwise
        """
        return self.dtype == self.DTYPE.PARAM

    def is_argument(self):
        """
        tests if the profile is an argument
        :return: True if it is an argument, False otherwise
        """
        return self.dtype == self.DTYPE.ARG

    def has_default_value(self):
        """
        Tests is this profile item defines a default value.
        :return: True if a default value is defined in the catalogue: accessed by self.default_value
        :rtype: boolean
        """
        return self.default_value and (type(self.default_value) is str) and (len(self.default_value) > 0)

    def __str__(self):
        return "%s %s [%i]" % (self.DIRECTIONS[int(self.direction)][1],
                               self.ITEM_DB_TYPES[int(self.dtype)][1], int(self.order_index))

    def build_business(self):
        """
        From the ORM object, this method will create the corresponding biz object.
        :return: The business object
        """
        if self.is_parameter():
            if (self.default_value is None) or (len(self.default_value) == 0):
                decoded_default_value = None
            else:
                # From DB: str encoded JSON => loaded into python object
                decoded_default_value = json.loads(self.default_value)

            return Parameter(name=self.name,
                             description=self.desc,
                             direction=self.direction,
                             order_index=self.order_index,
                             db_id=self.id,
                             data_format=self.data_format,
                             domain_of_values=self.domain_of_values, label=self.label,
                             default_value=decoded_default_value)
        else:
            # Presently: default_value is not handled for arguments
            return Argument(name=self.name,
                            description=self.desc,
                            direction=self.direction,
                            order_index=self.order_index,
                            db_id=self.id,
                            data_format=self.data_format,
                            domain_of_values=self.domain_of_values, label=self.label)

    @classmethod
    def init_orm(cls, business_profile_item, save=False):
        """
        Build the ORM object based on corresponding business class
        It will return the ORM object filled with business information
        :param cls:
        :type cls:
        :param business_profile_item: business object containing information
        :type business_profile_item: Parameter or Argument
        :param save:True if it is required to save object
        :type save: bool
        :return: the ORM object (instance of ProfileItemDao)
        """

        # Create the ORM object to return
        db_obj = ProfileItemDao()

        if isinstance(business_profile_item, Parameter):
            db_obj.dtype = ProfileItemDao.DTYPE.PARAM

            # Default value presently restricted to parameters
            if business_profile_item.default_value is not None:
                # Encode obj value from business into json string saved in database
                db_obj.default_value = json.dumps(business_profile_item.default_value)

        elif isinstance(business_profile_item, Argument):
            db_obj.dtype = ProfileItemDao.DTYPE.ARG
        else:
            raise Exception(
                "Unexpected business value for ProfileItemDao::dtype : %s" % str(type(business_profile_item)))

        # Fill in the object with the business data
        db_obj.name = business_profile_item.name
        db_obj.desc = business_profile_item.description
        db_obj.direction = business_profile_item.direction
        db_obj.order_index = business_profile_item.order_index
        db_obj.label = business_profile_item.label

        if business_profile_item.data_format:
            db_obj.data_format = business_profile_item.data_format

        if business_profile_item.domain_of_values:
            db_obj.domain_of_values = business_profile_item.domain_of_values

        if save:
            db_obj.save()

        return db_obj

    @classmethod
    def create(cls, business_profile_item, save=True):
        """
        Create (and save) the ORM instance associated to the business instance (see business_profile_item)
        Returns the business object mapping the created ORM
        :param cls: ORM class
        :type cls: ProfileItemDao (or any subclass of ProfileItemDao)
        :param business_profile_item: the business object defining the ORM instance
        :type business_profile_item:
        :param save: True if save() is called on the ORM created, default value is True.
        :type save: boolean
        """
        db_obj = ProfileItemDao.init_orm(business_profile_item, save)

        return db_obj.build_business()
