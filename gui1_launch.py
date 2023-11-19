import sys

from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit,
    QSpinBox, QCheckBox, QPushButton, QMessageBox
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QRect, QPropertyAnimation


class PlaylistGenLaunchGui(QWidget):
    """
    GUI for the first screen of the Spotify Festival Playlist Generator.

    Attributes:
        songkick_url (str): songkick.com link to a specific music festival web page.
        tracks_per_artist (int): Number of top tracks per artist to include in the created playlist.
        include_remixes (bool): Removes multiple remixes and edits of the same song.

    Methods:
        __init__(): Initializes the GUI with default values.
        init_ui(): Sets up the graphical user interface.
        start_animation(): Animation to make the button larger when the user hovers the mouse over it.
        proceed_to_artist_selection(): Updates variables with user input and closes the window.

    Returns (when running launch_gui function):
        songkick_url (str): songkick.com link to a specific festival web page, which contains an artist lineup.
        tracks_per_artist (int): Number of top tracks per artist to include in the created playlist. Can be b/w 1-10. Default = 5.
        include_remixes (bool): Removes multiple remixes and edits of the same song.

    GUI prompts the user through 5 steps:
    
    1) Go to www.songkick.com (hyperlink provided) and enter the name of the music festival you want into the website's search bar.
    
    2) Select the festival, then copy and paste the website link below:
       <QLineEdit provided for user to paste link into>
       
    3) Choose the number of tracks from each artists you want in your playlist (between 1-10): <QSpinBox>

    4) Check the box below if you want to include multiple remixes/edits.
       (Ex: Include both "Moon River Rock" and "Moon River Rock - Radio Edit")
       <QCheckBox for user to optionally select>

    5) Select which artist to include: <Big QPushButton in Spotify green that brings user to next page>

    ...

    Note on step 4 because my wife said it was confusing: When building the back-end of this project, I was using Electric Zoo 2023
    as the festival to do most of my testing. The popular 2023 House song "Where You Are" by John Summit was, unsurprisingly, added
    to the playlist because John Summit was a headliner for the event. However, there were multiple other headliners, including
    Zedd, Kaskade, and GRiZ, who all remixed the same song. It's a great song, but I didn't want 4 versions of the same song in
    the same playlist, so I added the option to not include multiple remixes/edits. Repeats of the exact same song are always
    removed, regardless of what is selected for this option.
    """
    
    def __init__(self):
        super().__init__()

        # Initialize variables to store user input. These are the 3 outputs from the GUI (explained in above docstrings).
        self.songkick_url = ""
        self.tracks_per_artist = 5
        self.include_remixes = False

        # Set up the GUI
        self.init_ui()

    def init_ui(self):
        """
        Defines layout and appearance of launch screen GUI.


        Widgets:
            Title label
            Step labels and explanations
            URL line edit
            Number of tracks spin box
            Checkbox for including remixes/edits
            Proceed button
        """
        
        # Define GUI's color scheme (based off of Spotify's) to be referenced in QWidget StyleSheets
        spotify_green = "rgb(30, 215, 96)"
        dark_grey = "rgb(18, 18, 18)"
        mid_grey = "rgb(40, 40, 40)"
        lt_grey = "rgb(80, 80, 80)"
        lighter_grey = "rgb(100, 100, 100)"
        transparent = "rgba(0, 0, 0, 0)" # This rgba style (w/ a=0) makes label's background transparent
        
        # Set window properties
        self.setGeometry(160, 100, 1600, 900)
        self.setWindowTitle('Spotify Festival Playlist Generator')
        self.setStyleSheet(f"background-color: {dark_grey}; color: white;")

        # Set font type and size. Rounded font type chosen to (somewhat) match Spotify's font style.
        font = QFont()
        font.setFamily("Arial Rounded MT Bold")
        font.setPointSize(16)

        # Horizontal spacing/formatting of widgets
        x_start = 40
        x_indent = 140

        # Vertical spacing/formatting of widgets
        y_spacing = 115 # For keeping consistent vertical spacing between each step section
        
        y_title = 60
        y_title_height = 70
        
        y_step1_label = y_title * 2 + y_title_height # Spacing above title = spacing below title
        
        y_step2_label = y_step1_label + y_spacing
        y_line_edit = y_step2_label + 45
        
        y_step3_label = y_line_edit + y_spacing
        
        y_step4_label1 = y_step3_label + y_spacing
        y_step4_label2 = y_step4_label1 + 30
        y_checkbox = y_step4_label2 + 50
        
        y_step5_label = y_checkbox + y_spacing
        y_proceed_button = y_step5_label - 30


        # Create widgets:

        # Grey label w/ rounded corners overlaid over a dark grey background to mimic Spotify's UI
        background_design = QLabel(self)
        background_design.setGeometry(15, 15, 1570, 870)
        background_design.setStyleSheet(f"background-color: {mid_grey}; border-radius: 40px;")

        # Title
        title_label = QLabel("Spotify Festival Playlist Generator", self)
        title_label.setGeometry(200, y_title, 1200, y_title_height)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet(
            f"color: {spotify_green};"
            f"background-color: {transparent};"
            f"font-size: 36pt; font-weight: bold;"
            f"font-family: 'Arial Rounded MT Bold';"
        )

        # Step 1 text
        link_template = '<a href="{0}">{1}</a>' # Allows a hyperlink to be added to the Step 1 text
        step1_label_text = (
            "Step 1) Go to "
            + link_template.format("https://www.songkick.com", "www.songkick.com")
            + " and enter the name of the music festival you want into the website's search bar."
        )
        step1_label = QLabel(step1_label_text, self)
        step1_label.setGeometry(x_start, y_step1_label, 1560, 40)
        step1_label.setOpenExternalLinks(True)
        step1_label.setFont(font)
        step1_label.setStyleSheet(f"color: white; background-color: {transparent};")

        # Step 2 text
        step2_label = QLabel("Step 2) Select the festival, then copy and paste the website link below:", self)
        step2_label.setGeometry(x_start, y_step2_label, 1560, 40)
        step2_label.setFont(font)
        step2_label.setStyleSheet(f"color: white; background-color: {transparent};")

        # Text-input line for entering URL
        self.url_lineedit = QLineEdit(self)
        self.url_lineedit.setPlaceholderText(
            " Enter your festival's website link"
        )
        self.url_lineedit.setGeometry(
            x_indent, y_line_edit, 1600 - x_indent * 2, 40
        )
        self.url_lineedit.setStyleSheet(f"background-color: {lt_grey}; color: white; border-radius: 20px; padding: 2px;")
        font_url = QFont()
        font_url.setFamily("Arial Rounded MT Bold")
        font_url.setPointSize(14)
        self.url_lineedit.setFont(font_url)
        
        # Step 3 text
        step3_label = QLabel(
            "Step 3) Choose the number of tracks from each artist "
            "you want in your playlist (between 1-10):",
            self
        )
        step3_label.setGeometry(x_start, y_step3_label, 1560, 40)
        step3_label.setFont(font)
        step3_label.setStyleSheet(f"color: white; background-color: {transparent}")

        # Empty label that goes behind the below QSpinBox widget (because it looks pretty this way)
        self.spin_label = QLabel(self)
        self.spin_label.setGeometry(x_start + 1242, y_step3_label - 3, 66, 46)
        self.spin_label.setStyleSheet(f"color: white; background-color: {lighter_grey}; border-radius: 5px;")

        # Spinbox users select how many of each artist's top tracks to include in the created playlist
        self.num_tracks_spinbox = QSpinBox(self)
        self.num_tracks_spinbox.setRange(1, 10) # Can be b/w 1-10 tracks per artist
        self.num_tracks_spinbox.setValue(5)  # Set the default number of tracks per artists to 5
        self.num_tracks_spinbox.setGeometry(x_start + 1245, y_step3_label, 60, 40)
        self.num_tracks_spinbox.setStyleSheet(f"border: 1px solid {lighter_grey}; background-color: {lt_grey}; color: white;")
        self.num_tracks_spinbox.setFont(font)

        # Step 4 (line 1) text
        step4_label1 = QLabel("Step 4) Check the box below if you want to include multiple song remixes/edits.", self)
        step4_label1.setGeometry(x_start, y_step4_label1, 1100, 60)
        step4_label1.setFont(font)
        step4_label1.setStyleSheet(f"color: white; background-color: {transparent}")

        # Step 4 (line 2) text. Set up this way (vs. a \n) so this label can be indented more easily.
        step4_label2 = QLabel('(Ex: Include both "Moon River Rock" and "Moon River Rock - Radio Edit")', self)
        step4_label2.setGeometry(x_indent, y_step4_label2, 1000, 60)
        step4_label2.setFont(font)
        step4_label2.setStyleSheet(f"color: white; background-color: {transparent};")

        # Checkbox for whether or not to include multiple remixes/edits of songs
        self.include_remixes_checkbox = QCheckBox("Include Multiple Remixes/Edits", self)
        self.include_remixes_checkbox.setStyleSheet("color: white; font-size: 16pt; font-family: 'Arial Rounded MT Bold';")
        self.include_remixes_checkbox.setChecked(False)  # Set the default value
        self.include_remixes_checkbox.setGeometry(x_indent, y_checkbox, 433, 40)
        self.include_remixes_checkbox.setFont(font)
        self.include_remixes_checkbox.setStyleSheet(f"background-color: {lt_grey}; border-radius: 10px; padding: 5px;")

        # Step 5 text
        step5_label = QLabel("Step 5) Select which artists to include:", self)
        step5_label.setGeometry(x_start, y_step5_label, 1000, 40)
        step5_label.setFont(font)
        step5_label.setStyleSheet(f"color: white; background-color: {transparent}")

        # Button that brings user to the next page of the GUI where they can select artists
        self.proceed_button = QPushButton("ARTIST SELECTION", self)
        self.proceed_button.clicked.connect(self.proceed_to_artist_selection)
        w_proceed_button = 370
        x_proceed_button = int((1600 - w_proceed_button) / 2)
        h_proceed_button = 100
        self.proceed_button.setGeometry(x_proceed_button, y_proceed_button, w_proceed_button, h_proceed_button)
        self.proceed_button.setStyleSheet(
            f"background-color: {spotify_green};"
            f"color: black;"
            f"border-style: outset;"
            f"border-color: {mid_grey};"
            f"border-radius: 40px;"
        )
        self.proceed_button.setFont(QFont("Arial Rounded MT Bold", 18))

        # Set up animation properties to make button larger when user hovers mouse over it
        self.animation = QPropertyAnimation(self.proceed_button, b"geometry")
        self.animation.setDuration(200)  # Set the animation duration in milliseconds

        # Connect the hover events to functions
        self.proceed_button.enterEvent = lambda event: self.start_animation(
            event, QRect(x_proceed_button - 5,
                         y_proceed_button - 5,
                         w_proceed_button + 10,
                         h_proceed_button + 10)
        )
        self.proceed_button.leaveEvent = lambda event: self.start_animation(
            event, QRect(
                x_proceed_button,
                y_proceed_button,
                w_proceed_button,
                h_proceed_button)
        )

    def start_animation(self, event, target_geometry):
        """
        Animation to make the proceed button larger when the user hovers the mouse over it.

        Parameters:
            event: Mouse hover event.
            target_geometry (QRect): Target geometry for the button.

        Note: This method is connected to hover events for the proceed button.
        """
        if not self.animation.state() == QPropertyAnimation.Running:
            self.animation.setStartValue(self.proceed_button.geometry())
            self.animation.setEndValue(target_geometry)
            self.animation.start()

    def proceed_to_artist_selection(self):
        """
        Updates variables with user input and closes the window.

        This method is called when the user clicks the proceed button.
        """
        self.songkick_url = self.url_lineedit.text()
        self.tracks_per_artist = self.num_tracks_spinbox.value()
        self.include_remixes = self.include_remixes_checkbox.isChecked()

        # Check if the songkick_url contains "songkick.com" and if not, prompts user to enter a valid link
        if "songkick.com" not in self.songkick_url:
            QMessageBox.warning(self, 'Invalid URL', 'Enter a valid songkick.com link.')
            return

        # Close the window when the proceed button is clicked
        self.close()


def launch_gui():
    """
    Instantiates a PlaylistGenLaunchGui class object. Launches the starting GUI
    screen and, once the user finishes with it, stores the users inputs.

    Returns:
        str: songkick.com link to a specific festival web page.
        int: Number of top tracks per artist to include in the created playlist.
        bool: Removes multiple remixes and edits of the same song.
    """
    app = QApplication(sys.argv)
    gui = PlaylistGenLaunchGui()
    gui.show()
    app.exec_()

    return gui.songkick_url, gui.tracks_per_artist, gui.include_remixes
