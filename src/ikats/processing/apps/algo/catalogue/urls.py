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
from apps.algo.catalogue.views import ws_catalogue

# Since [#141671]: following services are available:
# --------------------------------------------------
# GET /catalog/families returns NORMAL view of all families ...
#
# GET /catalog/families/{family_name} returns  NORMAL view of specified family
#
# GET /catalog/implementations returns SUMMARY view of visible implementations ...
#    Note: this SUMMARY is ignoring some implementations reserved to TU: under family  named Internal_Test_IKATS
#
# GET /catalog/implementations/{implementation name} returns NORMAL view of specified implementation
# GET /catalog/implementations/{internal id as integer} returns NORMAL view of specified implementation
#
# See more details in ws_catalogue: usage of additional query params ...
#
urlpatterns = [url(r'^implementations/(?P<name>[A-z]\w+)/?$',
                   ws_catalogue.get_implementation_by_name,
                   name="get_implementation_by_name"),
               url(r'^families/(?P<name>[A-z]\w+)/?$',
                   ws_catalogue.get_family_by_name,
                   name="get_family_by_name"),
               url(r'^algorithms/(?P<name>[A-z]\w+)/?$',
                   ws_catalogue.get_algorithm_by_name,
                   name="get_algorithm_by_name"),
               # DEPRECATED service before [#141671]: with database key
               url(r'^implementations/(?P<id_implementation>[0-9]+)/?$',
                   ws_catalogue.get_implementation,
                   name="getWsCatImplementation"),
               # search list of implementations
               url(r'^implementations/?$',
                   ws_catalogue.get_implementation_list,
                   name="get_implementation_list"),
               # search list of algorithms
               url(r'^algorithms/?$',
                   ws_catalogue.get_algorithm_list,
                   name="get_algorithm_list"),
               # search list of implementations
               url(r'^families/?$',
                   ws_catalogue.get_family_list,
                   name="get_family_list"),
               url(r'^export/implementations/?$',
                   ws_catalogue.export_all_implementations,
                   name="export_all_implementations")]
