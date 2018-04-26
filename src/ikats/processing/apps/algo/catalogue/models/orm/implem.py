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
import logging
from django.db import models as djmodels
from apps.algo.catalogue.models.business.implem import Implementation
from apps.algo.catalogue.models.orm.algorithm import AlgorithmDao
from apps.algo.catalogue.models.orm.element import ElementDao
from apps.algo.catalogue.models.orm.profile import ProfileItemDao

LOGGER = logging.getLogger(__name__)


class ImplementationDao(ElementDao):
    """
    ImplementationDao from the ORM layer: this piece of information from the catalogue defines
    one way to compute the referred algo.
    It provides all the configuration needed to submit an execution:
    library paths, kind of execution, the called function, the calling profile etc.
    """

    name = djmodels.CharField(max_length=60, null=False, blank=False, help_text='readable name', unique=True)
    execution_plugin = djmodels.CharField(help_text='the execution plugin', max_length=100, null=True)
    library_address = djmodels.CharField(help_text='the library address is a reference to the executable program',
                                         max_length=250, null=True)

    visibility = djmodels.BooleanField(help_text='visibility in ikats operators', default=True)
    algo = djmodels.ForeignKey(AlgorithmDao, null=True)

    input_desc_items = djmodels.ManyToManyField(to=ProfileItemDao, related_name='inputs')

    output_desc_items = djmodels.ManyToManyField(to=ProfileItemDao, related_name='outputs')

    def __str__(self):
        if self.algo:
            return "ImplementationDao [%s] of algorithm [%s]" % (
                ElementDao.__str__(self),
                self.algo.__str__())
        else:
            return "Orphan ImplementationDao [%s]" % (ElementDao.__str__(self))

    def __build_business_profile(self, db_profile_items):
        """
        Build a business profile list based on ORM profiles provided in arguments
        :param db_profile_items: list of profileItem
        :type db_profile_items: list, ManyToManyField
        :return: the business profile list
        """
        b_profile = []
        if db_profile_items:
            for item in db_profile_items.all():
                assert (isinstance(item, ProfileItemDao))
                b_profile_item = item.build_business()
                b_profile.append(b_profile_item)
        return b_profile

    def build_business(self):
        """
        Build the business formatted Implementation based on the current ORM data
        :return: the business instance Implementation mapping self instance
        """
        biz_inputs = self.__build_business_profile(self.input_desc_items)

        biz_outputs = self.__build_business_profile(self.output_desc_items)

        biz_algo = None
        if self.algo:
            biz_algo = self.algo.build_business()

        biz_impl = Implementation(name=self.name,
                                  description=self.desc,
                                  execution_plugin=self.execution_plugin,
                                  library_address=self.library_address,
                                  input_profile=biz_inputs,
                                  output_profile=biz_outputs,
                                  db_id=self.id,
                                  label=self.label,
                                  visibility=self.visibility)

        biz_impl.algo = biz_algo

        return biz_impl

    @classmethod
    def find_from_key(cls, primary_key):
        """
        Allow to retrieve an Implementation based on the primary key.
        :param primary_key: value of the key
        :return: the business object corresponding to the primary key
        """
        db_obj = ImplementationDao.objects.get(id=primary_key)
        if db_obj:
            return db_obj.build_business()
        else:
            return None

    @classmethod
    def find_from_definition(cls, name, execution_plugin, library_address):
        """
        This reading method finds implementations matching the same definition (name, execution_plugin, library_address)
        Note: should return list sized 0 or 1: case when length is greater than 1 is not nominal: a
        doubloon has been inserted in catalogue
        :param cls:
        :type cls:
        :param name:
        :type name:
        :param execution_plugin:
        :type execution_plugin:
        :param library_address:
        :type library_address:
        :return: list of found objects matching the same definition
        :rtype: list of business resources Implementation
        """
        res = []
        try:
            my_query_set = ImplementationDao.objects.filter(name=name)
            my_query_set2 = my_query_set.filter(execution_plugin=execution_plugin)
            my_query_set3 = my_query_set2.filter(library_address=library_address)

            for db_obj in my_query_set3:
                res.append(db_obj.build_business())
            return res

        except Exception as err:
            raise err

    @classmethod
    def create(cls, business_implementation):
        """
        CREATE resource in database.
        :param cls: class parameter.
        :type cls: ImplementationDao
        :param business_implementation: business resource created
        :type business_implementation: Implementation
        """
        assert (not business_implementation.is_db_id_defined())

        my_name = business_implementation.name
        my_exec_plugin = business_implementation.execution_plugin
        my_lib_address = business_implementation.library_address

        if ImplementationDao.find_from_definition(my_name, my_exec_plugin, my_lib_address):
            raise Exception(
                "ImplementationDao.create(...) aborted: definition (name, execution_plugin, library_address) "
                "already exists in database for %s" % str(business_implementation))

        db_obj = ImplementationDao()

        db_obj.name = my_name
        db_obj.label = business_implementation.label

        db_obj.desc = business_implementation.description

        db_obj.execution_plugin = my_exec_plugin
        db_obj.library_address = my_lib_address
        db_obj.visibility = business_implementation.visibility

        business_algo = business_implementation.algo

        if business_algo is not None:
            db_obj.algo = AlgorithmDao.get_sync_orm(business_algo)

        # save object BEFORE updating the many to many relationship !!!
        db_obj.save()

        for b_profile_item in business_implementation.input_profile:
            if b_profile_item.is_db_id_defined():
                # rare case: reused profile-item => read object from database
                profile_item = ProfileItemDao.objects.get(id=b_profile_item.db_id)
            else:
                profile_item = ProfileItemDao.init_orm(business_profile_item=b_profile_item,
                                                       save=True)
            # attach related ORMs for relation: input_desc_items
            db_obj.input_desc_items.add(profile_item)

        for b_profile_item in business_implementation.output_profile:
            if b_profile_item.is_db_id_defined():
                # rare case: reused profile-item => read object from database
                profile_item = ProfileItemDao.objects.get(id=b_profile_item.db_id)
            else:
                profile_item = ProfileItemDao.init_orm(business_profile_item=b_profile_item,
                                                       save=True)

            # attach related ORMs for relation: output_desc_items
            db_obj.output_desc_items.add(profile_item)

        # will save related ORMs: ProfileItemDao instances
        db_obj.save()

        # feed back to the business object: provide the created key
        return db_obj.build_business()

    @classmethod
    def update(cls, business_obj):
        """

        :param cls: class param
        :type cls: ImplementationDao
        :param business_obj: the business Implementation
        :type business_obj: Implementation
        """
        assert (business_obj.is_db_id_defined())

        db_obj = ImplementationDao()
        db_obj.id = business_obj.db_id
        # instead of ImplementationDao.objects.get(id=business_obj.db_id)
        # => simpler to start from lists of profile items !

        db_obj.name = business_obj.name
        db_obj.label = business_obj.label

        db_obj.desc = business_obj.description
        db_obj.execution_plugin = business_obj.execution_plugin
        db_obj.library_address = business_obj.library_address
        db_obj.visibility = business_obj.visibility

        business_algo = business_obj.algo
        if business_algo is not None:
            db_obj.algo = AlgorithmDao.get_sync_orm(business_algo)

        # save object BEFORE updating the many to many relationship !!!
        db_obj.save()

        db_obj.input_desc_items.clear()
        for b_profile_item in business_obj.input_profile:
            profile_item = ProfileItemDao.init_orm(business_profile_item=b_profile_item,
                                                   save=False)
            if b_profile_item.is_db_id_defined():
                # update existing profile item
                profile_item.id = b_profile_item.db_id
            # else: create and add profile item

            profile_item.save()

            # attach related ORMs for relation: input_desc_items
            db_obj.input_desc_items.add(profile_item)

        db_obj.output_desc_items.clear()
        for b_profile_item in business_obj.output_profile:
            profile_item = ProfileItemDao.init_orm(business_profile_item=b_profile_item,
                                                   save=False)
            if b_profile_item.is_db_id_defined():
                # update existing profile item
                profile_item.id = b_profile_item.db_id
            # else: create and add profile item

            profile_item.save()

            # attach related ORMs for relation: output_desc_items
            db_obj.output_desc_items.add(profile_item)

        # will save related ORMs: ProfileItemDao instances
        db_obj.save()

        # feed back to the business object: provide the created key(s)
        return db_obj.build_business()

    @classmethod
    def delete_resource(cls, business_obj):
        """
        Delete resource Implementation and associated ProfileItem list from Django database.

        Note: when there is a parent resource Algorithm of deleted Implementation:
        parent is not deleted by this operation, even if it has no more ImplementationDao child.

        Note: this method calls the default models.Model.delete() method on instance ImplementationDao,
        thus this class method name is delete_resource in order to avoid
        an unwanted extension of the models.Model.delete()

        :param business_obj:
        :type business_obj:
        :return: message list is logged on server and returned for Rest API
        :rtype: list of str
        """
        msg = []
        assert (isinstance(business_obj, Implementation))
        assert (business_obj.is_db_id_defined())
        db_obj = ImplementationDao.objects.get(id=business_obj.db_id)

        msg.append("Deleting Implementation with id={0}".format(db_obj.id))
        LOGGER.info(msg[-1])

        for db_input_item in db_obj.input_desc_items.all():
            db_obj.input_desc_items.remove(db_input_item)

            # note about db_input_item.inputs:
            #  db_input_item.inputs is resolved by django
            # - see ImplementationDao::input_desc_items def with arg related_name='inputs'
            #   => redefines the name of reverse association from ProfileItemDao to ImplementationDaoin
            #
            reverse_relation = db_input_item.inputs
            info_link = "input_desc_item"
            if reverse_relation.count() == 0:
                msg.append("Deleting {} target ProfileItemDao with id={}".format(info_link,
                                                                                 db_input_item.id))
                LOGGER.info(msg[-1])
                db_input_item.delete()
            else:
                msg.append("Not deleted: %s target ProfileItemDao with id=%s is linked" % (info_link,
                                                                                           db_input_item.id))
                LOGGER.warning(msg[-1])
                for other_db_impl in reverse_relation.all():
                    msg.append("- to another ImplementationDao with id={}".format(other_db_impl.id))
                    LOGGER.info("- with id=%s", other_db_impl.id)

        for db_output in db_obj.output_desc_items.all():
            db_obj.output_desc_items.remove(db_output)

            # note about db_output.outputs:
            #  db_output.outputs is resolved by django
            # - see ImplementationDao::input_desc_items def with arg related_name='outputs'
            #   => redefines the name of reverse association from ProfileItemDao to ImplementationDao
            #

            reverse_relation = db_output.outputs
            info_link = "output_desc_item"
            if reverse_relation.count() == 0:
                msg.append("Deleting {} target ProfileItemDao with id={}".format(info_link,
                                                                                 db_output.id))
                LOGGER.info(msg[-1])
                db_output.delete()
            else:
                msg.append("Not deleted: {} target ProfileItemDao with id={} is linked".format(info_link,
                                                                                               db_output.id))
                LOGGER.warning(msg[-1])
                for other_db_impl in reverse_relation.all():
                    msg.append("- to another ImplementationDao with id={}".format(other_db_impl.id, ))
                    LOGGER.info("- with id=%s", other_db_impl.id, )

        db_obj.delete()

        return msg
