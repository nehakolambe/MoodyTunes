import pandas as pd
import requests
from bs4 import BeautifulSoup
import json
from pydub import AudioSegment
from io import BytesIO
import os
import shutil

def download_audio(preview_url, save_path, track_id, formats=["mp3", "wav"]):
    try:
        # Fetch the audio data
        response = requests.get(preview_url)
        if response.status_code != 200:
            print(f"Failed to download audio: {response.status_code}")
            return
        
        audio = AudioSegment.from_file(BytesIO(response.content), format="mp3")
        
        # Save the audio in specified formats
        for fmt in formats:
            output_file = os.path.join(save_path, f"{track_id}.{fmt}")
            if fmt == "mp3":
                audio.export(output_file, format="mp3")
            elif fmt == "wav":
                audio.export(output_file, format="wav")
            print(f"Saved audio in {fmt} format: {output_file}")
    except Exception as e:
        print(f"Error downloading audio: {e}")

def get_preview_url(track_id):
    try:
        url = f"https://open.spotify.com/embed/track/{track_id}"
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Error fetching the page: {response.status_code}")
            return None
        
        # Parse the HTML response
        soup = BeautifulSoup(response.content, 'html.parser')
        script_tag = soup.find('script', id='__NEXT_DATA__')
        if not script_tag:
            print("Script tag with id '__NEXT_DATA__' not found.")
            return None

        # Load the JSON data from the script tag
        data = json.loads(script_tag.string)

        # Navigate the JSON to find the preview URL
        entity_data = data['props']['pageProps']['state']['data']['entity']
        preview_url = entity_data.get('audioPreview', {}).get('url')

        if preview_url:
            return preview_url
        else:
            print("Preview URL not found in the JSON data.")
            return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def process_uris_from_excel(input_file, output_file, save_path, start_row, end_row):
    # Load the Excel file
    df = pd.read_excel(input_file)

    # Ensure the 'spotify_uri' column exists
    if "spotify_uri" not in df.columns:
        raise ValueError("The Excel file must contain a column named 'spotify_uri'.")

    # Add a new column for preview URLs if it doesn't exist
    if "preview_url" not in df.columns:
        df["preview_url"] = None

    # Extract URIs for the specified range
    uris = df["spotify_uri"].iloc[start_row-1:end_row]
    track_ids = [uri.split(":")[-1] for uri in uris]

    # Create the save directory if it doesn't exist
    os.makedirs(save_path, exist_ok=True)

    # Process each track
    for idx, track_id in enumerate(track_ids):
        row_index = start_row-1 + idx
        print(f"Processing track ID: {track_id} (Row {row_index + 1})")

        # Skip if preview_url already exists for this row
        if pd.notna(df.loc[row_index, "preview_url"]):
            print(f"Preview URL already exists for track ID: {track_id}. Skipping.")
            continue

        # Fetch the preview URL
        preview_url = get_preview_url(track_id)

        if preview_url:
            # Update the preview URL in the DataFrame
            df.at[row_index, "preview_url"] = preview_url
            # Download the audio
            download_audio(preview_url, save_path, track_id)
        else:
            print(f"No preview URL available for track ID: {track_id}")

    # Filter the DataFrame to keep only the specified rows
    filtered_df = df.iloc[start_row-1:end_row]

    # Save the filtered DataFrame back to an Excel file
    filtered_df.to_excel(output_file, index=False)
    print(f"Filtered and updated Excel file saved to: {output_file}")

def organize_audio_files(base_path):
    # Define source and target directories
    wav_dir = os.path.join(base_path, "wav")
    mp3_dir = os.path.join(base_path, "mp3")

    # Create target directories if they don't exist
    os.makedirs(wav_dir, exist_ok=True)
    os.makedirs(mp3_dir, exist_ok=True)

    # Loop through all files in the base directory
    for file_name in os.listdir(base_path):
        source_path = os.path.join(base_path, file_name)

        # Skip directories
        if os.path.isdir(source_path):
            continue

        # Move .wav files
        if file_name.lower().endswith(".wav"):
            destination_path = os.path.join(wav_dir, file_name)
            shutil.move(source_path, destination_path)
            print(f"Moved: {file_name} -> {destination_path}")

        # Move .mp3 files
        elif file_name.lower().endswith(".mp3"):
            destination_path = os.path.join(mp3_dir, file_name)
            shutil.move(source_path, destination_path)
            print(f"Moved: {file_name} -> {destination_path}")

input_file = "<ENTER-INPUT-FILE-PATH>"  # Path to your input Excel file
output_file = "<ENTER-OUTPUT-FILE-PATH>"  # Path to save the updated Excel file
save_path = "./download"         # Directory to save the audio files
start_row = 5001                     # Starting row (inclusive, 1-based index)
end_row = 6000                     # Ending row (inclusive, 1-based index)

process_uris_from_excel(input_file, output_file, save_path, start_row, end_row)
organize_audio_files(save_path)