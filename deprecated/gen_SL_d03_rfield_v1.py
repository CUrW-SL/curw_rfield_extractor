#!/home/uwcc-admin/curw_rfield_extractor/venv/bin/python3
# rfields goes to todays folder
import traceback
import pymysql
import json
import sys
import getopt
import os
import re
import multiprocessing as mp
from datetime import datetime, timedelta


# connection params
HOST = ""
USER = ""
PASSWORD = ""
DB =""
PORT = ""

VALID_MODELS = ["WRF_A", "WRF_C", "WRF_E", "WRF_SE"]
VALID_VERSIONS = ["4.0"]
SIM_TAGS = ["gfs_d0_18", "gfs_d1_00", "gfs_d0_00", "dwrf_gfs_d0_18"]
root_directory = '/home/uwcc-admin/rfields'
bucket_root = '/mnt/disks/wrf_nfs'


def read_attribute_from_config_file(attribute, config):
    """
    :param attribute: key name of the config json file
    :param config: loaded json file
    :return:
    """
    if attribute in config and (config[attribute]!=""):
        return config[attribute]
    else:
        print("{} not specified in config file.".format(attribute))
        exit(1)


def write_to_file(file_name, data):
    with open(file_name, 'w+') as f:
        f.write('\n'.join(data))


def create_rfield(connection, wrf_model, version, sim_tag, timestamp, rfield_home):
    # rfield = [['latitude', 'longitude', 'rainfall']]
    rfield = []
    with connection.cursor() as cursor0:
        cursor0.callproc('get_d03_rfield', (wrf_model, version, sim_tag, timestamp))
        results = cursor0.fetchall()
        for result in results:
            rfield.append('{}'.format(result.get('value')))

    if rfield[0] != "None":
        write_to_file('{}/{}_{}_{}_rfield.txt'
                  .format(rfield_home, wrf_model, version, timestamp.strftime('%Y-%m-%d_%H-%M')), rfield)


def gen_rfield_d03(wrf_model, version, sim_tag, rfield_home):

    # remove outdated rfield files
    try:
        os.system("rm -f {}/{}_{}_*".format(rfield_home, wrf_model, version))
    except Exception as e:
        traceback.print_exc()

    # Connect to the database
    connection = pymysql.connect(host=HOST, user=USER, password=PASSWORD, db=DB,
            cursorclass=pymysql.cursors.DictCursor)

    start_time = ''
    end_time = ''

    now = datetime.strptime((datetime.now()+timedelta(hours=5, minutes=30)).strftime('%Y-%m-%d 00:00:00'), '%Y-%m-%d %H:%M:%S')

    try:
        # Extract timeseries start time and end time
        with connection.cursor() as cursor1:
            cursor1.callproc('get_TS_start_end', (wrf_model, version, sim_tag))
            result = cursor1.fetchone()
            start_time = result.get('start')
            end_time = result.get('end')

        if end_time > now:
            # Extract rfields
            timestamp = start_time

            while timestamp <= end_time:
                create_rfield(connection=connection, wrf_model=wrf_model, version=version, sim_tag=sim_tag,
                              timestamp=timestamp, rfield_home=rfield_home)

                timestamp = datetime.strptime(str(timestamp), '%Y-%m-%d %H:%M:%S') + timedelta(minutes=15)

        return True
    except Exception as ex:
        traceback.print_exc()
        return False
    finally:
        connection.close()
        print("Process finished")


def usage():
    usageText = """
    Usage: ./gen_SL_d03_rfield.py -m WRF_X1,WRF_X2,WRF_X3 -v vX -s "evening_18hrs"

    -h  --help          Show usage
    -m  --wrf_model     List of WRF models (e.g. WRF_A, WRF_E). Compulsory arg
    -v  --version       WRF model version (e.g. v4, v3). Compulsory arg
    -s  --sim_tag       Simulation tag (e.g. evening_18hrs). Compulsory arg
    """
    print(usageText)


if __name__=="__main__":

    mp_pool = None

    try:
        wrf_models = None
        version = None
        sim_tag = None

        try:
            opts, args = getopt.getopt(sys.argv[1:], "h:m:v:s:",
                    ["help", "wrf_model=", "version=", "sim_tag="])
        except getopt.GetoptError:
            usage()
            sys.exit(2)
        for opt, arg in opts:
            if opt in ("-h", "--help"):
                usage()
                sys.exit()
            elif opt in ("-m", "--wrf_model"):
                wrf_models = arg.strip()
            elif opt in ("-v", "--version"):
                version = arg.strip()
            elif opt in ("-s", "--sim_tag"):
                sim_tag = arg.strip()

        # load connection parameters
        config = json.loads(open('/home/uwcc-admin/curw_rfield_extractor/config.json').read())

        # connection params
        HOST = read_attribute_from_config_file('host', config)
        USER = read_attribute_from_config_file('user', config)
        PASSWORD = read_attribute_from_config_file('password', config)
        DB = read_attribute_from_config_file('db', config)
        PORT = read_attribute_from_config_file('port', config)

        wrf_model_list = wrf_models.split(',')

        for wrf_model in wrf_model_list:
            if wrf_model is None or wrf_model not in VALID_MODELS:
                usage()
                exit(1)
        if version is None or version not in VALID_VERSIONS:
            usage()
            exit(1)
        if sim_tag is None or sim_tag not in SIM_TAGS:
            usage()
            exit(1)

        sim_tag_parts = re.findall(r'\d+', sim_tag)
        gfs_run = "d{}".format(sim_tag_parts[0])
        gfs_data_hour = sim_tag_parts[1]
        today = (datetime.now() + timedelta(hours=5, minutes=30)).strftime('%Y-%m-%d')

        if sim_tag.split("_")[0] == 'dwrf':
            rfield_home = "{}/dwrf/{}/{}/{}/d03/rfield".format(root_directory, version, gfs_run, gfs_data_hour)
            bucket_rfield_home = "{}/dwrf/{}/{}/{}/{}/rfield/d03".format(bucket_root, version, gfs_run, gfs_data_hour,
                                                                        today)
        else:
            rfield_home = "{}/wrf/{}/{}/{}/d03/rfield".format(root_directory, version, gfs_run, gfs_data_hour)
            bucket_rfield_home = "{}/wrf/{}/{}/{}/{}/rfield/d03".format(bucket_root, version, gfs_run, gfs_data_hour,
                                                                        today)

        try:
            os.makedirs(rfield_home)
        except FileExistsError:
            # directory already exists
            pass

        try:
            os.makedirs(bucket_rfield_home)
        except FileExistsError:
            # directory already exists
            pass

        # copy file containing xy coordinates to the rfield home
        try:
            os.system("cp /home/uwcc-admin/curw_rfield_extractor/d03_xy.csv {}/xy.csv".format(rfield_home))
        except Exception:
            pass

        mp_pool = mp.Pool(mp.cpu_count())

        results = mp_pool.starmap(gen_rfield_d03,
                                        [(wrf_model, version, sim_tag, rfield_home) for wrf_model in wrf_model_list])

        print("results: ", results)

        os.system("tar -C {} -czf {}/rfield.tar.gz rfield".format('/rfield'.join(rfield_home.split('/rfield')[:-1]), bucket_rfield_home))

    except Exception as e:
        print('JSON config data loading error.')
        traceback.print_exc()
    finally:
        if mp_pool is not None:
            mp_pool.close()
        # os.system("tar -czvf {}/rfield.tar.gz {}/*".format(bucket_rfield_home, rfield_home))

