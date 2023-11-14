from typing import Dict, Tuple, List
import pandas as pd
from datetime import datetime, timedelta
from requests.exceptions import HTTPError

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth

# For get_token_header() function:
from dotenv import load_dotenv
import os
import base64
from requests import post, get
import json
load_dotenv()


def auth_client():
    """
    Authenticate user with Client Credential Flow. 
    Assumes SPOTIPY_CLIENT_ID and SPOTIPY_CLIENT_SECRET env vars have been setup.

    May not be needed at all anymore (entirely replaced by auth_flow()).
    """
    return spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())

def auth_flow():
    """
    Authenticate user with Authorization Code Flow.
    Needed for accessing Spotify account and associated actions (ex: add to playlist).
    """
    auth_manager = SpotifyOAuth(
        redirect_uri = 'http://localhost:8080',
        scope=["playlist-modify-private",
               "playlist-modify-public",
               "user-read-currently-playing",
               "user-read-playback-state",
               "user-modify-playback-state"])
    #List of scopes: https://developer.spotify.com/documentation/web-api/concepts/scopes
    return spotipy.Spotify(auth_manager=auth_manager)


def get_token_header() -> Dict[str, str]:
    """Setup function to allow for artist or song searching."""
    # Most of this function is from https://www.youtube.com/watch?v=WAmEZBEeNmg&t=1002s
    client_id = os.getenv("SPOTIPY_CLIENT_ID")
    secret_key = os.getenv("SPOTIPY_CLIENT_SECRET")
    auth_string = client_id + ":" + secret_key
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    url = "https://accounts.spotify.com/api/token"
    headers = {"Authorization": "Basic " + auth_base64,
               "Content-Type": "application/x-www-form-urlencoded"}
    data = {"grant_type": "client_credentials"}
    result = post(url, headers=headers, data=data)
    json_result = json.loads(result.content)
    token = json_result["access_token"]
    search_header = {"Authorization": "Bearer " + token}
    return search_header


def find_artists(search_header: Dict[str, str], artist_names: List[str]) -> pd.DataFrame:
    """Take in header and list of artists and return df containing artist info and URI."""
    name, genres, popularity, uri, img_url = [], [], [], [], []
    search_url = "https://api.spotify.com/v1/search"
    for artist_name in artist_names:
        query = f"?q={artist_name}&type=artist&limit=1"
        #Could modify this query to instead search for songs, playlists, etc.
        result = get(search_url + query, headers=search_header)
        artist_info = json.loads(result.content)["artists"]["items"][0]

        # Prints a warning if result of query isn't exactly what was searched
        name_query_result = artist_info['name']
        if name_query_result.upper() != artist_name.upper():
            print(f"Warning: Searching for {artist_name} yielded result {name_query_result}.")
        
        name.append(name_query_result)
        genres.append(artist_info['genres'])
        popularity.append(artist_info['popularity'])
        uri.append(artist_info['uri'].split(':')[-1])
        if artist_info['images']: # If artist has an image
            img_url.append(artist_info['images'][-1]['url'])
        else:
            img_url.append(None)
            
    df = pd.DataFrame({'Artist': name,
                       'Genres': genres,
                       'Popularity': popularity,
                       'uri': uri,
                       'img_url': img_url,
                       })
    return df


def top_tracks(spot: spotipy.Spotify, df_artists: pd.DataFrame) -> pd.DataFrame:
    songs, artists, song_popularities = [], [], []
    danceabilities, energies, tempos, speechinesses = [], [], [], []
    artist_genres, artist_popularities, artist_uris, song_uris = [], [], [], []
    
    for i, row in df_artists.iterrows():
        try:
            top_tracks = spot.artist_top_tracks(row['uri'])['tracks']
        except HTTPError as e:
            if e.response.status_code == 429:
                # Rate limit reached, wait for Retry-After seconds
                retry_after = int(e.response.headers.get('Retry-After', 10))
                print(f"Rate limit reached. Waiting for {retry_after} seconds.")
                wait_until = datetime.now() + timedelta(seconds=retry_after)
                while datetime.now() < wait_until:
                    # Wait until the specified time
                    pass
                # Retry the request
                top_tracks = spot.artist_top_tracks(row['uri'])['tracks']
            else:
                # Handle other HTTP errors
                print(f"HTTP error: {e}")
                continue

        for track in top_tracks:
            songs.append(track['name'])
            song_popularities.append(track['popularity'])
            song_uris.append(track['uri'].split(':')[-1])
            
            artists.append(row['Artist'])
            artist_genres.append(row['Genres'])
            artist_popularities.append(row['Popularity'])
            artist_uris.append(row['uri'])
            
            features = spot.audio_features(track['uri'])[0]
            if features:
                danceabilities.append(features['danceability'])
                energies.append(features['energy'])
                tempos.append(features['tempo'])
                speechinesses.append(features['speechiness'])
            else:
                danceabilities.append(None)
                energies.append(None)
                tempos.append(None)
                speechinesses.append(None)
            
    df = pd.DataFrame({'Song': songs,
                       'Artist': artists,
                       'Song Popularity': song_popularities,
                       'Danceability': danceabilities,
                       'Energy': energies,
                       'Tempo': tempos,
                       'Speechiness': speechinesses,
                       "Artist's Genres": artist_genres,
                       "Artist's Popularity": artist_popularities,
                       'Artist URI': artist_uris,
                       'Song URI': song_uris})
    return df


def create_playlist(playlist_name: str, spot: spotipy.Spotify, df_songs: pd.DataFrame):
    user = os.getenv("SPOTIFY_USER")
    playlist_id = spot.user_playlist_create(user=user, name=playlist_name, public=is_public,
                                            description='Created using Spotipy.')
    song_list = [uri for uri in df_songs['Song URI']]
    #playlist_add_items() method can only pass 100 songs per call, so added:
    song_list_split = [song_list[i*100: (i+1)*100] for i in range((len(song_list) + 99) // 100)]
    for song_sub_list in song_list_split:
        spot.playlist_add_items(playlist_id['uri'], song_sub_list)
