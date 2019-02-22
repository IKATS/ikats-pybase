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
from django.conf.urls import patterns, url

urlpatterns = patterns(
    'apps.algo.execute.views',
    # runalgo: launches an algorithm execution with the input parameters
    # - url = ".../ikats/algo/execute/runalgo/-algoId-"
    # - web service with POST http request with parameters:
    #   input Json parameter { ... }
    #   output Json { ... }
    # See doc: IKATS_Spec_ModulesSpecifiques part. Executer
    #
    url(r'^runalgo/([A-z]\w+)$', 'algo.run', name="algo_run"),

    # getstatus: retrieves an execution state for a given processid
    # - url = ".../ikats/algo/execute/getstatus/-processid-"
    # - web service with POST http request with parameters:
    #   input Json parameter { ... }
    #   output Json { ... }
    # See doc: IKATS_Spec_ModulesSpecifiques part. Executer
    #
    url(r'^getstatus/(\d+)$', 'algo.getstatus', name="algo_getstatus")
)
