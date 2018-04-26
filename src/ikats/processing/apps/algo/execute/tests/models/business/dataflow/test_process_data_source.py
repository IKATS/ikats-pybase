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
from logging import StreamHandler
import os
import sys
import unittest
from unittest import skipIf

from apps.algo.execute.models.business.dataflow.process_data_receiver import ProcessDataPickleWriter, \
    ProcessDataPlainTextWriter
from apps.algo.execute.models.business.dataflow.process_data_sources import ProcessDataPickleReader, \
    LOG_PROCESS_DATA_READER, ProcessDataPlainTextReader
from ikats.core.resource import api

LOGGER = logging.getLogger(__name__)

# Defines the log level to DEBUG
LOGGER.setLevel(logging.DEBUG)

# Create the handler to a file, append mode, 3 backups, max size = 1Mo
FILE_HANDLER = StreamHandler(sys.stdout)
FILE_HANDLER.setLevel(logging.DEBUG)
LOGGER.addHandler(FILE_HANDLER)


class TestProcessDataPlainTextReader(unittest.TestCase):
    """
    Unittest class testing ProcessDataPlainTextReader
    """

    @skipIf('TEST_WITH_DOCKER' not in os.environ
            or "{}".format(os.environ['TEST_WITH_DOCKER']).lower() != 'true',
            "This test requires to be run with the DOCKER environment")
    def test_get_value_with_text(self):
        """
        Tests nominal case: read a text value
        """

        text = "this is my text"
        try:
            # prepare data => write model into processdata

            my_writer_id = "test_get_value_with_text::init"

            receiver = ProcessDataPlainTextWriter(catalog_output_name="mock_text_output",
                                                  writer_id=my_writer_id)

            written_pid = "processid::" + my_writer_id
            receiver.set_process_id(written_pid)

            rid = receiver.send_value(text)

            LOG_PROCESS_DATA_READER.info("written rid={}".format(receiver.get_written_data_id()))

        except Exception:
            self.fail("Failed to prepare the unittest: test aborted")

        try:

            my_source_id = "test_get_value_with_text"
            source = ProcessDataPlainTextReader(identifier=rid,
                                                catalog_input_name="mock_text_input",
                                                reader_id=my_source_id)

            reader_pid = "processid::" + my_source_id
            source.set_process_id(reader_pid)

            read_text = source.get_value()
            self.assertEqual(text, read_text)

            LOG_PROCESS_DATA_READER.info("text={}".format(read_text))

        finally:
            try:
                api.IkatsProcessData.delete(written_pid)
            except Exception:
                msg = "Unittest failed to remove initialized data: process_id={}"
                LOG_PROCESS_DATA_READER.error(msg.format(written_pid))


class TestProcessDataPickleReader(unittest.TestCase):
    """
    Unittest class testing ProcessDataPickleReader
    """

    @skipIf('TEST_WITH_DOCKER' not in os.environ
            or "{}".format(os.environ['TEST_WITH_DOCKER']).lower() != 'true',
            "This test requires to be run with the DOCKER environment")
    def test_get_value_with_sk_model(self):
        """
        Tests nominal case: read an object (sk_model) pickled in database
        """
        from sklearn import tree
        from sklearn.datasets import load_iris

        try:
            # prepare data => write model into processdata
            clf = tree.DecisionTreeClassifier()
            iris = load_iris()
            clf = clf.fit(iris.data, iris.target)
            my_writer_id = "test_get_value_with_sk_model::init"

            receiver = ProcessDataPickleWriter(catalog_output_name="mock_clf_output", writer_id=my_writer_id)

            written_pid = "processid::" + my_writer_id
            receiver.set_process_id(written_pid)

            rid = receiver.send_value(clf)

            LOG_PROCESS_DATA_READER.info("written rid={}".format(receiver.get_written_data_id()))

        except Exception:
            self.fail("Failed to prepare the unittest: test aborted")

        try:

            my_source_id = "test_get_value_with_sk_model"
            source = ProcessDataPickleReader(identifier=rid, catalog_input_name="mock_clf_output",
                                             reader_id=my_source_id)

            reader_pid = "processid::" + my_source_id
            source.set_process_id(reader_pid)

            read_clf = source.get_value()
            data_values = iris.data

            try:
                predicted = read_clf.predict(data_values[0:1])
                LOG_PROCESS_DATA_READER.info("predicted={}".format(predicted))
            except Exception:
                self.fail("Failed to call predict() on the de-pickled scikit-learn model !")

        finally:
            try:
                api.IkatsProcessData.delete(written_pid)
            except Exception:
                msg = "Unittest failed to remove initialized data: process_id={}"
                LOG_PROCESS_DATA_READER.error(msg.format(written_pid))
