# ![IKATS Logo](https://ikats.github.io/img/Logo-ikats-icon.png) IKATS pybase


![Docker Automated build](https://img.shields.io/docker/automated/ikats/pybase.svg)
![Docker Build Status](https://img.shields.io/docker/build/ikats/pybase.svg)
![MicroBadger Size](https://img.shields.io/microbadger/image-size/ikats/pybase.svg)

**An overview of IKATS global architecture is available [here](https://github.com/IKATS/IKATS)**

This component, developed in python, is the core of IKATS python part.
It is directly used by algorithms implementations to access data to compute (read/write).
It is composed of:
 * a RESTful API to access to the data model (datasets, functional identifiers, metadata, tables, time series, process data) through ikats-datamodel component
 * an execution engine for IKATS algorithms
 * an access to algorithms catalog

Some examples of use of IKATS API:
```bash
from ikats.core.resource.api import IkatsApi
# retrieving metadata for a list of tsuid
meta_list = IkatsApi.md.read(tsuid_list)
# Creating new reference in database for new timeseries
IkatsApi.ts.create_ref(func_id)
# Importing time series data in database
IkatsApi.ts.create(fid=fid, data=data, generate_metadata=True, sparkified=True)
# Retrieve imported number of points from database
qual_nb_points = IkatsApi.ts.nb_points(tsuid=tsuid)
# Inherit metadat from parent
IkatsApi.ts.inherit(tsuid, tsuid_origin)
```
