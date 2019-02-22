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


class AbstractTsRef(object):
    """
    Abstraction of TS references for ikats resources
    - one TS reference is targeting one timeseries in IKATS database.

    At this level: we gather mutual information: see subclass to complete information

    """

    def __init__(self, arg_start_date=0, arg_end_date=None):
        """
        Constructor of Abstraction
        :param arg_start_date: millisec first date
        :type arg_start_date: expects type castable to int
        :param arg_end_date: millisec last date
        :type arg_end_date: expects type castable to int
        """
        if arg_end_date:
            assert(arg_end_date > arg_start_date), "Error: end_date > start_date for any AbstractTsRef"
            self.__end_date = int(arg_end_date)
        else:
            assert (arg_end_date is None), "Error: end_date is int or else None"
            self.__end_date = arg_end_date

        self.__start_date = int(arg_start_date)

        self.__metric = None

    def get_end_date(self):
        return self.__end_date

    def set_metric(self, my_metric):

        assert(self.__metric is None), "Impossible to redefined metric more than one time"
        self.__metric = my_metric

    def get_metric(self):
        return self.__metric

    def get_start_date(self):
        return self.__start_date

    end_date = property(get_end_date, None, None, "")
    metric = property(get_metric, set_metric, None, "")
    start_date = property(get_start_date, None, None, "")


class TsuidTsRef(AbstractTsRef):
    """
    Use instance of TsuidTsRef when you are technically working with TSUIDs.
    This is the technical tsref version.
    Instance of tsuid_ref may also hold additional piece of meta-information about ts:
       - func_id as functional identifier
       - metric as opentsdb metric
       - tag as opentsdb defined tags
    """

    def __init__(self, arg_tsuid, arg_start_date=0, arg_end_date=None,
                 arg_func_id=None,
                 arg_metric=None,
                 arg_tags=None):
        """
        Constructor
        :param arg_tsuid: required: TSUID is the technical reference
        :type arg_tsuid: str
        :param arg_start_date: optional, default 0: start date of the TS
        :type arg_start_date: int
        :param arg_end_date: optional, default None: end date of the TS ( None => last timestamp in database)
        :type arg_end_date: int
        :param arg_func_id: optional, default None: additional information, may be defined later by setter
        :type arg_func_id: str
        :param arg_metric: optional, default None: additional information, may be defined later by setter
        :type arg_metric: str
        :param arg_tags: optional, default None: additional information, may be defined later by setter
        :type arg_tags: dict
        """
        super(TsuidTsRef, self).__init__(arg_start_date, arg_end_date)
        self.metric = arg_metric

        assert(arg_tsuid and isinstance(arg_tsuid, str)), "Error: tsuid required for TsuidTsRef"

        self.__tsuid = arg_tsuid

        self.__func_id = arg_func_id

        self.__tags = arg_tags

    def get_tsuid(self):
        """
        :return: tsuid identifier of TS (required)
        :rtype: str
        """
        return self.__tsuid

    def get_func_id(self):
        """
        :return: functional identifier if defined or None
        :rtype: str
        """
        return self.__func_id

    def set_func_id(self, arg_func_id):
        """
        Set functional identifier: useful to import a new TS.
        Note: it is forbidden to redefine a new value over a previous defined value => keep consistency
        :param arg_func_id: functional identifier
        :type arg_func_id: str
        """
        assert((self.__func_id is None) or (self.__func_id == arg_func_id)
               ), "Impossible to redefine different functional ids (%s, %s) on same tsuid %s" % (self.__func_id,
                                                                                                 arg_func_id,
                                                                                                 self.__tsuid)
        self.__func_id = arg_func_id

    def set_tags(self, arg_tags):
        """
        Set new tags: useful in order to import a new TS.
        :param arg_tags: tags are defined as (key, value) pairs
        :type arg_tags: dict
        """
        self.__tags = arg_tags

    def get_tags(self):
        """
        :return: tags if defined or None
        :rtype: dict
        """
        return self.__tags

    def __str__(self):
        return "TsuidTsRef tsuid=[%s], func_id=[%s], metric=[%s], start_date[%i], end_date[%s]" % \
            (self.tsuid, self.func_id, self.get_metric(), self.start_date, str(self.end_date))

    tsuid = property(get_tsuid, None, None, "")
    func_id = property(get_func_id, set_func_id, None, "")
    tags = property(get_tags, set_tags, None, "")
