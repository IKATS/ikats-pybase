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
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import migrations, models
from apps.algo.catalogue.migrations.data import init_data_db


def create_algo_catalogue(apps, schema_editor):
    """
    The data migration activating init_db_V2.create_algo_catalogue():
      - restricted to the databases configured with sqlite3: DEV or PÏC
      - in other words: cluster INT or PREPROD are not concerned,
      assuming that Postgres database have been already migrated
    About django data migrations:
      - see https://docs.djangoproject.com/en/1.8/topics/migrations/
    :param apps: django param required by Data migration Operation interface
    :type apps: AppConfig
    :param schema_editor: django param required by Data migration Operation interface
    :type schema_editor: SchemaEditor
    """
    from django.conf import settings as djsettings
    # migration is restricted to the DEV environment ... in order to initialize the catalogue
    if djsettings.DATABASES['default']['ENGINE'] == "django.db.backends.sqlite3":
        init_data_db.create_algo_catalogue()


class Migration(migrations.Migration):
    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AlgorithmDao',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('label', models.CharField(help_text='readable label adapted to the display', max_length=60)),
                ('desc', models.TextField(help_text='full description', null=True)),
                ('name', models.CharField(help_text='readable name', max_length=60)),
            ],
            options={
                'ordering': ['name'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='FunctionalFamilyDao',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('label', models.CharField(help_text='readable label adapted to the display', max_length=60)),
                ('desc', models.TextField(help_text='full description', null=True)),
                ('name', models.CharField(help_text='readable name', max_length=60)),
            ],
            options={
                'ordering': ['name'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ImplementationDao',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('label', models.CharField(help_text='readable label adapted to the display', max_length=60)),
                ('desc', models.TextField(help_text='full description', null=True)),
                ('name', models.CharField(help_text='readable name', max_length=60, unique=True)),
                ('execution_plugin', models.CharField(help_text='the execution plugin', max_length=100, null=True)),
                ('library_address',
                 models.CharField(help_text='the library address is a reference to the executable program',
                                  max_length=250, null=True)),
                ('visibility', models.BooleanField(help_text='visibility in ikats operators', default=True)),
                ('algo', models.ForeignKey(to='catalogue.AlgorithmDao', null=True)),
            ],
            options={
                'ordering': ['name'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ProfileItemDao',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('label', models.CharField(help_text='readable label adapted to the display', max_length=60)),
                ('desc', models.TextField(help_text='full description', null=True)),
                ('name', models.CharField(help_text='readable name', max_length=60)),
                ('direction', models.PositiveSmallIntegerField(choices=[(0, 'Input'), (1, 'Output')])),
                ('dtype', models.PositiveSmallIntegerField(choices=[(0, 'Parameter'), (1, 'Argument')])),
                ('order_index', models.PositiveSmallIntegerField(default=0)),
                ('data_format', models.TextField(verbose_name='expected data format', null=True)),
                ('domain_of_values', models.TextField(verbose_name='domain of values', null=True)),
                ('default_value',
                 models.TextField(help_text='optional: string encoding the default value defined in the catalogue',
                                  verbose_name='default value', null=True)),
            ],
            options={
                'ordering': ['name'],
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='implementationdao',
            name='input_desc_items',
            field=models.ManyToManyField(related_name='inputs', to='catalogue.ProfileItemDao'),
        ),
        migrations.AddField(
            model_name='implementationdao',
            name='output_desc_items',
            field=models.ManyToManyField(related_name='outputs', to='catalogue.ProfileItemDao'),
        ),
        migrations.AddField(
            model_name='algorithmdao',
            name='family',
            field=models.ForeignKey(to='catalogue.FunctionalFamilyDao'),
        ),
        migrations.RunPython(create_algo_catalogue),
    ]
