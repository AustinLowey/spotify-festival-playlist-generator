import os
from datetime import datetime
from typing import List, Dict
from collections import Counter

import pandas as pd
import plotly.express as px


def create_playlist_summary(
        df_songs: pd.DataFrame,
        festival_name: str,
        recommended_artists: List[str]
) -> Dict[str, str]:
    """
    Generate a summary of playlist information.

    Parameters:
        df_songs (pd.DataFrame): DataFrame containing song and artist info.
        festival_name (str): Name of the music festival.
        recommended_artists (List[str]): List of recommended artists.

    Returns:
        Dict[str, str]: Dictionary containing summary information.
    """
    
    # Create a label for playlist name and creation date
    today = datetime.now().strftime("%m-%d-%Y")
    created_on_msg = f'Public playlist created on {today}'

    # Calculate playlist summary information
    playlist_total_songs = len(df_songs)
    playlist_duration_mins = (
        df_songs["Song Duration"].sum() // 60000
     ) # Convert ms to mins

    # Convert total songs and duration to format "# songs, #hr #min"
    if playlist_duration_mins // 60 > 0: # Runtime display: # hr # min
        num_dur_songs = (
            f"{playlist_total_songs} songs, "
            f"{playlist_duration_mins // 60} hr "
            f"{playlist_duration_mins % 60} min"
        )
    else: # Runtime display: # min (edge case where playlist runtime < 60min)
        num_dur_songs = (
            f"{playlist_total_songs} songs, "
            f"{playlist_duration_mins % 60} min"
        )

    # Flattened list of all genres across all artists, including repeat genres
    unique_artists = df_songs.drop_duplicates(subset='Artist', keep='first')
    all_genres = [
        genre for genres in unique_artists['Artist Genres'] for genre in genres
    ]

    # Get top 5 recurring genres in the playlist based on artists
    # (not accounting for # songs by each artist, which was a design choice)
    counter = Counter(all_genres)
    top_genres = [
        genre for genre, count in counter.most_common(5)
    ] # List of up to 5 genres
    top_genres_str = ", ".join(top_genres)

    # Generate a string of recommended artists
    recommended_artists_str = ", ".join(recommended_artists)

    return {
        "created_on_msg": created_on_msg,
        "num_dur_songs": num_dur_songs,
        "top_genres_str": top_genres_str,
        "recommended_artists_str": recommended_artists_str
    }


def create_artist_summary(
        df_songs: pd.DataFrame,
        festival_name: str
) -> pd.DataFrame:
    """
    Generate a summary of artist information from a DataFrame and save it to
        an HTML file.

    Parameters:
        df_songs (pd.DataFrame): DataFrame containing song and artist info.
        festival_name (str): Name of the music festival.

    Returns:
        pd.DataFrame: DataFrame containing summary information for each artist.
    """
    
    # Get unique artists in the DataFrame
    unique_artists = df_songs["Artist"].unique()

    # Create a DataFrame to store artist summary information
    artist_summary_data = []

    # Convert lists in genres column to strings
    df_songs['Artist Genres'] = (
        df_songs['Artist Genres'].apply(", ".join)
    )

    # For each artist, get summary of each column, including number of tracks,
    # mean for all track features, total runtime
    for artist in unique_artists:
        artist_data = df_songs[df_songs["Artist"] == artist]
        genres = artist_data["Artist Genres"].unique()
        num_songs = len(artist_data)
        runtime_sec = artist_data["Song Duration"].sum() // 1000
        runtime_str = f"{runtime_sec // 60} min {runtime_sec % 60} sec"
        popularity = artist_data["Artist Popularity"].iloc[0]
        avg_tempo = int(artist_data["Tempo"].mean())
        avg_danceability = round(artist_data["Danceability"].mean(), 2)
        avg_energy = round(artist_data["Energy"].mean(), 2)
        avg_speechiness = round(artist_data["Speechiness"].mean(), 2)

        # Append summary data for current artist
        artist_summary_data.append({
            "Artist": artist,
            "Total Songs": num_songs,
            "Total Runtime": runtime_str,
            "Artist Popularity (0-100)": popularity,
            "Artist Genres": "\n".join(genres),
            "Average Tempo (bpm)": avg_tempo,
            "Average Danceability (0-1)": avg_danceability,
            "Average Energy (0-1)": avg_energy,
            "Average Speechiness (0-1)": avg_speechiness
        })

    # Create a DataFrame from summary data
    artist_summary_df = pd.DataFrame(artist_summary_data)

    # Convert DataFrame to HTML with left-aligned columns
    html_content = artist_summary_df.to_html(index=False, justify='left')

    # Adding style/formatting rules. This likely to be replaced by CSS later.
    table_head_style = (
        "text-align: left;"
        "color: white;"
        "font-size: 16px;"
        "font-family: Arial, Helvetica, sans-serif;"
    )
    table_rows_style = (
        "text-align: left;"
        "color: rgb(200, 200, 200);"
        "font-size: 15px;"
        "font-family: Arial, Helvetica, sans-serif;"
    )
    html_content = html_content.replace(
        '<thead>',
        f'<thead style="{table_head_style}">'
    )
    html_content = html_content.replace(
        '<tbody>',
        f'<tbody style="{table_rows_style}">'
    )
    html_content = html_content.replace(
        '<th>Artist</th>',
        '<th style="width: 150px;">Artist</th>'
    )
    html_content = html_content.replace(
        '<th>Total Runtime</th>',
        '<th style="width: 110px;">Total Runtime</th>'
    )

    # Wrap the current HTML content with a div for overflow/scrollbar
    html_content = f'<div style="overflow: auto;">{html_content}</div>'

    # Save the artist summary DataFrame to an HTML file
    today = datetime.now().strftime("%Y-%m-%d")
    file_dir = (
        f"output/created_playlists/{festival_name.replace(' ','')}"
        f"Summary_Created{today}/summary_dashboard_components/"
    )
    if not os.path.exists(file_dir): # Create dir if it DNE yet
        os.makedirs(file_dir)
    file_name = f"{file_dir}artist_summary.html"

    # Save the modified HTML file
    with open(file_name, 'w') as file:
        file.write(html_content)

    return artist_summary_df


