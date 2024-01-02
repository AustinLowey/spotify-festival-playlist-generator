import os
from datetime import datetime
from typing import Tuple

import pandas as pd

from gui.gui1ab_launch import launch_gui_start_screen
from gui.gui2a_festival_link import launch_gui_festival_link
from gui.gui3a_artist_selection import launch_gui_artist_selection
from gui.gui3b_artist_manual_entry import launch_gui_artist_manual_entry
from gui.gui4ab_song_customization import launch_gui_song_customization

from festival_lineup_scraper import get_artist_names
from spotipy_utils import (
    auth_flow, get_token_header, search_for_artists,
    recommend_artists, get_top_tracks, create_playlist
)
from playlist_mods import (
    remove_duplicates, remove_remixes_and_edits,
    filter_songs_by_artist_popularity, create_df_playlist_artists
)
from playlist_analytics import (
    create_playlist_summary, create_artist_summary,
    create_feature_plots, create_dashboard
)


def main(
    create_new_playlist: bool = True,
    analyze_playlist: bool = True,
    save_df_songs: bool = True,
    save_df_artists: bool = False
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Main function of Spotify Festival Playlist Generator.

    Parameters:
        create_new_playlist (bool): Flag indicating whether to create a new playlist.
        analyze_playlist (bool): Flag indicating whether to perform playlist
            analysis.
        save_df_songs (bool): Flag indicating whether to save song information
            as a CSV file.
        save_df_artists (bool): Flag indicating whether to save artist
            information as a CSV file.

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: A tuple containing DataFrames for
            songs and selected/new artists.

    
    DataFrames used throughout this function:

    df_artists (or any similarly-named df) - DataFrame with columns:
        Artist - str
        Artist Genres - List[str] (may be an empty list)
        Artist Popularity - int (between 1-100)
        Artist uri - str
        Artist Image url - str

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
        Artist Image url - str

    Note: Track feature descriptions available at
    https://developer.spotify.com/documentation/web-api/
    reference/get-audio-features

    This function requires prior setup of 3 environment variables:
    SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, and SPOTIFY_USER. The first and
    second are used for retrieving artist top tracks, track metadata, etc. The
    third links to a Spotify account.

    Depending on selection on the first GUI screen, the GUI sequence will be:
        Option a)   1ab -> 2a -> 3a -> 4ab
        Option b)   1ab ->       3b -> 4ab
    """
    
    # Launch GUI screen 1. Asks user if they want to create playlist from
    # a specific music festival or if they want to manually enter artist names.
    create_from_festival = launch_gui_start_screen()

    # Set up Spotipy auth flow and artist search header
    spot = auth_flow()
    search_header = get_token_header()

    while create_from_festival: # Create playlist for specific music festival

        # Launch GUI screen 2a. Prompts user for festival link. Also has
        # option to skip festival link step and enter artist names instead.
        festival_link, skip_this_step = launch_gui_festival_link()

        if skip_this_step: # Skip festival link search step
            print(
                "Skipping festival link screen."
                "Enter artists' names manually instead."
            )
            create_from_festival = False # End while loop

        else: # Search for festival, extract lineup, and get data for artists

            # Search songkick.com for lineup and process festival name from URL
            festival_name, lineup_artist_names = get_artist_names(
                festival_link
            )

            # Search Spotify for each artist name in festival lineup.
            df_lineup_artists = search_for_artists(
                search_header,
                lineup_artist_names
            )

            # GUI screen 3a. Select artists from lineup (and add other artists)
            selected_artist_names, new_artist_names = (
                launch_gui_artist_selection(
                    df_lineup_artists,
                    festival_name
                )
            )

            # Get new artist data and add it to df_artists
            df_new_artists = search_for_artists(
                search_header,
                new_artist_names
            ) # Artists added (i.e., not in lineup)
            df_playlist_artists = create_df_playlist_artists(
                df_lineup_artists,
                df_new_artists,
                selected_artist_names
            )

        break # End while loop

    if not create_from_festival: # Create playlist by manually entering artists

        # Launch GUI screen 3b. Prompts user to enter artist names manually.
        entered_artist_names = launch_gui_artist_manual_entry()

        # Get data for user-entered artists
        df_playlist_artists = search_for_artists(
            search_header,
            entered_artist_names
        )
        festival_name = "Custom Playlist"

    # Launch GUI screen 4. Contains multiple playlist customization options.
    (
        playlist_name,
        tracks_per_artist,
        artist_popularity_filtering,
        include_remixes
    ) = launch_gui_song_customization(df_playlist_artists, festival_name)

    # Get between 1-10 top tracks from each selected artist using Spotipy
    df_songs = get_top_tracks(spot, df_playlist_artists, tracks_per_artist)

    # Drop duplicates of the same song, if any
    df_songs, duplicate_songs_removed = remove_duplicates(df_songs)
    if duplicate_songs_removed:
        print(f"Duplicate songs removed: {duplicate_songs_removed}")

    # Drop multiple versions of songs if user selected this option
    if not include_remixes:
        df_songs, remix_songs_removed = remove_remixes_and_edits(df_songs)
        if remix_songs_removed:
            print("Multiple versions of song(s) present.\n")
            print(f"Songs removed: {remix_songs_removed}")

    # Adjust qty of songs per artist, scaling with artist popularity
    if artist_popularity_filtering:
        df_songs = filter_songs_by_artist_popularity(df_songs)

    # Create a new playlist using df_songs
    if create_new_playlist:
        create_playlist(playlist_name, spot, df_songs)

    # Perform feature analysis and create summary
    if analyze_playlist:
        recommended_artists = recommend_artists(
            spot,
            df_playlist_artists
        ) # Get top 3 artist recs
        summary_data = create_playlist_summary(
            df_songs, playlist_name, recommended_artists
        )
        create_artist_summary(df_songs, playlist_name)
        feature_trend_msgs = create_feature_plots(df_songs, playlist_name)
        create_dashboard(summary_data, feature_trend_msgs, playlist_name)

    # Create folder name for saving .csv file(s)
    if save_df_songs or save_df_artists:
        today = datetime.now().strftime("%Y-%m-%d")
        file_dir = (
            f"output/created_playlists/{playlist_name.replace(' ','')}"
            f"Summary_Created{today}/"
        )
        if not os.path.exists(file_dir): # If directory DNE yet
            os.makedirs(file_dir) # Create the directory
        
    # Save df_songs as a .csv file
    if save_df_songs:
        file_name = f"{file_dir}Playlist_Songs.csv"
        df_songs.to_csv(file_name, index=False)

    # Save df_artists as a .csv file
    if save_df_artists:
        file_name = f"{file_dir}Playlist_Artists.csv"
        df_playlist_artists.to_csv(file_name, index=False)

    return df_songs, df_playlist_artists


if __name__ == "__main__":
    df_songs, df_playlist_artists = main()

"""
songkick.com URLs provided below for quick reference/testing:

Austin City Limits 2023 link:
ACL_URL = (
    "https://www.songkick.com/festivals/129-austin-city-limits-music"
    "/id/41123551-austin-city-limits-music-festival-2023"
)

EDC Orlando 2023 link:
EDC_URL = (
    "https://www.songkick.com/festivals/562824-edc-orlando"
    "/id/40754508-edc-orlando-2023"
)

Great North Folk Festival 2023 link (contains 1 artist in lineup):
GNF_URL = (
    "https://www.songkick.com/festivals/1550489-great-north-folk"
    "/id/41010280-great-north-folk-festival-2023"
)
"""