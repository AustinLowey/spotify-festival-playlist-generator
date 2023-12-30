import sys
from typing import List, Tuple

import pandas as pd
from PyQt5.QtWidgets import (
    QApplication, QDesktopWidget, QGridLayout, QGroupBox, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QScrollArea, QSizePolicy, QTextBrowser, 
    QVBoxLayout, QWidget
)
from PyQt5.QtCore import Qt

from gui.gui_components import (
    ArtistSelectionButton, ColorScheme, CustomProceedButton
)


class PlaylistGenArtistSelection(QWidget):
    """Artist Selection screen GUI class."""

    def __init__(self, df_artists: pd.DataFrame, festival_name: bool) -> None:
        """
        Initialize the GUI

        Parameters:
            df_artists (pd.DataFrame): DataFrame containing artist info.
            festival_name (str): Name of the festival for the title label.
        """

        super().__init__()
        self.df_artists = df_artists
        self.festival_name = festival_name

        # Set extra_artists_display to False on GUI launch
        self.extra_artists_displaying = False

        # Initialize variables that will be outputs from this GUI screen
        self.selected_artist_names = []
        self.extra_artist_names = []
        
        self.init_ui() # Set up GUI


    def init_ui(self) -> None:
        """Set up the GUI screen."""

        # Initialize color scheme
        color = ColorScheme()

        # Set window name and bg color
        self.setWindowTitle(
            "Spotify Festival Playlist Generator - Select Artists"
        )
        self.setStyleSheet(f"background-color: black;")

        # Create a QVBoxLayout for the main layout
        screen_layout = QVBoxLayout(self)
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

        # GroupBox for top-container (for container/background StyleSheet)
        container_top_groupbox = QGroupBox(self)
        container_top_groupbox.setStyleSheet(container_style)

        # QVBoxLayout for top-container
        container_top_layout = QVBoxLayout(container_top_groupbox)
        screen_layout.addWidget(container_top_groupbox)

        # Title label in top container
        title_style = (
            f"font-size: 16pt;"
            f"color: {color.spotify_green};"
        ) # Used in 2 labels (title labels of each container)
        top_title_label = QLabel(
            f'Select "{self.festival_name}" artists for your playlist:'
        )
        top_title_label.setStyleSheet(title_style)
        top_title_label.setIndent(10)
        container_top_layout.addWidget(top_title_label)

        # Define button styles for use in multiple buttons in this GUI screen
        self.buttons_style = (
            f"background-color: {color.mid_grey};"
            f"border: 2px solid {color.lighter_grey};"
            f"border-radius: 10px;"
            f"padding: 8px 25px 8px 25px;"
            f"font-size: 11pt;"
        )
        self.buttons_hover_style = (
            f"background-color: {color.mid_grey};"
            f"border: 2px solid white;"  # Change border color on hover
            f"border-radius: 10px;"
            f"padding: 8px 25px 8px 25px;"
            f"font-size: 11pt;"
        )

        # Add button to select/de-select all artists
        select_all_button_layout = QHBoxLayout()
        container_top_layout.addSpacing(5) # Spacing above button
        container_top_layout.addLayout(select_all_button_layout)
        container_top_layout.addSpacing(5) # Spacing below button
        select_all_button = QPushButton("Select All Artists")
        select_all_button.setStyleSheet(self.buttons_style)
        select_all_button.enterEvent = (
            lambda event: self.on_hover_enter(select_all_button)
        ) # Hover effect - change border color
        select_all_button.leaveEvent = (
            lambda event: self.on_hover_leave(select_all_button)
        ) # End hover effect
        select_all_button.clicked.connect(self.select_all_artists)
        select_all_button_layout.addSpacing(10)
        select_all_button_layout.addWidget(select_all_button)
        
        # QLabel - Add notes on popularity and genres
        notes_label = QLabel(
            "Artist popularity is between 1-100.\n"
            "Genres that say N/A are not available in Spotify's database."
        )
        notes_label.setStyleSheet(
            "font-size: 11pt;"
        )
        select_all_button_layout.addSpacing(10) # Spacing b/w button and notes
        select_all_button_layout.addWidget(notes_label)
        select_all_button_layout.addStretch() # Push button and notes left

        # Scroll area to contain grid of artist selection buttons
        scroll_area = QScrollArea()
        scrollbar_stylesheet = (
            f"""
            QScrollBar:vertical, QScrollBar:horizontal {{
                border: 1px solid {color.mid_grey};
                background: {color.dark_grey};
                width: 12px;
                margin: 0px 0px 0px 0px;
            }}

            QScrollBar::handle:vertical, QScrollBar::handle:horizontal {{
                background: {color.spotify_green};
                min-height: 20px;
            }}

            QScrollBar::add-line:vertical, QScrollBar::add-line:horizontal {{
                background: {color.dark_grey};
                height: 0px;
                subcontrol-position: bottom;
                subcontrol-origin: margin;
            }}

            QScrollBar::sub-line:vertical, QScrollBar::sub-line:horizontal {{
                background: {color.dark_grey};
                height: 0px;
                subcontrol-position: top;
                subcontrol-origin: margin;
            }}

            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical,
            QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
                background: {color.dark_grey};
            }}
            """
        )
        scroll_area.setStyleSheet(scrollbar_stylesheet) # Add custom scrollbar
        container_top_layout.addWidget(scroll_area)
        scroll_widget = QWidget()
        scroll_widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)

        # Grid layout containing artist selection buttons
        artist_selection_gridlayout = QGridLayout()
        artist_selection_gridlayout.setSpacing(10)
        scroll_widget.setLayout(artist_selection_gridlayout)

        # Create an artist selection button for each
        for i, artist_row in self.df_artists.iterrows():
            # Create custom button
            artist_button = ArtistSelectionButton(
                artist_row['Artist'],
                artist_row['Artist Popularity'],
                artist_row['Artist Genres'],
                artist_row['Artist Image url']
            )

            # Add button to layout
            buttons_per_row = 3
            row_position = i // buttons_per_row
            col_position = i % buttons_per_row
            artist_selection_gridlayout.addWidget(
                artist_button,
                row_position,
                col_position
            )

        # GroupBox for bottom-container (for container/background StyleSheet)
        container_bottom_groupbox = QGroupBox(self)
        container_bottom_groupbox.setStyleSheet(container_style)

        # QVBoxLayout for bottom-container
        container_bottom_layout = QVBoxLayout(container_bottom_groupbox)
        container_bottom_layout.setContentsMargins(20, 10, 40, 10)
        screen_layout.addWidget(container_bottom_groupbox)

        # Title label in bottom container
        bottom_title_label = QLabel(
            "(Optional) Add extra artists for your playlist:"
        )
        bottom_title_label.setStyleSheet(title_style)
        container_bottom_layout.addWidget(bottom_title_label)
        container_bottom_layout.addSpacing(10) # Add space above QLineEdit

        # QLineEdit for user to input extra artist names to use in playlist
        self.extra_artists_lineedit = QLineEdit()
        self.extra_artists_lineedit.setPlaceholderText(
            "Type artist's name then press Enter"
        )
        self.extra_artists_lineedit.setStyleSheet(
            f"background-color: {color.mid_grey};"
            f"border: 3px solid white;"
            f"padding: 10px 18px 10px 18px;"
            f"border-radius: 27px;" # Semi-circle border-radius
        )
        self.extra_artists_lineedit.setFixedWidth(445)
        self.extra_artists_lineedit.returnPressed.connect(
            self.add_extra_artist_name
        ) # Add inputted text to extra artists list when Enter is pressed
        container_bottom_layout.addWidget(self.extra_artists_lineedit)

        # Extra artists display (only shown after first artist entered)
        self.extra_artists_display_groupbox = QGroupBox()
        container_bottom_layout.addWidget(self.extra_artists_display_groupbox)
        extra_artists_display_layout = QVBoxLayout()
        self.extra_artists_display_groupbox.setLayout(
            extra_artists_display_layout
        )
        extra_artists_display_layout.addSpacing(10) # Spacing at top of section
        self.extra_artists_display_groupbox.hide() # Hidden during GUI start

        # Extra artists display label
        self.extra_artists_display_label = QLabel("Extra artists being added:")
        extra_artists_display_layout.addWidget(
            self.extra_artists_display_label
        )

        # Extra artists display QTextBrowser
        self.extra_artists_display_browser = QTextBrowser()
        self.extra_artists_display_browser.setFixedHeight(50)
        self.extra_artists_display_browser.setStyleSheet(
            # Custom scroll bar within widget:
            scrollbar_stylesheet +

            # Widget border and padding:
            """
            QTextBrowser {
               border: 2px solid white;
               border-radius: 10px;
               padding: 5px 10px 5px 10px;
            }
            """
        )
        extra_artists_display_layout.addWidget(
            self.extra_artists_display_browser
        )

        # QHBoxLayout to hold buttons for removing artist(s) from extra display
        remove_artists_buttons_layout = QHBoxLayout()
        extra_artists_display_layout.addLayout(
            remove_artists_buttons_layout
        )

        # Override inherited margins from parent container_bottom_layout
        extra_artists_display_layout.setContentsMargins(0, 0, 0, 0) 

        # Button to remove most recently-entered extra artist
        pop_extra_artists_button = QPushButton("Remove Last Entered Artist")
        pop_extra_artists_button.setStyleSheet(self.buttons_style)
        pop_extra_artists_button.enterEvent = (
            lambda event: self.on_hover_enter(pop_extra_artists_button)
        ) # Hover effect - change border color
        pop_extra_artists_button.leaveEvent = (
            lambda event: self.on_hover_leave(pop_extra_artists_button)
        ) # End hover effect
        pop_extra_artists_button.clicked.connect(
            self.pop_extra_artist_name
        )
        remove_artists_buttons_layout.addWidget(pop_extra_artists_button)

        # Button to remove all extra artists
        reset_extra_artist_button = QPushButton("Reset All Extra Artists")
        reset_extra_artist_button.setStyleSheet(self.buttons_style)
        reset_extra_artist_button.enterEvent = (
            lambda event: self.on_hover_enter(reset_extra_artist_button)
        ) # Hover effect - change border color
        reset_extra_artist_button.leaveEvent = (
            lambda event: self.on_hover_leave(reset_extra_artist_button)
        ) # End hover effect
        reset_extra_artist_button.clicked.connect(
            self.reset_extra_artist_names
        )
        reset_extra_artist_button.setFixedWidth(
            pop_extra_artists_button.sizeHint().width()
        ) # Set this button to match the size of the other
        remove_artists_buttons_layout.addWidget(reset_extra_artist_button)
        
        # Push buttons in this row left
        remove_artists_buttons_layout.addStretch()

        # Use Custom Button class. Proceed button to go to playlist creation.
        proceed_button = CustomProceedButton(
            ["Customize Playlist"],
            click_handler=self.proceed_to_customization_screen
        )

        # Use below code to move button to lower-left side of screen:
        """
        # Create a QGridLayout to control layout of buttons
        # Note: Grid chosen over QHBoxLayout to get best button hover effect
        proceed_button_layout = QGridLayout()
        screen_layout.addLayout(proceed_button_layout)

        # Add button margins to add a little space above and below button and
        # add push button to the left with the 3rd arg value.
        proceed_button_layout.setContentsMargins(0, 10, 950, 10)

        proceed_button_layout.addWidget(
            proceed_button,
            0, 0, 1, 1,
            alignment=Qt.AlignCenter
        )

        # Spacer to push button to the left. This approach chosen for best
        # button hover effects.
        spacer_label = QLabel()
        proceed_button_layout.addWidget(
            spacer_label,
            0, 1, 1, 1,
            alignment=Qt.AlignCenter
        )
        """

        # Center proceed_button and add spacing
        screen_layout.addSpacing(10) # Spacing above proceed button
        screen_layout.addWidget(proceed_button, alignment=Qt.AlignCenter)
        screen_layout.addSpacing(10) # Spacing below proceed button

    
    def select_all_artists(self) -> None:
        """
        Sets all artist selection buttons to selected state,
        OR deselects all buttons if they are all currently selected.
        """

        # Check if all artist buttons are currently selected
        all_selected = all(
            button.is_selected for button in self.findChildren(
                ArtistSelectionButton
            )
        )

        # Toggle selection for all artist buttons
        for button in self.findChildren(ArtistSelectionButton):
            button.is_selected = not all_selected
            button.update_style()

        # Update list of selected artist names based on selected buttons
        self.selected_artist_names = [
            button.name
            for button in self.findChildren(ArtistSelectionButton)
            if button.is_selected
        ]


    def add_extra_artist_name(self) -> None:
        """
        Adds QLineEdit's input to extra artist names list on Enter press.
        Also unhides the extra artists display after first interaction
        with this section.
        """

        name = self.extra_artists_lineedit.text()
        if name.strip():
            self.extra_artist_names.append(name)
            self.extra_artists_lineedit.clear()
            self.update_extra_artists_display()
            if not self.extra_artists_displaying:
                self.extra_artists_display_groupbox.show()
                self.extra_artists_displaying = True


    def update_extra_artists_display(self) -> None:
        """Updates the extra artists display for each user interaction."""

        self.extra_artists_display_browser.setPlainText(
            ", ".join(self.extra_artist_names)
        )

    
    def pop_extra_artist_name(self) -> None:
        """Remove most recently-entered extra artist name."""
        if self.extra_artist_names: # Only pop and update if list not empty
            self.extra_artist_names.pop()
            self.update_extra_artists_display()


    def reset_extra_artist_names(self) -> None:
        """Remove all entered extra artist names."""
        self.extra_artist_names = []
        self.update_extra_artists_display()


    def proceed_to_customization_screen(self) -> None:
        """Finish this GUI screen and proceed to next one on button press."""

        # Update list of selected artist names based on selected buttons
        self.selected_artist_names = [
            button.name
            for button in self.findChildren(ArtistSelectionButton)
            if button.is_selected
        ]

        # Close the window
        self.close()


    def on_hover_enter(self, button: QPushButton) -> None:
        """When hovering over the button, change its border color."""
        button.setStyleSheet(self.buttons_hover_style)


    def on_hover_leave(self, button: QPushButton) -> None:
        """When hovering ends, reset the border color."""
        button.setStyleSheet(self.buttons_style)


