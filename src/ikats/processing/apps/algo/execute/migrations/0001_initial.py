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
    Maxime PERELMUTER <maxime.perelmuter@c-s.fr>
"""
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ExecutableAlgoDao',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('creation_date',
                 models.DecimalField(max_digits=18, help_text='Creation EPOCH date of exec algo: decimal in secs',
                                     decimal_places=8)),
                ('start_execution_date', models.DecimalField(
                    max_digits=18,
                    help_text='Starting execution date: EPOCH date of exec algo: decimal in secs',
                    null=True, decimal_places=8)),
                ('end_execution_date', models.DecimalField(
                    max_digits=18,
                    help_text='Ending execution date: EPOCH date of exec algo: decimal in secs',
                    null=True, decimal_places=8)),
                ('state', models.IntegerField(
                    default=0,
                    help_text='State: INIT, RUN, SUCCESS, ALGO_KO, ENGINE_KO, resp encoded by 0, 1, 2, 3, 4)')),
            ],
        ),
    ]
