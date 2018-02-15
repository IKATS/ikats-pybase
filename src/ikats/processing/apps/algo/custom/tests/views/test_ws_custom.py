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

from django.core.urlresolvers import reverse
from django.http.request import HttpRequest
from django.test import TestCase, RequestFactory, Client

from apps.algo.catalogue.models.business.factory import FactoryCatalogue
from apps.algo.custom.models.business.algo import CustomizedAlgo
from apps.algo.custom.models.business.check_engine import CheckEngine
from apps.algo.custom.models.business.params import CustomizedParameter
from apps.algo.custom.models.orm.algo import CustomizedAlgoDao
from apps.algo.custom.models.ws.algo import CustomizedAlgoWs
from apps.algo.custom.tests.tu_commons import CommonsCustomTest
from apps.algo.custom.views.ws_custom import create_custom_algo, update_custom_algo, delete_custom_algo, get_custom_algo

from ikats_processing.core.http import HttpResponseFactory, HttpCommonsIkats
from ikats_processing.core.json import decode as json_io


class TestCustomRestAPI(TestCase, CommonsCustomTest):
    """
    TU on End-User Rest API from module
    """

    @classmethod
    def setUpTestData(cls):
        """
        Sets up the TU class: prepare the DB
        :param cls:
        :type cls:
        """

        cls.init_tu()
        cls.request_factory = RequestFactory()
        cls.prepare_custom_database()

    @classmethod
    def tearDownClass(cls):
        """
        Tears down the TU class: writes the tu diagnostic
        :param cls:
        :type cls:
        """
        cls.commons_tear_down_class()

        super(TestCustomRestAPI, cls).tearDownClass()
        # It is important to call superclass

    def init_resource_with_bad_type(self):
        """
        Initializer of CustomizedAlgo with a CustomizedParameter raising a bad type checking error
        """
        my_custom_algo_bad_type = CustomizedAlgo(arg_implementation=self.my_pseudo_impl_from_db,
                                                 custom_params=None,
                                                 name="CustoW generating check errors by TU",
                                                 label="CustoW",
                                                 db_id=None,
                                                 description="CustoW description")
        my_custo_param_factor_bad_type = CustomizedParameter(cat_parameter=self.my_param_factor,
                                                             value=0.885)
        my_custom_algo_bad_type.add_custom_param(my_custo_param_factor_bad_type)

        # Type incorrect: parsed value from json is not a number: "0.33" is a str
        my_custom_algo_bad_type.add_custom_value(param_name=self.my_param_phase.name,
                                                 value="0.33")

        return my_custom_algo_bad_type

    def test_custo_read_200(self):
        """
        Tests the nominal reading of resource initialized in test DB: self.my_custom_algo_in_DB
        """

        my_id = self.my_custom_algo_in_DB.db_id

        http_response = get_custom_algo(http_request=HttpRequest(), customized_algo_id=my_id, query_dict=None)

        self.assertTrue(http_response.status_code == HttpResponseFactory.OK_HTTP_STATUS)

        # Check result content: ... self.my_custom_algo_in_DB == biz_result
        dict_result = json_io.decode_json_from_http_response(http_response)

        ws_result = CustomizedAlgoWs.load_from_dict(dict_result)

        biz_result = ws_result.get_customized_algo()

        self.assertTrue(self.my_custom_algo_in_DB == biz_result)

    def test_custo_read_404(self):
        """
        Tests the NOT_FOUND case of the reading of resource: ID=9999999
        """

        http_response = get_custom_algo(http_request=HttpRequest(), customized_algo_id=9999999, query_dict=None)

        self.assertTrue(http_response.status_code == HttpResponseFactory.NOT_FOUND_HTTP_STATUS)

    def test_custo_read_400(self):
        """
        Tests the bad request case, reading one CustomizedAlgo resource
          - returned status is 400 when a query param has unexpected value:
        """

        client = Client()
        my_id = self.my_custom_algo_2_in_DB.db_id
        http_response = client.get('/ikats/algo/custom/custom_algos/{}?info_level=4'.format(my_id))

        result = json_io.decode_json_from_http_response(http_response)
        self.info("test_read_custom_collection_nominal result={}".format(result))

        self.assertEqual(HttpResponseFactory.BAD_REQUEST_HTTP_STATUS, http_response.status_code)

    def test_custo_405(self):
        """
        Tests the method not allowed case, reading a customized algo resource
            - returned code is 405
        In that case, the tested method is POST
        """

        client = Client()
        my_id = self.my_custom_algo_2_in_DB.db_id
        http_response = client.post('/ikats/algo/custom/custom_algos/{}'.format(my_id))
        self.assertTrue(http_response.status_code == HttpResponseFactory.NOT_ALLOWED_METHOD_HTTP_STATUS)

    def test_custo_create_200(self):
        """
        Tests the nominal Creation of CustomizedAlgo: we prepare the data and then submit creation
        """

        # Preparing the data ...
        my_new_custom_algo = self.init_resource_named(name="custom algo for create seq3", save_in_db=False)

        data = CustomizedAlgoWs(my_new_custom_algo).to_json()

        # ... testing the service
        http_req = self.request_factory.post(path=reverse('pattern_custom_algos_dummy'),
                                             data=data,
                                             content_type="application/json_util")

        http_response = create_custom_algo(http_req)

        result = json_io.decode_json_from_http_response(http_response)

        self.info("!!! response loaded={} !!!".format(result))
        self.info("!!! response status={} !!!".format(http_response.status_code))

        self.assertTrue(http_response.status_code == HttpResponseFactory.CREATED_HTTP_STATUS)

    def test_custo_create_409(self):
        """
        Tests the Creation failure case: CONFLICT_HTTP_STATUS
        """

        http_req = self.request_factory.post(path=reverse('pattern_custom_algos_dummy'),
                                             data=CustomizedAlgoWs(self.my_custom_algo_in_DB).to_json(),
                                             content_type="application/json_util")

        http_response = create_custom_algo(http_req)

        self.assertTrue(http_response.status_code == HttpResponseFactory.CONFLICT_HTTP_STATUS)

    def test_custo_create_400(self):
        """
        Tests the Creation failure case: BAD_REQUEST_HTTP_STATUS
        """

        http_req = self.request_factory.post(path=reverse('pattern_custom_algos_dummy'),
                                             data="bad content",
                                             content_type="application/json_util")

        http_response_2 = create_custom_algo(http_req)

        self.assertTrue(http_response_2.status_code == HttpResponseFactory.BAD_REQUEST_HTTP_STATUS)

    def test_custo_update_200(self):
        """
        Tests the nominal Update of CustomizedAlgo
        """

        my_modif = self.my_custom_algo_in_DB

        my_modif.label = "Modified label"

        http_req = self.request_factory.put(path=reverse(viewname='pattern_custom_algos_with_id',
                                                         args=[my_modif.db_id]),
                                            data=CustomizedAlgoWs(my_modif).to_json(),
                                            content_type="application/json_util")

        http_response = update_custom_algo(http_req,
                                           customized_algo_id=my_modif.db_id)

        self.assertTrue(http_response.status_code == HttpResponseFactory.OK_HTTP_STATUS)

    def test_custo_update_400(self):
        """
        Tests the CustomizedAlgo Update failure case with BAD_REQUEST_HTTP_STATUS:
          - case when the CustomizedAlgo ID is unknown by database
        """

        # TEST: bad id in the URL => input error
        my_modif = self.my_custom_algo_in_DB

        http_req = self.request_factory.put(path=reverse(viewname='pattern_custom_algos_with_id',
                                                         args=["9999999"]),
                                            data=CustomizedAlgoWs(my_modif).to_json(),
                                            content_type="application/json_util")

        http_response = update_custom_algo(http_request=http_req, customized_algo_id="9999999")

        self.assertTrue(http_response.status_code == HttpResponseFactory.BAD_REQUEST_HTTP_STATUS)

    def test_custo_update_404(self):
        """
        Tests the not found case, updating a CustomizedAlgo resource
          - returned status is 404
        """

        my_ws_modif = CustomizedAlgoWs(self.my_custom_algo_in_DB).to_dict()
        unknown = 99999
        my_ws_modif['id'] = unknown
        my_json_data = json.dumps(obj=my_ws_modif)

        client = Client()
        http_response_bis = client.put('/ikats/algo/custom/custom_algos/{}'.format(unknown),
                                       data=my_json_data)

        self.assertTrue(http_response_bis.status_code == HttpResponseFactory.NOT_FOUND_HTTP_STATUS)

    def test_custo_delete_204(self):
        """
        Tests the CustomizedAlgo Deletion nominal case
        """

        # Preparing data ...
        my_custom_algo_3 = CustomizedAlgo(arg_implementation=self.my_pseudo_impl_from_db,
                                          custom_params=None,
                                          name="CustoW to be deleted by TU",
                                          label="CustoW",
                                          db_id=None,
                                          description="CustoW description")

        my_custo_param_factor_3 = CustomizedParameter(cat_parameter=self.my_param_factor,
                                                      value="0.885")
        my_custom_algo_3.add_custom_param(my_custo_param_factor_3)

        my_custom_algo_3.add_custom_value(param_name=self.my_param_phase.name,
                                          value="0.33")

        buzz_to_be_deleted = CustomizedAlgoDao.create(my_custom_algo_3)
        # ... prepared data

        # Testing deletion on prepared data

        my_id = buzz_to_be_deleted.db_id

        http_req = self.request_factory.delete(path=reverse(viewname='pattern_custom_algos_with_id',
                                                            args=[my_id]),
                                               content_type="application/json_util")

        nb_before = CustomizedAlgoDao.objects.count()

        http_response = delete_custom_algo(http_req, my_id)

        nb_after = CustomizedAlgoDao.objects.count()

        self.assertTrue(http_response.status_code == HttpResponseFactory.NO_CONTENT_HTTP_STATUS)
        self.assertTrue((nb_before - nb_after) == 1)

        with self.assertRaises(CustomizedAlgoDao.DoesNotExist):
            my_key = CustomizedAlgoDao.parse_dao_id(my_id)
            CustomizedAlgoDao.find_business_elem_with_key(primary_key=my_key)

    def test_custo_delete_404(self):
        """
        Tests the CustomizedAlgo Deletion failure case: NOT_FOUND_HTTP_STATUS
        """

        http_req = self.request_factory.delete(
            path=reverse(viewname='pattern_custom_algos_with_id', args=['9999999']),
            content_type="application/json_util")

        http_response = delete_custom_algo(http_req, '9999999')

        self.assertTrue(http_response.status_code == HttpResponseFactory.NOT_FOUND_HTTP_STATUS)

        ref_content = {'internal_error': 'Delete canceled: no CustomizedAlgo with id=9999999',
                       'http_msg': 'DELETE failed on CustomizedAlgo with id=9999999: resource not found'}

        obj_content = HttpCommonsIkats.load_json_from_response(http_response)

        self.assertDictEqual(ref_content, obj_content, "")

        self.info(http_response.content)

    def test_read_custom_collec_200(self):
        """
        Tests the CustomizedAlgo collection reading Rest service: basic case without filtering criterion
        """

        client = Client()
        http_response = client.get('/ikats/algo/custom/custom_algos/')

        result = json_io.decode_json_from_http_response(http_response)
        self.info("test_read_custom_collection_nominal result={}".format(result))

        self.assertTrue(http_response.status_code == HttpResponseFactory.OK_HTTP_STATUS)
        self.assertTrue(len(result) == CustomizedAlgoDao.objects.count())

    def test_read_custom_collec_404(self):
        """
        Tests the resource not found case, reading a collection of  CustomizedAlgo
          - returned status is 404
        """

        client = Client()
        http_response = client.get('/ikats/algo/custom/custom_algos/?desc="nosuchexpression"')

        result = json_io.decode_json_from_http_response(http_response)
        self.info("test_read_custom_collection_nominal result={}".format(result))

        self.assertEqual(http_response.status_code, HttpResponseFactory.NOT_FOUND_HTTP_STATUS,
                         "code != 404 (not found)")

    def test_read_custom_collec_400(self):
        """
        Tests the bad request case, reading a collection of  CustomizedAlgo
          - returned status is 400

        One tested case: with query parameter info_level=5
        """

        client = Client()
        http_response = client.get('/ikats/algo/custom/custom_algos/?info_level=5')

        result = json_io.decode_json_from_http_response(http_response)

        self.assertEqual(http_response.status_code, HttpResponseFactory.BAD_REQUEST_HTTP_STATUS,
                         "code != 400 (bad request)")

    def test_custom_collection_405(self):
        """
        Tests not allowed methods cases, dealing with the CustomizedAlgo collections
          - PUT custom_algos -> 405
          - DELETE custom_algos -> 405
        """

        client = Client()
        http_response = client.put('/ikats/algo/custom/custom_algos/')
        self.assertTrue(http_response.status_code == HttpResponseFactory.NOT_ALLOWED_METHOD_HTTP_STATUS)

        client = Client()
        http_response = client.delete('/ikats/algo/custom/custom_algos/')
        self.assertTrue(http_response.status_code == HttpResponseFactory.NOT_ALLOWED_METHOD_HTTP_STATUS)

    def test_find_custom_of_implem_200(self):
        """
        Tests the finding of CustomizedAlgo instances having a specified parent Implementation
        """

        id_implem = self.my_pseudo_impl_from_db.db_id

        client = Client()
        http_response = client.get('/ikats/algo/implementations/{}/custom_algos'.format(id_implem))

        self.assertTrue(http_response.status_code == HttpResponseFactory.OK_HTTP_STATUS)

        result = json_io.decode_json_from_http_response(http_response)
        self.assertTrue(len(result) == 3)
        self.info("test_find_custom_of_implem_nominal result={}".format(json.dumps(result, indent=2)))

    def test_find_custom_of_implem_400(self):
        """
        Tests the bad request, finding the CustomizedAlgo collection child of an implementation
          - returned status is 400 when the query param 'level' is incorrect
        """

        client = Client()
        m_id = self.my_pseudo_impl_from_db.db_id
        http_response = client.get('/ikats/algo/implementations/{}/custom_algos/?info_level=5'.format(m_id))

        json_io.decode_json_from_http_response(http_response)

        self.assertEqual(http_response.status_code, HttpResponseFactory.BAD_REQUEST_HTTP_STATUS,
                         "code != 400 (bad request)")

    def test_find_custom_of_implem_404(self):
        """
        Tests the not found case, finding the CustomizedAlgo collection child of an implementation
          - returned status is 404 : test case when the implementation is not found
        """

        client = Client()
        m_id = 99999
        http_response = client.get('/ikats/algo/implementations/{}/custom_algos'.format(m_id))

        json_io.decode_json_from_http_response(http_response)

        self.assertEqual(http_response.status_code, HttpResponseFactory.NOT_FOUND_HTTP_STATUS,
                         "code != 400 (bad request)")

    def test_custom_of_implem_405(self):
        """
        Tests all of the "method not allowed" cases, dealing with
        the CustomizedAlgo collection child of an implementation
          - returned status is 405
        3 cases: POST, PUT or DELETE are not allowed.
        """

        # ID of existing implementation ...
        m_id = self.my_pseudo_impl_from_db.db_id

        client = Client()
        http_response_post = client.post('/ikats/algo/implementations/{}/custom_algos'.format(m_id))

        http_response_put = client.put('/ikats/algo/implementations/{}/custom_algos'.format(m_id))

        http_response_delete = client.delete('/ikats/algo/implementations/{}/custom_algos'.format(m_id))

        tested_codes = [http_response_post.status_code,
                        http_response_put.status_code,
                        http_response_delete.status_code]

        ref_codes = [HttpResponseFactory.NOT_ALLOWED_METHOD_HTTP_STATUS,
                     HttpResponseFactory.NOT_ALLOWED_METHOD_HTTP_STATUS,
                     HttpResponseFactory.NOT_ALLOWED_METHOD_HTTP_STATUS]

        msg = "{} != [405, 405, 405] (resp. for POST, PUT, DELETE)"
        self.assertListEqual(tested_codes, ref_codes, msg.format(tested_codes))

    def test_check_errors_create(self):
        """
        Tests that CheckEngine produces expected CheckStatus, when checking type error exists
        with the CustomizedAlgo creation Rest service.
        """

        client = Client()
        m_id = self.my_pseudo_impl_from_db.db_id
        http_response = client.get('/ikats/algo/implementations/{}/custom_algos/?info_level=5'.format(m_id))

        json_io.decode_json_from_http_response(http_response)

        self.assertEqual(http_response.status_code, HttpResponseFactory.BAD_REQUEST_HTTP_STATUS,
                         "code != 400 (bad request)")

    def test_check_err_create_bad_type(self):
        """
        Tests that CheckEngine produces expected CheckStatus, when checking type error exists
        with the CustomizedAlgo creation Rest service.
        """

        # Re-activate checking rules
        CheckEngine.set_checking_rules(FactoryCatalogue.TYPE_CHECKING_FUNCTIONS)

        my_custom_with_bad_type = self.init_resource_with_bad_type()

        http_req = self.request_factory.post(path=reverse('pattern_custom_algos_dummy'),
                                             data=CustomizedAlgoWs(my_custom_with_bad_type).to_json(),
                                             content_type="application/json_util")

        http_response = create_custom_algo(http_req)

        # Display the check result
        result = json_io.decode_json_from_http_response(http_response)

        self.info("response loaded={}".format(result))
        self.info("response status={}".format(http_response.status_code))

        self.assertTrue(http_response.status_code == HttpResponseFactory.BAD_REQUEST_HTTP_STATUS)

        CheckEngine.set_checking_rules({})

    def test_check_err_create_bad_dom(self):
        """
        Tests that CheckEngine produces expected CheckStatus, when checking domain error exists
        with the CustomizedAlgo creation Rest service.
        """

        # Re-activate checking rules
        CheckEngine.set_checking_rules(FactoryCatalogue.TYPE_CHECKING_FUNCTIONS)

        my_custom_outside_domain = self.init_rsrc_outside_domain()

        http_req = self.request_factory.post(path=reverse('pattern_custom_algos_dummy'),
                                             data=CustomizedAlgoWs(my_custom_outside_domain).to_json(),
                                             content_type="application/json_util")

        http_response = create_custom_algo(http_req)

        # Display the check result
        result = json_io.decode_json_from_http_response(http_response)

        self.info("response loaded={}".format(result))
        self.info("response status={}".format(http_response.status_code))

        self.assertTrue(http_response.status_code == HttpResponseFactory.BAD_REQUEST_HTTP_STATUS)
