import sys

from PyQt5.QtWidgets import (
    QApplication, QDesktopWidget, QGroupBox, QLabel, QVBoxLayout, QWidget
)
from PyQt5.QtCore import Qt

from gui.gui_components import ColorScheme, CustomProceedButton


class PlaylistGenLaunchGui(QWidget):
    """Launch screen main GUI class."""

    def __init__(self) -> None:
        """
        Initialize the PlaylistGenLaunchGui.

        Sets up the GUI components and initializes GUI output variables.
        """

        super().__init__()
        self.create_from_festival = None # Output from this GUI screen
        self.init_ui() # Set up GUI
        
    def init_ui(self) -> None:
        """
        Set up the user interface.
        Initializes the color scheme, window properties, and layouts.

        Layout is split into 2 main containers:
            Top container: Contains title label
            Bottom container: Contains prompt label and 2 buttons
        """

        # Initialize color scheme
        color = ColorScheme()

        # Set window name and bg color
        self.setWindowTitle("Spotify Festival Playlist Generator")
        self.setStyleSheet(f"background-color: black;")

        # Create a QVBoxLayout for the main layout
        screen_layout = QVBoxLayout(self)
        margin = 10 # Space between containers and window edges
        screen_layout.setContentsMargins(margin, margin, margin, margin)
        screen_layout.setSpacing(margin)

        # Launch screen title. Acts as its own container.
        title_label = QLabel("Spotify Festival Playlist Generator", self)
        title_label.setStyleSheet(
            f"background-color: {color.dark_grey};"
            f"border-radius: 15px;"
            f"padding: 20px;"
            f"color: {color.spotify_green};"
            f"font-size: 24pt; font-weight: bold;"
            f"font-family: 'Arial Rounded MT Bold';"
        )
        title_label.setAlignment(Qt.AlignCenter)
        screen_layout.addWidget(title_label, Qt.AlignTop)

        # GroupBox container (for container/background design)
        container_groupbox = QGroupBox(self)
        container_groupbox.setStyleSheet(
            f"background-color: {color.dark_grey};"
            f"border-radius: 15px;"
        )

        # Add QVBoxLayout to control container layout
        container_layout = QVBoxLayout(container_groupbox)
        screen_layout.addWidget(container_groupbox)

        # Control spacing within container
        margin2 = 30
        container_layout.setContentsMargins(margin2, margin2, margin2, margin2)
        container_layout.setSpacing(margin2)

        # Create label to contain user prompt
        prompt_label = QLabel("How do you want to create your playlist?")
        prompt_label.setStyleSheet(
            "color: white;"
            "font-size: 16pt;"
            "font-family: 'Arial Rounded MT Bold';"
        )
        prompt_label.setAlignment(Qt.AlignCenter)
        container_layout.addWidget(prompt_label)

        # Define button size for buttons on this GUI screen
        button_size = (415, 120)

        # Use Custom Button class to create option "From Music Festival"
        button1 = CustomProceedButton(
            ["From Music Festival",
             "Create playlist for artists from a specific",
             "festival's lineup (using songkick.com).",
             "More artist names can be added later."
            ],
            click_handler=self.on_button1_clicked,
            size=button_size,
            hover_effect="expand"
        )
        container_layout.addWidget(button1, alignment=Qt.AlignCenter)

        # Use Custom Button class to create option "Enter Artist Names"
        button2 = CustomProceedButton(
            ["Enter Artist Names",
             "Manually enter multiple artist names."
            ],
            click_handler=self.on_button2_clicked,
            size=button_size,
            hover_effect="expand"
        )
        container_layout.addWidget(button2, alignment=Qt.AlignCenter)

    def on_button1_clicked(self):
        """If first button "From Music Festival" is clicked."""
        self.create_from_festival = True
        self.close()

    def on_button2_clicked(self):
        """If second button "Enter Artist Names" is clicked."""
        self.create_from_festival = False
        self.close()


def launch_gui_start_screen() -> bool:
    """
    Launch the PlaylistGenLaunchGui and return the user's button selection.

    Returns:
        bool: True if the user chooses to create a playlist from a festival,
              False if the user chooses to enter artist names manually.
    """
    # Initialize the QApplication and the PlaylistGenFestivalLink GUI instance
    app = QApplication(sys.argv)
    gui = PlaylistGenLaunchGui()

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

    return gui.create_from_festival

# Automatically launch GUI if this file executed as main script
if __name__ == "__main__":
    create_from_festival = launch_gui_start_screen()
    print(f"'Create from festival' selected? (T/F): {create_from_festival}")