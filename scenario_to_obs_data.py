"""
-   Converts computed tsunami waveform from comcot format to a regular format (time-amplitude). 
-   resamples computed data to 1-min sampling rate.
-   saves to .csv files.
"""

import os
import pandas as pd
import numpy as np
from pathlib import Path


# ------ CONFIGURATION ---
origin_time = '2026-04-01 12:00:00'                             # UTC
run_dir = Path.cwd() / 'GF' / 'B2'
sta_param_file = Path.cwd() / 'sta_param.txt'
inv_time_window = 35                                            # minutes

station_codes = [
    '0001',
    '0002',
    '0003',
    '0004'
]

station_naming = {
    '0001': 'DART1',
    '0002': 'DART2',
    '0003': 'DART3',
    '0004': 'DART4',
}

# ------------------------------------------------------------------------------ #
origin_time = pd.to_datetime(origin_time)

# -------------------------- LOAD STATION PARAMS ------------------------------- #
sta_param_df = pd.read_csv(sta_param_file, header=None, names=['station', 'travel_time'])
sta_travel_time_dict = dict(zip(sta_param_df['station'], sta_param_df['travel_time']))
#print(f"\n----- Origin Time (UTC) : {origin_time} -----")
#print("\n----- Station Arrival -----")
#for station, time_travel in sta_travel_time_dict.items():
#    arrival_time = pd.to_datetime(origin_time) + pd.Timedelta(minutes=time_travel)
#    print(f"{station} : {arrival_time} UTC | Travel time : {time_travel} min")
# ------------------------------------------------------------------------------ #

for sta_obs in station_codes:
    sta_obs_name = station_naming[sta_obs]
    print(f"\n--- Processing station : {sta_obs_name} ---")
    time_path = os.path.join(run_dir, 'time.dat')
    time_sec_array = np.loadtxt(time_path)
    amp_path = os.path.join(run_dir, f'ts_record{sta_obs}.dat')
    amp_array = np.loadtxt(amp_path, usecols=0)
    dt = pd.to_timedelta(time_sec_array.flatten(), unit='s')
    time_utc_array = origin_time + dt
    
    df = pd.DataFrame({
        'time_utc': time_utc_array,
        'amp_m': amp_array
    })
    
    # Resample to 1-min sampling rate
    df.set_index('time_utc', inplace=True)
    df_resampled = df.resample('1min').first()
    df_resampled.reset_index(inplace=True)

    
    # Filter data to inversion window
    #arr_min = sta_travel_time_dict.get(sta_obs_name, 0.0)
    #crop_start = origin_time + pd.Timedelta(minutes=arr_min)
    #crop_end = crop_start + pd.Timedelta(minutes=inv_time_window)
    #mask = (df_resampled['time_utc'] >= crop_start) & (df_resampled['time_utc'] < crop_end)
    #df_cropped = df_resampled.loc[mask].copy()
    

    output_file_path = os.path.join(run_dir, f'TS_{sta_obs}_{sta_obs_name}.csv')
    
    # Save as CSV
    df_resampled.to_csv(
            output_file_path, 
            sep=',',           
            index=False,        
            date_format='%Y-%m-%d %H:%M:%S' 
        )
    
    print(f"  -> Saved: {output_file_path}")

