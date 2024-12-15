import pandas as pd
import requests
import hashlib
import re
import time
import enchant

# Last.fm API Key
LASTFM_API_KEY = "<ENTER-YOUR-LASTFM-API-KEY>"

def search_lastfm_track(artist, track, api_key):
    """
    Search for a track on Last.fm by artist and track name.
    """
    url = "http://ws.audioscrobbler.com/2.0/"
    params = {
        "method": "track.search",
        "artist": artist,
        "track": track,
        "api_key": api_key,
        "format": "json"
    }

    try:
        response = requests.get(url, params=params)
        if response.status_code == 200: 
            print('Last.fm API: 200 - Response was successfully received.')
            results = response.json().get("results", {}).get("trackmatches", {}).get("track", [])
        elif response.status_code == 401:
            print('Last.fm API: 401 - Unauthorized. Please check your API key.')
            exit()
        elif response.status_code == 403:
            print('Last.fm API: 403 - Forbidden. Please check your API key.')
            exit()
        elif response.status_code == 429:
            print('Last.fm API: 429 - Too many requests. Waiting 60 seconds.')
            time.sleep(60)
        else:
            print('Last.fm API: Unspecified error. No response was received. Trying again after 60 seconds...')
            time.sleep(60)
    except OSError as err:
        print('Error: ' + str(err))
        print('Trying again...')
        time.sleep(3)
    if results:
        return results[0].get("url", None)
    return None

def generate_md5_hash(value):
    if value:
        return hashlib.md5(value.encode('utf-8')).hexdigest()
    return None

def get_lastfm(params, api_key):
    url = "http://ws.audioscrobbler.com/2.0/"
    params["api_key"] = api_key
    params["format"] = "json"

    try:
        response = requests.get(url, params=params)
        if response.status_code == 200: 
            print('Last.fm API: 200 - Response was successfully received.')
        elif response.status_code == 401:
            print('Last.fm API: 401 - Unauthorized. Please check your API key.')
            exit()
        elif response.status_code == 403:
            print('Last.fm API: 403 - Forbidden. Please check your API key.')
            exit()
        elif response.status_code == 429:
            print('Last.fm API: 429 - Too many requests. Waiting 60 seconds.')
            time.sleep(60)
        else:
            print('Last.fm API: Unspecified error. No response was received. Trying again after 60 seconds...')
            time.sleep(60)
    except OSError as err:
        print('Error: ' + str(err))
        print('Trying again...')
        time.sleep(3)
    return response.json()

def getTopTags(annotations, api_key):
    for i in range(len(annotations)):
        try:
            print(f'\nGet top tags for track {i+1}/{len(annotations)}')

            # Fetch top tags from Last.fm API
            track_tags_json = get_lastfm({
                'method': 'track.getTopTags',
                'artist': annotations.at[i, 'artist_name'],
                'track': annotations.at[i, 'track_name']
            }, api_key)

            # Process top tags and update annotations
            if 'toptags' in track_tags_json and 'tag' in track_tags_json['toptags']:
                track_tags_list = pd.DataFrame(track_tags_json['toptags']['tag'])
                for j in range(len(track_tags_list)):
                    tag_name = track_tags_list.at[j, 'name']
                    tag_count = int(track_tags_list.at[j, 'count'])

                    # Add a column for the tag if not already present
                    if tag_count >= 50 and tag_name not in annotations.columns:
                        annotations[tag_name] = 0

                    # Mark the tag for this track
                    if tag_count >= 50:
                        annotations.at[i, tag_name] = 1
            else:
                print(f"Error: No tags found for track {annotations.at[i, 'track_name']} by {annotations.at[i, 'artist_name']}. Skipping.")
        except Exception as e:
            print(f"Error processing track {i+1}: {e}")

    return annotations

def tokenize_tag(tag):
    return set(re.split(r"[_\s-]", tag))

# Group tags based on overlapping token sets
def group_tags_by_tokens(tags):
    grouped = []
    visited = set()
    
    for i, tag in enumerate(tags):
        if tag in visited:
            continue
        
        # Tokenize current tag
        token_set = tokenize_tag(tag)
        group = [tag]
        visited.add(tag)

        # Compare against all other tags
        for other_tag in tags:
            if other_tag in visited:
                continue
            
            other_token_set = tokenize_tag(other_tag)
            if token_set & other_token_set:  # Check for overlapping tokens
                group.append(other_tag)
                visited.add(other_tag)
        
        grouped.append(group)
    return grouped

# Function to check if a tag contains valid dictionary words
def is_valid_word(tag):
    dictionary = enchant.Dict("en_US")
    if not tag.isalpha():
        return False
    return dictionary.check(tag)


