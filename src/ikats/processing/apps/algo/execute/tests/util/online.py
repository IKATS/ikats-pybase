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
import logging

import numpy

from ikats.core.data.ts import TimestampedMonoVal

LOGGER = logging.getLogger(__name__)


def replace_missing_values(ts_data):
    LOGGER.info(repr(ts_data))
    assert (isinstance(ts_data, TimestampedMonoVal))
    LOGGER.info("TU: calling replace_missing_values ")
    l_numpy = ts_data.data
    LOGGER.info("TU: input %s", str(l_numpy))

    ts_out = numpy.array([[1.5, 5.0], [3.0, 6.7], [5.5, 134.34]])

    return TimestampedMonoVal(ts_out)
