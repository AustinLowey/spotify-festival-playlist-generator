import os
from datetime import datetime
from typing import List, Dict
from collections import Counter

import pandas as pd
import plotly.express as px


def create_playlist_summary(df_songs: pd.DataFrame, festival_name: str, recommended_artists: List[str]) -> Dict[str, str]:
    """
    Generate a summary of playlist information.

    Parameters:
        df_songs (pd.DataFrame): DataFrame containing information about songs, including artists.
        festival_name (str): Name of the festival for which the summary is generated.
        recommended_artists (List[str]): List of recommended artists.

    Returns:
        Dict[str, str]: Dictionary containing summary information.
    """
    
    # Create a label for playlist name and creation date
    today = datetime.now().strftime("%m-%d-%Y")
    created_on_msg = f'Public playlist "Spotipy Playlist - {festival_name}" created on {today}.'

    # Calculate playlist summary information
    playlist_total_songs = len(df_songs)
    playlist_duration_mins = df_songs["Song Duration"].sum() // 60000 # Convert ms to mins

    # Convert total songs and duration to format "# songs, #hr #min"
    num_dur_songs = (f"{playlist_total_songs} songs, "
                     f"{playlist_duration_mins // 60} hr {playlist_duration_mins % 60} min"
    )

    # Get flattened list of all genres across all artists, including repeat genres
    unique_artists = df_songs.drop_duplicates(subset='Artist', keep='first')
    all_genres = [genre for genres in unique_artists['Artist Genres'] for genre in genres]

    # Get top 5 recurring genres in the playlist (not accounting for # songs by each artist)
    counter = Counter(all_genres)
    top_genres = [genre for genre, count in counter.most_common(5)] # List of up to 5 genres
    top_genres_str = ", ".join(top_genres)

    # Generate a string of recommended artists
    recommended_artists_str = ", ".join(recommended_artists)

    return {
        "created_on_msg": created_on_msg,
        "num_dur_songs": num_dur_songs,
        "top_genres_str": top_genres_str,
        "recommended_artists_str": recommended_artists_str
    }


def create_artist_summary(df_songs: pd.DataFrame, festival_name: str) -> pd.DataFrame:
    """
    Generate a summary of artist information from a DataFrame and save it to an HTML file.

    Parameters:
        df_songs (pd.DataFrame): DataFrame containing information about songs, including artists.
        festival_name (str): Name of the festival for which the summary is generated.

    Returns:
        pd.DataFrame: DataFrame containing the summary information for each artist.
    """
    
    # Get unique artists in the DataFrame
    unique_artists = df_songs["Artist"].unique()

    # Create a DataFrame to store artist summary information
    summary_data = []

    # Convert lists in genres column to strings
    df_songs['Artist Genres'] = df_songs['Artist Genres'].apply(", ".join)

    # Iterate over unique artists
    for artist in unique_artists:
        artist_data = df_songs[df_songs["Artist"] == artist]
        genres = artist_data["Artist Genres"].unique()
        num_songs = len(artist_data)
        runtime_sec = artist_data["Song Duration"].sum() // 1000
        runtime_str = f"{runtime_sec // 60} min {runtime_sec % 60} sec"
        avg_tempo = int(artist_data["Tempo"].mean())
        avg_danceability = round(artist_data["Danceability"].mean(), 2)
        avg_energy = round(artist_data["Energy"].mean(), 2)
        avg_speechiness = round(artist_data["Speechiness"].mean(), 2)

        # Create artist summary info dict
        summary_data.append({
            "Artist": artist,
            "Total Songs": num_songs,
            "Total Runtime": runtime_str,
            "Artist Popularity (0-100)": artist_data["Artist Popularity"].iloc[0],
            "Artist Genres": "\n".join(genres),
            "Average Tempo (bpm)": avg_tempo,
            "Average Danceability (0-1)": avg_danceability,
            "Average Energy (0-1)": avg_energy,
            "Average Speechiness (0-1)": avg_speechiness
        })

    # Create a DataFrame from summary data
    artist_summary_df = pd.DataFrame(summary_data)

    # Save the artist summary DataFrame to an HTML file
    today = datetime.now().strftime("%Y-%m-%d")
    file_dir = f"html_exports/{festival_name.replace(' ','')}Summary_Created{today}/"
    if not os.path.exists(file_dir): # Check if the directory exists yet
        os.makedirs(file_dir) # Create the directory
    file_name = f"{file_dir}artist_summary.html"

    # Convert DataFrame to HTML with left-aligned columns
    html_content = artist_summary_df.to_html(index=False, justify='left')
    html_content = html_content.replace('<th>', '<th style="text-align: left;">')

    # Save the modified HTML file
    with open(file_name, 'w') as file:
        file.write(html_content)

    return artist_summary_df


