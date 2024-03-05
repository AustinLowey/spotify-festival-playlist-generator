import unittest
import pandas as pd

from src.playlist_mods import (
    create_df_playlist_artists, filter_songs_by_artist_popularity,
    remove_duplicates, remove_remixes_and_edits,
)

class TestPlaylistMods(unittest.TestCase):
    def setUp(self):
        self.df1 = pd.read_csv(
            "output/sample_data/EdcOrlando2023FullSongs.csv"
        ) # Large df w/ len>1,000

    def test_create_df_playlist_artists(self):
        pass

    def test_filter_songs_by_artist_popularity(self):
        pass
    
    def test_remove_duplicates(self):
        df_no_duplicates1, removed_songs1 = remove_duplicates(self.df1)
        self.assertGreater(len(self.df1), len(df_no_duplicates1))
        self.assertEqual(len(self.df1), len(df_no_duplicates1) + len(removed_songs1))

    def test_remove_remixes_and_edits(self):
        pass