###############################################################################
#
# This file contains utility functions for using Spotipy/Spotify API:
#   - auth_flow authenticates user
#   - get_token_header creates search header for artist querying
#   - capitalize_genre is a helper function to capitalize genres, including
#      common genre acronyms, in the succeeding search_for_artists function
#   - search_for_artists queries for specific artists and returns a df
#      containing important artist info (uri, popularity, genres, img url)
#   - retry_spotify_request is a helper function to retry Spotify API
#      requests in the following top_tracks function
#   - recommend_artists returns similar artists to those in playlist
#   - get_top_tracks gets the top 1-10 songs for each artist and returns a df
#      containing song metadata (uri, popularity, danceability, etc)
#   - create_playlist creates a new playlist for many songs
#
###############################################################################

import base64
from collections import Counter
import json
import os
import time
from typing import Any, Callable, Dict, List, Tuple

import pandas as pd
import requests

from spotipy import Spotify
from spotipy.client import SpotifyException
from spotipy.oauth2 import SpotifyOAuth


def auth_flow() -> Spotify:
    """
    Authenticate user with Authorization Code Flow
    (as opposed to Client Credential Flow).

    Parameters:
        None

    Returns:
        Spotify: Authenticated Spotify instance.

    Needed for accessing Spotify account and associated actions
    (ex: adding songs to playlist).

    List of scopes available at:
    https://developer.spotify.com/documentation/web-api/concepts/scopes
    """
    
    auth_manager = SpotifyOAuth(
        redirect_uri = 'http://localhost:8080',
        scope=[
            "playlist-modify-private",
            "playlist-modify-public",
            "user-read-currently-playing",
            "user-read-playback-state",
            "user-modify-playback-state"
        ]
    )
    
    return Spotify(auth_manager=auth_manager)


def get_token_header() -> Dict[str, str]:
    """
    Setup function to allow for artist or song searching.

    Parameters:
        None

    Returns:
        Dict[str, str]: Search header for Spotify API.
    """

    # Get environment variable values to use Spotipy API
    SPOTIPY_CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
    SPOTIPY_CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")

    # Create authorization string
    auth_string = f"{SPOTIPY_CLIENT_ID}:{SPOTIPY_CLIENT_SECRET}"
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    # Spotify API token request
    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}

    # Make post request to obtain token
    response = requests.post(url, headers=headers, data=data)

    # Parse JSON response
    json_response = json.loads(response.content)
    token = json_response["access_token"]

    # Create and return search header
    search_header = {"Authorization": "Bearer " + token}
    return search_header


def capitalize_genre(genre):
    """
    Title case genre and capitalize acronyms if in the acronyms dictionary.

    Parameters:
        genre (str): Input genre.

    Returns:
        str: Capitalized genre.

    Examples:
        'funk rock'  -> 'Funk Rock'
        'edm'        -> 'EDM'
        'pov: indie' -> 'POV: Indie'
        'uk garage'  -> 'UK Garage'

    List of all 6,300 Spotify genres available at:
    https://everynoise.com/everynoise1d.cgi?scope=all
    """

    # Acronyms (dict keys) and what they'll be replaced with (dict values).
    # Probably non-exhaustive. Others can be added over time as discovered.
    acronyms = {
        'Edm': 'EDM',
        'Dnb': 'DnB',
        'Uk': 'UK',
        'Pov': 'POV',
        'Mbp': 'MBP',
        'Atl': 'ATL',
        'Nyc': 'NYC',
    }

    # Convert the genre string to the preferred capitalization format
    genre = genre.title()
    for key, value in acronyms.items():
        if key in genre:
            genre = genre.replace(key, value)
            
    return genre