def create_feature_plots(df_songs: pd.DataFrame,
                         festival_name: str,
                         x_axis: str="Song Popularity",
                         y_axis: List[str]=["Tempo", "Danceability", "Energy", "Speechiness"]
                         ) -> None:
    """
    Generate scatter plots for selected features and save them to HTML files.

    Parameters:
        df_songs (pd.DataFrame): DataFrame containing information about songs, including artists.
        festival_name (str): Name of the festival for which the plots are generated.
        x_axis (str): Feature to be plotted on the x-axis.
        y_axis (List[str]): List of features to be plotted on the y-axis. Can also be a string.

    Returns:
        None
    """
    
    # Get unique artists in the DataFrame
    unique_artists = df_songs["Artist"].unique()

    # A bunch of custom colors for plotting
    colors = [
        0x00FF00, 0xFF0000, 0x0000FF,  # Vibrant primary colors
        0xFFA500, 0x800080, 0x8B0000,  # Orange, Purple, Dark Red
        0x008080, 0x008000, 0x9ACD32,  # Teal, Green, Yellow Green
        0x000080, 0x808080, 0x8000FF,  # Navy, Grey, Indigo
        0xFF00FF, 0x00FFFF, 0xFFFF00,  # Magenta, Cyan, Yellow
        0xFF6347, 0x4682B4, 0x800000,  # Tomato, Steel Blue, Maroon
        0x556B2F, 0xFF69B4, 0x9932CC,  # Dark Olive Green, Hot Pink, Dark Orchid
        0x483D8B, 0x32CD32, 0xFF4500,  # Dark Slate Blue, Lime Green, Orange Red
        0x9400D3, 0x00CED1, 0x2E8B57,  # Dark Violet, Dark Turquoise, Sea Green
        0x7FFF00, 0x6A5ACD, 0xDC143C,  # Chartreuse, Slate Blue, Crimson
        0x8A2BE2, 0xFF8C00, 0xFFD700,  # Blue Violet, Dark Orange, Gold
        0x000000, 0xB22222, 0x8B4513,  # Black, Firebrick, Saddle Brown
        0xADFF2F, 0x8B008B,            # Green Yellow, Dark Magenta
        0xFF1493, 0x228B22             # Deep Pink, Forest Green
    ]

    # Manually specify colors for each artist (total 3 colors right now)
    color_map = {artist: f"#{i:06x}" for artist, i in zip(unique_artists, colors)}

    # If a single y is entered as a string, convert it to list
    if isinstance(y_axis, str):
        y_axis = [y_axis]

    # Generate plots for each y-axis feature
    for feature in y_axis:
        fig = px.scatter(
            df_songs,
            x=x_axis,
            y=feature,
            color="Artist",
            hover_data=["Song"],
            color_discrete_map=color_map
        )

        # Create and center plot title
        fig.update_layout(
            title=f"{feature} vs. Song Popularity",
            title_x=0.5,
        )

        # Save each plot to an HTML file
        today = datetime.now().strftime("%Y-%m-%d")
        file_dir = f"html_exports/{festival_name.replace(' ','')}Summary_Created{today}/"
        if not os.path.exists(file_dir): # Check if the directory exists yet
            os.makedirs(file_dir) # Create the directory
        file_name = f"{file_dir}{feature.replace(' ', '_')}_plot.html"
        fig.write_html(file_name)


