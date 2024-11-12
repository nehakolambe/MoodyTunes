import pandas as pd
import requests
import base64
import json
import time
import os

# Spotify API credentials (replace with your own)
client_id = '<your-client-id>'
client_secret = '<your-client-secret>'

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
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error processing track {track_id}: {e}")
        return None

# Load the dataset
file_path = 'split_dataset_part_1.csv'  # Update with your actual file path
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

for i in range(num_batches):
    batch_track_ids = unique_track_ids[i*batch_size:(i+1)*batch_size]
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
    temp_df = pd.DataFrame(audio_features_list)
    temp_df.to_csv(f'{output_dir}/batch_results_{i}.csv', index=False)
    print(f"Batch {i+1}/{num_batches} processed and saved.")

# Combine all batch files into a single dataset
audio_features_df = pd.concat([pd.read_csv(f'{output_dir}/batch_results_{i}.csv') for i in range(num_batches)], ignore_index=True)

# Merge with original DataFrame if needed
merged_df = pd.merge(df, audio_features_df, on='track_id', how='left')

# Save the final dataset to a CSV file
output_file = 'enhanced_dataset_with_all_features.csv'
merged_df.to_csv(output_file, index=False)

print(f"Enhanced dataset saved to {output_file}")
