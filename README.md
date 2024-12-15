# MoodyTunes

## Overview

### 1. Initial Dataset Details

* Source Dataset: A subset of approximately 5000 songs was selected from the original 278K song dataset.
* Columns: The dataset includes nine features: danceability, energy, loudness, speechiness, acousticness, instrumentalness, liveness, valence, tempo, and the Spotify URI.

### 2. Track and Artist Name Extraction

* Objective: Metadata (track and artist name) was required to fetch tags from LastFM, but these were missing.
* Solution:
  * Extracted track_id from the Spotify URI.
  * Queried the Spotify API using the track_id to fetch track name and artist name.

### 3. LastFM Tags

* Objective : Fetch tags for each song using the track name and artist name via the LastFM API.
* Results : Retrieved approximately 7000 tags in columnar format for the 5000 songs.

### 4. Preprocessing of Tags

* Challenges : A dataset with 7000 tag columns is computationally expensive and impractical for modeling.
* Steps Taken :
  * Cleaned tags by:
    * Removing unwanted spaces.
    * Grouping synonymous tags under unified categories.
  * Removing irrelevant or overly generic tags.
  * Performed correlation analysis on tags to identify and drop tags with less than  50% correlation threshold .
* Result : Reduced the tag count from  7000 to 35 relevant tags .

### 5. Fetching Preview URLs

* Objective: Download 30-second audio previews for feature extraction.
* Queried the Spotify API using track_id to retrieve preview_url links for each song.

### 6. Audio Download and Format Conversion

* Downloaded audio files using preview_url in both .mp3 and .wav formats.
* Stored the audio files for further processing.

### 7. Audio Feature Extraction

Once, audio were downlaoded and stored, we calculated the audio features -  Mel-frequency cepstral coefficients (MFCCs), Spectral centroid, Spectral rolloff, Chroma features, Tempo, Zero-crossing rate, Root mean square energy, Spectral contrast, Tonnetz for each track and saved them in the dataset

## Flow of the project

### 1. Install Requirement.txt

```
pip install -r requirements.txt
```

### 2. Run trackAndArtistName.py

* Enter spotify client Id and secret
* Enter path of old dataset in input_file variable i.e., data/old_dataset.xlsx
* ```
  python3 trackAndArtistName.py
  ```
* This creates 2 new columns called trackname and atrist_name on the dataset

### 3. Run datasetFormation.py

* Enter Last.fm API key
* Enter path of old dataset in input_file variable i.e., data/old_dataset.xlsx
* ```
  python3 datasetFormation.py
  ```
* This will get user tags for each track, preprocess tags, remove irrelavant tags, and saves tags in the form of columns in the dataset

### 4. Run correlation.py

* Enter path of old dataset in input_file variable i.e., data/old_dataset.xlsx
* ```
  python3 correlation.py
  ```
* This will eliminate tag columns whose correlation are less than ±5% i.e. loosely correlated

### 5. Run previewURL.py

* Enter path of old dataset in input_file variable i.e., data/old_dataset.xlsx
* ```
  python3 previewURL.py
  ```
* This will get 30 second preview URL of each track and save the URL in the dataset
* It will download 30 seconds audio for each track in MP3 and wav format and store it in ./downloads/mp3 and ./downloads/wav folder respectively

### 6. Run audioFeatures.py

* Enter path of old dataset in output_excel variable i.e., data/old_dataset.xlsx
* ```
  python3 audioFeatures.py
  ```
* Reads all the mp3 files in ./downlaods/mp3 folder
* Calculate audio features from the mp3 passed, create their columns and enter values of each feature for each track in the dataset

## Models

The models we've trained as part of this project can be found in the ./models folder

## Key Results

### 1. Dataset Enrichment

* Enhanced the original dataset (old_dataset) )by incorporating **35 user-generated tags** from Last.fm and **audio features** extracted from 30-second preview clips.
* Successfully created a comprehensive dataset by combining original features, refined tags, and detailed audio characteristics.

### 2. Improved Model Performance

* The enriched dataset consistently outperformed the original dataset across all models.

* **Artificial Neural Network (ANN)** achieved the highest accuracy of **90.67%** with the enriched dataset, up from **86.84%** on the original dataset.
* Significant accuracy improvements observed in other models:
  * **RCNN** : 90.03% (enriched) vs. 83.74% (original).
  * **LSTM** : 88.86% (enriched) vs. 84.41% (original).
  * **MLP** : 88.10% (enriched) vs. 84.44% (original).
  * **GRU** : 87.97% (enriched) vs. 81.51% (original).
  * **CNN** : 84.89% (enriched) vs. 83.16% (original).

### 3. Key Insights from Audio Features

* Audio features like  **energy** ,  **valence** , and **tempo** distinctly defined emotional moods:
  * **Energetic tracks** had high energy, loudness, and tempo.
  * **Calm tracks** exhibited high acousticness, instrumentalness, and lower dynamic range.
  * **Happy tracks** showed the highest positivity (valence), while **sad tracks** had the lowest.

### 4. Impact of Feature Enrichment

* Enrichment with user tags and detailed audio features significantly enhanced the models' ability to classify moods accurately.
* Models like ANN and RCNN demonstrated the greatest ability to leverage the enriched dataset.

### 5. Challenges Overcome

* Addressed the challenge of noisy and irrelevant tags by refining and grouping them into 35 meaningful categories.
* Successfully extracted additional audio features using Spotify preview clips despite computational constraints.

### 6. API Challenges

* Encountered and partially mitigated issues due to the **deprecation of Spotify’s audio-features and get-recommendations APIs** during testing.

### 7. Feature Trends

* Identified meaningful trends in audio features:
  * **Acousticness** dominated in calm moods, while **speechiness** peaked in energetic tracks.
  * **Zero-crossing rate** and **spectral centroid** were highest in energetic tracks, showcasing their bright and dynamic characteristics.

### 8. Overall Contribution

* Demonstrated the effectiveness of combining user-generated tags and audio features for mood-based music classification.
* Highlighted the importance of enriched datasets in achieving higher classification accuracy and generalization across deep learning models.
