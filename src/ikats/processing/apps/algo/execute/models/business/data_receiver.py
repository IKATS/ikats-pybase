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


class AbstractDataReceiver(object):
    """
    This abstraction will be used by executable algo in order to write the output value at runtime
    """

    @abstractmethod
    def get_received_value(self):
        pass

    @abstractmethod
    def get_process_id(self):
        pass

    @abstractmethod
    def set_process_id(self, arg_process_id):
        pass

    @abstractmethod
    def get_received_progress_status(self):
        pass

    @abstractmethod
    def send_value(self, value, progress_status=None):
        pass


class SimpleDataReceiver(AbstractDataReceiver):
    """
    Simplest data receiver: one value, and one progress_status are recorded directly in the instance
    """

    def __init__(self, process_id=None):
        self.__received_value = None
        self.received_progress_status = None
        self.__process_id = process_id

    def __str__(self):
        return "%s" % self.__received_value

    def get_received_value(self):
        return self.__received_value

    def get_received_progress_status(self):
        return self.received_progress_status

    def send_value(self, value, progress_status=None):
        self.__received_value = value
        self.received_progress_status = progress_status

    def get_process_id(self):
        return self.__process_id

    def set_process_id(self, arg_process_id):
        self.__process_id = arg_process_id
