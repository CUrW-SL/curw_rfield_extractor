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


#sim_tag="evening_18hrs" #optional
date=$1

if [ -z $date ]
then
  date=$(date -u -d '- 2 day +5 hour +30 min' '+%F')
fi


echo $date

##### dwrf #####

#dwrf_gfs_d1_06    @22
config_file_path='config/dwrf_config.json'
wrf_root_directory='/mnt/disks/wrf_nfs/wrf'
gfs_run=d1
gfs_data_hour='06'
wrf_systems='A,C,E,SE'

fgt="$date 22:00:00"
echo $fgt

echo "Running scripts to generate rfields based on active observational stations."
echo "Params passed:: config_file_path=$config_file_path, wrf_root_directory=$wrf_root_directory, gfs_run=$gfs_run,
gfs_data_hour=$gfs_data_hour, wrf_system=$wrf_systems, date=$date, fgt=$fgt"
./gen_active_stations_rfields_for_given_time.py -c $config_file_path -d $wrf_root_directory -r $gfs_run -H $gfs_data_hour -s $wrf_systems -D $date -f "$fgt" >> past_active_stations_rfields.log 2>&1
./gen_hybrid_wrf_rfields_for_given_time.py -c $config_file_path -d $wrf_root_directory -r $gfs_run -H $gfs_data_hour -s $wrf_systems -D $date -f "$fgt" >> past_hybrid_wrf_rfields.log 2>&1


#dwrf_gfs_d1_12    @02
config_file_path='config/dwrf_config.json'
wrf_root_directory='/mnt/disks/wrf_nfs/wrf'
gfs_run=d1
gfs_data_hour=12
wrf_systems='A,C,E,SE'

fgt="$date 02:00:00"
echo $fgt

echo "Running scripts to generate rfields based on active observational stations."
echo "Params passed:: config_file_path=$config_file_path, wrf_root_directory=$wrf_root_directory, gfs_run=$gfs_run,
gfs_data_hour=$gfs_data_hour, wrf_system=$wrf_systems, date=$date, fgt=$fgt"
./gen_active_stations_rfields_for_given_time.py -c $config_file_path -d $wrf_root_directory -r $gfs_run -H $gfs_data_hour -s $wrf_systems -D $date -f "$fgt" >> past_active_stations_rfields.log 2>&1
./gen_hybrid_wrf_rfields_for_given_time.py -c $config_file_path -d $wrf_root_directory -r $gfs_run -H $gfs_data_hour -s $wrf_systems -D $date -f "$fgt" >> past_hybrid_wrf_rfields.log 2>&1


#dwrf_gfs_d1_18    @09
config_file_path='config/dwrf_config.json'
wrf_root_directory='/mnt/disks/wrf_nfs/wrf'
gfs_run=d1
gfs_data_hour=18
wrf_systems='A,C,E,SE'

fgt="$date 09:00:00"
echo $fgt

echo "Running scripts to generate rfields based on active observational stations."
echo "Params passed:: config_file_path=$config_file_path, wrf_root_directory=$wrf_root_directory, gfs_run=$gfs_run,
gfs_data_hour=$gfs_data_hour, wrf_system=$wrf_systems, date=$date, fgt=$fgt"
./gen_active_stations_rfields_for_given_time.py -c $config_file_path -d $wrf_root_directory -r $gfs_run -H $gfs_data_hour -s $wrf_systems -D $date -f "$fgt" >> past_active_stations_rfields.log 2>&1
./gen_hybrid_wrf_rfields_for_given_time.py -c $config_file_path -d $wrf_root_directory -r $gfs_run -H $gfs_data_hour -s $wrf_systems -D $date -f "$fgt" >> past_hybrid_wrf_rfields.log 2>&1


#dwrf_gfs_d1_00    @17
config_file_path='config/dwrf_config.json'
wrf_root_directory='/mnt/disks/wrf_nfs/wrf'
gfs_run=d1
gfs_data_hour='00'
wrf_systems='A,C,E,SE'

fgt="$date 17:00:00"
echo $fgt

echo "Running scripts to generate rfields based on active observational stations."
echo "Params passed:: config_file_path=$config_file_path, wrf_root_directory=$wrf_root_directory, gfs_run=$gfs_run,
gfs_data_hour=$gfs_data_hour, wrf_system=$wrf_systems, date=$date, fgt=$fgt"
./gen_active_stations_rfields_for_given_time.py -c $config_file_path -d $wrf_root_directory -r $gfs_run -H $gfs_data_hour -s $wrf_systems -D $date -f "$fgt" >> past_active_stations_rfields.log 2>&1
./gen_hybrid_wrf_rfields_for_given_time.py -c $config_file_path -d $wrf_root_directory -r $gfs_run -H $gfs_data_hour -s $wrf_systems -D $date -f "$fgt" >> past_hybrid_wrf_rfields.log 2>&1


#mwrf_gfs_d0_18    @02
#config_file_path='config/mwrf_config.json'
#wrf_root_directory='/mnt/disks/wrf_nfs/wrf'
#gfs_run=d0
#gfs_data_hour=18
#wrf_systems='T5'
#
#fgt="$date 02:00:00"
#echo $fgt
#
#echo "Running scripts to generate rfields based on active observational stations."
#echo "Params passed:: config_file_path=$config_file_path, wrf_root_directory=$wrf_root_directory, gfs_run=$gfs_run,
#gfs_data_hour=$gfs_data_hour, wrf_system=$wrf_systems, date=$date, fgt=$fgt"
#./gen_active_stations_rfields_for_given_time.py -c $config_file_path -d $wrf_root_directory -r $gfs_run -H $gfs_data_hour -s $wrf_systems -D $date -f "$fgt" >> past_active_stations_rfields.log 2>&1
#./gen_fcst_only_hybrid_rfields_for_given_time.py -c $config_file_path -d $wrf_root_directory -r $gfs_run -H $gfs_data_hour -s $wrf_systems -D $date -f "$fgt" >> past_hybrid_wrf_rfields.log 2>&1


# Deactivating virtual environment
echo "Deactivating virtual environment"
deactivate
