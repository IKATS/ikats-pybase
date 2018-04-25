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
from enum import IntEnum


class State(IntEnum):
    """
    Execution State
    """
    INIT = 0
    RUN = 1
    ALGO_OK = 2
    ALGO_KO = 3
    ENGINE_KO = 4

    @classmethod
    def parse(cls, number):
        """
        Parse the state from the corresponding number and return the enum member
        :param number:
        :return:
        """
        assert(type(number) is int)
        for enum_attr in State:
            if enum_attr.value == number:
                return enum_attr
        raise ValueError("Unexpected integer %s for ikats.library.status.STATE" % number)


# Enumerated tuples to be assigned to self.__status
STATES = ("Initializing",
          "Running",
          "Finished wit success",
          "Finished with errors raised by algo",
          "Finished with errors in engine implementation")
