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
    Pierre BONHOURE <pierre.bonhoure@c-s.fr>
"""

import json

from django.db import models

from apps.algo.catalogue.models.orm.element import ElementDao
from apps.algo.catalogue.models.orm.implem import ImplementationDao
from apps.algo.catalogue.models.orm.profile import ProfileItemDao
from apps.algo.custom.models.business.algo import CustomizedAlgo
from apps.algo.custom.models.business.params import CustomizedParameter
from ikats.core.library.exception import IkatsException


class CustomizedAlgoDao(ElementDao):
    """
    CustomizedAlgoDao from the ORM layer:
     * one instance of CustomizedAlgoDao is mapping the custom database content:
       it associates edited values to an ImplementationDao from catalogue database.
     * several CustomizedAlgoDao may be defined on the same ImplementationDao in the catalogue
     * one instance of CustomizedAlgoDao is associated to its equivalent business resource CustomizedAlgo

    CustomizedAlgoDao provides the CRUD operations on business resource CustomizedAlgo: see available class methods
    in CustomizedAlgoDao or superclass ElementDao

     ORM Properties:
     * one instance of CustomizedAlgoDao inherits properties of ElementDao, as its self describing fields
      * desc,
      * label,
      * name,
      * id

    ORM Relationships:
     * *CustomizedAlgoDao* object is linked to its *ImplementationDao* object
      * by **ref_implementation** ForeignKey relationship,
      * and its reverse relationship **custom_algo_set**, available on ImplementationDao object.
     * *CustomizedAlgoDao* object is linked to its set of *CustomizedParameterDao*
      * by ForeinKey relationship **custom_algo** on CustomizedParameterDao,
      * and its reverse relationship **custom_parameters_set** available on CustomizedAlgoDao object.

    CRUD operations:
     * available from ElementDao:
      * find_business_elem_with_key
      * find_business_elem_with_name
      * find_business_from_element_def
     * defined from this class:
      * create
      * update
      * delete_resource
      * delete_resource_with_id
      * find_from_implementation_id
    """
    ERROR_CREATE_PREFIX = "Error: Create CustomizedAlgo:"
    ERROR_UPDATE_PREFIX = "Error: Update CustomizedAlgo:"
    ERROR_DELETE_PREFIX = "Error: Delete CustomizedAlgo:"
    ERROR_READ_PREFIX = "Error: Read CustomizedAlgo:"

    name = models.CharField(max_length=60, null=False, blank=False, help_text='readable name')

    ref_implementation = models.ForeignKey(ImplementationDao, null=False, related_name="custom_algo_set")

    # reverse relationship defined in CustomizedParameterDao:
    #   custom_parameters_set defined on instance of CustomizedAlgoDao

    def build_business(self):
        """
        Build the business formatted CustomizedAlgo based on the current ORM data.

        .. WARNING:: The build does not include the attached CustomizedParameters

        :return: the business instance CustomizedAlgo mapping self instance
        :rtype: CustomizedAlgo
        """
        bus_implem = self.ref_implementation.build_business()

        business_obj = CustomizedAlgo(arg_implementation=bus_implem,
                                      custom_params=None,
                                      name=self.name,
                                      label=self.label,
                                      db_id=self.id,
                                      description=self.desc)

        for orm_custom_param in self.custom_parameters_set.all():
            buzz_custom_param = orm_custom_param.build_business()
            business_obj.add_custom_param(buzz_custom_param)

        return business_obj

    def __create_linked_custom_params(self, specified_business_custo_algo, returned_business_obj, save_now=True):
        """
        Evaluates and creates the list of CustomizedParameters specified by specified_business_custo_algo:
         - create in DB each new CustomizedParameterDao, attached to self instance of CustomizedAlgoDao
         - computes each CustomizedParameter from created CustomizedParametersDao
         - append each CustomizedParameter to returned_business_obj
         - return returned_business_obj
        :param specified_business_custo_algo: the customized algo specifying the list of CustomizedParameter
        :type specified_business_custo_algo: CustomizedAlgo
        :param returned_business_obj: updated business object equivalent to specified_business_custo_algo,
                but with created db_id
        :type returned_business_obj: CustomizedAlgo
        :param save_now: optional, default True: flag activating the save on each CustomizedParameterDao.
        :type save_now: boolean
        """
        my_implem = specified_business_custo_algo.implementation
        for buz_edited_value in specified_business_custo_algo.custom_params.values():
            # 1: retrieve referenced ProfileItemDao
            #  it is cool to look up the existence of named parameter under the implementation definition
            my_profile_item = my_implem.find_by_name_input_item(buz_edited_value.parameter.name)
            ref_id_profile_item = ProfileItemDao.parse_dao_id(my_profile_item.db_id)
            try:
                db_profile_item = ProfileItemDao.objects.get(id=ref_id_profile_item)
            except ProfileItemDao.DoesNotExist:
                my_mess = "Error in CustomizedAlgoDao: unresolved param definition: " + \
                          "no ProfileItemDao with id={}. See {}"
                raise IkatsException(my_mess.format(ref_id_profile_item, specified_business_custo_algo))

            db_cust_param = CustomizedParameterDao()
            # 2: init
            # foreign keys => assign retrieved DAO models
            db_cust_param.ref_profile_item = db_profile_item
            db_cust_param.custom_algo = self
            # value + is_aliased
            #
            # encoding the DB value:
            #    the business value => DB value is the json encoded value
            db_cust_param.edited_value = json.dumps(buz_edited_value.value)
            db_cust_param.is_aliased = False
            if save_now:
                db_cust_param.save()
            business_custo_param = db_cust_param.build_business()
            returned_business_obj.add_custom_param(business_custo_param)

        return returned_business_obj

    @classmethod
    def init_orm(cls, business_custom_algo, save=False):
        """
        Build the ORM object based on corresponding business class
        It will return the ORM object filled with business information
        :param cls:
        :type cls:
        :param business_custom_algo: business object containing information
        :type business_custom_algo:  CustomizedAlgo
        :param save:True if it is required to save object
        :type save: bool
        :return: the ORM object (instance of CustomizedAlgoDao)
        """

        #  Step1: creates/updates inherited attributes from ElementDao:
        #   - name
        #   - label
        #   - desc
        #   - db
        if not business_custom_algo.is_db_id_defined():
            db_obj = CustomizedAlgoDao.init_elem_orm(business_custom_algo, save=False)
        else:
            db_obj = CustomizedAlgoDao.objects.get(id=business_custom_algo.db_id)
            if db_obj is None:
                msg = "Undefined in database: {2} with id={0} name={1}"
                raise IkatsException(msg.format(business_custom_algo.db_id,
                                                business_custom_algo.name,
                                                cls.__name__))
            db_obj.name = business_custom_algo.name
            db_obj.desc = business_custom_algo.description
            db_obj.label = business_custom_algo.label

        # Step2: creates/updates:
        # - ref_implementation
        implem_id = business_custom_algo.implementation.db_id

        impl = ImplementationDao.objects.get(id=implem_id)

        if impl is None:
            my_mess = "Error in CustomizedAlgoDao: did not find ImplementationDao with id={}. See {}"
            raise IkatsException(my_mess.format(implem_id, business_custom_algo))

        db_obj.ref_implementation = impl

        # If required: save CustomizedAlgo before updating the linked CustomizedParameter list
        if save:
            db_obj.save()

        # init of CustomizedParameter list is done elsewhere
        return db_obj

    @classmethod
    def create(cls, business_custo_algo):
        """
        CREATE resource in database.
        :param cls: class parameter.
        :type cls: CustomizedAlgoDao
        :param business_custo_algo: business resource needing to be created in custom database
        :type business_custo_algo: CustomizedAlgo
        :return: business resource wrapping the created record in custom database: database ids are filled.
        :rtype: CustomizedAlgo
        :raise IkatsException: inconsistency error, or resource already created
        """

        if not isinstance(business_custo_algo, CustomizedAlgo):
            my_mess = "{}: expects arg type CustomizedAlgo: unexpected type={}"
            raise IkatsException(msg=my_mess.format(cls.ERROR_CREATE_PREFIX,
                                                    type(business_custo_algo).__name__))

        if business_custo_algo.is_db_id_defined():
            my_mess = "{} unexpected: db_id already defined for {}".format(cls.ERROR_CREATE_PREFIX,
                                                                           business_custo_algo)
            raise IkatsException(msg=my_mess)

        if len(business_custo_algo.custom_params) == 0:
            my_mess = "{} unexpected and useless: no customized value defined for {}".format(cls.ERROR_CREATE_PREFIX,
                                                                                             business_custo_algo)
            raise IkatsException(msg=my_mess)

        if ((not business_custo_algo.implementation) or
                (not business_custo_algo.implementation.is_db_id_defined())):
            my_mess = "{} self.implementation must be defined in DB: undefined implementation: {}"
            raise IkatsException(msg=my_mess.format(cls.ERROR_CREATE_PREFIX,
                                                    business_custo_algo))

        # init and save now
        orm_obj = CustomizedAlgoDao.init_orm(business_custo_algo, save=True)

        # returned_business_obj will be completed with associated CustomizedParameter
        returned_business_obj = orm_obj.build_business()

        returned_business_obj = orm_obj.__create_linked_custom_params(specified_business_custo_algo=business_custo_algo,
                                                                      returned_business_obj=returned_business_obj,
                                                                      save_now=True)

        return returned_business_obj

    @classmethod
    def update(cls, business_custo_algo):
        """
        UPDATE operation on the resource CustomizedAlgo
        :param cls: class parameter.
        :type cls: CustomizedAlgoDao
        :param business_obj: business resource needing to be created in custom database
        :type business_obj: CustomizedAlgo
        :return: business resource wrapping the created record in custom database: database ids are filled.
        :rtype: CustomizedAlgo
        """

        if not isinstance(business_custo_algo, CustomizedAlgo):
            my_mess = "{}: expects arg type CustomizedAlgo: unexpected type={}"
            raise IkatsException(msg=my_mess.format(cls.ERROR_UPDATE_PREFIX,
                                                    type(business_custo_algo).__name__))

        if not business_custo_algo.is_db_id_defined():
            my_mess = "{} unexpected: undefined db_id for {}".format(cls.ERROR_UPDATE_PREFIX,
                                                                     business_custo_algo)
            raise IkatsException(msg=my_mess)

        if len(business_custo_algo.custom_params) == 0:
            my_mess = "{} unexpected and useless: no customized value defined for {}"
            raise IkatsException(msg=my_mess.format(cls.ERROR_UPDATE_PREFIX,
                                                    business_custo_algo))

        if ((not business_custo_algo.implementation) or
                (not business_custo_algo.implementation.is_db_id_defined())):
            my_mess = "{} self.implementation must be defined in DB: undefined implementation: {}"
            raise IkatsException(msg=my_mess.format(cls.ERROR_UPDATE_PREFIX,
                                                    business_custo_algo))

        # init and save now
        orm_obj = CustomizedAlgoDao.init_orm(business_custo_algo, save=True)

        # returned_business_obj will be completed with associated CustomizedParameter
        returned_business_obj = orm_obj.build_business()
        returned_business_obj.clear_custom_params()

        # updating strategy for associated list of CustomizedParameter:
        #  1: delete all CustomizedParameter from DB
        #  2: add all CustomizedParameter from business_custo_algo

        # 1: delete all CustomizedParameter from DB
        #   read each obsolete CustomizedParameter
        #   using reverse relationship defined by CustomizedParameterDao::custom_algo
        for old_db_edited_value in CustomizedParameterDao.objects.filter(custom_algo__id=orm_obj.id):
            old_db_edited_value.delete()

        for param in business_custo_algo.custom_params.values():
            # remove obsolete db id : all previous children have been deleted
            param.db_id = None

        # 2: add all CustomizedParameter from business_custo_algo
        # cls.create_edited_params( business_custo_algo, orm_obj, save_now)
        returned_business_obj = orm_obj.__create_linked_custom_params(specified_business_custo_algo=business_custo_algo,
                                                                      returned_business_obj=returned_business_obj,
                                                                      save_now=True)

        return returned_business_obj

    @classmethod
    def delete_resource(cls, business_obj):
        """
        DELETE operation on the business resource CustomizedAlgo and its related
        CustomizedParameter resources from Django database.

        Note: catalogue db resources ImplementationDao and ProfileDao are never
        deleted by the DELETE on CustomizedAlgo.

        Note: this method calls the default models.Model.delete() method on instance CustomizedAlgoDao,
        thus this class method name is delete_resource in order to avoid an unwanted extension of
        the models.Model.delete()
        :param cls: class parameter.
        :type cls: CustomizedAlgoDao
        :param business_obj:
        :type business_obj: CustomizedAlgo with required db_id
        :return: report: message list that is logged on server and returned for Rest API
        :rtype: list of str
        """
        if business_obj.is_db_id_defined():
            orm_obj = CustomizedAlgoDao.objects.get(id=business_obj.db_id)

            if orm_obj is None:
                my_mess = "{} resource CustomizedAlgo not found in DB with id={}: delete cancelled on {}"
                raise IkatsException(my_mess.format(cls.ERROR_DELETE_PREFIX,
                                                    business_obj))

            # read each obsolete CustomizedParameter
            #   using reverse relationship defined by CustomizedParameterDao::custom_algo
            for cust_param in CustomizedParameterDao.objects.filter(custom_algo__id=orm_obj.id):
                cust_param.delete()

            orm_obj.delete()

        else:
            my_mess = "{} Undefined db_id: the delete is impossible and is cancelled for {}"
            raise IkatsException(my_mess.format(cls.ERROR_DELETE_PREFIX,
                                                business_obj))

    @classmethod
    def delete_resource_with_id(cls, db_id):
        """
        DELETE operation of the business resource CustomizedAlgo and its related CustomizedParameter
        resources from Django database:
          * this is the variant of delete_resource with database id value passed (i.e. the primary key)

        Note: catalogue db resources ImplementationDao and ProfileDao are never deleted by the DELETE on CustomizedAlgo.

        Note: this method calls the default models.Model.delete() method on instance CustomizedAlgoDao,
        thus this class method name is delete_resource_with_id in order to avoid an unwanted extension
             of the models.Model.delete()
        :param cls: class parameter.
        :type cls: CustomizedAlgoDao
        :param business_obj:
        :type business_obj: CustomizedAlgo with required db_id
        :return: the message list that would be logged on the server and would be returned for Rest API
        :rtype: list of str
        """
        my_business_obj = cls.find_business_elem_with_key(primary_key=db_id)
        if my_business_obj is not None:
            return cls.delete_resource(business_obj=my_business_obj)
        else:
            return ["DELETE cancelled on CustomizedAlgo: in delete_resource_with_id: unmatched id=" + db_id]

    @classmethod
    def find_from_implementation_id(cls, primary_key):
        """
        Finds the list of CustomizedAlgo resources, customizing the Implementation specified with primary key.

        :param cls: class parameter.
        :type cls: CustomizedAlgoDao
        :param primary_key: the db_id property of the Implementation resource
        :type primary_key: int
        :return: the list of business resources CustomizedAlgo customizing the specified Implementation
        :rtype: list of CustomizedAlgo
        """
        # See doc: https://docs.djangoproject.com/fr/1.8/topics/db/queries/#lookups-that-span-relationships
        orm_query_set = cls.objects.filter(ref_implementation__id=primary_key)
        res = []
        for orm_object_found in orm_query_set:
            res.append(orm_object_found.build_business())
        return res


class CustomizedParameterDao(models.Model):
    """
    CustomizedParameterDao from the ORM layer:
     * one instance of CustomizedParameterDao is definition part of one specific customized algorithm \
       CustomizedAlgoDao
     * one instance of CustomizedParameterDao is mapping the custom database content: \
       it defines the edited value of one parameter of an implementation from the catalogue database: \
       this parameter is mapped by one ProfileItemDao whose dtype is PARAM.
     * one instance of CustomizedParameterDao is associated to its equivalent business resource CustomizedParameter

    CustomizedParameterDao provides the CRUD operations on business resource CustomizedParameter

    ORM Relationships:
     * *CustomizedParameterDao* object is linked to the *ProfileItemDao*
      * by **ref_profile_item** ForeignKey relationship,
      * and its reverse relationship **custom_values_set**, available on *ProfileItemDao* object.
     * *CustomizedParameterDao* object is attached to its unique *CustomizedAlgoDao*
      * by ForeignKey relationship **custom_algo**,
      * and its reverse relationship **custom_parameters_set** available on CustomizedAlgoDao object.

    .. note:: CRUD operations are not available from CustomizedParameterDao: all is managed
              from resource CustomizedAlgoDao
    """
    # id: automatically added by Django
    id = models.AutoField(primary_key=True)

    custom_algo = models.ForeignKey(CustomizedAlgoDao, null=False, related_name="custom_parameters_set")

    ref_profile_item = models.ForeignKey(ProfileItemDao, null=False, related_name="custom_values_set")

    edited_value = models.TextField(help_text='edited value (text encoded)', null=False)

    # is_aliased will be used later, with story about the workflow shared context
    is_aliased = models.BooleanField(help_text="flag is aliased", null=False, default=False)

    def build_business(self):
        """
        Build the business resource CustomizedParameter from the django model CustomizedParameterDao

        Note: **self.custom_algo** is not saved under **CustomizedParameter**. See how foreign-key is saved in
         **CustomizedAlgoDao::__create_linked_custom_params**
        """
        my_catalogue_param = self.ref_profile_item.build_business()

        # From DB: str encoded JSON => loaded into python object
        my_parsed_value = json.loads(self.edited_value)
        my_customized_param = CustomizedParameter(cat_parameter=my_catalogue_param, value=my_parsed_value,
                                                  db_id=self.id)
        return my_customized_param
