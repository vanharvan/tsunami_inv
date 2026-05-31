import os
import numpy as np
import pandas as pd


obs_dir = r'D:\PROJECT\inversion_test_3\obs_data\2x2'
sim_dir = r'D:\PROJECT\inversion_test_3\GF'
sta_param_file = 'sta_param.txt'
origin_time = '2026-04-01 12:00:00' 
time_window = 30
sampling_rate = 1

unit_sources = [
    'A1',
    'A2',
    'B1',
    'B2'
]

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

# ------------------------------------------------------------------------------------------------------------ #
num_sta_obs = len(station_codes)
num_unit_sources = len(unit_sources)

total_rows_A = int(num_sta_obs * (time_window / sampling_rate))
total_cols_A = num_unit_sources

sta_param_df = pd.read_csv(sta_param_file, header=None, names=['station', 'travel_time'])
sta_travel_time_dict = dict(zip(sta_param_df['station'], sta_param_df['travel_time']))
origin_time = pd.to_datetime(f'{origin_time}')
# ------------------------------------------------------------------------------------------------------------ #
# --- INITIALIZE THE MATRIX A (GREEN FUNCTION / COMPUTED DATA) --- #
# ---------------------------------------------------------------- #
matrix_A = np.zeros((total_rows_A, total_cols_A))
print(f"Initialized Matrix A with shape: {matrix_A.shape}\n")

for col_idx, unit in enumerate(unit_sources):
    print(f"Loading data for Unit Source {unit} (Column {col_idx + 1})...")
    
    for stack_idx, sta_obs in enumerate(station_codes):
        sta_obs_name = station_naming[sta_obs]
        start_row_A = int(stack_idx * (time_window/sampling_rate))
        end_row_A = int(start_row_A + (time_window/sampling_rate))
        
        tt_min = sta_travel_time_dict.get(sta_obs_name, 0.0)
        arrival_time = origin_time + pd.Timedelta(minutes=tt_min)
        time_window_start = arrival_time
        time_window_end = arrival_time + pd.Timedelta(minutes=(int(time_window/sampling_rate) - 1))
        
        
        file_name = f'TS_{sta_obs}_{sta_obs_name}.csv'
        file_path = os.path.join(sim_dir, unit, file_name)
        df = pd.read_csv(file_path)
        df["time_utc"] = pd.to_datetime(df["time_utc"])
        df_cropped = df[(df["time_utc"] >= time_window_start) & (df["time_utc"] <= time_window_end)].copy()
        sim_data = df_cropped['amp_m'].values[:int(time_window/sampling_rate)]

        matrix_A[start_row_A:end_row_A, col_idx] = sim_data
        print(f"  -> {sta_obs} stacked to collumn {col_idx + 1} row {start_row_A + 1}-{end_row_A}")
        
print("\nMatrix A construction complete!")

matrix_A_df = pd.DataFrame(matrix_A, columns=unit_sources)
output_file_A = 'Matrix_A_GF.csv'

np.savetxt(output_file_A, matrix_A_df, delimiter=',', fmt='%.6f')

# ----------- INITIALIZE THE MATRIX B (OBSERVED DATA) ------------ #
# ---------------------------------------------------------------- #
        
total_rows_B = int(num_sta_obs * (time_window / sampling_rate))
total_cols_B = 1

matrix_B = np.zeros((total_rows_B, total_cols_B))
print(f"Initialized Matrix B with shape: {matrix_B.shape}\n")

for row_idx, sta_obs in enumerate(station_codes):
    print(f"Loading data for station {sta_obs}...")
    sta_obs_name = station_naming[sta_obs]
    
    start_row_B = row_idx * time_window
    end_row_B = start_row_B + time_window
     
    file_name = f'TS_{sta_obs}_{sta_obs_name}.csv'
    file_path = os.path.join(obs_dir, file_name)
    df = pd.read_csv(file_path)
    df["time_utc"] = pd.to_datetime(df["time_utc"])
    df_cropped = df[(df["time_utc"] >= time_window_start) & (df["time_utc"] <= time_window_end)].copy()
    obs_data = df_cropped['amp_m'].values[:int(time_window/sampling_rate)]
    matrix_B[start_row_B:end_row_B, 0] = obs_data
    print(f"  -> {sta_obs} stacked to collumn {row_idx + 1} row {start_row_B + 1}-{end_row_B}")

print("\nMatrix B construction complete!")

matrix_B_df = pd.DataFrame(matrix_B, columns=[0])
output_file_B = 'Matrix_B_OBS.csv'
np.savetxt(output_file_B, matrix_B_df, delimiter=',', fmt='%.6f')
print(f"Matrix saved to {output_file_B}")