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

from apps.algo.catalogue.models.business.family import FunctionalFamily
from apps.algo.catalogue.models.orm.element import ElementDao
from django.db import models as djmodels


class FunctionalFamilyDao(ElementDao):
    """
    FunctionalFamilyDao from ORM layer: the functional family is grouping some algorithms matching the same
    generic mathematical problem.

    For example: the "classifier" functional family may be addressed by several kinds of algorithms.
    """

    name = djmodels.CharField(max_length=60, null=False, blank=False, help_text='readable name')

    def __str__(self):
        return "FunctionalFamilyDao[%s]" % (ElementDao.__str__(self))

    def build_business(self):
        """
        Build the business formatted FunctionalFamily based on the current ORM data
        :return: the business instance FunctionalFamily mapping self instance
        """
        return FunctionalFamily(name=self.name, description=self.desc, db_id=self.id, label=self.label)

    @classmethod
    def create(cls, business_family):
        """
        :param business_family: business family
        :type business_family: FunctionalFamily
        :return: FunctionalFamily
        """

        assert (not business_family.is_db_id_defined())

        my_name = business_family.name

        if FunctionalFamilyDao.find_business_elem_with_name(my_name):
            raise Exception(
                "FunctionalFamilyDao.create(...) aborted: definition (name) already exists in database for %s" % str(
                    business_family))

        db_obj = FunctionalFamilyDao.init_elem_orm(business_family, save=False)

        # save object BEFORE updating the many to many relationship !!!
        db_obj.save()

        # feed back to the business object: provide the created key
        return db_obj.build_business()

    @classmethod
    def get_sync_orm(cls, business_obj):
        """
        Build the ORM object associated to the business object:
         - case 1: db_id key is defined and is matching a database element => returns the synchronized element
            requiring optional update when needed (see TODO!!!)
         - case 2: undefined db_id key: create the object, and return it

        :param business_obj: business object containing information
        :type business_obj: FunctionalFamily
        :return: orm object synchronized with db
        :rtype: FunctionalFamilyDao
        """
        if not business_obj.is_db_id_defined():

            orm_obj = cls.init_elem_orm(business_obj, save=True)
        else:
            # assumes that orm object exists in database ...
            orm_obj = cls.objects.get(id=business_obj.db_id)
            if orm_obj is None:
                raise Exception("Undefined in database: {2} with id={0} name={1}".format(business_obj.db_id,
                                                                                         business_obj.name,
                                                                                         cls.__name__))

        return orm_obj

    @classmethod
    def init_orm(cls, business_obj, save=False):
        """
        The specific implementation of init_orm for the FunctionalFamilyDao is simply
        the basic init_elem_orm() from superclass. It may Evolve later.
        :param business_obj: business object containing information
        :type business_obj: FunctionalFamily
        :param save: optional flag, default=False: True activates the save in database
        :type save: bool
        :return: the ORM object (instance of ProfileItemDao)
        """
        return cls.init_elem_orm(business_obj, save)

    @classmethod
    def update(cls, business_obj):
        """

        :param business_obj: the business object to update
        :type business_obj: FunctionalFamily
        :return: the business object updated
        :rtype: FunctionalFamily
        """
        assert (business_obj.is_db_id_defined())

        if not FunctionalFamilyDao.find_business_elem_with_key(business_obj.db_id):
            raise Exception(
                "FunctionalFamilyDao.update(...) aborted: resource not found with db_id=%s" % str(
                    business_obj.db_id))

        db_obj = FunctionalFamilyDao.init_elem_orm(business_obj, save=False)
        db_obj.id = business_obj.db_id
        # save object BEFORE updating the many to many relationship !!!
        db_obj.save()

        # feed back to the business object: provide the created key
        return db_obj.build_business()

    @classmethod
    def delete(cls, business_fam):
        """
        Delete resource Algorithm from database, without deleting parent family
        :param cls:
        :type cls:
        :param business_fam:

        """
        cls.delete_from_id(business_fam.db_id)

    @classmethod
    def delete_from_id(cls, db_id):
        """
        Delete resource Algorithm from database
        """
        db_obj = cls.objects.get(id=db_id)
        db_obj.delete()
