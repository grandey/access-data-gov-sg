#!/usr/bin/env python3

"""
get_data_gov_sg_met.py:
    Download meteorological station data for a specified month via the data.gov.sg APIs.

API key requirement:
    In order to use this script, an API key needs to be obtained via
    https://developers.data.gov.sg.

Usage:
    To download a specific month, specify the month (e.g. 2017_02):
        ./get_data_gov_sg_met.py 2017_02
    To download data from last month, just run the script with no command-line arguments:
        ./get_data_gov_sg_met.py
    This can be performed automatically on e.g. the 2nd day of each month using crontab:
        0 0 2 * * tar -zcf <path_to_here>/get_data_gov_sg_met.py
    
Output files:
    Gzipped CSV files, corresponding to different variables, will be saved in data_gov_sg_met_v1/
    The file naming convention is as follows:
        data_gov_sg_met_v1/<variable>_<yyyy-mm>_c<today>.csv.gz
    where <today> is the date on which the file was created.
    For example,
        data_gov_sg_met_v1/wind-speed_2017-02_c20170526.csv.gz

Information about input data:
    For information about the input data used to derive the output CSV files, please see
    https://developers.data.gov.sg, https://data.gov.sg/open-data-licence, and
    https://data.gov.sg/api-terms.
    
Author:
    Benjamin S. Grandey, 2017
"""

import calendar
import os
import pandas as pd
import requests
import sys
import time

# Get my API keys
from my_api_keys import my_api_dict
# Note: this module, containing my API keys, will not be shared via GitHub
# You can obtain your own API key(s) by registering at https://developers.data.gov.sg
my_key = my_api_dict['data.gov.sg']  # API key for data.gov.sg


# Output directory
here = os.path.abspath(os.path.dirname(__file__))
data_dir = os.path.join(here, 'data_gov_sg_met_v1')
# If directory does not exist, create it
if not os.path.exists(data_dir):
    os.makedirs(data_dir)
    print('Created {}'.format(data_dir))


def retrieve_data_via_api(variable, dt, n_attempts=10):
    """
    Function to attempt to retrieve data for a specific datetime.
    
    Args:
        variable: string of variable name used by API (e.g. 'rainfall')
        dt: pd.datetime, corresponding to 'date_time' in the API
        n_attempts: number of attempts to retry if API connection fails
        
    Returns:
        pd.DataFrame containing data (if successful), or None
    """
    try:
        # Try to connect to API
        r = requests.get('https://api.data.gov.sg/v1/environment/{}'.format(variable),
                         headers={'api-key': my_key},
                         params={'date_time': dt.strftime('%Y-%m-%dT%H:%M:%S')},
                         timeout=30)
        if r.status_code == 200:
            # If API connection was successful, load data into DataFrame, unless no data present
            if len(r.json()['items'][0]['readings']) >= 1:
                result = pd.DataFrame(r.json()['items'][0]['readings'])
                if variable == 'pm25':  # necessary due to diff in pm25 API return format
                    result = result.reset_index()
                    result = result.rename(columns={'index': 'region'})
                result['timestamp_sgt'] = pd.to_datetime(r.json()['items'][0]['timestamp']
                                                         .split('+')[0])
            else:
                result = None
        else:
            # If API query failed, sleep one minute, then retry recursively (up to n_attempts)
            if n_attempts > 1:
                print('    dt = {}, r.status_code = {}, (n_attempts-1) = {}. '
                      'Retrying in 60s.'.format(dt, r.status_code, (n_attempts-1)))
                time.sleep(60)
                result = retrieve_data_via_api(variable, dt, n_attempts=(n_attempts-1))
            else:
                print('    dt = {}, r.status_code = {}, (n_attempts-1) = {}. '
                      'FAILED TO RETRIEVE DATA.'.format(dt, r.status_code, (n_attempts-1)))
                result = None
        r.close()
    except (requests.exceptions.SSLError, requests.exceptions.ConnectionError,
            requests.exceptions.ConnectTimeout):
        # If connection failed, sleep one minute, then retry recursively (up to n_attempts)
        if n_attempts > 1:
            print('    dt = {}, error = {}, (n_attempts-1) = {}. '
                  'Retrying in 60s.'.format(dt, sys.exc_info()[0], (n_attempts-1)))
            time.sleep(60)
            result = retrieve_data_via_api(variable, dt, n_attempts=(n_attempts-1))
        else:
            print('    dt = {}, error = {}, (n_attempts-1) = {}. '
                  'FAILED TO CONNECT.'.format(dt, sys.exc_info()[0], (n_attempts-1)))
            result = None
    return result


def download_month(variable, yyyy, mm):
    """
    Function to attempt to retrieve data for a specific month.

    Args:
        variable: string of variable name used by API (e.g. 'rainfall')
        yyyy: string containing year (e.g. '2017')
        mm: string containing month (e.g. '05')

    Output file:
        CSV file:
            data_gov_sg_met_v1/<variable>_<yyyy-mm>_c<today>.csv
        where <today> is today's date.
    """
    print('variable = {}, yyyy = {}, mm = {}'.format(variable, yyyy, mm))
    # Number of days in month
    ndays = calendar.monthrange(int(yyyy), int(mm))[1]  # supports leap years
    # Datetime range to search through - at 5-min intervals
    datetime_range = pd.date_range('{}-{}-01 00:00:00'.format(yyyy, mm),
                                   periods=((ndays * 24 * 12) + 1),
                                   freq='5 min')
    # Loop over datetimes
    for dt, i in zip(datetime_range, range(len(datetime_range))):
        # Attempt to retrieve data via API
        temp_df = retrieve_data_via_api(variable, dt)
        # If data available and timestamp indicates correct month, then append to DataFrame df
        if temp_df is not None:
            if temp_df['timestamp_sgt'].loc[0].month == int(mm):  # querying 00:00 on 1st day may
                try:                                              # may return 23:59 on prev. day
                    df = df.append(temp_df, ignore_index=True)
                except UnboundLocalError:  # 1st time, initialise df
                    df = temp_df
        # Indicate progress
        perc = i / ((ndays * 24 * 12) + 1) * 100  # percentage progress
        print('    {:000.1f}%'.format(perc), end='\r', flush=True)
    print()  # start new line
    # Print summary of number of records
    print('    {} records'.format(len(df)))
    # Remove duplicates
    df = df.drop_duplicates()
    print('    {} records after removing duplicates'.format(len(df)))
    # Save DataFrame to CSV file
    out_filename = '{}/{}_{}_{}_c{}.csv.gz'.format(data_dir, variable, yyyy, mm,
                                                   pd.datetime.today().strftime('%Y%m%d'))
    df.to_csv(out_filename, index=False, compression='gzip')
    print('    Written {}'.format(out_filename))
    return 0


if __name__ == '__main__':
    # Year and month to get data for
    try:
        yyyy, mm = sys.argv[1].split('_')  # if specified via command-line
    except IndexError:  # otherwise get data for last month
        month_ago = (pd.datetime.today() - pd.Timedelta(1, 'M'))  # ~1 month ago (not exact)
        yyyy, mm = month_ago.strftime('%Y_%m').split('_')
    # Loop over variables
    for variable in ['rainfall', 'wind-speed', 'wind-direction', 'air-temperature',
                     'relative-humidity', 'pm25']:
        download_month(variable, yyyy, mm)
