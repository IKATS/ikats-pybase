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

from django.conf.urls import url
from apps.algo.custom.views import ws_custom

# Configuration file for URL dispatching on custom django application
# ===================================================================
# For detailed description of Rest API refer to:
#  - doc/api_rest/api_rest_algo.yaml
#  - doc/api_rest/README.md
#
# Since [#139805]: following services are available:
# --------------------------------------------------
# Note: for resource customized algo we will manage two information levels: NORMAL or SUMMARY
# (whereas catalogue manages 3 levels : SUMMARY, NORMAL, DETAIL)
#
#
# READ services
# -------------
# GET /custom_algos/ returns JSON encoded SUMMARY view of
#   - all customized_algo, when no query params are passed in url
#   - or filtered search according to defined query parameters named name, label or else desc
#
# GET /custom_algos/{id} returns JSON encoded NORMAL view of specified customized algo
#
# GET /custom_algos/on_implementation/{id} returns JSON encoded SUMMARY view of customized algo
#     customizing implementation with id
#
# CREATE service
# --------------
# POST /custom_algos/ request with
#   - JSON encoded query content as NORMAL view of created customized algo
#   - JSON encoded response as
#                        - either NORMAL view of created customized algo
#                        - or diagnostic: about check status messages
# UPDATE service
# --------------
# PUT /custom_algos/{id} request JSON encoded content updating the resource customized algo with id=...
#   - JSON encoded query content as NORMAL view of updated customized algo
#   - JSON encoded response as
#                        - either NORMAL view of updated customized algo
#                        - or diagnostic: about check status messages
#
# DELETE service
# --------------
# DELETE /custom_algos/{id} simple query without body content, and with
#    - JSON encoded response as
#                       - either NORMAL view of deleted customized algo
#                       - or diagnostic about deleting failure
#
# Deduced URL patterns from Rest services
# ---------------------------------------
# pattern_custom_algos_with_id: /custom_algos/{id}
#   | => function ws_custom.pattern_custom_algos_with_id will
#   | call the good service according to GET/PUT/DELETE http method
#
# pattern_custom_algos_dummy: /custom_algos
#   | => function ws_custom.pattern_custom_algos_dummy will
#   | call the good service according to GET/POST http method
#
# last pattern required: /custom_algos/on_implementation/{id}
#   | => function ws_custom.find_custom_algo_for_implementation
#   | is directly plugged to unique service with GET http method
#
#
# See more details in ws_custom: usage of additional query params ...
#

urlpatterns = [

    url(r'^custom_algos/?$',
        ws_custom.pattern_custom_algos_dummy,
        name="pattern_custom_algos_dummy"),
    url(r'^custom_algos/(?P<customized_algo_id>[0-9]+)/?$',
        ws_custom.pattern_custom_algos_with_id,
        name="pattern_custom_algos_with_id"),
]
