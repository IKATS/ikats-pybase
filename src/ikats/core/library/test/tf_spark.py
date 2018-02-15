"""
LICENSE:
--------
Copyright 2017-2018 CS SYSTEMES D'INFORMATION

Licensed to CS SYSTEMES D'INFORMATION under one
or more contributor license agreements. See the NOTICE file
distributed with this work for additional information
regarding copyright ownership. CS licenses this file
to you under the Apache License, Version 2.0 (the
"License"); you may not use this file except in compliance
with the License. You may obtain a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an
"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
KIND, either express or implied. See the License for the
specific language governing permissions and limitations
under the License.

.. codeauthors::
    Fabien TORTORA <fabien.tortora@c-s.fr>
"""
import time
from scipy.stats.stats import pearsonr

from ikats.core.config.ConfigReader import ConfigReader
from ikats.core.library.spark import Connector
from ikats.core.resource.client import TemporalDataMgr
from pyspark import SparkContext


def test_spark_good_practice():
    """
    Tests the spark good practices
    """
    config_reader = ConfigReader()
    host = config_reader.get('cluster', 'tdm.ip')
    port = int(config_reader.get('cluster', 'tdm.port'))

    # Get Spark Context
    spark_context = SparkContext(appName="Spark_good_practice")

    tdm = TemporalDataMgr()

    # Get the meta data for the BIG dataset
    ds_items = tdm.get_data_set("BIG_DATA_SET_A340001")['ts_list']
    md_list = tdm.get_meta_data(ds_items)

    nb_flights = 4

    # Build the list of the TS for the 400 flights by keeping WSx and BRK_PRESSx metrics
    big_ts_list = []
    for flight_id in range(nb_flights):
        flight_ts_list = []
        for tsuid in md_list:
            try:
                if md_list[tsuid]['FlightIdentifier'] != str(flight_id):
                    continue
                if "WS" in md_list[tsuid]['metric'] or "BRK_PRESS" in md_list[tsuid]['metric']:
                    flight_ts_list.append(tsuid)
            except Exception:
                pass
        big_ts_list.append(flight_ts_list)

    # Final list of all single rdd computed in below for loop
    final_rdd_list = []

    # List of cached rdd to be able to unpersist them at the end of the calculation
    rdd_cached_list = []

    # We must redo the process in a for loop for every flight.
    # map chain allows only sequential transformations/actions
    # This for loop is really fast since there is only spark transformations.
    # Transformations are "lazy" and are evaluated only during actions call
    for flight_id in range(nb_flights):
        rdd = spark_context.parallelize(big_ts_list[flight_id])

        # For each ts in ts_list, get the data
        #  [tsuid1, ...] -> [(tsuid1, ts_data1), ...]
        rdd_ts_data = rdd.map(lambda x: (x, Connector.get_ts(x, host, port)))

        # Store ts_data in memory to speed up the next spark needs (in case of worker failure)
        rdd_ts_data.cache().collect()
        rdd_cached_list.append(rdd_ts_data)

        # Create all combinations (cartesian product)
        #  [x,y] -> [(x,y),(y,x)]
        # Filter to reduce to half matrix
        #  [(x,y),(y,x)] -> [(x,y)]
        # Then compute correlation
        #  [(tsuid1, ts1_data),(tsuid2, ts2_data),...] --> [(tsuid1, tsuid2, correlation coeff), ...]
        raw_results_rdd = rdd_ts_data.cartesian(rdd_ts_data) \
            .filter(lambda x: x[0][0] <= x[1][0]) \
            .map(lambda x: (x[0][0], x[1][0], pearsonr(x[0][1][:min(len(x[0][1][:]), len(x[1][1][:])), 1],
                                                       x[1][1][:min(len(x[0][1][:]), len(x[1][1][:])), 1])[0]))
        # Here, the pearson calculation is performed in a single call.
        # This is sufficient to keep the reliability of the calculation
        # We can have a better/deeper optimization by breaking down the pearson correlation calculation to smaller
        # distributed tasks.

        # The RDD is prepared, store it until all RDD are prepared and ready to compute
        final_rdd_list.append(raw_results_rdd)

    # Do the union of all RDD to perform the calculation in one shot
    #  [(tsuid1,tsuid2,coeff),...] --> [(flight_id,(tsuid1,tsuid2,coeff)),...]
    final_rdd = final_rdd_list[0].map(lambda x: (0, x))
    for flight_id in range(1, len(final_rdd_list)):
        final_rdd += final_rdd_list[flight_id].map(lambda x: (flight_id, x))

    time_1 = time.time()
    # Effective Computation (collect is an action whereas previous 'map' are transformation)
    # [(flight_id,(tsuid1,tsuid2,coeff)),...] --> {flight_id : [(tsuid1,tsuid2,coeff),...],...}
    results = final_rdd.groupByKey().map(lambda x: (x[0], list(x[1]))).collectAsMap()

    time_2 = time.time()
    # Release memory
    for rdd in rdd_cached_list:
        rdd.unpersist()

    # 479 seconds to compute all correlation matrix -> 8min

    t_result = time_2 - time_1

    with open('/tmp/spark_good_practice_execution_time.log', 'w') as opened_file:
        opened_file.write("%s\n" % t_result)

    for flight in results:
        ts_list = big_ts_list[flight]

        # Convert result to matrix
        # results = [(ts1,ts2,value),...] --> matrix[ts1][ts2] = value
        matrix = [[0 for _ in range(len(ts_list))] for _ in range(len(ts_list))]
        for item in results[flight]:
            matrix[ts_list.index(item[0])][ts_list.index(item[1])] = item[2]
            matrix[ts_list.index(item[1])][ts_list.index(item[0])] = item[2]

        with open('/tmp/spark_good_practice_pearson_matrix_flight_%s' % flight, 'w') as opened_file:
            opened_file.write(';'.join(ts_list) + '\n')
            i = 0
            for line in matrix:
                opened_file.write("%s;%s\n" % (ts_list[i], ';'.join([str(x) for x in line])))
                i += 1
    return t_result


if __name__ == "__main__":
    TIME_0 = time.time()
    print("Execution Time: %s" % test_spark_good_practice())
    print("Total Time: %s" % (time.time() - TIME_0))