def create_feature_plots(
    df_songs: pd.DataFrame,
    festival_name: str,
    x_axis: str="Song Popularity",
    y_axis: List[str]=["Tempo", "Danceability", "Energy", "Speechiness"]
) -> Dict[str, str]:
    """
    Generate scatter plots, perform feature analysis, and save plots as
        HTML files.

    Parameters:
        df_songs (pd.DataFrame): DataFrame containing song and artist info.
        festival_name (str): Name of the music festival.
        x_axis (str): Feature to be plotted on the x-axis.
        y_axis (List[str]): List of features to be plotted on the y-axis.
            Can also be a single string.

    Returns:
        Dict[str, str]: Dictionary containing feature trend summary info.
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
        0x556B2F, 0xFF69B4, 0x9932CC,  # Olive Green, Hot Pink, Dark Orchid
        0x483D8B, 0x32CD32, 0xFF4500,  # Dark Blue, Lime Green, Orange Red
        0x9400D3, 0x00CED1, 0x2E8B57,  # Dark Violet, Dark Turquoise, Sea Green
        0x7FFF00, 0x6A5ACD, 0xDC143C,  # Chartreuse, Slate Blue, Crimson
        0x8A2BE2, 0xFF8C00, 0xFFD700,  # Blue Violet, Dark Orange, Gold
        0x000000, 0xB22222, 0x8B4513,  # Black, Firebrick, Saddle Brown
        0xADFF2F, 0x8B008B,            # Green Yellow, Dark Magenta
        0xFF1493, 0x228B22             # Deep Pink, Forest Green
    ]

    # Map colors to be used in plot legend
    color_map = {
        artist: f"#{i:06x}" for artist, i in zip(unique_artists, colors)
    }

    # If a single y is entered as a string, convert it to list
    # Allows this function to be used for generating other plots in the future
    if isinstance(y_axis, str):
        y_axis = [y_axis]

    # Initialize a dict to store messages for each identified feature trend
    feature_trend_msgs = {}

    # Perform analysis and generate plots for each y-axis feature
    for feature in y_axis:

        # Create feature plot with interacative hover capability
        fig = px.scatter(
            df_songs,
            x=x_axis,
            y=feature,
            color="Artist",
            hover_data=["Song"],
            color_discrete_map=color_map
        )

        # Define a 30 BPM range since most genres are characterized by ranges.
        # of 20-30 BPM. This design decision based on researching genre norms.
        if feature == 'Tempo':
            feature_range = 30

        # Define a 0.3 range for the 3 features whose values are b/w 0 and 1.
        # This design decision based mainly on Exploratory Data Analysis (EDA)
        # with multiple datasets.
        elif feature in {'Danceability', 'Energy', 'Speechiness'}:
            feature_range = 0.3

        # Edge case: If this function gets used in the future for some other
        # feature before function is updated.
        else:
            feature_range = 0

        # Calculate feature mean and range upper/lower bounds
        mean_feature = df_songs[feature].mean()
        lower_bound = mean_feature - feature_range / 2
        upper_bound = mean_feature + feature_range / 2

        # Edge cases for if upper/lower bounds are out of range
        if lower_bound < 0:
            lower_bound = 0
        if (
            feature in {'Danceability', 'Energy', 'Speechiness'}
            and upper_bound > 1
        ):
            upper_bound = 1

        # Identify songs within feature range
        within_range = df_songs[
            (df_songs[feature] >= lower_bound) &
            (df_songs[feature] <= upper_bound)
        ]

        # Calculate the percentage of songs within the feature range
        percent_within_range = round((len(within_range) / len(df_songs)) * 100)

        # Determine if there is a trend based on if 79% (z within +-1.25) of
        # songs are within defined feature range
        if percent_within_range >= 79:

            # Process lower/upper bounds into desired format for msg creation
            if feature == "Tempo":
                within_msg = (
                    f"{round(lower_bound)} - {round(upper_bound)} BPM"
                )

            elif feature in {'Danceability', 'Energy', 'Speechiness'}:
                within_msg = (
                    f"{round(lower_bound, 2)} - {round(upper_bound, 2)}"
                )

            # Create messages and add to dict to add to summary dashboard
            trend_details_msg = (
                f"{percent_within_range}% of songs "
                f"within {within_msg} {feature} range"
            )
            feature_trend_msgs[feature] = trend_details_msg

            # Print outlier songs:
            # outside_range = df_songs[
            #     (df_songs[feature] < lower_bound) |
            #     (df_songs[feature] > upper_bound)
            # ]
            # print(outside_range[['Song', 'Artist', feature]])

            # Add uppper and lower bound lines to the plot
            fig.add_shape(
                type="line",
                x0=df_songs[x_axis].min(),
                x1=df_songs[x_axis].max(),
                y0=lower_bound,
                y1=lower_bound,
                line=dict(color="red", width=2),
            )

            fig.add_shape(
                type="line",
                x0=df_songs[x_axis].min(),
                x1=df_songs[x_axis].max(),
                y0=upper_bound,
                y1=upper_bound,
                line=dict(color="red", width=2),
            )

        # For adding units to plot y-axis
        if feature == "Tempo":
            y_units = "BPM"

        elif feature in {'Danceability', 'Energy', 'Speechiness'}:
            y_units = "0-1"

        # Create and center plot title, define spacing/margins, choose colors
        fig.update_layout(
            title=f"{feature} vs. Song Popularity",
            title_x=0.5,
            xaxis_title=f"Song Popularity (1-100)",
            yaxis_title=f"{feature} ({y_units})",
            paper_bgcolor='rgb(200, 200, 200)',
            #plot_bgcolor='rgb(200, 200, 200)',
            margin=dict(l=25, r=20, t=40, b=5),
            legend=dict(
                x=1,
                y=1,
                traceorder='normal',
                orientation='v',
                xanchor='left',
                yanchor='top',
            ),
            title_font=dict(color='black'),
            xaxis=dict(
                title_font=dict(color='black'),
                tickfont=dict(color='black')
            ),
            yaxis=dict(
                title_font=dict(color='black'),
                tickfont=dict(color='black')
            ),
            font=dict(color='black')
        )

        # Save each plot to an HTML file
        today = datetime.now().strftime("%Y-%m-%d")
        file_dir = (
            f"output/created_playlists/{festival_name.replace(' ','')}"
            f"Summary_Created{today}/summary_dashboard_components/"
        )
        if not os.path.exists(file_dir):
            os.makedirs(file_dir)
        file_name = f"{file_dir}{feature.replace(' ', '_')}_plot.html"
        fig.write_html(
            file_name,
            full_html=False,
            include_plotlyjs='cdn',
            default_width=605,
            default_height=335
        )
          
    return feature_trend_msgs


def create_dashboard(
        summary_data: Dict[str, str],
        feature_trend_msgs: Dict[str, str],
        festival_name: str
) -> None:
    """
    Generate an HTML dashboard combining playlist summary details and plots.

    Parameters:
        summary_data (Dict[str, str]): Dictionary containing playlist info.
        feature_trend_msgs Dict[str, str]: Dictionary containing feature
            trend summary messages.
        festival_name (str): Name of the music festival.

    Returns:
        None
    """

    # Define sizes for html components. Set 25px above default width and
    # height from create_feature_plots function.
    f_plot_w = 630
    f_plot_h = 360
    artist_summary_h = 275
    artist_summary_w = 1390

    # Create trend messages for features that have strong trends present
    if len(feature_trend_msgs) == 4:
        trend_msg_html1 = "All song features"
    else:
        trend_msg_html1 = ', '.join(feature_trend_msgs.keys())
    trend_msg_html2 = '\n'.join(
        f'<div id="line2">{trend_details_msg}</span></div>'
        for trend_details_msg in feature_trend_msgs.values()
    )

    # Generate the HTML for the dashboard format
    dashboard_html = f"""
    <!DOCTYPE html>
    <html>

    <head>
        <title>{festival_name} Playlist Summary</title>
        <link rel="stylesheet" type="text/css" href="../styles/dashboard_style.css">  
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
        <div id="playlist-summary">
            <h2>Playlist Summary</h2>
            <div id="line0">Spotipy Playlist - {festival_name}</div>
            <div id="line2">{summary_data["created_on_msg"]}</div>
            <div id="line1">{summary_data["num_dur_songs"]}</div>
            <div id="line2">Total song runtime</div>
            <div id="line1">{summary_data["top_genres_str"]}</div>
            <div id="line2">Top 5 genres</div>
            <div id="line1">{summary_data["recommended_artists_str"]}</div>
            <div id="line2">Similar artists you may want to add</div>
            <div id="line1">{trend_msg_html1} have strong trends</div>
            {trend_msg_html2}
        </div>

        <!-- Feature Plots -->
        <div id="feature-plots">
            <h2>Feature Plots</h2>
            <div class="plot-buttons">
                <button onclick="showPlot('tempo_plot')">Show Tempo Plot</button>
                <button onclick="showPlot('danceability_plot')">Show Danceability Plot</button>
                <button onclick="showPlot('energy_plot')">Show Energy Plot</button>
                <button onclick="showPlot('speechiness_plot')">Show Speechiness Plot</button>
            </div>
            <div class="plots-container" style="overflow: hidden;">
                <div id="tempo_plot" class="plot">
                    <embed src="summary_dashboard_components/Tempo_plot.html" type="text/html" width="{f_plot_w}" height="{f_plot_h}" style="overflow: hidden;">
                </div>
                <div id="danceability_plot" class="plot" style="display: none;">
                    <embed src="summary_dashboard_components/Danceability_plot.html" type="text/html" width="{f_plot_w}" height="{f_plot_h}" style="overflow: hidden;">
                </div>
                <div id="energy_plot" class="plot" style="display: none;">
                    <embed src="summary_dashboard_components/Energy_plot.html" type="text/html" width="{f_plot_w}" height="{f_plot_h}" style="overflow: hidden;">
                </div>
                <div id="speechiness_plot" class="plot" style="display: none;">
                    <embed src="summary_dashboard_components/Speechiness_plot.html" type="text/html" width="{f_plot_w}" height="{f_plot_h}" style="overflow: hidden;">
                </div>
            </div>
        </div>

        <!-- Artist Summary -->
        <div id="artist-summary">
            <h2>Artist Summary</h2>
            <embed src="summary_dashboard_components/artist_summary.html" type="text/html" width="{artist_summary_w}" height="{artist_summary_h}">
        </div>

    </body>

    </html>
    """

    # Save the dashboard HTML to a file
    today = datetime.now().strftime("%Y-%m-%d")
    file_dir = (
        f"output/created_playlists/{festival_name.replace(' ','')}"
        f"Summary_Created{today}/"
    )
    if not os.path.exists(file_dir): # Create directory if it DNE yet
        os.makedirs(file_dir)
    file_name = f"{file_dir}Summary_Dashboard.html"
    with open(file_name, "w") as dashboard_file:
        dashboard_file.write(dashboard_html)


# Test the functions if this script is executed directly
if __name__ == '__main__':
    # Import df then change string representation (from .csv) of genres to list
    df_songs = pd.read_csv(
        "output/sample_data/EdcOrlando2023SampleSongs.csv"
    )
    df_songs['Artist Genres'] = df_songs['Artist Genres'].apply(eval)
    
    recommended_artists = ['Nicky Romero', 'Sebastian Ingrosso', 'Hardwell']
    print(f"df loaded with length: {len(df_songs)}")
    print("---------------------------------------")

    # Call all functions in the module
    summary_data = create_playlist_summary(
        df_songs,
        "Edc Orlando 2023",
        recommended_artists
    )
    artist_summary_df = create_artist_summary(df_songs, "Edc Orlando 2023")
    feature_trend_msgs = create_feature_plots(df_songs, "Edc Orlando 2023")
    create_dashboard(summary_data, feature_trend_msgs, "Edc Orlando 2023")