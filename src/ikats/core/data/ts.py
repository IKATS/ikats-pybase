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

from ikats.core.data.convert import ts_mono_to_np, get_std_millisec, get_std_float


class AbstractTs(object):
    """
    Abstraction of timeseries.

    This class provides abstract interface:
    each subclass will provide a specific implementation,
    adapted to algorithms in ikats_pre library or other
    """

    def __init__(self):
        pass

    @property
    def data(self):
        """
        Get the internal data
        """
        raise NotImplementedError

    @abstractmethod
    def get_first_date(self):
        """
        :return: timestamp of first point
        """
        pass

    @abstractmethod
    def get_last_date(self):
        """
        :return: timestamp of last point
        """
        pass


class TimestampedMonoVal(AbstractTs):
    """
    This class provides ikats standard type for timeseries with each data point having
        * one timestamp (the date associated to the point)
        * one value

    Internal implementation: is compatible with the resource package of ikats_core
    (numpy array: format defined from extract services on the TemporalDataMgr)
    """

    def __init__(self, numpy_array_client):
        """
        This constructor sets TimestampedMonoVal with numpy array, which should be compatible with resource client.

        Note: a conversion is applied only if needed, to guarantee compatibility:
          - See: the ikats.core.data.convert function: ts_mono_to_np,
                 with option only_if_needed=True

        :param numpy_array_client: see numpy format defined from extract services on the TemporalDataMgr
        :type numpy_array_client: numpy: array. this
        """
        super(TimestampedMonoVal, self).__init__()
        if type(numpy_array_client) == TimestampedMonoVal:
            self.__numpy_array = numpy_array_client
        else:
            self.__numpy_array = ts_mono_to_np(array=numpy_array_client, only_if_needed=True)

    @property
    def data(self):
        """
        Get the numpy array
        """
        return self.__numpy_array

    @property
    def timestamps(self):
        """
        Get all the timestamps as one array
        """
        return self.__numpy_array[:, 0]

    @property
    def values(self):
        """
        Get all values as one array
        """
        return self.__numpy_array[:, 1]

    def __len__(self):
        """
        Return the length of the data data
        """
        return int(self.__numpy_array.shape[0])

    def get_first_date(self):
        """
        Gets the internal timestamp of first point
        :return: timestamp of first point
        :rtype: numpy.datetime64
        """
        return self.__numpy_array[0][0]

    def get_first_date_std(self):
        """
        Gets the standard timestamp of first point
        :return: timestamp of first point, in milliseconds
        :rtype:  int
        """
        return self.get_timestamp_millisec_std(0)

    def get_last_date(self):
        """
        Gets the internal timestamp of last point
        :return: timestamp of last point
        :rtype: numpy.datetime64
        """
        return self.__numpy_array[-1][0]

    def get_last_date_std(self):
        """
        Gets the standard timestamp of last point
        :return: timestamp of last point, in millisecond
        :rtype: int
        """
        return self.get_timestamp_millisec_std(-1)

    def get_point_std(self, index):
        """
        Convert numpy point (internal format) into standard python point: [<int>, <float>]
        :param index:
        :type index:
        """
        internal_point = self.__numpy_array[index]
        return [get_std_millisec(internal_point[0]),
                get_std_float(internal_point[1])]

    def get_point(self, index):
        """
        Get numpy point (internal format: provided by resource client)
        :param index:
        :type index: int
        """
        return self.__numpy_array[index]

    def get_timestamp_millisec(self, index):
        """
        Return the internal timestamp of point at index
        :param index: index of point
        :type index: int
        :return: internal timestamp in milliseconds
        :rtype: internal numpy type
        """
        return self.__numpy_array[index][0]

    def get_timestamp_millisec_std(self, index):
        """
        Return the timestamp of point at index, as standard type int
        :param index: index of point
        :type index: int
        :return: converted timestamp in milliseconds
        :rtype: int
        """
        return get_std_millisec(self.__numpy_array[index][0])

    def get_value(self, index):
        """
        Return the internal value of point at index
        :param index: index of point
        :type index: int
        :return: internal value
        :rtype: internal numpy type
        """
        return self.__numpy_array[index][1]

    def get_value_float_std(self, index):
        """
        Return the value of point at index, as standard float
        :param index: index of point
        :type index: int
        :return: converted value
        :rtype: float type
        """
        return get_std_float(self.__numpy_array[index][1])
