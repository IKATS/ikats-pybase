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
from apps.algo.execute.models import ExecutableAlgoDao

# RemovedInDjango19Warning: Model class apps.algo.execute.models.orm.algo.ExecutableAlgoDao
# doesn't declare an explicit app_label and either isn't in an application in INSTALLED_APPS or
# else was imported before its application was loaded. This will no longer be supported in Django 1.9.

# Break the status of running algorithms to have ENGINE_KO
try:
    COUNT = ExecutableAlgoDao.objects.filter(state=1).update(state=4)
    print("%s Running algorithms have been stopped since this new deployment" % COUNT)
except Exception:
    print("No algorithm to stop")
