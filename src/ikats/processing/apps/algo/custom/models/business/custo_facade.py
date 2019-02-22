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
from apps.algo.custom.models.orm.algo import CustomizedAlgoDao
from ikats.core.library.exception import IkatsInputError, IkatsNotFoundError
from apps.algo.catalogue.models.orm.implem import ImplementationDao
from apps.algo.custom.models.business.check_engine import CheckEngine


class CustomFacade(object):
    """
    Main business services of custom application are grouped in this facade, as class
    methods.
    """

    def __init__(self):
        """
        Constructor
        """
        pass

    @classmethod
    def check_edited_params(cls, business_algo, checked_value_context):
        """
        Apply the consistency checks on the business_algo
        :param cls:
        :type cls:
        :param business_algo: the customized algo
        :type business_algo: CustomizedAlgo
        :param checked_value_context: additional information about the processing context of the check:
        passed to the CheckEngine constructor.
        :return: the checkStatus completed with these checks
        :rtype: checkStatus
        """
        engine = CheckEngine(business_algo, checked_value_context)
        return engine.check_customized_values()

    @classmethod
    def create_custom_algo(cls, business_custo_algo):
        """
        Check and then create the resource in database
        :param cls:
        :type cls:
        :param business_custo_algo: the custom algorithm which is created, unless there are errors in check_status
        :type business_custo_algo: CustomizedAlgo
        :return: tuple ( created_resource, check_status)
        :rtype: (CustomizedAlgo, CheckStatus) or (None, CheckStatus)
        """
        check_status = cls.check_edited_params(business_custo_algo, "Creation of CustomizedAlgo")

        if check_status.has_errors():
            return None, check_status
        else:
            created_algo = CustomizedAlgoDao.create(business_custo_algo)
            return created_algo, check_status

    @classmethod
    def get_custom_algo(cls, custom_id):
        """
        Get the resource with db_id=custom_id
        :param custom_id: the CustomizedAlgo db_id, defined when the search result
        :type custom_id: str.
        :return: the CustomizedAlgo retrieved from the database
        :rtype: CustomizedAlgo
        :raise CustomizedAlgo.DoesNotExist: unknown resource in database
        """

        if type(custom_id) is str:
            my_id = int(custom_id)
        elif type(custom_id) is not int:
            raise IkatsInputError("Unexpected format: int or parsable str expected for database id")
        else:
            my_id = custom_id

        return CustomizedAlgoDao.find_business_elem_with_key(primary_key=my_id)

    @classmethod
    def search_with_criteria(cls, implem_id=None, name=None, label=None, desc_content=None):
        """
        Get the list of CustomizedAlgo matching the search specified by filtering criterion.
        Note: if no argument is defined: the complete list of CustomizedAlgo is returned.

        :param implem_id: optional default None: the Implementation db_id, defined when the search result
         is a list of CustomizedAlgo addressing such specific Implementation id. The argument implem_id.
        :type implem_id: str, None
        :param name: optional default None: criterion specifying searched name of the CustomizedAlgo
        :type name: str, None
        :param label: optional default None: criterion specifying searched label of the CustomizedAlgo
        :type label: str, None
        :param desc_content: optional default None: criterion specifying searched substring within the description
        of the CustomizedAlgo
        :type desc_content: str, None
        :return: the search result as a list
        :rtype: list
        """
        my_query = CustomizedAlgoDao.objects.all()
        if implem_id is not None:
            my_implem_id = ImplementationDao.parse_dao_id(implem_id)

            my_query = my_query.filter(ref_implementation__id=my_implem_id)

        if name is not None:
            my_query = my_query.filter(name=name)

        if label is not None:
            my_query = my_query.filter(label=label)

        if desc_content is not None:
            my_query = my_query.filter(desc__contains=desc_content)

        result = []
        for dao_resource in my_query:
            business_resource = dao_resource.build_business()
            result.append(business_resource)
        return result

    @classmethod
    def update_custom_algo(cls, business_custo_algo):
        """
        Check and then update in database the resource
        :param cls:
        :type cls:
        :param business_custo_algo: the custom algorithm which is updated, unless there are errors in check_status
        :type business_custo_algo: CustomizedAlgo
        :return: tuple ( created_resource, check_status)
        :rtype: (CustomizedAlgo, CheckStatus) or (None, CheckStatus)
        """
        check_status = cls.check_edited_params(business_custo_algo, "Update of CustomizedAlgo")

        if check_status.has_errors():
            return None, check_status
        else:
            updated_algo = CustomizedAlgoDao.update(business_custo_algo)
            return updated_algo, check_status

    @classmethod
    def delete_custom_algo(cls, cust_id):
        """
        Deletes the specified CustomizedAlgo from database
        :param cls:
        :type cls:
        :param cust_id: ID specifying the CustomizedAlgo
        :type cust_id:
        :raise IkatsNotFoundException: resource does not exist
        """

        try:
            my_id = CustomizedAlgoDao.parse_dao_id(cust_id)
            CustomizedAlgoDao.delete_resource_with_id(my_id)
        except CustomizedAlgoDao.DoesNotExist:
            raise IkatsNotFoundError("Delete canceled: no CustomizedAlgo with id={}".format(cust_id))
