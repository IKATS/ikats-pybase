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
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('catalogue', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomizedAlgoDao',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('label', models.CharField(help_text='readable label adapted to the display', max_length=60)),
                ('desc', models.TextField(help_text='full description', null=True)),
                ('name', models.CharField(help_text='readable name', max_length=60)),
                ('ref_implementation',
                 models.ForeignKey(to='catalogue.ImplementationDao', related_name='custom_algo_set')),
            ],
            options={
                'ordering': ['name'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CustomizedParameterDao',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('edited_value', models.TextField(help_text='edited value (text encoded)')),
                ('is_aliased', models.BooleanField(default=False, help_text='flag is aliased')),
                ('custom_algo', models.ForeignKey(to='custom.CustomizedAlgoDao', related_name='custom_parameters_set')),
                ('ref_profile_item',
                 models.ForeignKey(to='catalogue.ProfileItemDao', related_name='custom_values_set')),
            ],
        ),
    ]
