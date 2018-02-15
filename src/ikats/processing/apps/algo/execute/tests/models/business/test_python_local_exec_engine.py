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
"""

import importlib
import logging
from unittest import TestCase

from apps.algo.catalogue.models.business.implem import Implementation
from apps.algo.catalogue.models.business.profile import Argument, ProfileItem
from apps.algo.custom.models.business.algo import CustomizedAlgo
from apps.algo.execute.models.business.algo import ExecutableAlgo
from apps.algo.execute.models.business.data_receiver import SimpleDataReceiver
from apps.algo.execute.models.business.exec_engine import ExecStatus
from apps.algo.execute.models.business.python_local_exec_engine import PythonLocalExecEngine
from ikats.core.library.status import State as EnumState

LOGGER = logging.getLogger(__name__)


def init_basic_exec_algo_from_impl(implem, input_arg_value_list):
    custo_algo = CustomizedAlgo(arg_implementation=implem, custom_params=None)

    exec_algo = ExecutableAlgo(custom_algo=custo_algo)

    names = [x.name for x in implem.input_profile]
    for (name, value) in zip(names, input_arg_value_list):
        exec_algo.set_input_value(name, value)

    for name in [x.name for x in implem.output_profile]:
        exec_algo.set_data_receiver(name, SimpleDataReceiver())

    return exec_algo


def init_impl_without_params(lib_path, in_argnames_list, out_argnames_list=None):
    buzz_impl = Implementation(name="TestProtoExecEngine::init_algo_without_params",
                               description="TU init_algo_without_params",
                               execution_plugin="ProtoExecEngine", library_address=lib_path)

    index = 0
    my_input_profile = []
    for name in in_argnames_list:
        my_arg = Argument(name=name, description="in arg ...", direction=ProfileItem.DIR.INPUT,
                          order_index=index)

        index += 1
        my_input_profile.append(my_arg)

    buzz_impl.input_profile = my_input_profile

    my_res_profile = []
    if out_argnames_list and type(out_argnames_list) is list:
        index = 0
        for name in out_argnames_list:
            my_arg = Argument(name=name, description="out arg ...", direction=ProfileItem.DIR.OUTPUT,
                              order_index=index)

            index += 1
            my_res_profile.append(my_arg)

    elif out_argnames_list:
        my_res = Argument(name=str(out_argnames_list), description="out arg...", direction=ProfileItem.DIR.OUTPUT,
                          order_index=0)
        my_res_profile.append(my_res)

    else:
        my_res = Argument(name="result", description="out arg...", direction=ProfileItem.DIR.OUTPUT,
                          order_index=0)
        my_res_profile.append(my_res)

    buzz_impl.output_profile = my_res_profile

    return buzz_impl


def init_basic_exec_algo(lib_path,
                         in_argnames_list,
                         input_arg_value_list,
                         out_argnames_list=None):
    my_impl = init_impl_without_params(lib_path, in_argnames_list, out_argnames_list)
    return init_basic_exec_algo_from_impl(my_impl, input_arg_value_list)


class TestPythonLocalExecEngine(TestCase):
    def test_find_plugin_engine(self):
        my_module_path = "apps.algo.execute.tests.util.exec_engine"
        my_plugin = "ExecEngineForTU"

        my_cat_implem = init_impl_without_params(lib_path="math::cos", in_argnames_list=["angle"])

        my_exec_algo = init_basic_exec_algo_from_impl(
            implem=my_cat_implem, input_arg_value_list=[0.0])

        # instantiate a new ExecEngineForTU:
        # equivalent to : my_obj = ExecEngineForTU( my_exec_algo )
        #
        my_obj = self.eval_plugin_exec_engine(
            my_module_path, my_plugin, [my_exec_algo])

        my_obj.run_command()

        assert (my_obj.status.msg == "hello")

    def eval_plugin_exec_engine(self, str_plugin_path, str_plugin, eval_args_list):
        """
        utility for TU : test_find_plugin_engine
        => Test mechanism used in order to evaluate the configured engine from module+plugin
        :return: instance of exec engine built with eval_args_list
        """
        my_module_path = str_plugin_path
        my_plugin = str_plugin

        my_module = importlib.import_module(my_module_path)

        evaluated_plugin_str = "my_module.%s" % my_plugin

        my_class = eval(evaluated_plugin_str)

        my_obj = my_class(*eval_args_list)

        return my_obj

    def test_evaluate_cos(self):
        """
        Test the mechanism used in order to evaluate the configured module+function
        """
        my_module_path = "math"
        my_function = "cos"

        my_module = importlib.import_module(my_module_path)

        evaluated_function_str = "my_module.%s" % my_function

        self.assertTrue(
            evaluated_function_str == "my_module.cos", "testing eval str")

        evaluated_function = eval(evaluated_function_str)
        evaluated_pi = eval("my_module.pi")
        self.assertTrue(evaluated_function(0.0) == 1.0,
                        "cos(0) == 1 ")
        self.assertTrue(abs(evaluated_function(evaluated_pi / 2.0)) < 0.1e-10,
                        "cos( my_module.PI / 2.0 ) == 0 ")

        copysign_t1 = self.eval_function("math", "copysign", [1, 2])
        copysign_t2 = self.eval_function("math", "copysign", [2, -3])
        copysign_t3 = self.eval_function("math", "copysign", [-1, 2])
        copysign_t4 = self.eval_function("math", "copysign", [2, -2])

        self.assertTrue(copysign_t1 == 1)
        self.assertTrue(copysign_t2 == -2)
        self.assertTrue(copysign_t3 == 1)
        self.assertTrue(copysign_t4 == -2)

    def eval_function(self, str_module_path, str_function, eval_args_list):
        """
        utility for TU test_evaluate_cos:
        => Test mechanism used in order to evaluate the configured module+function
        """
        my_module_path = str_module_path
        my_function = str_function

        my_module = importlib.import_module(my_module_path)

        evaluated_function_str = "my_module.%s" % my_function
        evaluated_function = eval(evaluated_function_str)

        return evaluated_function(*eval_args_list)

    def test_execute_nominal1(self):

        my_exec_algo = init_basic_exec_algo(
            lib_path="apps.algo.execute.tests.models.business.assets_test_python_local_exec_engine::method_test1",
            in_argnames_list=[],
            input_arg_value_list=[],
            out_argnames_list=["res"])
        exec_engine = PythonLocalExecEngine(my_exec_algo)

        self.assertListEqual(my_exec_algo.get_ordered_output_names(), ["res"])

        status = exec_engine.execute()
        self.assertIsInstance(status, ExecStatus, "Failed to retrieve status")
        self.assertTrue(my_exec_algo.state == EnumState.ALGO_OK)

        # command has results
        my_res = my_exec_algo.get_data_receiver("res").get_received_value()
        self.assertEquals(my_res, "results of the testing method1")

    def test_execute_nominal2(self):

        local_variable = "test_local_var"
        my_exec_algo = init_basic_exec_algo(
            lib_path="apps.algo.execute.tests.models.business.assets_test_python_local_exec_engine::method_test3",
            in_argnames_list=["input"],
            input_arg_value_list=[
                local_variable],
            out_argnames_list=["res"])
        exec_engine = PythonLocalExecEngine(my_exec_algo)
        self.assertListEqual(my_exec_algo.get_ordered_input_names(), ["input"])
        self.assertListEqual(my_exec_algo.get_ordered_output_names(), ["res"])

        status = exec_engine.execute()
        self.assertIsInstance(status, ExecStatus, "Failed to retrieve status")
        self.assertTrue(my_exec_algo.state == EnumState.ALGO_OK)

        # command has results
        my_res = my_exec_algo.get_data_receiver("res").get_received_value()
        self.assertEquals(
            my_res, "results of the testing method3 : test_local_var")

    def test_execute_nominal3(self):
        local_variable = 0.0
        my_exec_algo = init_basic_exec_algo(
            lib_path="math::cos",
            in_argnames_list=["angle"],
            input_arg_value_list=[
                local_variable],
            out_argnames_list=["res"])
        exec_engine = PythonLocalExecEngine(my_exec_algo)
        self.assertListEqual(my_exec_algo.get_ordered_input_names(), ["angle"])
        self.assertListEqual(my_exec_algo.get_ordered_output_names(), ["res"])

        status = exec_engine.execute()
        self.assertIsInstance(status, ExecStatus, "Failed to retrieve status")
        self.assertTrue(my_exec_algo.state == EnumState.ALGO_OK)

        # command has results
        my_res = my_exec_algo.get_data_receiver("res").get_received_value()
        self.assertTrue((1.0 - my_res) < 0.1e-10, "cos(0.0) = 1.0")

    def test_execute_nominal4(self):
        local_value = [1, 2, 5]
        my_exec_algo = init_basic_exec_algo(
            lib_path="apps.algo.execute.tests.models.business.assets_test_python_local_exec_engine::method_test4",
            in_argnames_list=["input"],
            input_arg_value_list=[
                local_value],
            out_argnames_list=["res"])
        exec_engine = PythonLocalExecEngine(my_exec_algo)
        self.assertListEqual(my_exec_algo.get_ordered_input_names(), ["input"])
        self.assertListEqual(my_exec_algo.get_ordered_output_names(), ["res"])

        status = exec_engine.execute()
        self.assertIsInstance(status, ExecStatus, "Failed to retrieve status")
        self.assertTrue(my_exec_algo.state == EnumState.ALGO_OK)

        # command has results
        my_res = my_exec_algo.get_data_receiver("res").get_received_value()
        self.assertListEqual(my_res, local_value)

    def test_execute_nominal5(self):
        left_val = 1
        right_val = -2
        my_exec_algo = init_basic_exec_algo(
            lib_path="math::copysign",
            in_argnames_list=[
                "float_left", "float_right"],
            input_arg_value_list=[
                left_val, right_val],
            out_argnames_list=["res"])
        exec_engine = PythonLocalExecEngine(my_exec_algo)
        self.assertListEqual(my_exec_algo.get_ordered_input_names(), [
            "float_left", "float_right"])
        self.assertListEqual(my_exec_algo.get_ordered_output_names(), ["res"])

        status = exec_engine.execute()
        self.assertIsInstance(status, ExecStatus, "Failed to retrieve status")
        try:
            self.assertTrue(my_exec_algo.state == EnumState.ALGO_OK)
        except Exception:
            raise status.error

        # command has results
        my_res = my_exec_algo.get_data_receiver("res").get_received_value()
        self.assertTrue(my_res == - left_val, "copysign(1, -2 ) == -1")

    def test_execute_nominal6(self):

        local_values = [1, 2, 5]
        expected_res = [5, 2, 1]
        my_exec_algo = init_basic_exec_algo(
            lib_path="apps.algo.execute.tests.models.business.assets_test_python_local_exec_engine::method_test5",
            in_argnames_list=[
                "arg1", "arg2", "arg3"],
            input_arg_value_list=local_values,
            out_argnames_list=["res1", "res2", "res3"])
        exec_engine = PythonLocalExecEngine(my_exec_algo)
        self.assertListEqual(
            my_exec_algo.get_ordered_input_names(), ["arg1", "arg2", "arg3"])
        self.assertListEqual(
            my_exec_algo.get_ordered_output_names(), ["res1", "res2", "res3"])

        status = exec_engine.execute()
        self.assertIsInstance(status, ExecStatus, "Failed to retrieve status")
        try:
            self.assertTrue(my_exec_algo.state == EnumState.ALGO_OK)
        except Exception:
            raise status.error

        # command has results
        for index, _ in enumerate(expected_res):
            my_res_name = "res%s" % (index + 1,)
            my_res = my_exec_algo.get_data_receiver(
                my_res_name).get_received_value()
            self.assertEqual(my_res, expected_res[index])