def search_for_artists(
    search_header: Dict[str, str],
    artist_names: List[str]
) -> pd.DataFrame:
    """
    Query for specific artists. Finds top query for each artists in
    artist_names list, then returns a DataFrame containing important
    artist info.

    Parameters:
        search_header (Dict[str, str]): Search header for Spotify API.
        artist_names (List[str]): List of artist names.

    Returns:
        pd.DataFrame: DataFrame with artist information. Columns:
            Artist - str
            Artist Genres - List[str] (may be an empty list)
            Artist Popularity - int (between 1-100)
            Artist uri - str
            Artist Image url - str
    """

    # If a single artist name is entered as a string, convert it to list
    if isinstance(artist_names, str):
        artist_names = [artist_names]

    # Initialize lists to store artist information
    name = []
    all_genres = []
    popularity = []
    uri = []
    img_url = []

    # Establish search url for artist querying
    search_url = "https://api.spotify.com/v1/search"

    # Loop through every artist name to get all artists' info
    for artist_name in artist_names:
        # Build API query and make the API request
        # Note: This query can be modified to instead search
        # for songs, playlists, etc.
        query = f"?q={artist_name}&type=artist&limit=1"
        response = requests.get(
            search_url + query,
            headers=search_header
        )
        artist_info = json.loads(response.content)["artists"]["items"][0]

        # Prints a warning if result of query isn't exactly
        # what was searched (ex: Tiesto vs Tiësto)
        name_query_result = artist_info['name']
        if name_query_result.upper() != artist_name.upper():
            print(
                f"Warning: Searching for {artist_name} "
                f"yielded result {name_query_result}."
            )

        # Extract artist genres and convert to preferred capitalization format
        genres = artist_info['genres']
        genres_capitalized = [capitalize_genre(genre) for genre in genres]

        # Extract and append artist information to lists
        name.append(name_query_result)
        popularity.append(artist_info['popularity'])
        uri.append(artist_info['uri'].split(':')[-1])
        all_genres.append(genres_capitalized)

        # Get artist image url for image use in GUI        
        if artist_info['images']: # If artist has an image
            img_url.append(artist_info['images'][-1]['url'])
        else:
            img_url.append(None)

    # Create DataFrame from collected information
    df_artists = pd.DataFrame({
        'Artist': name,
        'Artist Genres': all_genres,
        'Artist Popularity': popularity,
        'Artist uri': uri,
        'Artist Image url': img_url,
    })
    
    return df_artists


def retry_spotify_request(func: Callable[..., Any], *args: Tuple) -> Any:
    """
    Helper function to retry a Spotify API request if a rate limit is reached.

    Parameters:
        func: Spotify API function to be retried.
        *args: Variable arguments for the function.

    Returns:
        Any: Result of the successful API request or None if unsuccessful.
    """
    try:
        return func(*args)
    
    except SpotifyException as e:
        if e.http_status == 429:
            # Rate limit reached, wait for Retry-After seconds
            retry_after = int(e.headers.get('Retry-After', 10))
            print(f"Rate limit reached. Waiting for {retry_after} seconds.")
            time.sleep(retry_after)
            
            # Retry the request
            return retry_spotify_request(func, *args)
        
        else:
            # If some other SpotifyException error, print error
            print(f"SpotifyException: {e}")
            return None

        
def recommend_artists(
    spot: Spotify,
    df_artists: pd.DataFrame,
    num_recs: int=3
) -> List[str]:
    """
    Recommends new artists based on artists related to those in df_artists.
    The artist_related_artists method give 20 artist recommendations for any
    artist. This method is called for each artist in df_artists; repeated
    artist recommendations are counted and the top recurring artist names
    are returned.

    Parameters:
        spot: Spotify object for making API requests
        df_artists: DataFrame. Can be df_songs or df_artists
            (df argument is used just to see unique playlist artists)
        num_recs: Number of recommended artists to return (default is 3)

    Returns:
        List[str]: List of recommended artist names.

    Note: Spotipy also has a recommendations() method that returns track recs
    (as opposed to artist recs). An alternative solution using that approach
    may be useful.
    """
    
    artist_counter = {}  # Empty counter dict

    # Iterate over each artist in the dataframe
    artist_uris = list(df_artists['Artist uri'].unique()) # Unique Artist URIs
    for artist_uri in artist_uris:
        artist_recs = retry_spotify_request(
            spot.artist_related_artists,
            artist_uri
        )['artists']
        if artist_recs: # List of 20 artist dicts, if no requests error
            for rec in artist_recs:
                artist_name = rec['name']
                # Increment dict counter for artist rec
                if artist_name not in artist_counter:
                    artist_counter[artist_name] = 1
                else:
                    artist_counter[artist_name] += 1

    # Remove artists that are in df_artists from counter dict
    for artist in df_artists['Artist'].unique():
        artist_counter.pop(artist, None)

    # Get the top num_recs highest occurring artists
    top_artists_count = Counter(artist_counter).most_common(num_recs)
    # top_artists_count is a list of tuples [(artist name, count), ...]

    # Extract the artist names from the list of tuples
    top_artist_recs = [artist[0] for artist in top_artists_count]

    return top_artist_recs


