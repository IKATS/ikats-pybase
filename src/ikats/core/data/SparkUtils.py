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
from math import ceil

from ikats.core.library.exception import IkatsException


class SparkUtils(object):
    """
    Spark Ikats library
    Contains some useful methods to work with Ikats Timeseries
    """

    def __init__(self):
        """
        Since there is no other methods than static ones, the init is not used.
        For pylint checking reasons, we create it to prevent from having misused instantiation
        """
        raise RuntimeError("This class shall not be instantiated")

    @staticmethod
    def get_chunks_count(tsuid, md_list, chunk_size):
        """
        Get the count of chunks for a TSUID split into chunks of <chunk_size> points each

        :param tsuid: tsuid to get points from
        :type tsuid: str

        :param md_list: List of metadata
        :type md_list: dict

        :param chunk_size: the size of the chunk
        :type chunk_size: int

        :return: the number of chunks generated
        :rtype: int
        """

        if tsuid not in md_list:
            raise IkatsException("No metadata for TS %s" % tsuid)

        if chunk_size <= 0:
            raise ValueError("Chunk size must be positive")
        try:
            number_of_points = int(md_list[tsuid]["qual_nb_points"])
        except KeyError:
            raise IkatsException("qual_nb_points metadata not found for TSUID %s" % tsuid)
        return int(ceil(number_of_points / chunk_size))

    @staticmethod
    def _get_chunk_info(tsuid, index, md_list, chunk_size):
        """
        Get the chunk <index> information for a TSUID split into chunks of <chunk_size> points each

        :param tsuid: tsuid to get points from
        :type tsuid: str

        :param index: the index of the chunk to get
        :type index: int

        :param md_list: List of metadata
        :type md_list: dict

        :param chunk_size: the size of the chunk
        :type chunk_size: int

        :return: information about the chunk (chunk_index, chunk_start_window, chunk_end_window)
        :rtype: list
        """

        if tsuid not in md_list:
            raise IkatsException("No metadata for TS %s" % tsuid)

        # Number of points
        if "qual_nb_points" not in md_list[tsuid]:
            raise IkatsException("No qual_nb_points in metadata for TS %s" % tsuid)
        nb_points = int(md_list[tsuid]["qual_nb_points"])

        if nb_points <= 0:
            raise ValueError("qual_nb_points shall be a positive number for %s" % tsuid)

        # Timeseries start date
        if "ikats_start_date" not in md_list[tsuid]:
            raise IkatsException("No ikats_start_date in metadata for TS %s" % tsuid)
        start_date = int(md_list[tsuid]["ikats_start_date"])

        # Timeseries end date
        if "ikats_end_date" not in md_list[tsuid]:
            raise IkatsException("No ikats_end_date in metadata for TS %s" % tsuid)
        end_date = int(md_list[tsuid]["ikats_end_date"])

        # Extrapolation of the number of points
        delta = int((end_date - start_date) * chunk_size / nb_points)

        # Chunk start date
        chunk_start = start_date + index * delta

        # Chunk end date
        chunk_end = chunk_start + delta
        if chunk_end + delta > end_date:
            chunk_end = end_date

        return [index, chunk_start, chunk_end]

    @classmethod
    def get_chunks(cls, tsuid, md_list, chunk_size):
        """
        Get the chunks information as an array composed of 3 pieces of information:
        * the index identifying the chunk
        * the start date of the chunk
        * the end date of the chunk

        :param tsuid: tsuid to compute chunks for
        :param md_list: the metadata containing the tsuid information
        :param chunk_size: the number of points per chunks

        :type tsuid: str
        :type md_list: dict
        :type chunk_size: int

        :return: the chunks information
        :rtype: list of ChunkInfo
        """
        ts_chunk_info = []
        for chunk_index in range(cls.get_chunks_count(tsuid=tsuid,
                                                      md_list=md_list,
                                                      chunk_size=chunk_size)):
            ts_chunk_info.append(cls._get_chunk_info(tsuid=tsuid,
                                                     index=chunk_index,
                                                     md_list=md_list,
                                                     chunk_size=chunk_size))
        return ts_chunk_info
