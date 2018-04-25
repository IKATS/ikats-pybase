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

from django.db import models as djmodels

from apps.algo.catalogue.models.business.algorithm import Algorithm
from apps.algo.catalogue.models.orm.element import ElementDao
from apps.algo.catalogue.models.orm.family import FunctionalFamilyDao


class AlgorithmDao(ElementDao):
    """
    AlgorithmDao from ORM layer: the AlgorithmDao is responding to one specific problem from a FunctionalFamilyDao.
    The AlgorithmDao is the formal definition, typically like a mathematical paper describing how to solve a problem.
    IKATS is linking one AlgorithmDao to several (0, *) ImplementationDao's.

    For example: the K-means clustering algorithm belongs to the "clustering" FunctionalFamilyDao.
    """

    name = djmodels.CharField(max_length=60, null=False, blank=False, help_text='readable name')
    family = djmodels.ForeignKey(FunctionalFamilyDao)

    def build_business(self):
        """
        Build the business formatted Algorithm based on the current ORM data
        :return: the business instance Algorithm mapping self instance
        """
        business_family = None
        if self.family:
            business_family = self.family.build_business()

        business_algo = Algorithm(name=self.name, description=self.desc, db_id=self.id, label=self.label)
        business_algo.family = business_family

        return business_algo

    def __str__(self):
        if self.family:
            return "AlgorithmDao [%s] from family [%s]" % (ElementDao.__str__(self), self.family.__str__())
        else:
            return "Orphan AlgorithmDao [%s]" % (ElementDao.__str__(self))

    @classmethod
    def init_orm(cls, business_algo, save=False):
        """
        Build the ORM object based on corresponding business class
        It will return the ORM object filled with business information
        :param business_algo: business object containing information
        :type business_algo: Algorithm
        :param save:True if it is required to save object
        :type save: bool
        :return: the ORM object (instance of AlgorithmDao)
        """

        # Create the ORM object to return
        db_obj = AlgorithmDao.init_elem_orm(business_algo, False)

        if (save is True) and business_algo.family:
            db_obj.family = FunctionalFamilyDao.get_sync_orm(business_algo.family)

        elif business_algo.family:
            db_obj.family = FunctionalFamilyDao.init_elem_orm(business_algo.family, save=False)

        if save is True:
            db_obj.save()

        return db_obj

    @classmethod
    def create(cls, business_algo):
        """
        :param business_algo: the business algorithm not yet saved in database
        :type business_algo: Algorithm
        :return: Algorithm
        """

        assert (not business_algo.is_db_id_defined())

        my_name = business_algo.name

        if AlgorithmDao.find_business_elem_with_name(my_name):
            raise Exception(
                "AlgorithmDao.create(...) aborted: definition (name) already exists in database for %s" % str(
                    business_algo))

        db_obj = AlgorithmDao()
        db_obj.name = my_name
        db_obj.desc = business_algo.description
        db_obj.label = business_algo.label

        business_family = business_algo.family

        if business_family is not None:
            db_obj.family = FunctionalFamilyDao.get_sync_orm(business_family)

        # save object BEFORE updating the many to many relationship !!!
        db_obj.save()

        # feed back to the business object: provide the created key
        return db_obj.build_business()

    @classmethod
    def get_sync_orm(cls, business_obj):
        """
        Build the ORM object associated to the business object:
         - case 1: db_id key is defined and is matching a database element => returns the synchronized element
            requiring optional update when needed
         - case 2: undefined db_id key: create the object, and return it

        :param business_obj: business object
        :type business_obj: Algorithm
        :return: orm object synchronized with db
        :rtype: AlgorithmDao
        """
        if not business_obj.is_db_id_defined():
            # !!! init_orm() is specific to the class, not init_elem_orm() !!!
            #
            orm_obj = cls.init_orm(business_obj, save=True)
        else:
            # assumes that orm object exists in database ...
            orm_obj = cls.objects.get(id=business_obj.db_id)
            if orm_obj is None:
                raise Exception("Undefined in database: {2} with id={0} name={1}".format(business_obj.db_id,
                                                                                         business_obj.name,
                                                                                         cls.__name__))

        return orm_obj

    @classmethod
    def update(cls, business_algo):
        """
        Update the database from an Algorithm business resource
        :param business_algo: the Algorithm business resource. Required: db_id is defined.
        :type business_algo: new Algorithm instance for updated resource in database. Note: new object is returned.
        """
        assert (business_algo.is_db_id_defined())

        if not AlgorithmDao.find_business_elem_with_key(business_algo.db_id):
            raise Exception(
                "AlgorithmDao.update(...) aborted: resource not found with db_id=%s" % str(
                    business_algo.db_id))

        db_obj = AlgorithmDao.init_elem_orm(business_algo, save=False)
        db_obj.id = business_algo.db_id
        business_family = business_algo.family

        if business_family is not None:
            db_obj.family = FunctionalFamilyDao.init_elem_orm(business_family, save=True)
        else:
            db_obj.family = None

        # save object BEFORE updating the many to many relationship !!!
        db_obj.save()

    @classmethod
    def delete(cls, business_algo):
        """
        Delete resource Algorithm from database, without deleting parent family
        :param cls:
        :type cls:
        :param business_algo:
        :type business_algo:
        :return: parent family id or None
        """
        parent_id = None
        if business_algo.family:
            parent_id = business_algo.family.db_id

        cls.delete_from_id(business_algo.db_id)
        return parent_id

    @classmethod
    def delete_from_id(cls, db_id):
        """
        Delete resource Algorithm from database by its identifier
        :param db_id:
        :return:
        """
        db_obj = cls.objects.get(id=db_id)
        db_obj.delete()
