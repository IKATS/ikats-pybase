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
from apps.algo.catalogue.models.ws.element import ElementWs
from apps.algo.catalogue.models.business.algorithm import Algorithm
from ikats.core.json_util.rest_utilities import LevelInfo


class AlgorithmWs(ElementWs):
    """
    WS resource: AlgorithmWs wraps the Algorithm business object

    This WS resource is the model for Web services about Algorithm,
    masking some internal information of business model Implementation.
    AlgorithmWs is also used by the templates generating HTML views on Algorithm
    """

    def __init__(self, business_obj):
        """
        Constructor
        """
        super(AlgorithmWs, self).__init__(business_obj)

        assert (isinstance(business_obj, Algorithm)), \
            "Expects Algorithm type for argument business_obj in AlgorithmWs constructor"

    def to_dict(self, level=LevelInfo.NORMAL):
        """
        :param level: level of details, optional, default is NORMAL
        :type level: enum value ikats.core.json.rest_utilities.LevelInfo
        :return: a dictionary Json-serializable resource ImplementationWs
        :rtype: dict
        """
        my_family = None
        if self.model_business.family:
            my_family = self.model_business.family.name

        resource = {"id": self.model_business.db_id,
                    "family": my_family}
        self.add_element_properties_to_dict(completed_impl_dict=resource, element=None, level=level)
        return resource
