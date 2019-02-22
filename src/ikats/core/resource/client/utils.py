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
import logging
import mimetypes
import socket

UTILS_LOGGER = logging.getLogger(__name__)

TDM_ROOT = 'http://%(host)s:%(port)s/TemporalDataManagerWebApp/webapi'

# List of templates used to build URL.
#
# * Key corresponds to the web app method to use
# * Value contains
#    * the pattern of the url to connect to
TEMPLATES = {

    # TEMPORAL DATA MANAGER
    # ---------------------

    'remove_ts': {
        'pattern': TDM_ROOT + '/ts/%(tsuid)s',
    },
    'extract_by_metric': {
        'pattern': TDM_ROOT + '/ts/extract/metric/%(metric)s',
    },
    'get_ts_list': {
        'pattern': TDM_ROOT + '/ts/tsuid',
    },
    'get_ts_meta': {
        'pattern': TDM_ROOT + '/ts/tsuid/%(tsuid)s',
    },
    'extract_by_tsuid': {
        'pattern': TDM_ROOT + '/ts/extract/tsuid',
    },
    'direct_extract_by_tsuid': {
        'pattern': 'http://%(host)s:%(port)s/api/query?start=%(sd)s&end=%(ed)s&tsuid=%(ts_info)s&ms=true',
    },
    'import_data': {
        'pattern': TDM_ROOT + '/ts/put/%(metric)s',
    },
    'get_fid': {
        'pattern': TDM_ROOT + '/metadata/funcId/%(tsuid)s',
    },
    'import_fid': {
        'pattern': TDM_ROOT + '/metadata/funcId/%(tsuid)s/%(fid)s',
    },
    'delete_fid': {
        'pattern': TDM_ROOT + '/metadata/funcId/%(tsuid)s',
    },
    'lookup_meta_data': {
        'pattern': TDM_ROOT + '/metadata/list/json',
    },
    'import_meta_data': {
        'pattern': TDM_ROOT + '/metadata/import/%(tsuid)s/%(name)s/%(value)s',
    },
    'update_meta_data': {
        'pattern': TDM_ROOT + '/metadata/%(tsuid)s/%(name)s/%(value)s',
    },
    'import_meta_data_file': {
        'pattern': TDM_ROOT + '/metadata/import/file',
    },
    'import_data_set': {
        'pattern': TDM_ROOT + '/dataset/import/%(data_set)s',
    },
    'get_data_set': {
        'pattern': TDM_ROOT + '/dataset/%(data_set)s',
    },
    'get_data_set_list': {
        'pattern': TDM_ROOT + '/dataset',
    },
    'remove_data_set': {
        'pattern': TDM_ROOT + '/dataset/%(data_set)s',
    },
    'deep_remove_data_set': {
        'pattern': TDM_ROOT + '/dataset/%(data_set)s?deep=true',
    },
    'search': {
        'pattern': TDM_ROOT + '/ts/lookup/%(metric)s',
    },
    'ts_match': {
        'pattern': TDM_ROOT + '/metadata/tsmatch',
    },
    'get_one_functional_identifier': {
        'pattern': TDM_ROOT + '/metadata/funcId/%(tsuid)s',
    },
    'search_functional_identifier_list': {
        'pattern': TDM_ROOT + '/metadata/funcId',
    },

    # NON TEMPORAL DATA MANAGER
    # -------------------------
    'add_process_data': {
        'pattern': TDM_ROOT + '/processdata/%(process_id)s',
    },
    'add_process_data_json': {
        'pattern': TDM_ROOT + '/processdata/%(process_id)s/JSON',
    },
    'add_process_data_any': {
        'pattern': TDM_ROOT + '/processdata?name=%(name)s&processId=%(process_id)s',
    },
    'get_process_data': {
        'pattern': TDM_ROOT + '/processdata/%(id)s',
    },
    'remove_process_data': {
        'pattern': TDM_ROOT + '/processdata/%(id)s',
    },
    'download_process_data': {
        'pattern': TDM_ROOT + '/processdata/id/download/%(id)s',
    },

    # FILE MANAGER
    # ------------
    'file_exists': {
        'pattern': 'http://%(host)s:%(port)s/',
    },
    'list_file': {
        'pattern': 'http://%(host)s:%(port)s/',
    },
    'write_file': {
        'pattern': 'http://%(host)s:%(port)s/',
    },
    'pull_file': {
        'pattern': 'http://%(host)s:%(port)s/',
    },
    'push_file': {
        'pattern': 'http://%(host)s:%(port)s/',
    },
    'read_file': {
        'pattern': 'http://%(host)s:%(port)s/',
    },
    'delete_file': {
        'pattern': 'http://%(host)s:%(port)s/',
    },
    'is_file': {
        'pattern': 'http://%(host)s:%(port)s/',
    },
    'is_folder': {
        'pattern': 'http://%(host)s:%(port)s/',
    },
    'is_empty': {
        'pattern': 'http://%(host)s:%(port)s/',
        'q_params': []
    },
    'get_absolute_path': {
        'pattern': 'http://%(host)s:%(port)s/',
    },

    # TABLES

    'list_tables': {
        'pattern': TDM_ROOT + '/table'
    },
    'create_table': {
        'pattern': TDM_ROOT + '/table'
    },
    'read_table': {
        'pattern': TDM_ROOT + '/table/%(name)s'
    },
    'delete_table': {
        'pattern': TDM_ROOT + '/table/%(name)s'
    },

}


