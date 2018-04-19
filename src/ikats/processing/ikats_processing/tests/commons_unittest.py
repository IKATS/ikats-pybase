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


class CommonsUnittest(object):
    """
    Mutual services about TU in ikats_django project
    """

    TU_KO_LIST = []
    TU_OK_LIST = []
    SUMMARY = {'tu ok': TU_OK_LIST, 'tu failed': TU_KO_LIST}

    @staticmethod
    def save_tu_failure(tu_name):
        """
        Records the specified tu name in the CommonsUnittest.TU_KO_LIST used by write_tu_diagnostic service
        :param tu_name:
        :type tu_name:
        """
        CommonsUnittest.TU_KO_LIST.append(tu_name)

    @staticmethod
    def save_tu_success(tu_name):
        """
        Records the specified tu name in the CommonsUnittest.TU_OK_LIST used by write_tu_diagnostic service
        :param tu_name:
        :type tu_name:
        """
        CommonsUnittest.TU_OK_LIST.append(tu_name)

    @classmethod
    def write_tu_diagnostic(cls):
        """
        Writes the diagnostic summary on the executed tests.
        :param cls:
        :type cls:
        """
        # Backup of effective level of TU
        effective_level = cls.logger().getEffectiveLevel()
        # Force INFO level: logs INFO+ERROR below
        cls.logger().setLevel(logging.INFO)
        cls.logger().info("#########################################################################")
        cls.logger().info("#                  TU summary                                           #")
        cls.logger().info("#-----------------------------------------------------------------------#")
        cls.logger().info("#- Failed tests:                                                        #")
        cls.logger().info("#---------------                                                        #")
        for msg in CommonsUnittest.TU_KO_LIST:
            cls.logger().info("# - %s", msg)
        cls.logger().info("#-----------------------------------------------------------------------#")
        cls.logger().info("#- Successful tests:                                                    #")
        cls.logger().info("#-------------------                                                    #")
        for msg in CommonsUnittest.TU_OK_LIST:
            cls.logger().info("# - %s", msg)
        cls.logger().info("#########################################################################")

        # Resets the effective level
        cls.logger().setLevel(effective_level)

    @classmethod
    def init_logger(cls):
        """
        Updates the logger according to Test class
        :param cls: Test class
        :type cls: CommonsCatalogueTests subclass
        """
        cls.tu_logger = logging.getLogger(cls.__module__ + "." + cls.__name__)
        cls.set_verbose(logging.ERROR)

    @classmethod
    def set_verbose(cls, verbose):
        """
        Explicit setter of the accepted log level for the TU logger:
          - logging.ERROR is the default value: the usual value for PIC + clusters
          - other values may be used for devs, or specific analysis:
            logging.INFO, logging.DEBUG, logging.WARN, logging.CRITICAL, logging.FATAL

        Note: this level will not be applied in forced logs from start() or end() class methods
        :param cls:
        :type cls:
        :param verbose: flag for verbose mode
        :type verbose: constant from logging
        """
        cls.tu_logger.setLevel(verbose)

    @classmethod
    def logger(cls):
        """
        Gets the logger on the unit-test class
        :param cls:
        :type cls:
        """
        # tu_logger field may be not initialized if we forget to call init_logger.
        #    solution one: define it statically ?
        #         no: we want to manage 1 logger per TU so static def will not work.
        #    => solution retained: raise exception in order to correct the TU
        #       - some tests are done: see test_commons_unittest
        try:
            return cls.tu_logger
        except Exception:
            msg = "Not initialized: CommonsUnittest logger: correct by calling initially init_logger()"
            raise Exception(msg)

    @classmethod
    def info(cls, msg):
        """
        Send info level message to the logger.
        :param cls:
        :type cls:
        :param msg:
        :type msg:
        """
        cls.logger().info(msg)

    @classmethod
    def error(cls, msg):
        """
        Send error level message to the logger
        :param cls:
        :type cls:
        :param msg:
        :type msg:
        """
        cls.logger().error(msg)

    @classmethod
    def warn(cls, msg):
        """
        Send warning level message to the logger
        :param cls:
        :type cls:
        :param msg:
        :type msg:
        """
        cls.logger().warning(msg)

    @classmethod
    def start(cls, tu_name):
        """
        Writes the header of the unit-test
        :param cls:
        :type cls:
        :param tu_name:
        :type tu_name:
        """
        # Backup of effective level of TU
        effective_level = cls.logger().getEffectiveLevel()
        # Force INFO level
        cls.logger().setLevel(logging.INFO)
        cls.logger().info("------------------------------------------------------------------------")
        cls.logger().info("--- Starting " + tu_name)
        cls.logger().info("---")
        # Resets the effective level
        cls.logger().setLevel(effective_level)

    @classmethod
    def end(cls, tu_name, error=False):
        """
        Writes the footer of the unit-test, with a conclusion success or failed.
        :param cls:
        :type cls:
        :param tu_name:
        :type tu_name:
        :param error:
        :type error:
        """
        # Backup of effective level of TU
        effective_level = cls.logger().getEffectiveLevel()
        # Force INFO level: logs INFO+ERROR below
        cls.logger().setLevel(logging.INFO)
        cls.logger().info("---")
        if not error:
            cls.logger().info("--- Successfully Ended: " + tu_name)
            CommonsUnittest.TU_OK_LIST.append(tu_name)
        else:
            cls.error("--- Failed: " + tu_name)
            CommonsUnittest.TU_KO_LIST.append(tu_name)
        cls.logger().info("------------------------------------------------------------------------")
        # Resets the effective level
        cls.logger().setLevel(effective_level)

    @classmethod
    def except_ko(cls, tu_name, error):
        """
        Code to be called in the main except block of TU:
          - logs the caught error
          - calls the classmethod end() for TU in KO context
            - adds "ko" footer
            - memorizes this TU ko status: required by write_tu_diagnostic()
          - raises the error

        :param cls:
        :type cls:
        :param tu_name:
        :type tu_name:
        :param error:
        :type error:
        """
        cls.logger().exception(error)
        cls.end(tu_name, True)
        # could be Exception or AssertionError
        raise error

    @classmethod
    def commons_tear_down_class(cls):
        """
        Additional processing which ought to be called by the tearDownClass() classmethod in Django TU:
          - write a brief diagnostic summary about all executed tests
        :param cls:
        :type cls:
        """
        # Note: the naming of method is based on the unittest naming "tearDownClass"
        # => that is why there is a mixture between CamL case and IKATS standard snake_case
        cls.write_tu_diagnostic()
