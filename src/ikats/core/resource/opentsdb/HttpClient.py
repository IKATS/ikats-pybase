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
    Maxime PERELMUTER <maxime.perelmuter@c-s.fr>
"""
import json
import logging
import os
import time
from queue import Queue
from threading import Thread, Event
import queue

import requests

from ikats.core.config.ConfigReader import ConfigReader


class QueueItem(object):
    """
    Definition of an item queued before sending to OpenTSDB
    """
    def __init__(self, url, metric, tags, points):
        self.url = url
        self.metric = metric
        self.tags = tags
        self.points = points


class HttpClientResult(object):
    """
    Class defining the result information about a HTTP send action
    """

    def __init__(self, timeouts=0, errors=None, failed=0, success=0, duration=0):
        """
        Initializer

        :param timeouts: Number of timeouts that occurred
        :param errors: List of all errors
        :param failed: Number of points not imported
        :param success: Number of points imported
        :param duration: Timings measurement (in seconds)

        :type timeouts: int
        :type errors: list or None
        :type failed: int
        :type success: int
        :type duration: float

        """

        # Number of encountered timeouts
        self.timeouts = timeouts
        # List of errors encountered by OpenTSDB
        self.errors = errors or []
        # Number of failed points (not imported)
        self.failed = failed
        # Number of successfully imported points
        self.success = success
        self.duration = 0
        # Protect against negative execution time
        if duration >= 0:
            self.duration = duration
        else:
            raise ValueError("duration parameter shall be positive number")

    def speed(self):
        """
        Returns the effective speed of imported points (based only on successful points)
        None is returned if duration is not set

        :return: the speed in points/second
        :rtype: float or None
        """
        if self.duration > 0:
            return self.success / self.duration
        return None

    def append(self, result):
        """
        Merge another instance of this class into this one.
        Useful when dealing with chunked import or multi TS import

        :param result: other result
        :type result: HttpClientResult
        """
        json_result = json.loads(result)
        self.timeouts += int(json_result['timeouts'])
        if self.errors is not list:
            self.errors = []
        self.errors.extend(json_result['errors'])
        self.failed += int(json_result['failed'])
        self.success += int(json_result['success'])


def chunks(original_list, chunk_size):
    """
    Yield successive chunk_size-sized chunks from original_list.

    :param original_list: list to split
    :param chunk_size: size of the chunk (in number of items per chunk)

    :type original_list: list
    :type chunk_size: int

    :return: iterator on chunked original_list
    """
    for i in range(0, len(original_list), chunk_size):
        yield original_list[i:i + chunk_size]


class HttpClient(object):
    """
    Connector to OpenTSDB
    """

    # Client logger
    LOGGER = logging.getLogger(__name__)

    def __init__(self, host=None, port=None, qsize=1000, threads_count=1):
        """
        Main OpenTSDB client.

        :param host: Host to connect to (overrides configuration file)
        :param port: port to connect to (overrides configuration file)
        :param qsize: Size of the send_queue to use (bigger implies big memory usage) (default:1k)
        :param threads_count: set the initial threads count (default:1 meaning, no multi-threaded)

        :type host: str
        :type port: int
        :type qsize: int
        :type threads_count: int
        """
        self.thr_list = []

        # Prepare events detecting the end of an import
        self._event_done = Event()
        self._event_abort = Event()

        # Get the cluster configuration
        config = ConfigReader()

        # Host and port to connect to
        self.host = host or config.get('cluster', 'opentsdb.write.ip')
        self.port = port or int(config.get('cluster', 'opentsdb.write.port'))

        self.use_threads = threads_count > 1
        if self.use_threads:
            self.send_queue = Queue(maxsize=qsize)
            self.result_queue = Queue()
            self.queue_max_size = qsize
            self.threads_count = threads_count
            # Start threads
            for _ in range(min(threads_count, os.cpu_count())):
                self.__add_thr()

    def send_http(self, metric, tags, data_points, max_points_per_query=250000, timeout=60000):
        """
        Send a list of data points to OpenTSDB

        :param metric: metric to use for OpenTSDB
        :param tags: tags to use for OpenTSDB
        :param data_points: list as np.array where first column is timestamp (ms), the second is the value (float)
        :param max_points_per_query: Upper limit of points per query
        :param timeout: maximum time (in millisecond) before considering a timeout for a query

        :type metric: str
        :type tags: dict
        :type data_points: np.array
        :type max_points_per_query: int
        :type timeout: int

        :return: the result of the import
        :rtype: HttpClientResult
        """

        # Send the request to get the TSUID information
        url = "http://%s:%s/api/put?details&sync&sync_timeout=%d" % (self.host, self.port, timeout)

        result = HttpClientResult()
        start_time = time.time()

        if self.use_threads:

            # Create chunks of max_points_per_query points and add each chunk to send_queue
            for _, chunk in enumerate(chunks(data_points, max_points_per_query)):
                data = QueueItem(url=url, metric=metric, tags=tags, points=chunk)
                self.send_queue.put(data, block=True)
            self.wait()

            # Dequeue the results
            self.__dequeue_results(result)

        else:
            with requests.Session() as session:
                for _, chunk in enumerate(chunks(data_points, max_points_per_query)):
                    data = QueueItem(url=url, metric=metric, tags=tags, points=chunk)
                    local_result = self.__send_http_task_single(data=data, session=session)
                    result.append(local_result)
        result.duration = time.time() - start_time
        return result

    def __del__(self):
        """
        Called when destroying instance
        """
        self.kill()

    def wait(self):
        """
        Wait for completion
        Close then block waiting for background thread to finish
        """
        self._event_done.set()

        # Scan for all threads to close
        for thr in self.thr_list:
            thr.join()
            self.LOGGER.debug("Closed %s", thr)
        self.LOGGER.debug("All threads closed")

    def abort(self):
        """
        Abort current import by stopping it immediately
        """
        self._event_abort.set()

    def kill(self):
        """
        Kill current import by stopping it immediately
        """
        if not self._event_abort.is_set() and not self._event_done.is_set():
            self.LOGGER.debug("Killing connection to OpenTSDB")
            self.abort()

    def is_queue_empty(self):
        """
        Simple checker of the send_queue status

        :return: True if send_queue is Empty, false otherwise
        """
        return self.send_queue.empty()

    def __add_thr(self):
        """
        Create a new thread to dequeue the sending send_queue
        """
        thr = Thread(
            target=self.__send_http_worker_multi,
            args=(self.send_queue, self._event_done, self._event_abort))
        thr.start()

        self.thr_list.append(thr)
        self.LOGGER.debug("New thread started %s (%s total threads started) ", thr, len(self.thr_list))

    def __send_http_worker_multi(self, writing_queue, event_done, event_abort):
        """
        Take one item from the sending send_queue and send it.
        Wait until last point is written
        Used in multi-processing mode

        :param writing_queue: Queue used to write data
        :param event_done: event indicating there is no more point to send
        :param event_abort: event indicating to stop immediately the send

        :type writing_queue: Queue
        :type event_done: Event
        :type event_abort: Event

        """

        with requests.Session() as session:
            while True:
                try:
                    # Try to pop send_queue within 1s
                    data = writing_queue.get(True, timeout=1)

                    result = self.__send_http_task_single(data=data, session=session)
                    self.result_queue.put(result)
                except queue.Empty:
                    if event_done.is_set():
                        # Stop current process if no items in send_queue and stop requested
                        self.LOGGER.debug("Done event detected and send_queue is empty")
                        break
                    else:
                        # No items in send_queue, more points expected
                        continue

                if event_abort.is_set():
                    # Stop current process if no items in send_queue and stop requested
                    self.LOGGER.debug("Abort event detected")
                    break

    @staticmethod
    def __send_http_task_single(data, session):
        """
        Send a set of points to OpenTSDB in a single request in single-process mode

        :param data: set of points to send
        :param session: Request session

        :type data: QueueItem
        :type session: Request

        :return: the response text
        """
        json_data = []
        for point in data.points:
            json_data.append({
                "metric": data.metric,
                "timestamp": point[0],
                "value": point[1],
                "tags": data.tags
            })
        for _ in range(3):
            # Retry at most 3 times until all points are imported
            result = session.post(
                url=data.url,
                timeout=600,
                json=json_data
            )
            if result.json()['failed'] == 0:
                break
        return result.text

    def __dequeue_results(self, global_results):
        """
        Dequeue the results stored in send_queue when using multiprocessing mode

        :param global_results: Result information summarized for every request
        :type global_results: HttpClientResult
        """
        while True:
            try:
                # Try to pop from send_queue within 1s
                local_results = self.result_queue.get(True, timeout=1)
                global_results.append(local_results)
            except queue.Empty:
                break
