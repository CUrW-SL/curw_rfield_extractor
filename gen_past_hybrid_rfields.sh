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
#sim_tag="evening_18hrs" #optional
#date=$6

#for date in "2019-10-17" "2019-10-18" "2019-10-19" "2019-10-20" "2019-10-21" "2019-10-28" "2019-10-29" "2019-10-30" "2019-10-31" "2019-11-01" "2019-11-02" "2019-11-03" "2019-11-04" "2019-11-05" "2019-11-06" "2019-11-07" "2019-11-07" "2019-11-08" "2019-11-12"
#do

date=2020-05-10
while [ "$date" != 2020-05-19 ]; do
  echo $date
	fgt="$date 05:00:00"
	echo $fgt

  echo "Running scripts to generate rfields based on active observational stations."
  echo "Params passed:: config_file_path=$config_file_path, wrf_root_directory=$wrf_root_directory, gfs_run=$gfs_run,
  gfs_data_hour=$gfs_data_hour, wrf_system=$wrf_systems, date=$date, fgt=$fgt"
  ./gen_active_stations_mean_rfields_for_given_time.py -c $config_file_path -d $wrf_root_directory -r $gfs_run -H $gfs_data_hour -s $wrf_systems -D $date -f "$fgt" >> past_active_stations_mean_rfields.log 2>&1
  ./gen_hybrid_wrf_mean_rfields_for_given_time.py -c $config_file_path -d $wrf_root_directory -r $gfs_run -H $gfs_data_hour -s $wrf_systems -D $date -f "$fgt" >> past_hybrid_wrf_mean_rfields.log 2>&1

#  ./gen_active_stations_rfields_for_given_time.py -c $config_file_path -d $wrf_root_directory -r $gfs_run -H $gfs_data_hour -s $wrf_systems -D $date -f "$fgt" >> past_active_stations_rfields.log 2>&1
#  ./gen_hybrid_wrf_rfields_for_given_time.py -c $config_file_path -d $wrf_root_directory -r $gfs_run -H $gfs_data_hour -s $wrf_systems -D $date -f "$fgt" >> past_hybrid_wrf_rfields.log 2>&1
  # with sim tag (optional set)
#  ./gen_active_stations_rfields_for_given_time.py -c $config_file_path -d $wrf_root_directory -r $gfs_run -H $gfs_data_hour -s $wrf_systems -D $date -f "$fgt" -S $sim_tag >> past_active_stations_rfields.log 2>&1
#  ./gen_hybrid_wrf_rfields_for_given_time.py -c $config_file_path -d $wrf_root_directory -r $gfs_run -H $gfs_data_hour -s $wrf_systems -D $date -f "$fgt" -S $sim_tag >> past_hybrid_wrf_rfields.log 2>&1
  date=$(date -I -d "$date + 1 day")
done

#
# Deactivating virtual environment
echo "Deactivating virtual environment"
deactivate
