from typing import List, Tuple

import pandas as pd
import numpy as np


def remove_duplicates(df_songs: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
    # Identify and make list of duplicate songs
    df_duplicates = df_songs[df_songs.duplicated(subset='Song uri', keep='last')]
    removed_songs = df_duplicates['Song'].tolist()

    # Drop duplicates and keep the first occurrence
    df_no_duplicates = df_songs.drop_duplicates(
        subset='Song uri',
        keep='first',
        ).reset_index(drop=True)
    
    return df_no_duplicates, removed_songs


def remove_remixes_and_edits(df_songs: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
    """
    Identifies multiple versions of songs and retains only the version with the highest 'Song Popularity'.

    Parameters:
        df_songs: Pandas DataFrame containing song information.

    Returns:
        df_filtered: DataFrame with the highest popularity version of each song (remixes removed)
        removed_song_names: List of names of the removed versions of songs.

    Ex: 'Where You Are', 'Where You Are - Kaskade Remix' -> retains only 'Where You Are'
    """
    
    # Split the 'Song' column into 'Base Song Name' and 'Version'
    # Ex: Splits 'Where You Are - Kaskade Remix' into 'Where You Are' and 'Kaskade Remix'
    df_songs[['Base Song Name', 'Version']] = df_songs['Song'].str.extract(r'(.+?)(?: - (.+))?$', expand=True)

    # Sort the DataFrame by 'Song Popularity' in descending order (to keep most popular version)
    df_sorted = df_songs.sort_values(by='Song Popularity', ascending=False)

    # Group by 'Base Song Name' and retain the first (highest pop.) for each, then drop the temp cols
    df_filtered = df_sorted.groupby('Base Song Name').head(1)
    df_filtered = df_filtered.drop(columns=['Base Song Name', 'Version'])

    # Get removed songs by comparing the original and new DataFrames
    removed_song_names = list(df_songs[~df_songs.index.isin(df_filtered.index)]['Song'])

    # Sort the final DataFrame alphabetically by artist
    df_filtered = df_filtered.sort_values(by='Artist')

    return df_filtered.reset_index(drop=True), removed_song_names


def filter_songs_by_artist_popularity(df_songs: pd.DataFrame) -> pd.DataFrame:
    """
    Filter songs based on the variation in popularity for each artist,
    keeping more songs the more popular an artist is.

    Parameters:
        df_songs: Pandas DataFrame containing song information.

    Returns:
        Filtered DataFrame with songs based on the artist popularity.
    """

    # Get the maximum number of songs by any artist in the DataFrame
    max_songs_by_artist = df_songs.groupby('Artist').size().max()

    # Get the maximum artist popularity in the DataFrame
    artist_max_pop = df_songs['Artist Popularity'].max()

    # Calculate the song retention percentage for each artist based on popularity
    # By design, this correlates to the diff b/w each artist's pop. and the max pop. in df
    df_songs['Retention Percentage'] = 100 - (artist_max_pop - df_songs['Artist Popularity'])

    # Ensure a minimum retention percentage of 30%
    df_songs['Retention Percentage'] = df_songs['Retention Percentage'].clip(lower=30)

    # Determine the number of songs to retain for each artist, then ensure always at least 2
    df_songs['Retained Songs'] = (df_songs['Retention Percentage'] / 100) * max_songs_by_artist
    df_songs['Retained Songs'] = df_songs['Retained Songs'].clip(lower=2)

    # Retain songs based on the calculated retained songs for each artist
    df_filtered = df_songs.groupby('Artist').apply(lambda x: x.head(int(x['Retained Songs'].iloc[0])))

    # Drop the temporary columns
    df_filtered = df_filtered.drop(['Retention Percentage', 'Retained Songs'], axis=1)

    return df_filtered.reset_index(drop=True)


def create_df_playlist_artists(
    df_lineup_artists: pd.DataFrame,
    df_new_artists: pd.DataFrame,
    selected_artist_names: List[str]
) -> pd.DataFrame:
    """
    Creates a DataFrame of artists to use in fetching songs for playlist creation.
    Combines GUI screen #2 outputs (selected artists buttons and new artisted entered).

    Parameters
        df_lineup_artists (pd.DataFrame): df containing the lineup artists.
        df_new_artists (pd.DataFrame): df containing newly entered artists.
        selected_artist_names (List[str]): List of selected artist names from lineup.
        
    Returns
        pd.DataFrame: df combining both selected lineup artists and new artists.
    """

    # Reduce df of lineup artists to a df of selected artists only
    df_selected_artists = df_lineup_artists[df_lineup_artists['Artist'].apply(
        lambda x: x in selected_artist_names
    )]

    # Combine both DataFrames (selected lineup artists and newly-entered artists)
    df_playlist_artists = pd.concat(
        [df_selected_artists, df_new_artists],
        ignore_index=True
    )

    # Remove artist duplicates and reset df index (edge case if artist entered multiple times)
    df_playlist_artists = (
        df_playlist_artists
        .drop_duplicates(subset='Artist')
        .reset_index(drop=True)
    )

    return df_playlist_artists


# Test the functions in this file if executed directly
if __name__ == '__main__':
    df_test1 = pd.read_csv(
        "csv_exports/EdcOrlando2023Songs_Created2023-11-13.csv"
        ) # Larger df w/ len>1,000
    df_test2 = pd.read_csv(
        "csv_exports/EdcOrlando2023Songs_Created2023-11-21.csv"
        ) # Smaller df w/ len=94 (containing no exact duplicate songs)

    print("#########################################################\n")
    print("---Testing remove_duplicates function---")
    df_no_duplicates1, removed_songs1 = remove_duplicates(df_test1)
    print(f"Test df1 length: {len(df_test1)} songs")
    print(f"After removing songs, df length is: {len(df_no_duplicates1)} songs\n")
    print(f"{len(removed_songs1)} duplicate songs removed: {removed_songs1}\n")
    
    print("#########################################################\n")

    print("---Testing remove_remixes_and_edits function---")
    df_one_version1, removed_song_names1 = remove_remixes_and_edits(df_test1)
    print(f"Test df1 length: {len(df_test1)} songs")
    print(f"After removing songs, df length is: {len(df_one_version1)} songs")
    print(f"{len(removed_song_names1)} remix/edit songs removed\n")
    df_one_version2, removed_song_names2 = remove_remixes_and_edits(df_test2)
    print(f"Test df1 length: {len(df_test1)} songs")
    print(f"After removing songs, df length is: {len(df_one_version1)} songs")
    print(f"{len(removed_song_names1)} remix/edit songs removed: {removed_song_names2}\n")
    print("#########################################################\n")
    
    print("---Testing filter_songs_by_artist_popularity function---")
    filtered_df1 = filter_songs_by_artist_popularity(df_test1)
    std_dev1 = round(df_test1['Artist Popularity'].std(), 1)
    print(f"Artist Popularity std dev for test df1: {std_dev1}")
    print(f"Test df1 length: {len(df_test1)} songs")
    print(f"After removing songs, df length is: {len(filtered_df1)} songs\n")
    filtered_df2 = filter_songs_by_artist_popularity(df_test2)
    std_dev2 = round(df_test2['Artist Popularity'].std(), 1)
    print(f"Artist Popularity std dev for test df2: {std_dev2}")
    print(f"Test df2 length: {len(df_test2)} songs")
    print(f"After removing songs, df length is: {len(filtered_df2)} songs\n")
    print("Note: Higher standard deviation = Higher % of songs removed\n")
    print("#########################################################\n")
    
