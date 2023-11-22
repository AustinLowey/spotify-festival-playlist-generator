from datetime import datetime
from typing import Tuple

import pandas as pd

from gui1_launch import launch_gui
from festival_lineup_scraper import get_artist_names
from spotipy_utils import (
    auth_flow, get_token_header, search_for_artists,
    get_top_tracks, create_playlist
    )
from gui2_artist_selection import select_artist_names
from img_conversion import img_url_to_array
from playlist_analytics import (
    create_playlist_summary, create_artist_summary,
    create_feature_plots, create_dashboard
    )

def main(
    new_playlist: bool = True,
    analyze_playlist: bool = True,
    save_df_songs: bool = True,
    save_df_artists: bool = False
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Main function of Spotify Festival Playlist Generator.

    Parameters:
        new_playlist (bool): Flag indicating whether to create a new playlist.
        analyze_playlist (bool): Flag indicating whether to perform playlist analysis.
        save_df_songs (bool): Flag indicating whether to save song information as a CSV file.
        save_df_artists (bool): Flag indicating whether to save artist information as a CSV file.

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: A tuple containing DataFrames for songs and selected/new artists.

    
    Variable data types (in order of which they appear):
    
    songkick_url - str
    tracks_per_artist - int
    include_remixes - bool

    festival_name - str
    lineup_artist_names - List[str]

    spot - spotipy.Spotify
    search_header - Dict[str, str]

    df_lineup_artists (or any similar df_artists) - DataFrame with columns:
        Artist - str
        Artist Genres - List[str] (may be an empty list)
        Artist Popularity - int (between 1-100)
        Artist uri - str
        Artist img_url - str

    selected_artist_names - List[str]
    new_artist_names - List[str]

    df_new_artists/df_selected_artists/df_playlist_artists - all same columns as df_lineup_artists

    df_songs - DataFrame with columns:
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
        Artist img_url - str

    Note: Track feature descriptions available at
    https://developer.spotify.com/documentation/web-api/reference/get-audio-features

    This function requires prior setup of 3 environment variables: SPOTIPY_CLIENT_ID,
    SPOTIPY_CLIENT_SECRET, and SPOTIFY_USER. The first and second are used for retrieving
    artist top tracks and track metadata. The third links to a Spotify account.
    """
    
    # Launch first GUI screen, which asks for a URL, number of tracks per artist, and whether or not to include remixes
    songkick_url, tracks_per_artist, include_remixes = launch_gui()

    # Search songkick.com to get artist lineup and process festival name from URL 
    festival_name, lineup_artist_names = get_artist_names(songkick_url)

    # Set up Spotipy auth flow and artist search header
    spot = auth_flow()
    search_header = get_token_header()

    # Search Spotify for each artist name in lineup and get their genres, popularity, URI, and img URL
    df_lineup_artists = search_for_artists(search_header, lineup_artist_names)

    # Second GUI screen, which asks user to select from lineup artists and/or add other artists
    selected_artist_names, new_artist_names = select_artist_names(df_lineup_artists, festival_name)

    # Get new artist data and add it to df_artists
    df_new_artists = search_for_artists(search_header, new_artist_names) # Artists added (i.e., not in lineup)
    df_selected_artists = df_lineup_artists[df_lineup_artists['Artist'].apply(lambda x: x in selected_artist_names)] # Artists selected from lineup
    df_playlist_artists = pd.concat([df_selected_artists, df_new_artists], ignore_index=True) # Combine both
    df_playlist_artists = df_playlist_artists.drop_duplicates(subset='Artist').reset_index(drop=True) # Remove duplicates and reset df index

    # Get between 1-10 top tracks from each selected artist using Spotipy
    df_songs = get_top_tracks(spot, df_playlist_artists, tracks_per_artist)

    # Drop duplicates of the same song, if any (needed for if the same song is in the top 10 of multiple artists)
    df_songs = df_songs.drop_duplicates(subset='Song uri', keep='first').reset_index(drop=True)

    # Save df_songs as a .csv file
    if save_df_songs == True:
        today = datetime.now().strftime("%Y-%m-%d")
        df_songs.to_csv(f"csv_exports/{festival_name.replace(' ','')}Songs_Created{today}.csv", index=False)

    if save_df_artists == True:
        today = datetime.now().strftime("%Y-%m-%d")
        df_playlist_artists.to_csv(f"csv_exports/{festival_name.replace(' ','')}Artists_Created{today}.csv", index=False)  

    # Create a new playlist using df_songs
    if new_playlist == True:
        create_playlist(f"Spotipy Playlist - {festival_name}", spot, df_songs)

    # Perform feature analysis and create summary
    recommended_artists = ['Placeholder #1', 'Placeholder #2'] # Placeholder for future feature
    if analyze_playlist == True:
        summary_data = create_playlist_summary(
            df_songs, festival_name, recommended_artists
            )
        create_artist_summary(df_songs, festival_name)
        create_feature_plots(df_songs, festival_name)
        create_dashboard(summary_data, festival_name)

    return df_songs, df_playlist_artists


def main_offline() -> pd.DataFrame:
    """
    Perform an offline test of the Spotify Festival Playlist Generator.

    This function mimics the entire flow of the application, allowing for testing
    without making API requests. It is useful for getting feedback on the graphical
    user interface (GUI) without the need for internet connectivity or for users
    who haven't configured their Spotipy client/secret key and environment variables,
    but still want to try a demo.

    Returns:
        DataFrame: A DataFrame containing information about selected artists and new artists.
    """
    
    # Test first GUI screen
    songkick_url, tracks_per_artist, include_remixes = launch_gui()
    print("---Testing 1st GUI screen---")
    print(f"Songkick url: {songkick_url}")
    print(f"Number of tracks per artist: {tracks_per_artist}")
    print(f"Include remixes: {include_remixes}")
    print("----------------------------")

    # Offline substitute of the functions between the 2 GUIs
    try:
        festival_name = songkick_url.split("id/")[1].split("-", 1)[1].replace("-", " ").title()
    except:
        festival_name = "your music festival"
    df_lineup_artists = pd.read_csv("csv_exports/OfflineTestEdcLineupArtists.csv")
    df_lineup_artists['Artist Genres'] = df_lineup_artists['Artist Genres'].apply(eval) # Change string representation (from .csv) of genres to list
    print(f"Festival name from user-provided url is: {festival_name}")
    print("Offline version: Festival name overrided as 'Edc Orlando 2023'")
    print(f"df_lineup_artists (from EDC Orlando 2023) loaded from .csv file and has length {len(df_lineup_artists)}")
    print(f"df_lineup_artists has columns {df_lineup_artists.columns}")
    print("----------------------------")

    # Test second GUI screen
    selected_artist_names, new_artist_names = select_artist_names(df_lineup_artists, "Edc Orlando 2023")
    print("---Testing 2nd GUI screen---")
    print(f"Selected artist names (using button selection): {selected_artist_names}")
    print(f"New/added artist names: {new_artist_names}")
    print("----------------------------")

    # Offline substitute of updating the Artists df based on Artist Selection GUI
    df_new_artists = pd.read_csv("csv_exports/OfflineTestNewArtists.csv") # Artists added (i.e., not in lineup). Offline version.
    df_new_artists['Artist Genres'] = df_new_artists['Artist Genres'].apply(eval) # Change string representation (from .csv) of genres to list
    df_selected_artists = df_lineup_artists[df_lineup_artists['Artist'].apply(lambda x: x in selected_artist_names)] # Artists selected from lineup

    df_playlist_artists = pd.concat([df_selected_artists, df_new_artists], ignore_index=True) # Combine both
    df_playlist_artists = df_playlist_artists.drop_duplicates(subset='Artist').reset_index(drop=True) # Remove duplicates and reset df index
    
    playlist_artists_list = [row['Artist'] for i, row in df_playlist_artists.iterrows()] # To print artists in df_playlist_artists
    print("Offline version: New/added artist names overrided as ['John Summit', 'David Guetta']")
    print(f"Offline version: df_new_artists loaded from .csv file and has length {len(df_new_artists)}")
    print(f"Offline version: df_new_artists has columns {df_new_artists.columns}")
    print(f"df_selected_artists has length {len(df_selected_artists)}")
    print(f"df_selected_artists has columns {df_selected_artists.columns}")
    print(f"df_playlist_artists has length {len(df_playlist_artists)}")
    print(f"df_playlist_artists has columns {df_playlist_artists.columns}")
    print(f"df_playlist_artists has artists {playlist_artists_list}")
    print("----------------------------")

    return df_playlist_artists


if __name__ == "__main__":
    df_songs, df_playlist_artists = main()

"""
songkick.com URLs provided below for quick reference/testing:

Austin City Limits 2023 link:
ACL_URL = "https://www.songkick.com/festivals/129-austin-city-limits-music\
/id/41123551-austin-city-limits-music-festival-2023"

EDC Orlando 2023 link:
EDC_URL = "https://www.songkick.com/festivals/562824-edc-orlando\
/id/40754508-edc-orlando-2023"

Great North Folk Festival 2023 link (contains 1 artist in lineup):
GNF_URL = "https://www.songkick.com/festivals/1550489-great-north-folk\
/id/41010280-great-north-folk-festival-2023"

"""
