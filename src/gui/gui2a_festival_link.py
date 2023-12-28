import sys
from typing import Tuple

from PyQt5.QtWidgets import (
    QApplication, QDesktopWidget, QGridLayout, QGroupBox,
    QLabel, QLineEdit, QMessageBox, QVBoxLayout, QWidget
)
from PyQt5.QtCore import Qt

from gui.gui_components import ColorScheme, CustomProceedButton


class PlaylistGenFestivalLinkGui(QWidget):
    """Festival link screen GUI class."""

    def __init__(self) -> None:
        """
        Initialize the PlaylistGenFestivalLink GUI.

        Sets up the GUI components and initializes GUI output variables.
        """

        super().__init__()
        self.skip_this_step = False # Output #1 from this GUI screen
        self.festival_link = ""  # Output #2 from this GUI screen
        self.init_ui() # Set up GUI
        
    def init_ui(self) -> None:
        """
        Set up the user interface.
        Initializes the color scheme, window properties, and layouts.
        
        Layout has a container, which has:
            4 labels of text, 1 containing a hyperlink
            1 QLineEdit for user to enter a link
            2 button options
        """

        # Initialize color scheme
        color = ColorScheme()

        # Set window name and bg color
        self.setWindowTitle(
            "Spotify Festival Playlist Generator - Enter Festival Link"
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

        # GroupBox container (for container/background design)
        container_groupbox = QGroupBox(self)
        container_groupbox.setStyleSheet(
            f"background-color: {color.dark_grey};"
            f"border-radius: 15px;"
            # Set font style for every label in this container:
            f"font-size: 14pt;"
            f"color: white;"
            f"font-family: 'Arial Rounded MT Bold';"
        )

        # Add QVBoxLayout to control container layout
        container_layout = QVBoxLayout(container_groupbox)
        screen_layout.addWidget(container_groupbox)

        # Control spacing within container
        container_margin = 30
        container_layout.setContentsMargins(
            container_margin,
            container_margin,
            container_margin,
            container_margin
        )
        container_layout.setSpacing(container_margin)

        # Create label to contain user prompt
        prompt_label = QLabel("Enter your festival's songkick link:")
        prompt_label.setStyleSheet("font-size: 16pt;") # Slightly larger font
        container_layout.addWidget(prompt_label)

        # Define indent value for the remaining QLabels and QLineEdit
        indent_value = 20

        # Create hyperlink to use in Step 1 label
        songkick_url = "https://www.songkick.com"
        display = "www.songkick.com"
        hyperlink = '<a href="{0}">{1}</a>'.format(songkick_url, display)

        # Create Step 1 label
        step1_label = QLabel(f"Step 1) Go to {hyperlink}")
        step1_label.setOpenExternalLinks(True)
        step1_label.setIndent(indent_value)
        container_layout.addWidget(step1_label)

        # Create Step 2 label
        step2_label = QLabel(
            "Step 2) Enter the name of the music festival "
            "you want into the website's search bar."
        )
        step2_label.setContentsMargins(
            indent_value,
            0,
            indent_value,
            0
        ) # Add indent to both left and right side of label (longest label)
        container_layout.addWidget(step2_label)

        # Create Step 3 label
        step3_label = QLabel(
            "Step 3) Select the festival, then copy and paste the link below."
        )
        step3_label.setIndent(indent_value)
        container_layout.addWidget(step3_label)

        # Create QLineEdit to let user input link
        self.url_lineedit = QLineEdit(self)
        self.url_lineedit.setPlaceholderText(
            "Enter your festival's website link"
        )
        self.url_lineedit.setStyleSheet(
            f"background-color: {color.mid_grey};"
            f"color: white;"
            f"border-radius: 16px;"
            f"padding: 2px;"
            f"padding-left: 10px;"
            f"margin-left: {indent_value};"
            f"margin-right: {indent_value};"
        )
        
        self.url_lineedit.returnPressed.connect(
            self.proceed_to_artist_selection
        ) # If ENTER key is pressed, proceed to next page
        container_layout.addWidget(self.url_lineedit)

        # Add some spacing between the QLineEdit and buttons_layout
        container_layout.addSpacing(50)

        # Create a QGridLayout to control layout of buttons
        # Note: Grid chosen over QHBoxLayout to get best button hover effect
        self.buttons_layout = QGridLayout()
        container_layout.addLayout(self.buttons_layout)

        # Add margins for buttons_layout
        # Left, right, and bottom margins equal to indent value
        self.buttons_layout.setContentsMargins(
            indent_value,
            0,
            indent_value,
            indent_value
        )

        # Extra spacing to push buttons further away from center
        self.buttons_layout.setHorizontalSpacing(225)

        # Use Custom Button class to create a proceed button to next page
        proceed_button = CustomProceedButton(
            [
                "Select Artists",
                "Go to artist selection page",
                "to choose artists from your  ",
                "festival's lineup."
            ],
            click_handler=self.proceed_to_artist_selection,
        )
        self.buttons_layout.addWidget(
            proceed_button,
            0, 0, 1, 1,
            alignment=Qt.AlignCenter
        )

        # Use Custom Button class to create a button to skip this page
        skip_button = CustomProceedButton(
            [
                "Skip This Step",
                "Can't find the link to your",
                "festival's lineup? Enter artist",
                "names manually instead."
             ],
             click_handler=self.skip_festival_link,
        )
        skip_button.setStyleSheet(
            # Override button style for color and border
            "QPushButton {"
            f"background-color: {color.mid_grey};"
            f"border: 2px solid {color.spotify_green};"
            "}"

            # Override label (button text) style for color
            "QLabel {"
            f"background-color: {color.mid_grey};"
            "}"
        )
        self.buttons_layout.addWidget(
            skip_button,
            0, 1, 1, 1,
            alignment=Qt.AlignCenter
        )
        

    def proceed_to_artist_selection(self) -> None:
        """
        Process the user's input and proceed to the artist selection page.

        Gets the festival link from the user input and checks if it is a
        valid songkick.com link. Displays a warning message box if invalid.
        """

        self.festival_link = self.url_lineedit.text()

        # Check if the QLineEdit text contains "songkick.com"
        # If not, warning message box prompts user to enter a valid link
        if "songkick.com" not in self.festival_link:
            color = ColorScheme()
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Invalid URL")
            msg_box.setText("Enter a valid songkick.com link.")
            msg_box.setIcon(QMessageBox.Warning) # Add warning icon
            msg_box.setStyleSheet(
                # Set warning message box text style
                "QMessageBox QLabel {"
                "color: white;"
                "font-family: 'Arial Rounded MT Bold';"
                "}"

                #Set warning message box "OK" button style
                "QMessageBox QPushButton {"
                f"background-color: {color.mid_grey};"
                f"color: white;"
                f"font-family: 'Arial Rounded MT Bold';"
                "}"
            )
            msg_box.exec_()
            return

        # Close the window
        self.close()


    def skip_festival_link(self) -> None:
        """
        Action to skip the festival link step when skip-button is clicked.
        """

        # Sets "skip step" bool to True and closes window
        self.skip_this_step = True
        self.close()


def launch_gui_festival_link() -> Tuple[bool, str]:
    """
    Launch the Festival Link GUI.

    Initializes the QApplication and PlaylistGenFestivalLink GUI instance.
    Centers the window on the screen and starts the application's event loop
    for interaction handling.

    Returns:
        Tuple[bool, str]: Tuple containing skip_this_step flag and
            festival link.
    """

    # Initialize the QApplication and the PlaylistGenFestivalLink GUI instance
    app = QApplication(sys.argv)
    gui = PlaylistGenFestivalLinkGui()

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

    return gui.festival_link, gui.skip_this_step


# Automatically launch GUI if this file executed as main script
if __name__ == "__main__":
    festival_link, skip_this_step = launch_gui_festival_link()
    print(f"'Skip this step' selected? (T/F): {skip_this_step}")
    print(f"Festival Link: {festival_link}")