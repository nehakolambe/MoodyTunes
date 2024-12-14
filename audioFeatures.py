import librosa
import numpy as np
import pandas as pd
import os

def extract_audio_features(file_path):
    try:
        # Load the audio file
        y, sr = librosa.load(file_path, sr=None, mono=True, duration=30.0, res_type='kaiser_fast')
        
        # Extract features
        features = {
            # Temporal Features
            "zero_crossing_rate": np.mean(librosa.feature.zero_crossing_rate(y)[0]),
            "tempo": librosa.beat.tempo(y=y, sr=sr)[0],
            
            # Spectral Features
            "spectral_centroid": np.mean(librosa.feature.spectral_centroid(y=y, sr=sr)),
            "spectral_bandwidth": np.mean(librosa.feature.spectral_bandwidth(y=y, sr=sr)),
            "spectral_rolloff": np.mean(librosa.feature.spectral_rolloff(y=y, sr=sr)),
            "spectral_contrast": np.mean(librosa.feature.spectral_contrast(y=y, sr=sr)),
            
            # Harmonic Features
            "mfcc_mean": np.mean(np.mean(librosa.feature.mfcc(y=y, sr=sr), axis=1).tolist()),
            "chroma_stft_mean": np.mean(np.mean(librosa.feature.chroma_stft(y=y, sr=sr), axis=1).tolist()),
            "tonnetz_mean": np.mean(np.mean(librosa.feature.tonnetz(y=librosa.effects.harmonic(y), sr=sr), axis=1).tolist()),
            
            # Energy Features
            "rms_energy": np.mean(librosa.feature.rms(y=y)),
            
            # Perceptual Features
            "loudness": np.mean(librosa.amplitude_to_db(np.abs(y))),
        }
        return features
    
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return None


def process_audio_files(folder_path, output_excel):
    features_list = []

    # Get all MP3 file paths
    audio_files = [os.path.join(folder_path, file) for file in os.listdir(folder_path) if file.endswith(".mp3")]
    print(f"Found {len(audio_files)} MP3 files to process.")

    for i, file_path in enumerate(audio_files, 1):
        print(f"Processing {i}/{len(audio_files)}: {file_path}")
        features = extract_audio_features(file_path)
        if features:
            features["file_name"] = os.path.basename(file_path)
            features_list.append(features)
        
        # Save progress to XLSX every 100 files
        if i % 100 == 0:
            print(f"Saving progress to {output_excel}...")
            pd.DataFrame(features_list).to_excel(output_excel, index=False)
    
    # Save final DataFrame to XLSX
    print("Saving final dataset to Excel...")
    pd.DataFrame(features_list).to_excel(output_excel, index=False)
    print(f"Feature extraction completed and saved to {output_excel}!")


if __name__ == "__main__":
    # Folder containing MP3 files
    mp3_folder = "downloads/mp3"
    # Path to save the XLSX file
    output_excel = "<PATH-TO-SAVE-OUTPUT-FILE>"

    # Process all MP3 files and save to XLSX
    process_audio_files(mp3_folder, output_excel)