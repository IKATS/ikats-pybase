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
import logging

from ikats.core.data.ts import AbstractTs, TimestampedMonoVal
from ikats.core.resource.client.temporal_data_mgr import TemporalDataMgr
from ikats_processing.core.data.tsref import AbstractTsRef, TsuidTsRef


class TsFactory(object):
    LOGGER = logging.getLogger(__name__)
    """
    TsFactory provides several methods to build various AbstractTs implementation

    """

    def __init__(self):
        pass

    def read_ts_from_temporal_db(self, ts_ref, timeseries_class, tmp_mgr):
        """
        Read and return the expected timeseries according to the reference and the timeseries class

        Required: ResourceClientSingleton has been initialized !!!

        :param ts_ref:
        :type ts_ref: subclass of AbstractTsRef
        :param timeseries_class: class from core.data.ts: as value returned by ResourceClientSingleton
                                may be transformed into specific data type
        :type timeseries_class: subclass of from core.data.ts.AbstractTs: from core.data.ts,
                               or your own subclass, accepting the numpy array internally  produced )
        :param tmp_mgr: temporal data manager
        :type tmp_mgr: TemporalDataMgr
        """
        assert (isinstance(ts_ref, AbstractTsRef))
        assert (isinstance(tmp_mgr, TemporalDataMgr))
        try:

            if isinstance(ts_ref, TsuidTsRef):
                self.LOGGER.info("Reading TS matching reference: %s", str(ts_ref))
                tsuid = ts_ref.tsuid
                start_date = ts_ref.start_date
                end_date = ts_ref.end_date
                value_db = tmp_mgr.get_ts_by_tsuid(tsuid, sd=start_date, ed=end_date)
            else:
                self.LOGGER.info("Reading TS matching reference: %s", str(ts_ref))
                raise Exception("Not yet implemented for ts_ref typed: %s" % type(ts_ref))

            if len(value_db) == 0:
                raise ValueError("Empty timeseries selection %s" % ts_ref)

            if timeseries_class is TimestampedMonoVal:
                self.LOGGER.info("Building TimestampedMonoVal with extracted value")
                data_value = TimestampedMonoVal(value_db)
            else:
                self.LOGGER.warning("Specific TS instance with custom class %s", timeseries_class.__name__)
                raise Exception("Not yet implemented")

            return data_value

        except Exception as err:
            self.LOGGER.error("Failure: TsFactory::read_ts_from_temporal_db")
            self.LOGGER.exception(err)
            raise err


class TsRefFactory(object):
    """
    TsRefFactory provides several methods to build various AbstractTsRef implementation

    """

    LOGGER = logging.getLogger(__name__)

    def write_ts_into_temporal_db(self, tmp_mgr, ts, metric, output_func_id, tags_dict=None):
        """
        Import the specified instance of timeseries in Ikats DB
        and return TsuidTsRef pointing to imported ts.
        :param output_func_id:
        :param ts: timeseries written in temporal database
        :type ts: instance of subclass of AbstractTs
        :param metric: required metric for import
        :type metric: str
        :param tmp_mgr: temporal data manager
        :type tmp_mgr: TemporalDataMgr
        :param tags_dict: optional tags: additional (key, value) pairs passed to the import
        :type tags_dict: dict

        :return: ts_ref, status
                - ts_ref is pointing to the imported data (possibly set to None in case of failure: see status),
                - status: dict returned by tempo_manager.import_ts_data(...): see status['error'] ...

        :rtype: tuple (ts_ref is tsuid_ref, and status is dict)
        :raises Exception if unexpected error occurred
        """
        assert (isinstance(ts, AbstractTs))
        assert (isinstance(tmp_mgr, TemporalDataMgr))

        try:

            data = ts.data
            start_date = ts.get_first_date()
            end_date = ts.get_last_date()

            ret_status = tmp_mgr.import_ts_data(metric=metric,
                                                data=data,
                                                fid=output_func_id,
                                                tags=tags_dict)

            if ret_status['status']:
                ts_ref = TsuidTsRef(ret_status['tsuid'], start_date, end_date)
                ts_ref.func_id = output_func_id
                ts_ref.metric = metric
            else:
                ts_ref = None

        except Exception as err:
            ret_status = {"status": False,
                          'errors': {"UnexpectedError": err},
                          'numberOfSuccess': 0,
                          'summary': "failed import with unexpected error"}
            ts_ref = None

        self.log_status(ret_status)
        return ts_ref, ret_status

    def log_status(self, res_status):
        """
        Send status to the logs
        :param res_status:
        :type res_status:
        """
        if (res_status is not None) and ('status' in res_status.keys()):
            if res_status['status']:
                self.LOGGER.debug("Success status: %s", str(res_status))
            else:
                self.LOGGER.error("Failure status: %s", str(res_status))

                if 'errors' in res_status.keys():
                    errors_dict = res_status['errors']
                    if errors_dict is dict:
                        self.LOGGER.error("- errors list:")
                        index = 0
                        for err in errors_dict.values():
                            self.LOGGER.error("  - error[%s]", index)
                            index += 1
                            self.LOGGER.exception(err)

        else:
            self.LOGGER.error("Malformed status dict from resource python client layer: %s", str(res_status))