def create_dashboard(summary_data: Dict[str, str], festival_name: str) -> None:
    """
    Generate an HTML dashboard combining playlist, artist, and feature plot summaries.

    Parameters:
        summary_data (Dict[str, str]): Dictionary containing various summary information.
        festival_name (str): Name of the festival for which the dashboard is generated.

    Returns:
        None
    """
    
    # Generate the HTML for the dashboard format
    dashboard_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{festival_name} Playlist Summary</title>
        <script>
            function showPlot(plotId) {{
                var plots = document.getElementsByClassName("plot");
                for (var i = 0; i < plots.length; i++) {{
                    plots[i].style.display = "none";
                }}
                document.getElementById(plotId).style.display = "block";
            }}
        </script>
    </head>
    <body>
        <!-- Playlist Summary -->
        <div>
            <h2>Playlist Summary</h2>
            <p>{summary_data["created_on_msg"]}</p>
            <p>Total Songs: {summary_data["num_dur_songs"]}</p>
            <p>Top 5 Genres: {summary_data["top_genres_str"]}</p>
            <p>Similar artists to the ones in this playlist:  {summary_data["recommended_artists_str"]}</p>
        </div>

        <!-- Artist Summary -->
        <div>
            <h2>Artist Summary</h2>
            <embed src="artist_summary.html" type="text/html" width="1200" height="600">
        </div>

        <!-- Feature Plots -->
        <div>
            <h2>Feature Plots</h2>
            <button onclick="showPlot('tempo_plot')">Show Tempo Plot</button>
            <button onclick="showPlot('danceability_plot')">Show Danceability Plot</button>
            <button onclick="showPlot('energy_plot')">Show Energy Plot</button>
            <button onclick="showPlot('speechiness_plot')">Show Speechiness Plot</button>

            <div id="tempo_plot" class="plot">
                <embed src="Tempo_plot.html" type="text/html" width="800" height="600">
            </div>
            <div id="danceability_plot" class="plot" style="display: none;">
                <embed src="Danceability_plot.html" type="text/html" width="800" height="600">
            </div>
            <div id="energy_plot" class="plot" style="display: none;">
                <embed src="Energy_plot.html" type="text/html" width="800" height="600">
            </div>
            <div id="speechiness_plot" class="plot" style="display: none;">
                <embed src="Speechiness_plot.html" type="text/html" width="800" height="600">
            </div>
        </div>
    </body>
    </html>
    """

    # Save the dashboard HTML to a file
    today = datetime.now().strftime("%Y-%m-%d")
    file_dir = f"html_exports/{festival_name.replace(' ','')}Summary_Created{today}/"
    if not os.path.exists(file_dir): # Check if the directory exists yet
        os.makedirs(file_dir) # Create the directory
    file_name = f"{file_dir}dashboard.html"
    with open(file_name, "w") as dashboard_file:
        dashboard_file.write(dashboard_html)


# Test the functions if this script is executed directly
if __name__ == '__main__':
    # Import df, then change string representation (from .csv) of genres to list
    df_songs = pd.read_csv("csv_exports/EdcOrlando2023Songs_Created2023-11-21.csv")
    df_songs['Artist Genres'] = df_songs['Artist Genres'].apply(eval)
    
    recommended_artists = ["Placholder Artist #1", "Placholder Artist #2", "Placholder Artist #3"]
    print(f"df loaded with length: {len(df_songs)}")

    # Call all functions in the module
    summary_data = create_playlist_summary(df_songs, "Edc Orlando 2023", recommended_artists)
    artist_summary_df = create_artist_summary(df_songs, "Edc Orlando 2023")
    create_feature_plots(df_songs, "Edc Orlando 2023")
    create_dashboard(summary_data, "Edc Orlando 2023")