def clean_and_merge_tags(annotations):
    with open("tags.txt", "r") as file:
        tags = [tag.strip("' ").lower() for tag in file.read().split(",")]

    # Group tags
    batch_synonyms = group_tags_by_tokens(tags)
    tags_synonyms = [group for group in batch_synonyms if len(group) >= 2]
    print("Processing synonyms")
    for tags_synonyms_current in tags_synonyms:
        tags_synonyms_drop_list = []
        for synonym in tags_synonyms_current:
            if synonym in annotations.columns:
                tags_synonyms_drop_list.append(synonym)
        if len(tags_synonyms_drop_list) > 1:
            annotations[tags_synonyms_drop_list] = annotations[tags_synonyms_drop_list].apply(pd.to_numeric, errors='coerce').fillna(0)
            annotations[tags_synonyms_drop_list[0]] = annotations[tags_synonyms_drop_list].max(axis=1)
            annotations = annotations.drop(tags_synonyms_drop_list[1:], axis=1)

    print("Processing Irrevalant tags")

    irrelavant_tags_file_path = "irrelavant_tags.txt"  # Replace with your file path
    with open(irrelavant_tags_file_path, "r") as file:
        words = file.read().split("\n")

    # Filter words with "- " prefix
    filtered_words = [word.strip() for word in words if word.strip().startswith("- ")]

    # Remove the "- " prefix for clean output
    tags_unrelevant = [re.sub(r"^- ", "", word) for word in filtered_words]

    for tag in tags:
        try:
            if not is_valid_word(tag):
                tags_unrelevant.append(tag)
        except:
            pass
    # print(len(tags_unrelevant))
    for tags_unrelevant_current in tags_unrelevant:
        if tags_unrelevant_current in annotations.columns:
            annotations = annotations.drop(tags_unrelevant_current, axis=1)
    
    print("Cleaning tags")
    # Clean tag names
    toptags_list_cleaned = list(annotations.columns)
    toptags_list_cleaned = [x.lower() for x in toptags_list_cleaned]  # Make all tags lowercase
    for i in range(len(toptags_list_cleaned)):
        tag_current_split = re.split(' |-', toptags_list_cleaned[i])
        if len(tag_current_split) > 1:
            temp_string = tag_current_split[0]
            for j in range(1, len(tag_current_split)):
                temp_string = temp_string + '_' + tag_current_split[j]
            toptags_list_cleaned[i] = temp_string
    annotations.columns = toptags_list_cleaned
    return annotations

def remove_invalid_rows(annotations):
    # Drop rows where 'url_lastfm' is None
    annotations = annotations.dropna(subset=["url_lastfm"])

    # Drop rows where all tag columns (binary values) are 0"
    tag_columns = [col for col in annotations.columns if col not in ["spotify_uri", "track_name", "artist_name", "url_lastfm", "id_dataset","unnamed:_0.1","unnamed:_0","duration_(ms)","danceability","energy",
                                                                     "loudness","speechiness","acousticness","instrumentalness","liveness","valence","tempo","spec_rate","labels"]]
    annotations = annotations.loc[annotations[tag_columns].sum(axis=1) > 0]
    return annotations

def create_annotations(input_file, api_key):
    # Load the Excel file
    df = pd.read_excel(input_file)

    # Check if necessary columns exist
    if not {"spotify_uri", "track_name", "artist_name"}.issubset(df.columns):
        raise ValueError("Input file must contain 'spotify_uri', 'track_name', and 'artist_name' columns.")

    # Initialize lists for Last.fm URLs and dataset IDs
    lastfm_urls = []
    dataset_ids = []

    # Iterate through each row and fetch the Last.fm URL
    for index, row in df.iterrows():
        try:
            track_name = row["track_name"]
            artist_name = row["artist_name"]

            # Get the Last.fm URL
            lastfm_url = search_lastfm_track(artist_name, track_name, api_key)
            lastfm_urls.append(lastfm_url)

            # Generate dataset ID using MD5 hash of the Last.fm URL
            dataset_id = generate_md5_hash(lastfm_url)
            dataset_ids.append(dataset_id)

            # Print progress
            print(f"[{index + 1}/{len(df)}] {track_name} by {artist_name}: {lastfm_url} -> {dataset_id}")
        except Exception as e:
            print(f"Error processing row {index + 1}: {e}")
            lastfm_urls.append(None)
            dataset_ids.append(None)

    # Add or update the 'url_lastfm' column
    if "url_lastfm" in df.columns:
        df["url_lastfm"] = lastfm_urls
    else:
        df["url_lastfm"] = lastfm_urls

    # Add or update the 'id_dataset' column
    if "id_dataset" in df.columns:
        df["id_dataset"] = dataset_ids
    else:
        df["id_dataset"] = dataset_ids

    # Fetch top tags and update annotations
    df = getTopTags(df, api_key)

    # Clean and merge tags
    df = clean_and_merge_tags(df)

    # Remove invalid rows
    df = remove_invalid_rows(df)

    # Overwrite the input file with updated data
    df.to_excel(input_file, index=False)
    print(f"\nInput file '{input_file}' has been updated with new columns and top tags.")


    # Return the DataFrame for annotation
    return df

if __name__ == "__main__":
    # Input Excel file path
    input_file = "<ENTER-YOUR-INPUT-FILE>"  # Replace with your input file
    try:
        annotations = create_annotations(input_file, LASTFM_API_KEY)
    except Exception as e:
        print(f"Error: {e}")