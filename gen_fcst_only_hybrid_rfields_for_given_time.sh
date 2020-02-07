#!/usr/bin/env bash

# Print execution date time
echo `date`

echo "Changing into ~/curw_rfield_extractor"
cd /home/uwcc-admin/curw_rfield_extractor
echo "Inside `pwd`"


# If no venv (python3 virtual environment) exists, then create one.
if [ ! -d "venv" ]
then
    echo "Creating venv python3 virtual environment."
    virtualenv -p python3 venv
fi

# Activate venv.
echo "Activating venv python3 virtual environment."
source venv/bin/activate

# Install dependencies using pip.
if [ ! -f "db.log" ]
then
    echo "Installing numpy"
    pip install numpy
    echo "Installing netCDF4"
    pip install netCDF4
    echo "Installing cftime"
    pip install cftime
    echo "Installing PyMySQL"
    pip install PyMySQL
    echo "Installing PyYAML"
    pip install PyYAML
    echo "Installing data layer"
#    pip install git+https://github.com/shadhini/curw_db_adapter.git -U
    pip install git+https://github.com/shadhini/curw_db_adapter.git
fi

config_file_path='config/wrf_config.json'
wrf_root_directory='/mnt/disks/wrf_nfs/wrf'
gfs_run=d0
gfs_data_hour=18
wrf_systems='A,C,E,SE'
#date=$6

for date in "2020-02-07" "2020-02-06" "2020-02-05" "2020-02-03" "2020-02-02" "2020-01-31" "2020-01-30" "2020-01-29" "2020-01-28" "2020-01-27" "2020-01-26" "2020-01-25" "2020-01-24" "2020-01-23" "2020-01-22" "2020-01-21" "2020-01-20" "2020-01-19" "2020-01-18" "2020-01-17" "2020-01-16" "2020-01-15" "2020-01-14" "2020-01-13" "2020-01-12" "2020-01-11" "2020-01-10" "2020-01-09" "2020-01-08" "2020-01-07" "2020-01-06" "2020-01-05" "2020-01-04" "2020-01-03" "2020-01-02" "2020-01-01"
do
	fgt="$date 05:00:00"
	echo $fgt
  ## Push WRFv4 data into the database
  echo "Running scripts to generate rfields based on active observational stations. Logs Available in past_hybrid_wrf_rfields.log file."
  echo "Params passed:: config_file_path=$config_file_path, wrf_root_directory=$wrf_root_directory, gfs_run=$gfs_run,
  gfs_data_hour=$gfs_data_hour, wrf_system=$wrf_systems, date=$date, fgt=$fgt"
  ./gen_fcst_only_hybrid_rfields_for_given_time.py -c $config_file_path -d $wrf_root_directory -r $gfs_run -H $gfs_data_hour -s $wrf_systems -D $date -f "$fgt" >> past_hybrid_wrf_rfields.log 2>&1
done

# Deactivating virtual environment
echo "Deactivating virtual environment"
deactivate
