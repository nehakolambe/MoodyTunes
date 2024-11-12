import pandas as pd
import os

# Directory containing the Excel files
input_dir = 'merged_dataset'
output_file = 'merged_dataset.xlsx'

# List to hold dataframes
df_list = []

# Read and concatenate all Excel files
for file_name in os.listdir(input_dir):
    if file_name.endswith('.xlsx'):
        file_path = os.path.join(input_dir, file_name)
        df = pd.read_excel(file_path)  # Read Excel file
        
        # Ensure the DataFrame has the specified headers
        expected_headers = [
            'track_id', 'meta_analyzer_version', 'meta_platform', 'meta_detailed_status',
            'meta_status_code', 'meta_timestamp', 'meta_analysis_time', 'meta_input_process',
            'track_num_samples', 'track_duration', 'track_sample_md5', 'track_offset_seconds',
            'track_window_seconds', 'track_analysis_sample_rate', 'track_analysis_channels',
            'track_end_of_fade_in', 'track_start_of_fade_out', 'track_loudness', 'track_tempo',
            'track_tempo_confidence', 'track_time_signature', 'track_time_signature_confidence',
            'track_key', 'track_key_confidence', 'track_mode', 'track_mode_confidence',
            'track_codestring', 'track_code_version', 'track_echoprintstring',
            'track_echoprint_version', 'track_synchstring', 'track_synch_version',
            'track_rhythmstring', 'track_rhythm_version', 'bars', 'beats', 'sections',
            'segments', 'tatums'
        ]
        
        # Only keep expected columns
        df = df[expected_headers]  # This ensures that only expected headers are present
        df_list.append(df)

# Concatenate all DataFrames into one
merged_df = pd.concat(df_list, ignore_index=True)

# Save the merged DataFrame to a single Excel file
merged_df.to_excel(output_file, index=False, engine='openpyxl')
print(f"All files have been merged into {output_file}")