def is_url_valid(address):
    """
    Check if address is a valid url

    :param address: string to parse
    :return: True if valid, False otherwise
    :raises TypeError: if address is not a string
    """
    if type(address) is not str:
        UTILS_LOGGER.error("address [%s] shall be a string", address)
        raise TypeError("address [%s] shall be a string" % address)

    return True


def close_files(json):
    """
    Closes the files opened with build_json_files method
    :param json: item built using build_json_files method
    :type json: dict or list
    """

    if type(json) is dict:
        # One file to handle
        json['file'].close()
    elif type(json) is list:
        # Multiple files
        for i in json:
            json[i][1][1].close()


def build_json_files(files):
    """
    Build the json files format to provide when sending files in a request

    :param files: file or list of files to use for building json format
    :type files: str OR list

    :return: the json to pass to request object
    :rtype: dict

    Single file return format
        | files = {'file': ('report.xls', open('report.xls', 'rb'), 'application/vnd.ms-excel', {'Expires': '0'})}

    Multiple files return format
        | files = [('images', ('foo.png', open('foo.png', 'rb'), 'image/png')),
        |          ('images', ('bar.png', open('bar.png', 'rb'), 'image/png'))]


    :raises TypeError: if file is not found
    :raises ValueError: if MIME hasn't been found for the file
    """

    if type(files) is str:

        # Only one file is provided
        working_file = files

        # Defines MIME type corresponding to file extension
        mime = mimetypes.guess_type(working_file)[0]
        if mime is None:
            UTILS_LOGGER.error("MIME type not found for file %s", working_file)
            raise ValueError("MIME type not found for file %s" % working_file)

        # Build results
        # results = {'file': (f, open(f, 'rb'), mime, {'Expires': '0'})}
        return {'file': open(working_file, 'rb')}

    elif type(files) is list:
        # Multiple files are provided
        results = []
        for working_file in files:
            # Defines MIME type corresponding to file extension
            mime = mimetypes.guess_type(working_file)[0]
            if mime is None:
                UTILS_LOGGER.error("MIME type not found for file %s", working_file)
                raise ValueError("MIME type not found for file %f" % working_file)
            # Build result
            results.append(('file', (working_file, open(working_file, 'rb'), mime)))
        return results

    elif files is None:
        # No file is provided -> No treatment
        return None

    else:
        # Handling errors
        UTILS_LOGGER.error("Files must be provided as str or list (got %s)", type(files))
        raise TypeError("Files must be provided as str or list (got %s)" % type(files))
