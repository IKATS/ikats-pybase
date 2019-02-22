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
import os
import unittest
from unittest.case import skipIf

from apps.algo.execute.models.business.dataflow.process_data_receiver import LOGGER, \
    ProcessDataPickleWriter, \
    ProcessDataPlainTextWriter
from ikats.core.resource.api import IkatsApi


class TestProcessDataPickleWriter(unittest.TestCase):
    """
    Unittest class testing ProcessDataPickleWriter
    """

    @skipIf('TEST_WITH_DOCKER' not in os.environ or
            "{}".format(os.environ['TEST_WITH_DOCKER']).lower() != 'true',
            "This test requires to be run with the DOCKER environment")
    def test_send_value_with_sk_model(self):
        """
        Nominal case testing the ProcessDataPickleWriter with a scikit-learn model
        """
        from sklearn.datasets import load_iris
        from sklearn import tree
        clf = tree.DecisionTreeClassifier()
        iris = load_iris()
        clf = clf.fit(iris.data, iris.target)
        my_writer_id = "test_send_value_with_sk_model"

        receiver = ProcessDataPickleWriter(catalog_output_name="mock_clf_output", writer_id=my_writer_id)

        test_pid = "processid::" + my_writer_id
        receiver.set_process_id(test_pid)

        rid = receiver.send_value(clf)

        self.assertEqual(rid, receiver.get_written_data_id())

        LOGGER.info(receiver.get_written_data_id())

        try:
            IkatsApi.pd.delete(process_id=test_pid)
        except Exception:
            msg = "Unittest failed to remove written data: process_id={}"
            LOGGER.error(msg.format(test_pid))

            # see also test: test_get_value_with_sk_model


class TestProcessDataPlainTextWriter(unittest.TestCase):
    """
    Unittest class testing ProcessDataPlainTextWriter
    """

    @skipIf('TEST_WITH_DOCKER' not in os.environ or
            "{}".format(os.environ['TEST_WITH_DOCKER']).lower() != 'true',
            "This test requires to be run with the DOCKER environment")
    def test_send_value_with_text(self):
        """
        Nominal case testing the ProcessDataPlainTextWriter with a text
        """

        my_plain_text = "this is my text"

        my_writer_id = "test_send_value_with_text"

        receiver = ProcessDataPlainTextWriter(catalog_output_name="mock_text_output", writer_id=my_writer_id)

        test_pid = "processid::" + my_writer_id

        receiver.set_process_id(test_pid)

        rid = receiver.send_value(my_plain_text)

        self.assertEqual(rid, receiver.get_written_data_id())

        LOGGER.info(receiver.get_written_data_id())

        try:
            IkatsApi.pd.delete(process_id=test_pid)
        except Exception:
            msg = "Unittest failed to remove written data: process_id={}"
            LOGGER.error(msg.format(test_pid))

            # see also test: test_get_value_with_sk_model
