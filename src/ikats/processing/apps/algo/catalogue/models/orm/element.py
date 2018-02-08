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

import sys

from django.db import models

from ikats.core.library.exception import IkatsException, IkatsInputError


class ElementDao(models.Model):
    """
    ElementDao (layer ORM) of catalogue is an abstraction: it defines common properties
    """

    # id: automatically added by Django
    id = models.AutoField(primary_key=True)

    label = models.CharField(max_length=60, null=False, blank=False, help_text='readable label adapted to the display')
    desc = models.TextField(help_text='full description', null=True)

    class Meta(object):
        """
        Defines Django abstract overriding : this model will not map a table "ElementDao" in the database.
        See: https://docs.djangoproject.com/fr/1.8/topics/db/models/#abstract-base-classes
        """
        abstract = True
        ordering = ['name']

    @classmethod
    def init_elem_orm(cls, business_obj, save=False):
        """
        Build the ORM object based on corresponding business class
        It will return the ORM object filled with business information
        :param cls:
        :type cls:
        :param business_obj: business object containing information
        :type business_obj: Parameter or Argument
        :param save:True if it is required to save object
        :type save: bool
        :return: the ORM object (instance of ProfileItemDao)
        """

        # Create the ORM object to return
        db_obj = cls()

        # Fill in the object with the business data
        db_obj.name = business_obj.name
        db_obj.desc = business_obj.description
        db_obj.label = business_obj.label

        if save:
            db_obj.save()

        return db_obj

    @classmethod
    def find_all_orm(cls):
        """
        Returns all elements
        :return:
        """
        return list(cls.objects.all())

    @classmethod
    def find_orm_accepted_by_filter(cls, filter_function):
        """
        Finds every elements matched by the filter

        :param cls: an ikats DAO element
        :type cls: ElementDao or subclass of ElementDao
        :param filter_function: the filter: bool function with one arg typed cls
        :type filter_function: function
        :return: filtered list of DAO element of class cls
        :rtype: list of cls instances -orm class- matched by the filter
        """

        if filter_function is None:
            raise Exception("Forbidden: find_accepted_by_filter(None): None not accepted as boolean function")
        else:
            return [x for x in cls.find_all_orm() if (filter_function(x))]

    @classmethod
    def find_orm_from_element_def(cls, name=None, description_part=None, label=None):
        """
        This reading method finds ElementDao matching the criteria (name, description_part, label)
        :param cls:
        :type cls:
        :param name: optional value, default None: if not None, the exact value matching the name of \
                     searched ElementDao. None disables the name filtering.
        :type name: str
        :param description_part: optional value, default None: if not None, the part of description \
                                 searched on the ElementDao. None disables the description_part filtering.
        :type description_part: str
        :param label: optional value, default None: if not None, the exact value matching the label of \
                      searched ElementDao. None disables the name filtering.
        :type label: str
        :return: the filtered QuerySet
        :rtype: QuerySet
        """
        try:
            if name is not None:
                my_query_set = cls.objects.filter(name=name)
            else:
                my_query_set = cls.objects.all()

            if label is not None:
                my_query_set2 = my_query_set.filter(label=label)
            else:
                my_query_set2 = my_query_set

            if description_part is not None:
                my_query_set3 = my_query_set2.filter(desc__contains=description_part)
            else:
                my_query_set3 = my_query_set2

            return my_query_set3

        except Exception as err:
            trace_back = sys.exc_info()[2]
            err_msg = "Failed: find_orm_from_element_def(name={},description_part={},label={}"
            raise IkatsException(msg=err_msg.format(name,
                                                    description_part,
                                                    label), cause=err).with_traceback(trace_back)

    @classmethod
    def find_business_from_element_def(cls, name=None, description_part=None, label=None):
        """
        This reading method finds business instances defined by cls and matching the criteria
        (name, description_part, label).

        :param cls: subclass of ElementDao: must provide object method build_business
        :type cls:
        :param name: optional value, default None: if not None, the exact value matching the name of \
                     searched ElementDao. None disables the name filtering.
        :type name: str
        :param description_part: optional value, default None: if not None, the part of description \
                                 searched on the ElementDao. None disables the description_part filtering.
        :type description_part: str
        :param label: optional value, default None: if not None, the exact value matching the label of \
                      searched ElementDao. None disables the name filtering.
        :type label: str
        :return: list of found objects matching the criteria
        :rtype: list of business instances
        """
        try:
            res = []
            query_set = cls.find_orm_from_element_def(name=name, description_part=description_part, label=label)
            for found in query_set:
                # !!! should exist: object method build_business in class cls !!!
                res.append(found.build_business())
            return res
        except Exception as err:
            trace_back = sys.exc_info()[2]
            err_msg = "Failed: find_business_from_element_def(name={},description_part={},label={}"
            raise IkatsException(msg=err_msg.format(name,
                                                    description_part,
                                                    label), cause=err).with_traceback(trace_back)

    @classmethod
    def find_business_elem_with_key(cls, primary_key):
        """
        Finds the unique instance of ElementDao matching the primary key, for the defined class.
        :param cls: subclass of ElementDao on which the finding request is applied
        :type cls: subclass of ElementDao
        :param primary_key: the primary key matching the instance of ElementDao
        :type primary_key: int
        :return: the business object having the primary key. None is returned when key is not found.
        :rtype: cls
        :raise cls.DoesNotExist: when the primary key did not match any record in database.
          Ex: ImplementationDao.find_business_elem_with_key(...) may raise ImplementationDao.DoesNotExist
          with unmatching primary key
        """
        db_obj = cls.objects.get(id=primary_key)
        if db_obj:
            return db_obj.build_business()
        else:
            return None

    @classmethod
    def find_business_elem_with_name(cls, name):
        """
        Search list of resources matched by name.
        Note: list size is may be
        :param cls:
        :type cls:
        :param name: name of searched resource(s)
        :type name: str
        :return: business objects found for given name
        """

        try:

            res = []

            my_query_set = cls.objects.filter(name=name)

            for db_obj in my_query_set:
                res.append(db_obj.build_business())
            return res

        except Exception as err:
            trace_back = sys.exc_info()[2]
            raise IkatsException(msg="Failed: find business element_with_name=" + name, cause=err).with_traceback(
                trace_back)

    @classmethod
    def parse_dao_id(cls, element_id):
        """
        Check and return parsed identifier compatible with DAO layer
        :param element_id:
        :type element_id:
        """
        if type(element_id) is str:
            my_id = int(element_id)
        elif type(element_id) is not int:
            raise IkatsInputError("Unexpected format: int or parsable str expected for database id")
        else:
            my_id = element_id
        return my_id

    def __str__(self):
        if self.label:
            return self.label
        else:
            return "UndefinedLabel"
