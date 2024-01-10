from collections import Counter
from datetime import datetime
import os
from typing import List
import webbrowser

import pandas as pd
import plotly.express as px


class PlaylistGenOutputs():
    """
    A class for creating outputs pertaining to a playlist, such as a summary
    dashboard containing playlist summary info, a table of artist summary info,
    and interactive plots of several track features. Also creates .csv files
    from DataFrames and creates folders to contain all of these outputs.

    Folder Structure and Created Files/Folders:

    root
    |-- src
        |-- gui
            |-- <all GUI Python files>
        |-- <all non-GUI Python files>
    |-- output
        |-- created_playlists
            |-- <playlist_name>Summary_Created<creation_date>   # CREATED
                |-- summary_dashboard_components                # CREATED
                        |-- artist_summary_table.html           # CREATED
                        |-- danceability_plot.html              # CREATED
                        |-- energy_plot.html                    # CREATED
                        |-- speechiness_plot.html               # CREATED
                        |-- tempo_plot.html                     # CREATED
                |-- Playlist_Songs.csv                          # CREATED
                |-- Summary_Dashboard                           # CREATED
            |-- ExistingPlaylistSummary_Created2024-01-02
            |-- styles
            |-- templates
        |-- sample_data
            |-- <.csv files>
    """

    def __init__(
        self,
        df_songs: pd.DataFrame,
        recommended_artists: List[str],
        playlist_name: str,
        playlist_uri: str = "",
        playlist_created_on: str = None,
    ) -> None:
        """
        Initialize the PlaylistGenOutputs class.

        Parameters:
            df_songs (pd.DataFrame): DataFrame containing song info.
            recommended_artists (List[str]): List of recommended artists.
            playlist_name (str): Name of the playlist.
            playlist_uri (str): Spotify URI of the playlist.
            playlist_created_on (str): Date when the playlist was created
                (default is the current date).
        """

        self.df_songs = df_songs
        self.recommended_artists_msg = ", ".join(recommended_artists)
        self.playlist_name = playlist_name

        # spotify:playlist:URI -> playlist/URI
        self.playlist_uri = playlist_uri.replace(":", "/").split("spotify/")[1]

        # Optional creation date parameter, if analyzing an existing playlist
        if playlist_created_on:
            self.playlist_created_on = playlist_created_on
        else:
            self.playlist_created_on = datetime.now().strftime("%m-%d-%Y")


    def create_dashboard(self) -> None:
        """Generate and save the playlist summary dashboard."""

        self.create_output_folders()
        self.create_playlist_summary()
        self.create_artist_summary_table()
        self.create_feature_plots()

        # Import HTML dashboard template from file
        print(f"CWD: {os.getcwd()}")
        dashboard_template_file_name = (
            "output/created_playlists/templates/dashboard_template.html"
        )
        with open(dashboard_template_file_name, "r") as template_file:
            dashboard_html = template_file.read()

        # Replace placeholders in the template with actual HTML content
        dashboard_html = dashboard_html.format(
            playlist_name=self.playlist_name,
            playlist_created_on=self.playlist_created_on,
            num_dur_songs_msg=self.num_dur_songs_msg,
            top_genres_msg=self.top_genres_msg,
            recommended_artists_msg=self.recommended_artists_msg,
            trend_msg_line1_html=self.trend_msg_line1_html,
            trend_msg_line2_html=self.trend_msg_line2_html,
            artist_summary_table_html=self.artist_summary_table_html
        )

        # Create file
        file_name = "summary_dashboard.html"
        with open(f"{self.dashboard_dir}{file_name}", "w") as dashboard_file:
            dashboard_file.write(dashboard_html)


    def save_df_as_csv(self, df: pd.DataFrame, file_name: str) -> None:
        """
        Saves a DataFrame as a .csv file to the dashboard folder.

        Parameters:
            df (pd.DataFrame): Any df to save; most likely df_songs or
                df_artists.
            file_name (str): Name of file being created.

        file_name will likely be Playlist_Songs.csv or Playlist_Artists.csv.
        """

        self.create_output_folders() # Create folder if DNE yet
        df.to_csv(f"{self.dashboard_dir}{file_name}", index=False)


    def create_output_folders(self) -> None:
        """
        Creates a folder (and intermediate folder) to store analytics outputs,
        if folder does not yet exist.

        root
        |-- output
            |-- created_playlists
                |-- <playlist_name>Summary_Created<creation_date>   # CREATED
                    |-- summary_dashboard_components                # CREATED
        """

        # Re-format to year-month-day so folders can be sorted by date
        month, day, year = self.playlist_created_on.split('-')
        formatted_creation_date = f"{year}-{month}-{day}"
        
        self.dashboard_dir = (
            f"output/created_playlists/{self.playlist_name.replace(' ','')}"
            f"Summary_Created{formatted_creation_date}/"
        )
        self.dashboard_components_dir = (
            f"{self.dashboard_dir}summary_dashboard_components/"
        )
        if not os.path.exists(self.dashboard_components_dir):
            os.makedirs(self.dashboard_components_dir) # Create dir if DNE yet


    def create_playlist_summary(self) -> None:
        """
        Creates a summary of playlist information.

        Example output for Playlist Summary section of dashboard:

        Spotipy Playlist - Edc Orlando 2023
        Public playlist created on 01-02-2024

        94 songs, 5 hr 22 min
        Total song runtime

        Pop Dance, EDM, House, UK Dance, Dance Pop
        Top 5 genres

        Nicky Romero, Sebastian Ingrosso, Hardwell
        Similar artists you may want to add

        Energy, Speechiness have strong trends
        82% of songs within 0.66 - 0.96 Energy range
        96% of songs within 0 - 0.23 Speechiness range
        """

        # Calculate playlist total # of songs and duration
        # Format: "# songs, # hr # min"
        # Edge case (<60min) format: "# songs, # min # sec"
        playlist_total_songs = len(self.df_songs)
        playlist_duration_secs = (
            self.df_songs["Song Duration"].sum() // 1000
        )  # Convert ms to seconds
        if playlist_duration_secs // 3600 > 0:
            self.num_dur_songs_msg = (
                f"{playlist_total_songs} songs, "
                f"{playlist_duration_secs // 3600} hr "
                f"{(playlist_duration_secs % 3600) // 60} min"
            )
        else: # Playlist duration < 60 min
            self.num_dur_songs_msg = (
                f"{playlist_total_songs} songs, "
                f"{playlist_duration_secs // 60} min "
                f"{playlist_duration_secs % 60} sec"
            )

        # Get top 5 recurring genres in the playlist based on artists (not
        # accounting for # songs by each artist, which was a design choice)
        df_unique_artists = self.df_songs.drop_duplicates(
            subset="Artist",
            keep="first"
        )
        all_genres = [
            genre
            for genres in df_unique_artists["Artist Genres"]
            for genre in genres
        ] # Flattened list of all artists' genres, including repeats
        top_genres = Counter(all_genres).most_common(5) # List of 5 tuples
        self.top_genres_msg = ", ".join(genre for genre, _ in top_genres)

    
    def create_artist_summary_table(self) -> None:
        """Create an html artist summary table."""

        # Apply aggregation functions for each artist to create data summary
        df_artist_summary_table = self.df_songs.groupby("Artist").agg(
            Total_Songs=("Artist", "count"),
            Total_Runtime=(
                "Song Duration",
                lambda ms: (
                    f"{ms.sum() // 60000} min "
                    f"{ms.sum() % 60000 // 1000} sec"
                )
            ),
            Artist_Popularity=("Artist Popularity", "first"),
            Artist_Genres=("Artist Genres", "first"),
            Average_Tempo=("Tempo", lambda x: round(x.mean())),
            Average_Danceability=(
                "Danceability",
                lambda x: round(x.mean(), 2)
            ),
            Average_Energy=("Energy", lambda x: round(x.mean(), 2)),
            Average_Speechiness=("Speechiness", lambda x: round(x.mean(), 2))
        ).reset_index()

        # Rename columns (these will be displayed in html dashboard table)
        df_artist_summary_table.columns = [
            "Artist",
            "Total Songs",
            "Total Runtime",
            "Artist Popularity (0-100)",
            "Artist Genres",
            "Average Tempo (BPM)",
            "Average Danceability (0-1)",
            "Average Energy (0-1)",
            "Average Speechiness (0-1)"
        ]

        # Convert table to html to later be added into dashboard
        self.artist_summary_table_html = df_artist_summary_table.to_html(
            header=True,
            justify="center",
            classes="table",
            index=False
        )


    def create_feature_plots(
        self,
        x_axis: str="Song Popularity",
        y_axis: List[str]=["Tempo", "Danceability", "Energy", "Speechiness"]
    ) -> None:
        """
        Generate scatter plots, perform feature analysis, and save plots as
            HTML files.

        Parameters:
            x_axis (str): Feature to be plotted on the x-axis.
            y_axis (List[str]): List of features to be plotted on the y-axis.
                Creates a new plot for each y-axis feature provided in list.
                Can also be a single string.
        """

        # Create a custom color map to be used in plots' legends
        unique_artists = self.df_songs["Artist"].unique()
        colors = [
            0x00FF00, 0xFF0000, 0x0000FF, 0xFFA500, 0x800080, 0x8B0000,
            0x008080, 0x008000, 0x9ACD32, 0x000080, 0x808080, 0x8000FF,
            0xFF00FF, 0x00FFFF, 0xFFFF00, 0xFF6347, 0x4682B4, 0x800000,
            0x556B2F, 0xFF69B4, 0x9932CC, 0x483D8B, 0x32CD32, 0xFF4500,
            0x9400D3, 0x00CED1, 0x2E8B57, 0x7FFF00, 0x6A5ACD, 0xDC143C,
            0x8A2BE2, 0xFF8C00, 0xFFD700, 0x000000, 0xB22222, 0x8B4513,  
            0xADFF2F, 0x8B008B, 0xFF1493, 0x228B22
        ] # A bunch of custom colors for plotting
        color_map = {
            artist: f"#{i:06x}" for artist, i in zip(unique_artists, colors)
        } # Dictionary mapping each unique artist to a different color

        # Edge case to handle a single string to be used for y-axis
        if isinstance(y_axis, str):
            y_axis = [y_axis]

        # Empty dict for adding identified feature trends based on analysis
        feature_trends = {}

        # Perform analysis and generate plots for each y-axis feature
        for feature in y_axis:

            # Create feature plot with interacative hover capability
            fig = px.scatter(
                self.df_songs,
                x=x_axis,
                y=feature,
                color="Artist",
                hover_data=["Song"],
                color_discrete_map=color_map,
            )

            # Define a 30 BPM range, as most genres are characterized by ranges
            # of 20-30 BPM. This design decision based on genre norms research.
            if feature == "Tempo":
                feature_range = 30

            # Define a 0.3 range for the 3 features whose values are b/w 0-1.
            # This design decision based mainly on Exploratory Data
            # Analysis (EDA) with multiple datasets.
            elif feature in {"Danceability", "Energy", "Speechiness"}:
                feature_range = 0.3

            # Edge case: If this function gets used in the future for another
            # feature before function is updated.
            else:
                feature_range = 0

            # Calculate feature mean and range upper/lower bounds
            feature_mean = self.df_songs[feature].mean()
            lower_bound = feature_mean - feature_range / 2
            upper_bound = feature_mean + feature_range / 2

            # Edge cases for if calculated upper/lower bounds are out of range
            if lower_bound < 0: # Apply this edge case to all features
                lower_bound = 0
            if (
                feature in {"Danceability", "Energy", "Speechiness"}
                and upper_bound > 1
            ): # Don't apply this edge case to Tempo (BPM)
                upper_bound = 1

            # Identify songs within feature range
            within_range = self.df_songs[
                (self.df_songs[feature] >= lower_bound) &
                (self.df_songs[feature] <= upper_bound)
            ]

            # Calculate the percentage of songs within the feature range
            percent_within_range = round(
                (len(within_range) / len(self.df_songs)) * 100
            )

            # Determine if there is a trend based on if 79% (z within +-1.25)
            # of songs are within defined feature range
            if percent_within_range >= 79:

                # Process lower/upper bounds into desired message format
                if feature == "Tempo":
                    within_range_msg = (
                        f"{round(lower_bound)} - {round(upper_bound)} BPM"
                    )
                elif feature in {"Danceability", "Energy", "Speechiness"}:
                    within_range_msg = (
                        f"{round(lower_bound, 2)} - {round(upper_bound, 2)}"
                    )

                # Create messages and add to dict to add to summary dashboard
                trend_details_msg = (
                    f"{percent_within_range}% of songs "
                    f"within {within_range_msg} {feature} range"
                )
                feature_trends[feature] = trend_details_msg

                # Add uppper and lower bound lines to the plot
                fig.add_shape(
                    type="line",
                    x0=self.df_songs[x_axis].min(),
                    x1=self.df_songs[x_axis].max(),
                    y0=lower_bound,
                    y1=lower_bound,
                    line=dict(color="red", width=2),
                )

                fig.add_shape(
                    type="line",
                    x0=self.df_songs[x_axis].min(),
                    x1=self.df_songs[x_axis].max(),
                    y0=upper_bound,
                    y1=upper_bound,
                    line=dict(color="red", width=2),
                )

            # For adding units to plot y-axis
            if feature == "Tempo":
                y_units = "BPM"

            elif feature in {"Danceability", "Energy", "Speechiness"}:
                y_units = "0-1"

            # Create and center plot title. Define spacing/margins and colors
            fig.update_layout(
                title=f"{feature} vs. Song Popularity",
                title_x=0.5,
                xaxis_title=f"Song Popularity (1-100)",
                yaxis_title=f"{feature} ({y_units})",
                paper_bgcolor="rgba(200, 200, 200, 0)", # Transparent, as...
                # ... part of a work-around for rounding the plot corners.
                # plot_bgcolor="rgb(200, 200, 200)",
                margin=dict(l=25, r=20, t=40, b=5),
                legend=dict(
                    x=1,
                    y=1,
                    traceorder="normal",
                    orientation="v",
                    xanchor="left",
                    yanchor="top",
                ),
                title_font=dict(color="black"),
                xaxis=dict(
                    title_font=dict(color="black"),
                    tickfont=dict(color="black")
                ),
                yaxis=dict(
                    title_font=dict(color="black"),
                    tickfont=dict(color="black")
                ),
                font=dict(color="black"),
            )

            # Save each plot to an HTML file
            file_name = f"{feature.lower().replace(' ', '_')}_plot.html"
            fig.write_html(
                f"{self.dashboard_components_dir}{file_name}",
                full_html=False,
                include_plotlyjs="cdn",
                default_width=605,
                default_height=335
            )

        # Process feature trends for Playlist Summary section of dashboard
        if len(feature_trends) == 4:
            features_with_trends = "All song features"
        elif len(feature_trends) == 0:
            features_with_trends = "No song features"
        else:
            features_with_trends = ", ".join(feature_trends.keys())
        self.trend_msg_line1_html = (
            f'<div id="line1">{features_with_trends} have strong trends</div>'
        )
        self.trend_msg_line2_html = "\n".join(
            f'<div id="line2">{trend_details_msg}</span></div>'
            for trend_details_msg in feature_trends.values()
        )


    def open_dashboard_and_playlist(self) -> None:
        """Opens dashboard file and Spotify playlist in web browser."""
    
        # Open the dashboard file (Note: MS Edge intended)
        current_directory = os.path.abspath(os.getcwd())
        full_dashboard_path = os.path.join(
            current_directory,
            f"{self.dashboard_dir}Summary_Dashboard.html"
        )
        webbrowser.open(full_dashboard_path, new=1)

        # Open playlist in Spotify web browser
        playlist_link = f"https://open.spotify.com/{self.playlist_uri}"
        webbrowser.open(playlist_link, new=2)


if __name__ == "__main__":
    # Import df from .csv then change string representation of genres to list
    df_songs = pd.read_csv(
        "output/sample_data/EdcOrlando2023SampleSongs.csv"
    )
    df_songs['Artist Genres'] = df_songs['Artist Genres'].apply(eval)
    recommended_artists = ['Nicky Romero', 'Sebastian Ingrosso', 'Hardwell']
    playlist_name = "Edc Orlando 2023"
    playlist_uri = "spotify:playlist:3yKYKDuCzErrYaZ1DXLdAS"

    print(f"df loaded for {playlist_name} with length: {len(df_songs)}")
    print("Instantiating dashboard/outputs class...")

    outputs = PlaylistGenOutputs(
        df_songs,
        recommended_artists,
        playlist_name,
        playlist_uri
    )
    outputs.create_dashboard()
    outputs.open_dashboard_and_playlist()
    outputs.save_df_as_csv(df_songs, "playlist_songs.csv")