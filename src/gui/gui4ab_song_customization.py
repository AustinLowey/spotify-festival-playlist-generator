import sys
from typing import List, Tuple
from collections import Counter

import pandas as pd
from PyQt5.QtWidgets import (
    QApplication, QDesktopWidget, QGridLayout, QGroupBox,
    QHBoxLayout, QLabel,QSpinBox, QVBoxLayout, QWidget
)
from PyQt5.QtCore import Qt

from gui.gui_components import (
    ColorScheme, CustomProceedButton, YesNoRadioButtons
)


class PlaylistGenSongCustomizationGui(QWidget):
    """Song Customization screen GUI class."""

    def __init__(self, df_artists: pd.DataFrame) -> None:
        """
        Initializes the Song Customization GUI.

        Parameters:
            df_artists (pd.DataFrame): DataFrame containing artist info.
        """

        super().__init__()
        self.df_artists = df_artists

        # Initialize variables that will be outputs from this GUI screen
        self.tracks_per_artist = 5 # Default=5. Input can be b/w 1-10
        self.artist_popularity_filtering = True
        self.include_remixes = False
        
        self.init_ui() # Set up GUI
        

    def init_ui(self) -> None:
        """Initializes the GUI screen and components."""

        # Initialize color scheme
        color = ColorScheme()

        # Set window name and bg color
        self.setWindowTitle(
            "Spotify Festival Playlist Generator - Customize Playlist"
        )
        self.setStyleSheet(f"background-color: black;")

        # Create a QHBoxLayout for the main layout
        screen_layout = QHBoxLayout(self)
        window_margin = 10 # Space between containers and window edges
        screen_layout.setContentsMargins(
            window_margin,
            window_margin,
            window_margin,
            window_margin
        )
        screen_layout.setSpacing(window_margin)

        # Define container style (to be used in 2 container style sheets)
        container_style = (
            # Add background design:
            f"background-color: {color.dark_grey};"
            f"border-radius: 15px;"
            # Set font style for every label in this container:
            f"font-size: 14pt;"
            f"color: white;"
            f"font-family: 'Arial Rounded MT Bold';"
        )

        # GroupBox for left-container (for container/background StyleSheet)
        container_left_groupbox = QGroupBox(self)
        container_left_groupbox.setStyleSheet(container_style)

        # Add QVBoxLayout to control left-container layout
        container_left_layout = QVBoxLayout(container_left_groupbox)
        screen_layout.addWidget(container_left_groupbox)

        # Control margins/spacing within left container
        container_margin = 30 # Also used later for right container margin
        container_left_layout.setContentsMargins(
            container_margin,
            container_margin,
            container_margin,
            container_margin
        )
        container_left_layout.setSpacing(container_margin)

        # Create title label to contain user prompt
        title_style = (
            f"font-size: 16pt;"
            f"color: {color.spotify_green}"
        ) # Re-used in both left and right containers in this GUI
        prompt_label = QLabel("Customize your playlist:")
        prompt_label.setStyleSheet(title_style)
        container_left_layout.addWidget(prompt_label)

        # Define indent value for the remaining QLabels
        indent_value = 20

        # Add QHBoxLayout row to contain Q1 label and spinbox. Create label.
        q1_layout = QHBoxLayout()
        container_left_layout.addLayout(q1_layout)
        q1_label = QLabel("Number of songs per artist (1-10): ")
        q1_label.setIndent(indent_value)
        q1_layout.addWidget(q1_label)

        # Setup Q1 spinbox, set min/max, and add to row layout.
        self.q1_spinbox = QSpinBox()
        self.q1_spinbox.setRange(1, 10)
        self.q1_spinbox.setValue(self.tracks_per_artist)  # Set default value
        self.q1_spinbox.valueChanged.connect(
            lambda value: setattr(self, 'tracks_per_artist', value)
        ) # Updates 'tracks_per_artist' with spinbox value
        self.q1_spinbox.setStyleSheet(
            "QSpinBox {"
            f"background-color: {color.mid_grey};"
            f"border: 4px solid {color.lt_grey};"
            f"border-radius: 10px;" # Override container border-radius value
            f"padding: 3px 20px 3px 3px;" # Add extra padding to right of text
            "}"
            # Move buttons from the right side, so not overlaid over border
            "QSpinBox::up-button, QSpinBox::down-button {"
            "right: 5px;"
            "}"
        )
        q1_layout.addWidget(self.q1_spinbox)

        # Adjust spacing of Q1 layout
        q1_layout.setSpacing(10) # Spacing b/w question and spinbox
        q1_layout.addStretch() # Pushes everything left

        # Create QVBoxLayout for Q2 Label and Radio Buttons (to remove spacing)
        q2_layout = QVBoxLayout()
        container_left_layout.addLayout(q2_layout)
        q2_layout.setSpacing(0)

        # Create Q2 label
        q2_label = QLabel(
            "Do you want less songs for less popular artists?\n"
            "If selected, number of songs per artist will\n"
            "scale with artist popularity.\n"
            "(Recommended)"
        )
        q2_label.setContentsMargins(
            indent_value,
            0,
            indent_value,
            0
        ) # Add indent to both left and right side of label
        q2_layout.addWidget(q2_label)

        # Add row containing custom Yes/No radio buttons
        self.q2_radio_buttons = YesNoRadioButtons(indent_value, True)
        q2_layout.addWidget(self.q2_radio_buttons)
        
        # Create QVBoxLayout for Q3 Label and Radio Buttons (to remove spacing)
        q3_layout = QVBoxLayout()
        container_left_layout.addLayout(q3_layout)
        q3_layout.setSpacing(0)

        # Create Q3 label
        q3_label = QLabel(
            'Include multiple remixes/edits?\n'
            '(Ex: Include both "Moon River Rock\n'
            'and "Moon River Rock - Radio Edit")'
        )
        q3_label.setIndent(indent_value)
        q3_layout.addWidget(q3_label)

        # Add row containing custom Yes/No radio buttons
        self.q3_radio_buttons = YesNoRadioButtons(indent_value, False)
        q3_layout.addWidget(self.q3_radio_buttons)

        # Create a QGridLayout to control layout of buttons
        # Note: Grid chosen over QHBoxLayout to get best button hover effect,
        # as QHBox approach made button width expand in only one direction.
        proceed_button_layout = QGridLayout()
        container_left_layout.addLayout(proceed_button_layout)

        # Define margins for proceed_button_layout
        # Left and bottom margins equal to indent value
        proceed_button_layout.setContentsMargins(
            indent_value,
            0,
            0,
            indent_value
        )

        # Note: 29 columns in QGridLayout, with button spanning first 15. While
        # convoluted, this gives the best button expansion hover effects. The
        # ratio 15/29 is associated with the button's current width and the
        # available space b/w the container_left_layout left and right margins.
        num_cols_in_grid = 29
        num_cols_button_spanning = num_cols_in_grid // 2 + 1
        for i in range(num_cols_in_grid):
            proceed_button_layout.setColumnStretch(i, 1)

        # Use Custom Button class. Proceed button to go to playlist creation.
        proceed_button = CustomProceedButton(
            ["Create Playlist"],
            click_handler=self.proceed_to_playlist_creation
        )
        proceed_button_layout.addWidget(
            proceed_button,
            0, 0, 1, num_cols_button_spanning,
            alignment=Qt.AlignCenter
        )
  
        # GroupBox for right-container (for container/background StyleSheet)
        container_right_groupbox = QGroupBox(self)
        container_right_groupbox.setStyleSheet(container_style)

        # Add QVBoxLayout to control right-container layout
        container_right_layout = QVBoxLayout(container_right_groupbox)
        screen_layout.addWidget(container_right_groupbox)

        # Control margins/spacing within right container
        container_right_layout.setContentsMargins(
            container_margin,
            container_margin,
            container_margin,
            container_margin
        )
        container_right_layout.setSpacing(container_margin)

        # Create title label for right container
        playlist_details_label = QLabel("Playlist Details:")
        # Slightly larger font for container title:
        playlist_details_label.setStyleSheet(title_style)
        container_right_layout.addWidget(playlist_details_label)

        # Process df_artists info to display in right container
        est_playlist_len = self.estimate_playlist_length()
        num_artists = len(self.df_artists)
        top_genres_list = self.get_top_genres() # Get (up to) top 5 genres

        # Create QVBoxLayout to remove spacing between playlist length labels
        est_playlist_len_layout = QVBoxLayout()
        est_playlist_len_layout.setSpacing(0)
        container_right_layout.addLayout(est_playlist_len_layout)

        # Connect signals to slots to dynammically update playlist length label
        self.q1_spinbox.valueChanged.connect(
            self.update_est_playlist_len_value_label
        )
        self.q2_radio_buttons.yes_button.toggled.connect(
            self.update_est_playlist_len_value_label
        )

        # Create label to display estimated playlist length value
        self.est_playlist_len_value_label = QLabel(est_playlist_len)
        self.est_playlist_len_value_label.setIndent(indent_value)
        self.est_playlist_len_value_label.setStyleSheet("font-size: 16pt;")
        est_playlist_len_layout.addWidget(self.est_playlist_len_value_label)

        # Create label to display estimated playlist length text
        est_playlist_len_text_label = QLabel("Estimated playlist length")
        est_playlist_len_text_label.setContentsMargins(
            indent_value,
            0,
            indent_value,
            0
        ) # Add indent to both left and right side of label
        est_playlist_len_layout.addWidget(est_playlist_len_text_label)

        # Create QVBoxLayout to remove spacing between number of artists labels
        num_artists_layout = QVBoxLayout()
        num_artists_layout.setSpacing(0)
        container_right_layout.addLayout(num_artists_layout)

        # Create label for number of artists value
        num_artists_value_label = QLabel(f"{num_artists} Artists")
        num_artists_value_label.setIndent(indent_value)
        num_artists_value_label.setStyleSheet("font-size: 16pt;")
        num_artists_layout.addWidget(num_artists_value_label)

        # Create label for number of artists text
        num_artists_text_label = QLabel("In playlist")
        num_artists_text_label.setIndent(indent_value)
        num_artists_layout.addWidget(num_artists_text_label)

        # Create QVBoxLayout to remove spacing between top genres labels
        top_genres_layout = QVBoxLayout()
        top_genres_layout.setSpacing(0)
        container_right_layout.addLayout(top_genres_layout)

        # Create label for top genres heading
        top_genres_heading_label = QLabel("Top Genres:")
        top_genres_heading_label.setIndent(indent_value)
        top_genres_heading_label.setStyleSheet("font-size: 16pt;")
        top_genres_layout.addWidget(top_genres_heading_label)

        # Create label for top genres
        top_genres_str = "" # Empty string to add lines of text to
        for i, genre in enumerate(top_genres_list): # Add 1 text line per genre
            top_genres_str += f"{i+1}) {genre}\n"
        top_genres_text_label = QLabel(top_genres_str)
        top_genres_text_label.setIndent(indent_value)
        top_genres_layout.addWidget(top_genres_text_label)

        # Add stretch to right container to push all widgets upward
        container_right_layout.addStretch()


    def proceed_to_playlist_creation(self) -> None:
        """
        When proceed button is pressed, process the user's input and proceed
            to playlist creation.
        
        Checks current radio button group states, then closes window.

        Note: tracks_per_artist is already automatically updated when the
            spinbox is updated, so no processing code is needed here.
        """

        # Retrieve the current states of the radio button groups
        self.artist_popularity_filtering = (
            self.q2_radio_buttons.yes_button.isChecked()
        )
        self.include_remixes = self.q3_radio_buttons.yes_button.isChecked()

        # Close the window
        self.close()


    def estimate_playlist_length(self) -> str:
        """
        Calculates an estimated playlist length based off of number of songs,
            average song length of 3min 17s, and (optionally, if 
            artist_popularity_filtering is enabled) artists' popularities.

        Uses Attributes:
            self.df_artists (pd.DataFrame): DataFrame containing artist info,
                including names and popularities
            self.tracks_per_artist (int): Max number of tracks per artist
            self.q2_radio_buttons.yes_button.isChecked() (bool): Option to
                filter out tracks proportionally to artist popularites
        
        Returns:
            str: Playlist length in format: #hr #min
        """

        AVERAGE_SONG_LENGTH = 197 # 3min17s average song length.

        # Assuming all artists get max number of songs
        # (i.e., no popularity filtering applied), then:
        num_playlist_tracks = len(self.df_artists) * self.tracks_per_artist

        if not self.q2_radio_buttons.yes_button.isChecked():
            est_runtime_sec = num_playlist_tracks * AVERAGE_SONG_LENGTH
            est_runtime_min = est_runtime_sec // 60
            est_runtime_str = (
                f"{est_runtime_min // 60} hr {est_runtime_min % 60} min"
            )
        else: # Estimate number of songs removed based on artist popularity
            
            # Use correlation between the df's Artist Popularity standard
            # deviation vs percentage of songs retained (using test data
            # points from playlists fed into the playlist_mods module)
            
            # Test data points (x1, y1) and (x2, y2)
            # std1, percent_retained1 = 17.8, 57.1
            # std2, percent_retained2 = 6.0, 88.3

            # Calculate slope (m) and y-intercept (b)
            # m = (percent_retained2 - percent_retained1) / (std2 - std1)
            # b = percent_retained1 - m * std1
            m = -2.644067796610169
            b = 104.16440677966102

            # Get standard deviation of Artist Popularity in df
            std_artist_popularity = self.df_artists['Artist Popularity'].std()

            # Resulting linear equation. Estimate percentage of songs retained
            percent_songs_retained = (m * std_artist_popularity + b) / 100

            # Combine with num_playlist_tracks and process into desired format
            num_tracks_retained = num_playlist_tracks * percent_songs_retained
            est_runtime_sec = num_tracks_retained * AVERAGE_SONG_LENGTH
            est_runtime_min = round(est_runtime_sec // 60)
            est_runtime_str = (
                f"{est_runtime_min // 60} hr {est_runtime_min % 60} min"
            )

        return est_runtime_str
    

    def update_est_playlist_len_value_label(self) -> None:
        """
        Dynamically update the estimated playlist length label any time
        the spinbox or q2 radio buttons are modified.
        """
        est_playlist_len = self.estimate_playlist_length()
        self.est_playlist_len_value_label.setText(est_playlist_len)


    def get_top_genres(self) -> List[str]:
        """
        Gets top artists genres (up to 5) in DataFrame of artists.

        Uses Attribute:
            self.df_artists (pd.DataFrame): DataFrame containing artist info,
                including names and popularities.
        
        Returns:
            List[str]: Top recurring artist genres in df. List of up to 5.
        """

        # Flattened list of all genres for all artists. Includes repeat genres.
        all_genres = [
            genre
            for genres in self.df_artists['Artist Genres']
            for genre in genres
        ]

        # Get top 5 recurring genres across all artists
        counter = Counter(all_genres)
        top_genres = [
            genre for genre, count in counter.most_common(5)
        ] # List of up to 5 genres

        return top_genres


def launch_gui_song_customization(
    df_artists: pd.DataFrame
) -> Tuple[int, bool, bool]:
    """
    Launches the GUI for song customization.

    Initializes the QApplication and PlaylistGenSongCustomizationGui instance,
    displays the GUI, and starts the application's event loop for interaction
    handling.

    Parameters:
        df_artists (pd.DataFrame): DataFrame containing artist information.

    Returns:
        Tuple[int, bool, bool]: Tuple containing the selected number of
        tracks per artist, the flag indicating whether to useartist popularity
        filtering, and the flag indicating whether to include remixes.
    """

    # Initialize the QApplication and the PlaylistGenFestivalLink GUI instance
    app = QApplication(sys.argv)
    gui = PlaylistGenSongCustomizationGui(df_artists)

    # Center the window on the screen
    screen_geometry = QDesktopWidget().screenGeometry()
    size = gui.sizeHint()
    gui.setGeometry(
        (screen_geometry.width() - size.width()) // 2,
        (screen_geometry.height() - size.height()) // 2,
        size.width(),
        size.height()
    )

    # Display GUI and start application's event loop for interaction handling
    gui.show()
    app.exec_()

    return (
        gui.tracks_per_artist,
        gui.artist_popularity_filtering,
        gui.include_remixes
    )


# Automatically launch GUI if this file executed as main script
if __name__ == "__main__":

    # Import df then change string representation (from .csv) of genres to list
    df_artists = pd.read_csv(
        "output/sample_data/EdcOrlando2023Artists.csv"
    )
    df_artists['Artist Genres'] = df_artists['Artist Genres'].apply(eval)
    print(f"df_artists loaded with len: {len(df_artists)}")

    # Run GUI and print outputs
    print("Launching GUI screen...")
    tracks_per_artist, artist_popularity_filtering, include_remixes = (
        launch_gui_song_customization(df_artists)
    )
    print(f"Number of tracks per artist: {tracks_per_artist}")
    print(
        f"'Artist Popularity Filtering' selected? (T/F): "
        f"{artist_popularity_filtering}"
    )
    print(f"'Include Remixes' selected? (T/F): {include_remixes}")