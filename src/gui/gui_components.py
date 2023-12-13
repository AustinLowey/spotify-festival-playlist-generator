from typing import List, Tuple, Callable

from PyQt5.QtWidgets import (
    QHBoxLayout, QLabel, QPushButton, QRadioButton, 
    QSizePolicy, QSpacerItem, QVBoxLayout, QWidget
)
from PyQt5.QtCore import Qt

class ColorScheme:
    """A class to manage the color scheme for GUIs. Based off Spotify."""

    def __init__(self):
        self.spotify_green = "rgb(30, 215, 96)"
        self.dark_grey = "rgb(18, 18, 18)"
        self.mid_grey = "rgb(40, 40, 40)"
        self.lt_grey = "rgb(80, 80, 80)"
        self.lighter_grey = "rgb(100, 100, 100)"

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

        # Call the constructor of the base class (QPushButton)
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
        layout.setSpacing(10) # Spacing between Yes and No buttons

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