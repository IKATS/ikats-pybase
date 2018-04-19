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


class Singleton(type):
    """
    Metaclass Singleton: my_class = my_metaclass()
    is calling the _new_ method below

    Use (python3):
    class MyClass([BaseClass,] metaclass=Singleton):
        pass
    """

    # see http://stackoverflow.com/questions/6760685/creating-a-singleton-in-python

    _instances = {}

    # Note of coder: ignore error possibily raised by Pydev or other:
    #     Method '__call__ - ikats.core.library.singleton' should have self as first parameter
    def __call__(cls, *args, **kwargs):
        """
        Hook creating a unique instance of cls.

        Note: cls is a class which declares its metaclass: Singleton
        :param cls:
        :type cls:
        """
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
