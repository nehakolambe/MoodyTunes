import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# Spotify API credentials
CLIENT_ID = "<ENTER-YOUR-CLIENT-ID>"
CLIENT_SECRET = "<ENTER-YOUR-CLIENT-SECRET>"

# Authenticate with Spotify
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET))

# Read the Excel file
input_file = "<PROVIDE-INPUT-FILE>"  # Replace with your Excel file name
df = pd.read_excel(input_file)

# Check if required columns exist
required_columns = ['spotify_uri', 'track_name', 'artist_name']
if not all(col in df.columns for col in required_columns):
    raise ValueError("The Excel file must contain 'uri', 'track_name', and 'artist_name' columns.")

# Find rows with empty 'track_name' and 'artist_name'
empty_rows = df[df['track_name'].isnull() & df['artist_name'].isnull()]

# Get URIs from rows with missing data
uris = empty_rows['spotify_uri'].tolist()

# Spotify API can handle up to 50 URIs in one request
batch_size = 50
updated_rows = []

for i in range(0, len(uris), batch_size):
    batch_uris = uris[i:i+batch_size]
    
    # Call Spotify API to get track details
    try:
        tracks = sp.tracks(batch_uris)
    except Exception as e:
        print(f"Error fetching details for URIs: {batch_uris}\nError: {e}")
        continue

    for track in tracks['tracks']:
        if track:  # Check if track data is valid
            uri = track['uri']
            track_name = track['name']
            artist_name = ', '.join(artist['name'] for artist in track['artists'])
            updated_rows.append({'spotify_uri': uri, 'track_name': track_name, 'artist_name': artist_name})

# Convert updated rows to DataFrame
updated_df = pd.DataFrame(updated_rows)

# Merge updated data with the original DataFrame
df = df.merge(updated_df, on='spotify_uri', how='left', suffixes=('', '_updated'))

# Update the 'track_name' and 'artist_name' columns
df['track_name'] = df['track_name'].fillna(df['track_name_updated'])
df['artist_name'] = df['artist_name'].fillna(df['artist_name_updated'])

# Drop helper columns
df = df.drop(columns=['track_name_updated', 'artist_name_updated'])

df.to_excel(input_file, index=False)
print(f"Updated Excel file saved as {input_file}")