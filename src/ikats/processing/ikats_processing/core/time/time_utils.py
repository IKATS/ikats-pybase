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
import time

"""
Ikats date management is defined in this module:
- provides standard methods building dates for ikats_processing
"""


def get_current_time_second_as_float():
    """
    Get current date with following type and format:
    - float: seconds since UNIX EPOCH
    """
    return time.time()
