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
import logging

from django.db import models as djmodels

from apps.algo.execute.models.business.algo import ExecutableAlgo

# For managed decimal numbers in seconds since EPOCH date: ex 1453974002.0023456
# - EPOCH_SECOND_DECIMAL_PLACES defines precision after comma: 7 for 1453974002.0023456
# Note : on centOs => manages up to 7 decimals
# this constant may change if we change precision
EPOCH_SECOND_DECIMAL_PLACES = 8
# - EPOCH_SECOND_INTEGER_DIGITS defines number of digits needed for int part: 10 here
#   this constant will not change for Ikats
EPOCH_SECOND_INTEGER_DIGITS = 10
# - EPOCH_SECOND_DECIMAL_DIGITS: total of digits needed
EPOCH_SECOND_DECIMAL_DIGITS = EPOCH_SECOND_INTEGER_DIGITS + EPOCH_SECOND_DECIMAL_PLACES

LOGGER = logging.getLogger(__name__)


class ExecutableAlgoDao(djmodels.Model):
    """
    ExecutableAlgoDao from the ORM layer: support database management of ExecutableAlgo resource
    It provides all the configuration needed to submit an execution:
    library paths, kind of execution, the called function, the calling profile etc.
    """

    creation_date = djmodels.DecimalField(help_text="Creation EPOCH date of exec algo: decimal in secs",
                                          null=False,
                                          max_digits=EPOCH_SECOND_DECIMAL_DIGITS,
                                          decimal_places=EPOCH_SECOND_DECIMAL_PLACES)

    start_execution_date = djmodels.DecimalField(
        help_text="Starting execution date: EPOCH date of exec algo: decimal in secs",
        null=True,
        max_digits=EPOCH_SECOND_DECIMAL_DIGITS,
        decimal_places=EPOCH_SECOND_DECIMAL_PLACES)

    end_execution_date = djmodels.DecimalField(
        help_text="Ending execution date: EPOCH date of exec algo: decimal in secs",
        null=True,
        max_digits=EPOCH_SECOND_DECIMAL_DIGITS,
        decimal_places=EPOCH_SECOND_DECIMAL_PLACES)

    state = djmodels.IntegerField(
        help_text="State: INIT, RUN, SUCCESS, ALGO_KO, ENGINE_KO, resp encoded by 0, 1, 2, 3, 4)",
        default=0)

    # implicit:
    #
    # id = <primary key> as int

    def __str__(self):
        msg = "ExecutableAlgoDao id=%s creation_date=%s start_date=%s end_date=%s state=%s"
        return msg % (self.id,
                      self.creation_date,
                      self.start_execution_date,
                      self.end_execution_date,
                      self.state)

    @classmethod
    def __merge_non_persistent(cls, original_obj, dest_obj):
        """
        A part of ExecutableAlgo is not managed by DAO in database:
        this method is copying the non-persistent content of original_obj into dest_obj
        :param cls:
        :type cls:
        :param original_obj:
        :type original_obj: ExecutableAlgo
        :param dest_obj:
        :type dest_obj: ExecutableAlgo
        :return: merged object : des_obj
        """
        assert (isinstance(original_obj, ExecutableAlgo))
        assert (isinstance(dest_obj, ExecutableAlgo))
        dest_obj.data_sources = original_obj.data_sources
        dest_obj.data_receivers = original_obj.data_receivers

        dest_obj.custom_algo = original_obj.custom_algo

        return dest_obj

    def build_business(self):
        """
        Build the business object based on this ORM data.
        :return: the business instance ExecutableAlgo mapping self instance
        :rtype: ExecutableAlgo
        """

        # story #140460 : at this time custom_algo is not persistent => pass None
        my_exec_algo = ExecutableAlgo(
            custom_algo=None, dict_data_sources=None, dict_data_receivers=None, arg_process_id=str(self.id))

        # reset the dates
        my_exec_algo.set_creation_date(self.creation_date)
        my_exec_algo.set_start_execution_date(self.start_execution_date)
        my_exec_algo.set_end_execution_date(self.end_execution_date)
        my_exec_algo.set_state(self.state)

        return my_exec_algo

    @classmethod
    def find_from_key(cls, primary_key):
        """
        Allow to retrieve an Implementation based on the primary key.
        :param cls:
        :type cls:
        :param primary_key: the primary key of ExecutableAlgo is its process_id value, converted to integer
        :type primary_key: str or int are accepted: internal key is typed int, but str is converted when needed.
        :return: the business object corresponding to the primary key
        :rtype: ExecutableAlgo
        """
        my_primary_key = None
        if type(primary_key) is str:
            my_primary_key = int(primary_key)
        elif type(primary_key) is int:
            my_primary_key = primary_key
        else:
            raise TypeError("ExecutableAlgoDao::find_from_key got unexpected type for primary_key=%s" % primary_key)

        try:
            db_obj = ExecutableAlgoDao.objects.get(pk=primary_key)
            buz_obj = db_obj.build_business()
        except ExecutableAlgoDao.DoesNotExist:
            buz_obj = None

        return buz_obj

    @classmethod
    def create(cls, original_business_obj, merge_with_unsaved_data=True):
        """
        CREATE resource in database.
        :param cls: class parameter.
        :type cls: ExecutableAlgoDao
        :param original_business_obj: business resource to create in DB
        :type original_business_obj: ExecutableAlgo
        :param merge_with_unsaved_data:
            - False : returned object reflects only the information created in database
            - True: returned object merges
                - information created in database
                - information not persisted in database, defined in original_business_obj
        :type merge_with_unsaved_data: boolean
        :return: created business object, with optional non persistent data when merge_with_unsaved_data is True
        """
        assert (isinstance(original_business_obj, ExecutableAlgo))

        # is_db_id_defined <=> "is process_id defined ?"
        assert (not original_business_obj.is_db_id_defined())

        db_obj = ExecutableAlgoDao()
        db_obj.creation_date = original_business_obj.get_creation_date()
        db_obj.start_execution_date = original_business_obj.start_execution_date
        db_obj.end_execution_date = original_business_obj.end_execution_date
        db_obj.state = original_business_obj.state

        # Save object BEFORE updating the many to many relationship !!!
        db_obj.save()

        LOGGER.debug("created %s", db_obj.__str__())

        # Feed back to the business object: provide the created key

        output_business_obj = db_obj.build_business()
        if merge_with_unsaved_data:
            cls.__merge_non_persistent(original_business_obj, output_business_obj)

        LOGGER.debug("created business: %s", output_business_obj.as_detailed_string())

        return output_business_obj

    @classmethod
    def update(cls, business_obj, merge_with_unsaved_data=True):
        """

        :param merge_with_unsaved_data:
        :param cls: class param
        :type cls: ExecutableAlgoDao
        :param business_obj: the business object ExecutableAlgo
        :type business_obj: ExecutableAlgo
        """
        assert (business_obj.is_db_id_defined())

        db_obj = ExecutableAlgoDao()
        db_obj.id = business_obj.process_id
        db_obj.creation_date = business_obj.creation_date
        db_obj.start_execution_date = business_obj.start_execution_date
        db_obj.end_execution_date = business_obj.end_execution_date
        db_obj.state = business_obj.state

        # Save object BEFORE updating the many to many relationship !!!
        db_obj.save()

        LOGGER.debug("updated %s", db_obj.__str__())

        # Feed back to the business object
        output_business_obj = db_obj.build_business()
        if merge_with_unsaved_data:
            cls.__merge_non_persistent(business_obj, output_business_obj)

        LOGGER.debug("updated business: %s", output_business_obj.as_detailed_string())

        return output_business_obj
