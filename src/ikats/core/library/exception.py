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


class IkatsException(Exception):
    """
    Exception raised by IKATS server.

    Generic exception: use more precise exception when possible: see other exceptions defined in this module.
    """

    def __init__(self, msg, cause=None):
        """
        Constructor
        :param msg: error message
        :type msg: str
        """
        super(IkatsException, self).__init__(msg)
        self.__cause = cause

    def __str__(self):
        if self.__cause is not None:
            return super(IkatsException, self).__str__() + " with cause=" + str(self.__cause)
        else:
            return super(IkatsException, self).__str__()


class IkatsInputError(IkatsException):
    """
    Error raised when one argument incorrect.

    - Use more precise exception if possible: IkatsInputTypeError or IkatsInputContentError.
    """

    def __init__(self, msg):
        """
        Constructor
        :param msg: error message
        :type msg: str
        """
        super(IkatsInputError, self).__init__(msg)


class IkatsNotFoundError(IkatsException):
    """
    Error raised when a resource is not found in the server

    """

    def __init__(self, msg, cause=None):
        """
        Constructor
        :param msg: error message
        :type msg: str
        """
        super(IkatsNotFoundError, self).__init__(msg, cause)


class IkatsInputTypeError(IkatsInputError):
    """
    Error raised when one argument type is incorrect.

    """

    def __init__(self, msg):
        """
        Constructor
        :param msg: error message
        :type msg: str
        """
        super(IkatsInputTypeError, self).__init__(msg)


class IkatsInputContentError(IkatsInputError):
    """
    Error raised when one argument content is incorrect.
    """

    def __init__(self, msg):
        """
        Constructor
        :param msg: error message
        :type msg: str
        """
        super(IkatsInputContentError, self).__init__(msg)


class IkatsConflictError(IkatsException):
    """
    Error raised when a conflict occurred for a resource in the server

    """

    def __init__(self, msg, cause=None):
        """
        Constructor
        :param msg: error message
        :type msg: str
        """
        super(IkatsConflictError, self).__init__(msg, cause)
