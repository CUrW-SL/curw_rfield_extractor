#!/home/uwcc-admin/curw_rfield_extractor/venv/bin/python3
import traceback
import numpy as np
import os
import json
from datetime import datetime, timedelta
import time
import sys
import getopt
import pandas as pd


from db_adapter.base import get_Pool, destroy_Pool

from db_adapter.curw_fcst.source import get_source_id, add_source
from db_adapter.curw_fcst.variable import get_variable_id, add_variable
from db_adapter.curw_fcst.unit import get_unit_id, add_unit, UnitType
from db_adapter.curw_fcst.station import StationEnum, get_station_id, add_station, get_wrf_stations
from db_adapter.curw_fcst.timeseries import Timeseries
from db_adapter.constants import COMMON_DATE_TIME_FORMAT
from db_adapter.constants import (
    CURW_FCST_DATABASE, CURW_FCST_PASSWORD, CURW_FCST_USERNAME, CURW_FCST_PORT,
    CURW_FCST_HOST,
)

from db_adapter.logger import logger

SRI_LANKA_EXTENT = [79.5213, 5.91948, 81.879, 9.83506]
KELANI_BASIN_EXTENT = [79.6, 6.6, 81.0, 7.4]


email_content = {}

local_output_root_dir = '/home/uwcc-admin/wrf_rfields'
d03_kelani_basin_rfield_home = ''
d03_rfield_home = ''
d01_rfield_home = ''

d03_kelani_basin_bucket_rfield_home = ''
d03_bucket_rfield_home = ''
d01_bucket_rfield_home = ''


def usage():
    usageText = """
    Usage: ./gen_active_stations_rfields.py -c [config_file_path] -d [wrf_root_directory] -r [gfs_run] -H [gfs_data_hour]
    -s [wrf_system] -D [date] 

    -h  --help          Show usage
    -c  --config        Config file name or path. e.g: "wrf_config.json"
    -d  --dir           WRF root directory. e.g.: "/mnt/disks/wrf_nfs/wrf"
    -r  --run           GFS run. e.g: d0 (for yesterday gfs data), d1 (for today gfs data) 
    -H  --hour          GFS data hour. e.g: 00,06,12,18
    -s  --wrf_systems   List of WRF Systems. e.g.: A,C,E,SE
    -D  --date          Run date. e.g.: 2019-10-07 (date of the directory containing the wrf output to be used)

    """
    print(usageText)


def read_attribute_from_config_file(attribute, config):
    """
    :param attribute: key name of the config json file
    :param config: loaded json file
    :return:
    """

    if attribute in config and (config[attribute] != ""):
        return config[attribute]
    else:
        msg = "{} not specified in config file.".format(attribute)
        logger.error(msg)
        email_content[datetime.now().strftime(COMMON_DATE_TIME_FORMAT)] = msg
        sys.exit(1)


def list_of_lists_to_df_first_row_as_columns(data):
    """

    :param data: data in list of lists format
    :return: equivalent pandas dataframe
    """
    return pd.DataFrame.from_records(data[1:], columns=data[0])


def write_to_file(file_name, data):
    with open(file_name, 'w+') as f:
        f.write('\n'.join(data))


def makedir_if_not_exist(dir_path):
    try:
        os.makedirs(dir_path)
    except FileExistsError:
        # directory already exists
        pass


# def remove_all_files(dir):
#     os.system("rm -f {}/*".format(dir))
#
#
# def zip_folder(source, destination):
#     os.system("tar -C {} -czf {}.tar.gz {}".format('/'.join(source.split('/')[:-1]), destination, source.split('/')[-1]))


def prepare_active_obs_stations_based_rfield(pool, tms_meta, config_data):

    for wrf_system in config_data['wrf_system_list']:
        source_name = "{}_{}".format(config_data['model'], wrf_system)

        source_id = None

        try:
            source_id = get_source_id(pool=pool, model=source_name, version=tms_meta['version'])
        except Exception:
            try:
                time.sleep(3)
                source_id = get_source_id(pool=pool, model=source_name, version=tms_meta['version'])
            except Exception:
                msg = "Exception occurred while loading source meta data for WRF_{} from database.".format(wrf_system)
                logger.error(msg)
                email_content[datetime.now().strftime(COMMON_DATE_TIME_FORMAT)] = msg

        if source_id is not None:
            TS = Timeseries(pool)
            fcst_ts = TS.get_latest_timeseries(sim_tag=config_data['sim_tag'], station_id=config_data['sim_tag'],
                                               source_id=source_id, variable_id=config_data['variable_id'],
                                               unit_id=config_data['sim_tag'])




