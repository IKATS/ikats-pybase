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
"""ikats_processing URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin

from django.conf import settings
from apps.algo.custom.views import ws_custom
from ikats_processing.core.resource_config import ResourceClientSingleton
urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^ikats/algo/custom/', include('apps.algo.custom.urls')),
    url(r'^ikats/algo/catalogue/', include('apps.algo.catalogue.urls')),
    url(r'^ikats/algo/execute/', include('apps.algo.execute.urls')),
    url(r'^ikats/algo/implementations/(?P<implementation_id>[0-9]+)/custom_algos/?$',
        ws_custom.find_custom_algos_for_implem,
        name="shortcut_find_custom_algos_for_implementation"),
]

# here: settings is an object which gathers properties defined from the
# settings module defined in the buildout: see run_install.sh which defines the good module
#
if settings.IKATS_RESOURCE_SERVER:
    ResourceClientSingleton.singleton_init(
        host=settings.IKATS_RESOURCE_SERVER['HOST'], port=settings.IKATS_RESOURCE_SERVER['PORT'])