def launch_gui_artist_selection(
    df_artists: pd.DataFrame,
    festival_name: str
) -> Tuple[List[str], List[str]]:
    """
    Launches the GUI for artist selection.

    Initializes the QApplication and PlaylistGenArtistSelection GUI instance,
    displays the GUI, and starts the application's event loop for interaction
    handling.

    Parameters:
        df_artists (pd.DataFrame): DataFrame containing artist information.
        festival_name (str): Name of the festival for the title label.

    Returns:
        Tuple[List[str], List[str]]: Tuple containing the selected artist
            names list (buttons) and extra artist names list (user-entered).
    """

    # Initialize the QApplication and the PlaylistGenFestivalLink GUI instance
    app = QApplication(sys.argv)
    gui = PlaylistGenArtistSelection(df_artists, festival_name)

    # Center the window on the screen. Hard code size for this 1 screen.
    screen_geometry = QDesktopWidget().screenGeometry()
    width_gui = 1600
    height_gui = 900
    gui.setGeometry(
        (screen_geometry.width() - width_gui) // 2,
        (screen_geometry.height() - height_gui) // 2,
        width_gui,
        height_gui
    )

    # Display GUI and start application's event loop for interaction handling
    gui.show()
    app.exec_()

    return gui.selected_artist_names, gui.extra_artist_names


if __name__ == "__main__":
    df_artists = pd.read_csv("output/sample_data/ElectricZoo2023Artists.csv")
    df_artists['Artist Genres'] = df_artists['Artist Genres'].apply(eval)
    print(f"df_artists loaded with len: {len(df_artists)}")

    festival_name = "Electric Zoo 2023"
    print(f"Launching GUI screen...")
    
    selected_artist_names, extra_artist_names = launch_gui_artist_selection(
        df_artists, festival_name
    )
    print(
        f"{len(selected_artist_names)} artist names selected:\n"
        f"{selected_artist_names}"
    )
    
    print(
        f"{len(extra_artist_names)} extra artist names entered:\n"
        f"{extra_artist_names}"
    )