if __name__ == "__main__":
    # config_data = {
    #             'model': "WRF",
    #             'version': "4.0",
    #             'wrf_system': "A"
    #         }
    # create_d01_rfields("/home/shadhini/dev/repos/curw-sl/curw_wrf_data_pusher/to_be_deprecated/wrf_4.0_18_A_2019-10-15_d01_RAINNC.nc", config_data)

    """
    Config.json
    {
      "version": "4.0",
      "wrf_type": "dwrf",
    
      "model": "WRF",
    
      "unit": "mm",
      "unit_type": "Accumulative",
    
      "variable": "Precipitation"
    }


    /wrf_nfs/wrf/4.0/d0/18/A/2019-07-30/d03_RAINNC.nc

    tms_meta = {
                    'sim_tag'       : sim_tag,
                    'latitude'      : latitude,
                    'longitude'     : longitude,
                    'model'         : model,
                    'version'       : version,
                    'variable'      : variable,
                    'unit'          : unit,
                    'unit_type'     : unit_type
                    }
    """
    config_data = {}

    try:

        config_path = None
        wrf_dir = None
        gfs_run = None
        gfs_data_hour = None
        wrf_systems = None
        date = None

        try:
            opts, args = getopt.getopt(sys.argv[1:], "h:c:d:r:H:s:D:",
                                       ["help", "config=", "dir=", "run=", "hour=", "wrf_systems=", "date="])
        except getopt.GetoptError:
            usage()
            sys.exit(2)
        for opt, arg in opts:
            if opt in ("-h", "--help"):
                usage()
                sys.exit()
            elif opt in ("-c", "--config"):
                config_path = arg.strip()
            elif opt in ("-d", "--dir"):
                wrf_dir = arg.strip()
            elif opt in ("-r", "--run"):
                gfs_run = arg.strip()
            elif opt in ("-H", "--hour"):
                gfs_data_hour = arg.strip()
            elif opt in ("-s", "--wrf_systems"):
                wrf_systems = arg.strip()
            elif opt in ("-D", "--date"):
                date = arg.strip()

        if config_path is None:
            msg = "Config file name is not specified."
            logger.error(msg)
            email_content[datetime.now().strftime(COMMON_DATE_TIME_FORMAT)] = msg
            sys.exit(1)

        config = json.loads(open(config_path).read())

        # source details
        if wrf_dir is None:
            msg = "WRF root directory is not specified."
            logger.error(msg)
            email_content[datetime.now().strftime(COMMON_DATE_TIME_FORMAT)] = msg
            sys.exit(1)
        if gfs_run is None:
            msg = "GFS run is not specified."
            logger.error(msg)
            email_content[datetime.now().strftime(COMMON_DATE_TIME_FORMAT)] = msg
            sys.exit(1)
        if gfs_data_hour is None:
            msg = "GFS data hour is not specified."
            logger.error(msg)
            email_content[datetime.now().strftime(COMMON_DATE_TIME_FORMAT)] = msg
            sys.exit(1)
        if wrf_systems is None:
            msg = "WRF systems are not specified."
            logger.error(msg)
            email_content[datetime.now().strftime(COMMON_DATE_TIME_FORMAT)] = msg
            sys.exit(1)
        model = read_attribute_from_config_file('model', config)
        version = read_attribute_from_config_file('version', config)
        wrf_type = read_attribute_from_config_file('wrf_type', config)
        wrf_system_list = wrf_systems.split(',')

        # sim_tag
        sim_tag_prefix = ''
        if wrf_type != 'wrf':
            sim_tag_prefix = wrf_type + "_"
        sim_tag = sim_tag_prefix + 'gfs_{}_{}'.format(gfs_run, gfs_data_hour)

        # unit details
        unit = read_attribute_from_config_file('unit', config)
        unit_type = UnitType.getType(read_attribute_from_config_file('unit_type', config))

        # variable details
        variable = read_attribute_from_config_file('variable', config)

        if date is None:
            msg = "Run date is not specified."
            logger.error(msg)
            email_content[datetime.now().strftime(COMMON_DATE_TIME_FORMAT)] = msg
            sys.exit(1)

        pool = get_Pool(host=CURW_FCST_HOST, port=CURW_FCST_PORT, user=CURW_FCST_USERNAME, password=CURW_FCST_PASSWORD,
                        db=CURW_FCST_DATABASE)

        try:
            wrf_v3_stations = get_wrf_stations(pool)

            variable_id = get_variable_id(pool=pool, variable=variable)
            unit_id = get_unit_id(pool=pool, unit=unit, unit_type=unit_type)
        except Exception:
            msg = "Exception occurred while loading common metadata from database."
            logger.error(msg)
            email_content[datetime.now().strftime(COMMON_DATE_TIME_FORMAT)] = msg
            sys.exit(1)

        if date is None:
            msg = "Run date is not specified."
            logger.error(msg)
            email_content[datetime.now().strftime(COMMON_DATE_TIME_FORMAT)] = msg
            sys.exit(1)

        tms_meta = {
            'sim_tag': sim_tag,
            'version': version,
            'variable': variable,
            'unit': unit,
            'unit_type': unit_type.value,
            'variable_id': variable_id,
            'unit_id': unit_id
        }
        config_data = {
            'model': model,
            'version': version,
            'date': date,
            'wrf_dir': wrf_dir,
            'gfs_run': gfs_run,
            'gfs_data_hour': gfs_data_hour,
            'wrf_system_list': wrf_system_list,
            'wrf_type': wrf_type
        }

        output_dir = os.path.join(config_data['wrf_dir'], config_data['version'], config_data['gfs_run'],
                                  config_data['gfs_data_hour'], config_data['date'], 'output',
                                  config_data['wrf_type'], config_data['wrf_system'])

        local_rfield_home = os.path.join(local_output_root_dir, config_data['version'], config_data['gfs_run'],
                                         config_data['gfs_data_hour'], 'rfields', config_data['wrf_type'])

        bucket_rfield_home = os.path.join(config_data['wrf_dir'], config_data['version'], config_data['gfs_run'],
                                  config_data['gfs_data_hour'], config_data['date'], 'rfields', config_data['wrf_type'])

        # make rfield directories
        makedir_if_not_exist(local_rfield_home)
        makedir_if_not_exist(bucket_rfield_home)


    except Exception as e:
        msg = 'Config data loading error.'
        logger.error(msg)
        email_content[datetime.now().strftime(COMMON_DATE_TIME_FORMAT)] = msg
        traceback.print_exc()
    finally:
        print("{} ::: Rfield Generation Process \n::: Email Content {} \n::: Config Data {}"
                    .format(datetime.now(), json.dumps(email_content), json.dumps(config_data)))

