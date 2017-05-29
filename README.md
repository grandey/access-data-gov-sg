# access-data-gov-sg

## Purpose
Exploration, downloading and post-processing of data from [data.gov.sg](https://data.gov.sg).

## Software
1. [explore_data_gov_sg_api.ipynb](explore_data_gov_sg_api.ipynb) - initial exploration of the
data.gov.sg APIs for meteorological station data.
1. [get_data_gov_sg_met.py](get_data_gov_sg_met.py) - download meteorological station data for a
specified month via the data.gov.sg APIs, and save in gzipped CSV files.

The software contained in this repository is released under the MIT License.

## Data
[data_gov_sg_met_v1/](data_gov_sg_met_v1/) contains gzipped CSV files produced by
[get_data_gov_sg_met.py](get_data_gov_sg_met.py).
The file naming convention is as follows:
    `data_gov_sg_met_v1/<variable>_<yyyy-mm>_c<today>.csv.gz`
where <today> is the date on which the file was created. For example,
    `data_gov_sg_met_v1/wind-speed_2017-02_c20170526.csv.gz`.

Based on [explore_data_gov_sg_api.ipynb](explore_data_gov_sg_api.ipynb), the important metadata for
each variable is as follows:
Variable | reading_type | reading_unit | other
---------|--------------|--------------|------
rainfall | TB1 Rainfall 5 Minute Total F | mm |
wind-speed | Wind Speed AVG(S)10M M1M | knots |
wind-direction | Wind Dir AVG (S) 10M M1M | degrees |
air-temperature | DBT 1M F | deg C |
relative-humidity | RH 1M F | percentage |
pm25 | | | pm25_one_hourly

For further information about the input data used to derive the output CSV files, please see
[developers.data.gov.sg](https://developers.data.gov.sg).
The [Singapore Open Data License](https://data.gov.sg/open-data-licence) v1.0 states that one
*"can use, access, download, copy, distribute, transmit, modify and adapt the datasets [provided by
data.gov.sg], or any derived analyses or applications, whether commercially or non-commercially"*
provided that attribution is given to data.gov.sg.
The License (v1.0) also states that one
*"must not Use the datasets in a way that suggests any official status or that an Agency endorses
you or your Use of the datasets"* - this GitHub repository has *no official status*.
For further information, please see:
1. The [Singapore Open Data License](https://data.gov.sg/open-data-licence); *and*
1. The [API Terms of Service](https://data.gov.sg/api-terms).

## Author
Benjamin S. Grandey, 2017
