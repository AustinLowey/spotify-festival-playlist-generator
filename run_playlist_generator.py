from datetime import datetime

from gui1_launch import *
from festival_lineup_scraper import *
from spotipy_utils import *
from gui2_artist_selection import *
from img_conversion import *
from playlist_analytics import *

def create_new_playlist(create_playlist=True, analyze_playlist=True, save_df_songs=True, backend_testing=False):
    songkick_url, tracks_per_artist, include_remixes = launch_gui()
    festival_name, artist_names = get_artist_names(songkick_url)
    spot = auth_flow()
    search_header = get_token_header()
    df_artists = find_artists(search_header, artist_names)
    selected_artist_names = select_artist_names(df_artists, festival_name, backend_testing)
    df_selected_artists = find_artists(search_header, selected_artist_names)
    df_songs = top_tracks(spot, df_selected_artists)
    if save_df_songs == True:
        today = datetime.now().strftime("%Y-%m-%d")
        df_songs.to_csv(f"df_{festival_name.replace(' ','')}_{today}.csv")
    create_playlist(f"Spotipy Playlist - {festival_name}", spot, df_songs)

"""
2 songkick.com URLs provided below for quick reference/testing:

Austin City Limits 2023 link:
acl_url = "https://www.songkick.com/festivals/129-austin-city-limits-music\
/id/41123551-austin-city-limits-music-festival-2023"

EDC Orlando 2023 link:
edc_url = "https://www.songkick.com/festivals/562824-edc-orlando\
/id/40754508-edc-orlando-2023"
"""

if __name__ == "__main__":
    create_new_playlist()
