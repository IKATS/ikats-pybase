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
# Required for Django inspection of ORM layer !!!
from apps.algo.catalogue.models.orm.algorithm import AlgorithmDao
from apps.algo.catalogue.models.orm.element import ElementDao
from apps.algo.catalogue.models.orm.family import FunctionalFamilyDao
from apps.algo.catalogue.models.orm.implem import ImplementationDao
