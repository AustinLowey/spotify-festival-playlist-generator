import sys
from typing import List

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication, QDesktopWidget, QGroupBox, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QTextBrowser, QVBoxLayout, QWidget
)

from gui.gui_components import (ColorScheme, CustomProceedButton)


class PlaylistGenArtistManualEntry(QWidget):
    """Artist Selection screen GUI class."""

    def __init__(self) -> None:
        """
        Initialize the GUI

        Parameters:
            df_artists (pd.DataFrame): DataFrame containing artist info.
        """

        super().__init__()

        # Initialize variable that will be output from this GUI screen
        self.entered_artist_names = []
        
        self.init_ui() # Set up GUI


    def init_ui(self) -> None:
        """Set up the GUI screen."""

        # Initialize color scheme
        color = ColorScheme()

        # Set window name and bg color
        self.setWindowTitle(
            "Spotify Festival Playlist Generator - Enter Artists"
        )
        self.setStyleSheet(f"background-color: black;")

        # Create a QVBoxLayout for the main layout
        screen_layout = QVBoxLayout(self)
        window_margin = 10 # Space between container and window edges
        screen_layout.setContentsMargins(
            window_margin,
            window_margin,
            window_margin,
            window_margin
        )

        # Define title QLabel, container, and QTextBrowser stylesheets
        title_style = (
            f"font-size: 16pt;"
            f"color: {color.spotify_green};"
        )
        container_style = (
            # Add background design:
            f"background-color: {color.dark_grey};"
            f"border-radius: 15px;"

            # Set font style for every child label in this container:
            f"font-size: 14pt;"
            f"color: white;"
            f"font-family: 'Arial Rounded MT Bold';"
        )
        textbrowser_style = (
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

            QTextBrowser {{
               border: 2px solid white;
               border-radius: 10px;
               padding: 5px 10px 5px 10px;
            }}
            """
        )

        # Define button styles for default and hover effects
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

        # GroupBox for container (for container/background StyleSheet)
        container_groupbox = QGroupBox(self)
        container_groupbox.setStyleSheet(container_style)

        # QVBoxLayout for container
        container_layout = QVBoxLayout(container_groupbox)
        container_margin = 20
        container_layout.setContentsMargins(
            container_margin,
            container_margin,
            container_margin,
            container_margin
        )
        screen_layout.addWidget(container_groupbox)
        
        # Title label in bottom container
        bottom_title_label = QLabel(
            "Add artists for your playlist:"
        )
        bottom_title_label.setStyleSheet(title_style)
        container_layout.addWidget(bottom_title_label)
        container_layout.addSpacing(15) # Add space below title label

        # QLineEdit for user to input artist names to use in playlist
        self.artists_lineedit = QLineEdit()
        self.artists_lineedit.setPlaceholderText(
            "Type artist's name then press Enter"
        )
        self.artists_lineedit.setStyleSheet(
            f"background-color: {color.mid_grey};"
            f"border: 3px solid white;"
            f"padding: 10px 18px 10px 18px;"
            f"border-radius: 27px;" # Semi-circle border-radius
        )
        self.artists_lineedit.setFixedWidth(445)
        self.artists_lineedit.returnPressed.connect(
            self.add_artist_name
        ) # Add inputted text to artists list when Enter is pressed
        container_layout.addWidget(self.artists_lineedit)
        container_layout.addSpacing(15) # Spacing below QLineEdit

        # Artists display label
        self.artists_display_label = QLabel("Artists being added:")
        container_layout.addWidget(self.artists_display_label)

        # QTextBrowser displaying entered artists
        self.artists_display_browser = QTextBrowser()
        self.artists_display_browser.setFixedHeight(120)
        self.artists_display_browser.setStyleSheet(textbrowser_style)
        container_layout.addWidget(self.artists_display_browser)

        # QHBoxLayout to hold buttons for removing artist(s) from display
        remove_artists_buttons_layout = QHBoxLayout()
        container_layout.addLayout(remove_artists_buttons_layout)

        # Button to remove most recently-entered artist
        pop_artists_button = QPushButton("Remove Last Entered Artist")
        pop_artists_button.setStyleSheet(self.buttons_style)
        pop_artists_button.enterEvent = (
            lambda event: self.on_hover_enter(pop_artists_button)
        ) # Hover effect - change border color
        pop_artists_button.leaveEvent = (
            lambda event: self.on_hover_leave(pop_artists_button)
        ) # End hover effect
        pop_artists_button.clicked.connect(
            self.pop_artist_name
        )
        remove_artists_buttons_layout.addWidget(pop_artists_button)

        # Reset button to remove all artists
        reset_artist_button = QPushButton("Reset All Artists")
        reset_artist_button.setStyleSheet(self.buttons_style)
        reset_artist_button.enterEvent = (
            lambda event: self.on_hover_enter(reset_artist_button)
        ) # Hover effect - change border color
        reset_artist_button.leaveEvent = (
            lambda event: self.on_hover_leave(reset_artist_button)
        ) # End hover effect
        reset_artist_button.clicked.connect(self.reset_artist_names)
        reset_artist_button.setFixedWidth(
            pop_artists_button.sizeHint().width()
        ) # Set this button to match the size of the other
        remove_artists_buttons_layout.addWidget(reset_artist_button)
        
        # Push buttons in this row leftward
        remove_artists_buttons_layout.addStretch()

        # Use Custom Button class. Proceed button to go to playlist creation.
        proceed_button = CustomProceedButton(
            ["Customize Playlist"],
            click_handler=self.proceed_to_customization_screen
        )

        # Center proceed_button and add spacing
        screen_layout.addSpacing(10) # Spacing above proceed button
        screen_layout.addWidget(proceed_button, alignment=Qt.AlignCenter)
        screen_layout.addSpacing(10) # Spacing below proceed button


    def add_artist_name(self) -> None:
        """Adds QLineEdit's input to artist names list on Enter press."""
        name = self.artists_lineedit.text()
        if name.strip():
            self.entered_artist_names.append(name)
            self.artists_lineedit.clear()
            self.update_artists_display()


    def update_artists_display(self) -> None:
        """Updates the artists display for each user interaction."""
        self.artists_display_browser.setPlainText(
            ", ".join(self.entered_artist_names)
        )

    
    def pop_artist_name(self) -> None:
        """Remove most recently-entered artist name."""
        if self.entered_artist_names: # Only pop and update if list not empty
            self.entered_artist_names.pop()
            self.update_artists_display()


    def reset_artist_names(self, button: QPushButton) -> None:
        """Remove all entered artist names."""
        self.entered_artist_names = []
        self.update_artists_display()


    def proceed_to_customization_screen(self, button: QPushButton) -> None:
        """Finish this GUI screen and proceed to next one on button press."""
        self.close()


    def on_hover_enter(self, button):
        """When hovering over the button, change its border color."""
        button.setStyleSheet(self.buttons_hover_style)


    def on_hover_leave(self, button):
        """When hovering ends, reset the border color."""
        button.setStyleSheet(self.buttons_style)


def launch_gui_artist_manual_entry() -> List[str]:
    """
    Launches the GUI for artist selection.

    Initializes the QApplication and PlaylistGenArtistManualEntry GUI instance,
    displays the GUI, and starts the application's event loop for interaction
    handling.

    Parameters:
        None

    Returns:
        List[str]: List of all artists' names entered by user.
    """

    # Initialize the QApplication and GUI instance
    app = QApplication(sys.argv)
    gui = PlaylistGenArtistManualEntry()

    # Center the window on the screen. Hard code size for this 1 screen.
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

    return gui.entered_artist_names


# Launch this GUI screen if executed directly (for testing).
if __name__ == "__main__":

    print(f"Launching GUI screen...")
    
    entered_artist_names = launch_gui_artist_manual_entry()

    print(
        f"{len(entered_artist_names)} artist names selected:\n"
        f"{entered_artist_names}"
    )