def get_top_tracks(
    spot: Spotify,
    df_artists: pd.DataFrame,
    tracks_per_artist: int=10
) -> pd.DataFrame:
    """
    Creates DataFrame containing rows of songs for selected artists.

    Parameters:
        spot (Spotify): Authenticated Spotify instance.
        df_artists (pd.DataFrame): DataFrame containing artist info.
        tracks_per_artist (int, optional): Number of tracks per artist to
            include in playlist.

    Returns:
        pd.DataFrame: DataFrame with song metadata. Columns:
            Song - str
            Artist - str
            Song Popularity - int (between 1-100)
            Danceability - float (between 0-1)
            Energy - float (between 0-1)
            Tempo - float (beats per minute)
            Speechiness - float (between 0-1)
            Song Duration - int (in ms)
            Artist Genres - List[str] (may be an empty list)
            Artist Popularity - int (between 1-100)
            Artist uri - str
            Song uri - str
            Artist Image url - str

    Note: Track feature descriptions available at:
    https://developer.spotify.com/documentation/web-api/reference/
    get-audio-features
    """

    # Initialize lists to store song/track and artist information

    # Song/Track general info:
    songs = []
    song_popularities = []
    song_durations = []
    song_uris = []

    # Song/track features:
    danceabilities = []
    energies = []
    tempos = []
    speechinesses = []

    # Artist info
    artists = []
    artist_genres = []
    artist_popularities = []
    artist_uris = []
    artist_img_url  = []

    # Iterate through each artist in the DataFrame
    for i, row in df_artists.iterrows():
        top_tracks = retry_spotify_request(
            spot.artist_top_tracks,
            row['Artist uri']
        )['tracks']

        for track in top_tracks[:tracks_per_artist]:
            # Append track info
            songs.append(track['name'])
            song_popularities.append(track['popularity'])
            song_durations.append(track['duration_ms'])
            song_uris.append(track['uri'].split(':')[-1])

            # Append artist info for each song row
            artists.append(row['Artist'])
            artist_genres.append(row['Artist Genres'])
            artist_popularities.append(row['Artist Popularity'])
            artist_uris.append(row['Artist uri'])
            artist_img_url.append(row['Artist Image url'])

            # Ensure there are track features, otherwise append None
            features = retry_spotify_request(
                spot.audio_features,
                track['uri']
            )[0]
            if features: # Append track features
                danceabilities.append(features['danceability'])
                energies.append(features['energy'])
                tempos.append(features['tempo'])
                speechinesses.append(features['speechiness'])
                
            # Edge case if artist query yields non-music page.
            # Ex: If user misspells an artist name and the search result is
            # "Air Conditioner Sounds"
            else: # No track features to append. Append None for that row.
                danceabilities.append(None)
                energies.append(None)
                tempos.append(None)
                speechinesses.append(None)

    # Create DataFrame from collected information
    df_songs = pd.DataFrame({
        'Song': songs,
        'Artist': artists,
        'Song Popularity': song_popularities,
        'Danceability': danceabilities,
        'Energy': energies,
        'Tempo': tempos,
        'Speechiness': speechinesses,
        'Song Duration': song_durations,
        'Artist Genres': artist_genres,
        'Artist Popularity': artist_popularities,
        'Artist uri': artist_uris,
        'Song uri': song_uris,
        'Artist Image url': artist_img_url,
    })
    
    return df_songs


def create_playlist(
    playlist_name: str,
    spot: Spotify,
    df_songs: pd.DataFrame
) -> str:
    """
    Creates a new Spotify playlist and adds songs to it from DataFrame.

    Parameters:
        playlist_name (str): Name of the new playlist.
        spot (Spotify): Authenticated Spotify instance.
        df_songs (pd.DataFrame): DataFrame with song and artist metadata.

    Returns:
        str: URI of the created playlist
    """

    # Get the user's Spotify ID
    user = os.getenv("SPOTIFY_USER")

    # Create a new playlist and get playlist URI
    playlist = spot.user_playlist_create(
        user=user,
        name=playlist_name,
        public=True,
        description='Created using Spotipy.'
    )
    playlist_uri = playlist['uri']

    # Get list of song URIs from df_songs
    song_uris = df_songs['Song uri'].tolist()
    
    # Add songs to playlist in batches of 100.
    # Note: playlist_add_items() method can only pass 100 songs per call
    batch_size = 100
    for i in range(0, len(song_uris), batch_size):
        batch_uris = song_uris[i : i + batch_size]
        spot.playlist_add_items(playlist_uri, batch_uris)

    return playlist_uri