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
from abc import abstractmethod


class AbstractDataSource(object):
    """
    This abstraction will be used by executable algo in order to read the input value at run time
    """

    @abstractmethod
    def get_value(self):
        return None

    @abstractmethod
    def get_process_id(self):
        return None

    @abstractmethod
    def set_process_id(self, process_id):
        pass


class SimpleValueDataSource(AbstractDataSource):
    """
    Simple wrapper of a value fully predefined with constructor
    """

    def __init__(self, value, process_id=None):
        self.value = value
        self.__process_id = process_id

    def __str__(self):
        return "%s" % self.value

    def get_value(self):
        return self.value

    def get_process_id(self):
        return self.__process_id

    def set_process_id(self, process_id):
        self.__process_id = process_id

# Todo
# autres sources:
# - evaluation de reference OpenTSDB d'une seule TS
# - evaluation de reference de metadata de TS
# - iterateur sur des references de TS ...
# - ...
#
