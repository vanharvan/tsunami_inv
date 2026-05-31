import os
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

#----- setting-up -----#
origin_time = '2026-04-01 12:00:00'                             # UTC
run_dir = Path.cwd() / 'GF' / 'B2'
unit_source = 'B2'
OT = '2026-04-01 12:00:00'
start_min = 0
end_min = 180
sta_param_file = 'sta_param.txt'
inv_time_window = 30

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



# ------ LOAD STATION PARAMS --- #
sta_param_df = pd.read_csv(sta_param_file, header=None, names=['station', 'travel_time'])
sta_travel_time_dict = dict(zip(sta_param_df['station'], sta_param_df['travel_time']))

#----- prepare Synthethic Obs. file -----#
for sta_obs in station_codes:
    sta_obs_name = station_naming[sta_obs]
    origin_time = pd.to_datetime(f'{OT}')
    arr_min = sta_travel_time_dict.get(sta_obs_name, 0.0)
    arrival_time = origin_time + pd.Timedelta(minutes=arr_min)
    start_time = origin_time - pd.Timedelta(minutes=start_min)
    end_time = origin_time + pd.Timedelta(minutes=end_min)
    df_obs = pd.read_csv(f'{run_dir}/TS_{sta_obs}_{sta_obs_name}.csv')
    df_obs['Time'] = pd.to_datetime(df_obs['time_utc'])

    y_min = df_obs['amp_m'].min()
    y_max = df_obs['amp_m'].max()
    padding = (y_max - y_min) * 0.1

    #----- PLOTTING -----#
    plt.figure(figsize=(12, 6))
    plt.plot(df_obs['Time'], df_obs['amp_m'], 
         color='tab:red', linewidth=1.5, label='Tsunami Sim.')
    plt.title(f'SIM - Station: {sta_obs_name} - Unit Source : {unit_source}', fontsize=14, fontweight='bold')
    plt.xlim(start_time, end_time)
    plt.ylim(y_min - padding, y_max + padding)
    plt.xlabel('Date Time (UTC)', fontsize=12)
    plt.ylabel('Tsunami Amplitude (m)', fontsize=12)
    plt.axvline(x=arrival_time, color='black', linestyle='--', linewidth=1.5, label=f'Arrival Time ({arrival_time} UTC)')
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.xticks(rotation=45)
    plt.axhline(y=0.0, color='black', linestyle='-', linewidth=0.8)

    highlight_end_time = arrival_time + pd.Timedelta(minutes=inv_time_window)
    plt.axvspan(arrival_time, highlight_end_time, color='yellow', alpha=0.3, label=f'Inversion Data ({inv_time_window}-min recording)')

    plt.legend(loc='upper right')
    plt.tight_layout()
    plt.savefig(f'{run_dir}/SIM_{sta_obs}_{sta_obs_name}.png', dpi=300)
