import os
import pandas as pd
from pathlib import Path

#----- setting-up -----#
run_dir = Path.cwd() / 'obs_data'
obs_dir = '2x2'
OT = '2026-04-01 12:00:00'
origin_time = pd.to_datetime(f'{OT}')

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


# travel_time threshold (in meter)
threshold = 0.01

obs_time_path = os.path.join(run_dir, obs_dir, 'time.dat')
df_obs_time = pd.read_csv(obs_time_path, sep=r'\s+', header=None, names=['time'])

output_file = 'sta_param.txt'

with open(output_file, 'w') as f:
    # Optional header line (uncomment if you want one)
    # f.write("station, travel_time (in minute)\n")
    
    for obs_dir_sta, station_name in station_naming.items():
        obs_amp_path = os.path.join(run_dir, obs_dir, f'ts_record{obs_dir_sta}.dat')
        
        # Check if the file exists to avoid crashing if a station file is missing
        if not os.path.exists(obs_amp_path):
            print(f"Skipping {station_name}: File {obs_amp_path} not found.")
            continue
            
        # Read amplitude for the current station
        df_obs_amp = pd.read_csv(obs_amp_path, sep=r'\s+', header=None, usecols=[0], names=['amp_synth'])
        
        # Combine time and amplitude
        df_synth_obs = pd.concat([df_obs_time, df_obs_amp], axis=1)
        
        # Filter for rows where the wave height breaches the 0.2m threshold
        # NOTE: If you want to include negative waves/drawdowns, use: df_synth_obs['amp_synth'].abs() > threshold
        travel_time_condition = df_synth_obs['amp_synth'] > threshold
        df_triggered = df_synth_obs[travel_time_condition]
        
        if not df_triggered.empty:
            # Pick the very first row where the threshold was exceeded
            first_travel_time_sec = df_triggered.iloc[0]['time']
            travel_time_minute = int(first_travel_time_sec / 60.0)
            
            # Write to file formatted to 2 decimal places
            f.write(f"{station_name}, {travel_time_minute:.2f}\n")
            print(f"{station_name}: arrival picked at {origin_time + pd.Timedelta(minutes=travel_time_minute)} UTC", f" | Travel Time : {travel_time_minute:.2f} minutes")
        else:
            # Handle cases where the wave never reaches 0.2m
            f.write(f"{station_name}, None\n")
            print(f"{station_name}: Threshold never exceeded.")

print(f"\nProcessing complete. Results saved to {output_file}!")