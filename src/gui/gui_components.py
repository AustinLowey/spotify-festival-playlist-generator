from typing import List, Tuple, Callable

import requests
import numpy as np
import cv2
from PyQt5.QtWidgets import (
    QHBoxLayout, QLabel, QPushButton, QRadioButton, 
    QSizePolicy, QSpacerItem, QVBoxLayout, QWidget
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush, QImage, QPainter, QPainterPath, QPixmap

class ColorScheme:
    """A class to manage the color scheme for GUIs. Based off Spotify."""

    def __init__(self):
        self.spotify_green = "rgb(30, 215, 96)"
        self.dark_grey = "rgb(18, 18, 18)"
        self.mid_grey = "rgb(40, 40, 40)"
        self.lt_grey = "rgb(80, 80, 80)"
        self.lighter_grey = "rgb(100, 100, 100)"
        self.lightest_grey = "rgb(160, 160, 160)" # For text

        # This rgba style (w/ a=0) makes color transparent
        self.transparent = "rgba(0, 0, 0, 0)"

        # Note: Black and white are also used in GUI color schemes.


class CustomProceedButton(QPushButton):
    """Custom next-screen button to be used throughout the entire GUI."""

    def __init__(
        self,
        button_text: List[str],
        click_handler: Callable[[], None] = None,
        size: Tuple[int, int] = (430, 125),
        hover_effect: str = "expand"
    ) -> None:
        """
        Custom button class for use across GUIs.

        Parameters:
            button_text (list): A list of strings, with each string
                representing a line of text for the button.
            click_handler (function): The function called on button click.
            size (tuple, optional): Button size. Defaults to (430, 125).
            hover_effect (str): Type of hover effect.
        """

        super().__init__()

        # Initialize color scheme
        color = ColorScheme()

        # Set the button size and style
        self.setFixedSize(*size) # * unpacks tuple
        self.setStyleSheet(
            f"background-color: {color.spotify_green};"
            f"border-radius: 15px;"
            f"color: black;"
            f"font-family: 'Arial Rounded MT Bold';"
        )

        # Create a layout to add margins
        self.button_layout = QVBoxLayout()
        self.button_layout.setContentsMargins(35, 10, 2, 2)

        # Generate HTML for the button text with different font sizes
        lines = []
        for i, line in enumerate(button_text):
            if i == 0: # If first line, make font larger
                lines.append(
                    f'<div style="font-size: 24px;'
                    f'margin-bottom: 5px;">{line}</div>'
                )
            else: # Smaller font for subsequent lines
                lines.append(
                    f'<div style="font-size: 18px;'
                    f'margin-bottom: 0px;">{line}</div>'
                )
        combined_text = "".join(lines)

        # Create a QLabel to display the combined HTML-formatted text
        combined_label = QLabel()
        combined_label.setTextFormat(Qt.RichText)
        combined_label.setText(combined_text)
        combined_label.setAlignment(Qt.AlignTop) # maybe delete this

        # Make QLabel transparent for mouse events (for clicking PushButton)
        combined_label.setAttribute(Qt.WA_TransparentForMouseEvents, True)

        # Add QLabel to vertical layout, then set button layout
        self.button_layout.addWidget(combined_label, alignment=Qt.AlignLeft)
        self.setLayout(self.button_layout)

        # Expand button when hovering
        if hover_effect == "expand":
            self.size = size
            self.enterEvent = self.on_hover_enter # When hovering over button
            self.leaveEvent = self.on_hover_leave # After hovering ends

        # Note: May later add another hover_effect for color change.
        # Maybe also one to make text bold during hover.

        # Connect the click event to the specified handler
        if click_handler:
            self.clicked.connect(click_handler)
         # else: Button is for show only, with no functionality yet


    def on_hover_enter(self, event):
        """When hovering over button, increase width and text left-padding."""

        self.setFixedSize(self.size[0] + 20, self.size[1])
        self.button_layout.setContentsMargins(45, 10, 2, 2)


    def on_hover_leave(self, event):
        """When hovering ends, reset button."""

        self.setFixedSize(*self.size)
        self.button_layout.setContentsMargins(35, 10, 2, 2)


class YesNoRadioButtons(QWidget):
    """Class for custom, side-by-side Yes/No radio buttons."""

    def __init__(
        self,
        indent_value: int,
        default_checked: bool = True
    ) -> None:
        super().__init__()

        # Import color scheme
        color = ColorScheme()

        # Define style to be used for both radio buttons
        button_style = (
            f"background-color: {color.mid_grey};"
            f"border-radius: 10px;"
            f"margin-left: {indent_value / 1.25};"
            f"padding: 5px 10px 5px 10px;" 
        )

        # Define style for hover effect
        button_hover_style = (
            f"background-color: {color.lt_grey};"  # Lighter color on hover
            f"border-radius: 10px;"
            f"margin-left: {indent_value / 1.25};"
            f"padding: 5px 10px 5px 10px;"
        )

        # Create yes button
        self.yes_button = QRadioButton("Yes")
        self.yes_button.setStyleSheet(button_style)
        self.yes_button.enterEvent = (
            lambda event: self.on_hover_enter(
                self.yes_button,
                button_hover_style
            )
        )
        self.yes_button.leaveEvent = (
            lambda event: self.on_hover_leave(
                self.yes_button,
                button_style
            )
        )

        # Create no button
        self.no_button = QRadioButton("No")
        self.no_button.setStyleSheet(button_style)
        self.no_button.enterEvent = (
            lambda event: self.on_hover_enter(
                self.no_button,
                button_hover_style
            )
        )
        self.no_button.leaveEvent = (
            lambda event: self.on_hover_leave(
                self.no_button,
                button_style
            )
        )

        # Make buttons have same width
        width = 105
        self.yes_button.setFixedWidth(width)
        self.no_button.setFixedWidth(width)

        # Create spacer to shift buttons toward the left of screen
        spacer_item = QSpacerItem(
            0,
            0,
            QSizePolicy.Expanding,
            QSizePolicy.Minimum
        )

        # Create row layout,combine buttons into it, and control spacing
        layout = QHBoxLayout(self)
        layout.addWidget(self.yes_button)
        layout.addWidget(self.no_button)
        layout.addSpacerItem(spacer_item)
        layout.setSpacing(0) # Spacing between Yes and No buttons

        # Set radio buttons group default state
        if default_checked:
            self.yes_button.setChecked(True)
        else:
            self.no_button.setChecked(True)
    
    
    def on_hover_enter(self, radio_button, hover_style):
        """When hovering over the radio button, change its style."""
        radio_button.setStyleSheet(hover_style)


    def on_hover_leave(self, radio_button, normal_style):
        """When hovering ends, reset the radio button style."""
        radio_button.setStyleSheet(normal_style)


class ArtistSelectionButton(QPushButton):
    """Custom button to be used in the Artist Selection screen."""

    def __init__(
        self,
        name: str,
        popularity: int,
        genres_list: List[str],
        img_url: str = None
    ) -> None:
        """
        Initializes the ArtistSelectionButton instance.

        Parameters:
            name (str): Artist name
            popularity (int): Popularity of the artist (b/w 1-100)
            genres_list (List[str]): List of artist genres, if any
            img_url (str, optional): URL of the artist's image/logo
        """
        
        super().__init__()
        self.is_selected = False # Initialize button selection state
        self.clicked.connect(self.toggle_selection) # Connect to click event

        # Initialize color scheme
        self.color = ColorScheme()

        # Button size
        self.button_width = 500
        self.button_height = 117
        self.radius = 10 # Rounded corners

        # Used in GUI screen code for returning list of names
        self.name = name

        self.setStyleSheet(
            # Button bg color and border:
            f"background-color: {self.color.mid_grey};"
            f"border-radius: {self.radius}px;"
        )
        self.setFixedSize(self.button_width, self.button_height)

        # Button layout, split between logo (left) and text (right)
        button_layout = QHBoxLayout(self)

        # If logo provided (so that this can be toggled on/off)
        try:
            # Fetch and process logo image, then add to layout
            logo_array = self.img_url_to_array(img_url)
            logo_label = self.create_logo_label(logo_array)
            button_layout.addWidget(logo_label)
        except:
            pass
        
        # QVBoxLayout for organizing text
        text_layout = QVBoxLayout()
        button_layout.addLayout(text_layout)
        button_layout.addStretch() # Push text_layout left
        button_layout.addSpacing(9) # Spacing b/w logo and text
        text_layout.addSpacing(10) # Spacing above top label
        text_layout.setSpacing(9) # Spacing b/w text labels

        # Top text line label (artist name). Slightly larger, white font.
        name_label = QLabel(name)
        name_label.setStyleSheet(
            "font-size: 14pt;"
            "color: white;"
        )
        text_layout.addWidget(name_label)
        text_layout.setAlignment(name_label, Qt.AlignTop)

        # Popularity and genres label. Slightly smaller, grey font.
        # Both in same label to keep spacing as tight as possible.
        if genres_list:
            genres_str = ', '.join(genres_list)
        else: # Edge case if Spotify doesn't have genre published for artist
            genres_str = "N/A"
        popularity_genres_label = QLabel(
            f"Popularity: {popularity}\n"
            f"Genres: {genres_str}"
        )
        popularity_genres_label.setStyleSheet(
            f"color: {self.color.lightest_grey};"
            f"font-family: 'Arial Rounded MT Bold';"
            f"font-size: 10pt;"
        )
        popularity_genres_label.setWordWrap(True)
        popularity_genres_label.setAlignment(Qt.AlignTop)
        popularity_genres_label.setMaximumHeight(
            3 * popularity_genres_label.fontMetrics().lineSpacing() + 12
        ) # Cut off genres if more than 2 lines of them
        button_layout.setContentsMargins(0, 0, 0, 0) # Crops bottom of text
        text_layout.addWidget(popularity_genres_label)

        # Push popularity_genres_label upward
        text_layout.addStretch()


    def toggle_selection(self):
        """Toggle button selection state."""
        self.is_selected = not self.is_selected
        self.update_style()


    def update_style(self):
        """Update button style based on current selection state."""
        if self.is_selected:
            self.setStyleSheet(
                f"background-color: {self.color.lt_grey};"
            )
        else:
            self.setStyleSheet(
                f"background-color: {self.color.mid_grey};"
        )


    def img_url_to_array(self, img_url: str) -> np.array:
        """Fetches image from given URL and converts it to a NumPy array."""
        
        response = requests.get(img_url)
        img_array = np.asarray(bytearray(response.content), dtype=np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

        return img


    def create_logo_label(self, logo_array: np.ndarray) -> QLabel:
        """Creates a QLabel with a rounded logo from a given image array."""

        # Convert image array to QPixmap
        logo_pixmap = QPixmap.fromImage(
            QImage(
                logo_array.data,
                logo_array.shape[1],
                logo_array.shape[0],
                QImage.Format_BGR888
            )
        )

        # Create a rounded rectangle mask
        mask = QPixmap(self.button_height, self.button_height)
        mask.fill(Qt.transparent)
        painter = QPainter(mask)
        painter.setRenderHint(QPainter.Antialiasing, True)

        # Create a QPainterPath for the rounded rectangle mask
        path = QPainterPath()
        path.addRoundedRect(
            0,
            0,
            self.button_height,
            self.button_height,
            self.radius,
            self.radius
        )

        # Set the painter clip path and draw rounded rect onto the mask
        painter.setClipPath(path)
        painter.setBrush(QBrush(Qt.black))
        painter.drawRoundedRect(
            0,
            0,
            self.button_height,
            self.button_height,
            self.radius,
            self.radius
        )
        painter.end()

        # Apply the mask to the original pixmap
        rounded_pixmap = QPixmap(self.button_height, self.button_height)
        rounded_pixmap.fill(Qt.transparent)
        painter.begin(rounded_pixmap)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setClipPath(path)
        painter.drawPixmap(0, 0, logo_pixmap)
        painter.end()

        # Create QLabel for processed logo
        logo_label = QLabel()
        logo_label.setPixmap(
            rounded_pixmap.scaled(
                self.button_height,
                self.button_height,
                aspectRatioMode=Qt.IgnoreAspectRatio,
                transformMode=Qt.SmoothTransformation
            )
        )

        return logo_label


# Test the custom button if executed as main
if __name__ == "__main__":
    def test_custom_button():
        import sys
        from PyQt5.QtWidgets import QApplication
        import numpy as np

        # Example data for testing
        name = "Artist Test Name"
        popularity = 75
        genres = ["Pop", "Rock", "Electronic", "Punk Rock", "Classic Rock"]
        image_url = (
            "https://i.scdn.co/image/ab6761610000f178133f44ab343b35c715a4ac97"
        )

        app = QApplication(sys.argv)
        custom_button = ArtistSelectionButton(
            name,
            popularity,
            genres,
            image_url
        )
        custom_button.show()
        sys.exit(app.exec_())

    test_custom_button()