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

#for date in "2019-12-31" "2019-12-30" "2019-12-29" "2019-12-28" "2019-12-27" "2019-12-26" "2019-12-25" "2019-12-24" "2019-12-23" "2019-12-22" "2019-12-21" "2019-12-20" "2019-12-19" "2019-12-18" "2019-12-17" "2019-12-16" "2019-12-15" "2019-12-14" "2019-12-13" "2019-12-12" "2019-12-11" "2019-12-10" "2019-12-09" "2019-12-08" "2019-12-07" "2019-12-06" "2019-12-05" "2019-12-04" "2019-12-03" "2019-12-02" "2019-12-01"
#do
date=2019-11-14
while [ "$date" != 2019-11-15 ]; do
  echo $date
	fgt="$date 05:00:00"
	echo $fgt

  ## Push WRFv4 data into the database
  echo "Running scripts to generate rfields based on active observational stations."
  echo "Params passed:: config_file_path=$config_file_path, wrf_root_directory=$wrf_root_directory, gfs_run=$gfs_run,
  gfs_data_hour=$gfs_data_hour, wrf_system=$wrf_systems, date=$date, fgt=$fgt"
  ./gen_active_stations_rfields_for_given_time.py -c $config_file_path -d $wrf_root_directory -r $gfs_run -H $gfs_data_hour -s $wrf_systems -D $date -f "$fgt" >> past_active_stations_rfields.log 2>&1
  ./gen_fcst_only_hybrid_rfields_for_given_time.py -c $config_file_path -d $wrf_root_directory -r $gfs_run -H $gfs_data_hour -s $wrf_systems -D $date -f "$fgt" >> past_hybrid_wrf_rfields.log 2>&1

  date=$(date -I -d "$date + 1 day")
done

# Deactivating virtual environment
echo "Deactivating virtual environment"
deactivate
