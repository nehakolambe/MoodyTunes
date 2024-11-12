import base64
import json
import os
import time

import pandas as pd
import requests

# Spotify API credentials (replace with your own)
client_id = 'bcd3392bcd874e39abf70c9d9f8cce51'
client_secret = '84104a422a6744778ad95585840fcf4b'
part = 'part_2'

# Function to get access token
def get_access_token(client_id, client_secret):
    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + base64.b64encode(f"{client_id}:{client_secret}".encode()).decode(),
    }
    data = {"grant_type": "client_credentials"}
    response = requests.post(url, headers=headers, data=data)
    if response.status_code != 200:
        raise Exception(f"Failed to get access token: {response.json()}")
    return response.json().get("access_token")

# Function to get audio analysis for a track
def get_audio_analysis(track_id, token):
    url = f"https://api.spotify.com/v1/audio-analysis/{track_id}"
    headers = {
        "Authorization": f"Bearer {token}"
    }

    max_retry_after = 300  # Maximum allowed retry time in seconds

    while True: # add a loop here to allow using the continue statement for timed sleep.
        try:
            response = requests.get(url, headers=headers, timeout=10)

            # Check if rate limited (HTTP 429)
            if response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", 1))  # Default to 1 second if header is missing
                if retry_after > max_retry_after:
                    print(f"Rate limit retry time ({retry_after} seconds) exceeds the maximum cutoff ({max_retry_after} seconds). Exiting.")
                    return None
                print(f"Rate limit hit. Retrying after {retry_after} seconds.")
                time.sleep(retry_after)
                continue  # Retry the request after waiting

            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error processing track {track_id}: {e}")
            return None

# Load the dataset
file_path = os.path.join('split_data', f'split_dataset_{part}.csv')  # Update with your actual file path
df = pd.read_csv(file_path)

# Extract track IDs
df['track_id'] = df['uri'].str.extract(r'spotify:track:(\w+)')

# Get access token
token = get_access_token(client_id, client_secret)

# Batch processing
batch_size = 100  # Adjust for optimal performance
unique_track_ids = df['track_id'].dropna().unique()
num_batches = len(unique_track_ids) // batch_size + (len(unique_track_ids) % batch_size != 0)

# Output directory for temporary results
output_dir = 'batch_results'
os.makedirs(output_dir, exist_ok=True)

try:
    for i in range(num_batches):
        batch_track_ids = unique_track_ids[i * batch_size:(i + 1) * batch_size]
        audio_features_list = []
        for track_id in batch_track_ids:
            print(track_id)
            audio_analysis = get_audio_analysis(track_id, token)
            if audio_analysis:
                flat_features = {'track_id': track_id}
                for key, value in audio_analysis.items():
                    if isinstance(value, dict):
                        for sub_key, sub_value in value.items():
                            flat_features[f"{key}_{sub_key}"] = sub_value
                    else:
                        flat_features[key] = value
                audio_features_list.append(flat_features)
                time.sleep(0.5)  # Small delay to prevent overwhelming the API
        
        # Save partial results after each batch
        if audio_features_list:  # Check if there is any data to save
            temp_df = pd.DataFrame(audio_features_list)
            output_file = f'{output_dir}/batch_results_{i}.xlsx'
            with pd.ExcelWriter(output_file) as writer:
                temp_df.to_excel(writer, index=False, sheet_name='BatchResults')
            print(f"Batch {i+1}/{num_batches} processed and saved.")
finally:
    # Combine all existing batch files into a single dataset
    batch_files = [f for f in os.listdir(output_dir) if f.startswith('batch_results_') and f.endswith('.xls')]
    if batch_files:
        combined_data = []
        for file in batch_files:
            temp_df = pd.read_excel(f'{output_dir}/{file}')
            combined_data.append(temp_df)
        audio_features_df = pd.concat(combined_data, ignore_index=True)

        # Merge with the original DataFrame if needed
        merged_df = pd.merge(df, audio_features_df, on='track_id', how='left')
        os.makedirs('merged_dataset', exist_ok=True)

        # Save the final dataset to an Excel file
        output_file = os.path.join('merged_dataset', f'{part}.xlsx')
        with pd.ExcelWriter(output_file) as writer:
            merged_df.to_excel(writer, index=False, sheet_name='EnhancedData')
        print(f"Enhanced dataset saved to {output_file}")
    else:
        print("No batch files were generated. Exiting.")

