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
from apps.algo.execute.models.business.exec_engine import ExecEngine


class ExecEngineForTU(ExecEngine):
    """
    Plugin resource used by the TU in apps.algo.execute.tests.models.business.exec_engine
    => simulate an external plugin extending ProtoExecLocal
    """

    def run_command(self):
        self.status.msg = "hello"
