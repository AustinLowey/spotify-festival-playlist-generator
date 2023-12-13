# This file going to be completely overhauled.

import sys

import pandas as pd

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QScrollArea, QLineEdit, QLabel, QTextBrowser, QFrame
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

class ArtistChooser(QMainWindow):
    def __init__(self, df_artists, festival, names_per_row=3):
        super().__init__()

        self.selected_names = []
        self.names_to_add = []
        self.additional_label_shown = False

        self.initUI(df_artists, festival, names_per_row)

    def initUI(self, df_artists, festival, names_per_row):
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()
        central_widget.setStyleSheet("background-color: rgb(18, 18, 18);")

        select_label = QLabel(f'Select "{festival}" artists to include in your playlist:')
        select_label.setStyleSheet("color: rgb(30, 215, 96); font-size: 32px;")
        layout.addWidget(select_label)

        scroll_area = QScrollArea()
        scroll_area.setStyleSheet(
            """
            QScrollBar:vertical, QScrollBar:horizontal {
                border: 1px solid #222222;
                background: #121212;
                width: 12px;
                margin: 0px 0px 0px 0px;
            }

            QScrollBar::handle:vertical, QScrollBar::handle:horizontal {
                background: #1ED760;
                min-height: 20px;
            }

            QScrollBar::add-line:vertical, QScrollBar::add-line:horizontal {
                background: #121212;
                height: 0px;
                subcontrol-position: bottom;
                subcontrol-origin: margin;
            }

            QScrollBar::sub-line:vertical, QScrollBar::sub-line:horizontal {
                background: #121212;
                height: 0 px;
                subcontrol-position: top;
                subcontrol-origin: margin;
            }

            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical,
            QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
                background: #121212;
            }
            """
        )
        scroll_widget = QWidget()
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)

        checkboxes_layout = QVBoxLayout()
        row = QWidget()
        row_layout = QHBoxLayout()

        max_button_width = 500
        
        for i, row_df in df_artists.iterrows():
            name = row_df['Artist']
            popularity = row_df['Artist Popularity']
            genres = row_df['Artist Genres']
            
            if i == len(df_artists) - 1:
                button = QPushButton()
            else:
                button = QPushButton()
            button.setText("")  # Set text of the QPushButton to an empty string
            button.setStyleSheet("background-color: rgb(40, 40, 40); border-style: outset; border-width: 2px; border-color: rgb(30, 215, 96); border-radius: 10px; text-align: center;")
            button.setFixedHeight(115)
            button.setCheckable(True)
            button.clicked.connect(self.button_clicked)
            button.setProperty("artist_name", name)  # Store the artist name as a property

            # Create a QLabel for the top line with a larger white font
            top_line_label = QLabel(name)
            top_line_label.setStyleSheet("color: white; border: none;")
            top_line_label.setFont(QFont("Arial Rounded MT Bold", 14))  # Increase font size
            
            if genres:
                genres_str = ', '.join(genres)
            else:
                genres_str = "N/A"
            other_lines_label = QLabel(f"Popularity: {popularity}\nGenres: {genres_str}")
            other_lines_label.setStyleSheet("color: grey; border: none;")
            other_lines_label.setFont(QFont("Arial Rounded MT Bold", 10))  # Decrease font size
            other_lines_label.setWordWrap(True)  # Allow text to wrap to the next line

            # Create a QVBoxLayout to contain the top and other lines labels
            label_layout = QVBoxLayout()
            label_layout.addWidget(top_line_label)
            label_layout.addWidget(other_lines_label)
            label_layout.setAlignment(Qt.AlignTop)

            button_layout = QVBoxLayout()
            button_layout.addLayout(label_layout)
            button.setLayout(button_layout)

            row_layout.addWidget(button)

            if (i + 1) % names_per_row == 0 or i == len(df_artists) - 1:
                row.setLayout(row_layout)
                checkboxes_layout.addWidget(row)
                row = QWidget()
                row_layout = QHBoxLayout()

        # Set a fixed width for all buttons
        for i in range(checkboxes_layout.count()):
            row = checkboxes_layout.itemAt(i).widget()
            for btn in row.findChildren(QPushButton):
                btn.setFixedWidth(max_button_width)

        scroll_widget.setLayout(checkboxes_layout)
        layout.addWidget(scroll_area)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Add additional artists to include in the playlist (type-in artist then press Enter)")
        self.name_input.setStyleSheet("color: white;")
        self.name_input.setFont(QFont("Arial Rounded MT Bold", 14))
        self.name_input.returnPressed.connect(self.add_name)
        layout.addWidget(self.name_input)

        self.additional_artists_label = QLabel("Additional artists that will be added to playlist:")
        self.additional_artists_label.setStyleSheet("color: white;")
        self.additional_artists_label.setFont(QFont("Arial Rounded MT Bold", 14))
        self.additional_artists_label.hide()  # Initially hide the label
        layout.addWidget(self.additional_artists_label)

        self.names_list = QTextBrowser()
        
        # Set the stylesheet for QTextBrowser scroll bars
        self.names_list.setStyleSheet(
            """
            QScrollBar:vertical, QScrollBar:horizontal {
                border: 1px solid #222222;
                background: #121212;
                width: 12px;
                margin: 0px 0px 0px 0px;
            }

            QScrollBar::handle:vertical, QScrollBar::handle:horizontal {
                background: #1ED760;
                min-height: 20px;
            }

            QScrollBar::add-line:vertical, QScrollBar::add-line:horizontal {
                background: #121212;
                height: 0px;
                subcontrol-position: bottom;
                subcontrol-origin: margin;
            }

            QScrollBar::sub-line:vertical, QScrollBar::sub-line:horizontal {
                background: #121212;
                height: 0 px;
                subcontrol-position: top;
                subcontrol-origin: margin;
            }

            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical,
            QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
                background: #121212;
            }
            
            QTextBrowser {
                color: white;
                border: 2px solid #1ED760; /* Set the border color */
            }
            """
        )
        self.names_list.setFont(QFont("Arial Rounded MT Bold", 14))
        self.names_list.setOpenExternalLinks(True)
        self.names_list.setFixedHeight(80)
        self.names_list.setLineWrapMode(QTextBrowser.WidgetWidth)  # Enable text wrapping
        self.names_list.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)  # Show vertical scroll bar when needed
        self.names_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)  # Show horizontal scroll bar when needed
        self.names_list.setFrameShape(QFrame.NoFrame)  # Initially set frame shape to NoFrame
        self.names_list.hide()  # Initially hide the QTextBrowser
        layout.addWidget(self.names_list)

        button_layout = QHBoxLayout()
        create_playlist_button = QPushButton("Create Playlist")
        create_playlist_button.clicked.connect(self.get_selected_names)
        create_playlist_button.setStyleSheet("background-color: rgb(30, 215, 96); color: black; border-style: outset; border-width: 2px; border-color: rgb(18, 18, 18); border-radius: 40px;")
        create_playlist_button.setFixedHeight(100)
        create_playlist_button.setFixedWidth(240)
        create_playlist_button.setFont(QFont("Arial Rounded MT Bold", 18))
        button_layout.addWidget(create_playlist_button)
        layout.addLayout(button_layout)

        central_widget.setLayout(layout)

    def button_clicked(self):
        button = self.sender()
        if button.isChecked():
            button.setStyleSheet("background-color: rgb(30, 215, 96); color: white; border-style: outset; border-width: 2px; border-color: rgb(40, 40, 40); border-radius: 10px;")
        else:
            button.setStyleSheet("background-color: rgb(40, 40, 40); border-style: outset; border-width: 2px; border-color: rgb(30, 215, 96); border-radius: 10px;")

    def add_name(self):
        name = self.name_input.text()
        if name.strip():
            self.names_to_add.append(name)
            self.name_input.clear()
            self.update_names_list()
            if not self.additional_label_shown:
                self.additional_artists_label.show()
                self.names_list.show()  # Show the QTextBrowser after the first name is added
                self.names_list.setFrameShape(QFrame.Box)  # Change frame shape to Box
                self.additional_label_shown = True

    def update_names_list(self):
        self.names_list.setPlainText(", ".join(self.names_to_add))

    def get_selected_names(self):
        selected_buttons = [widget.property("artist_name") for widget in self.findChildren(QPushButton) if widget.isChecked()]
        new_artist_names = self.names_to_add.copy()
        self.selected_names = selected_buttons.copy()
        self.close()
        return self.selected_names, new_artist_names

    def get_selected_names_list(self):
        return self.selected_names, self.names_to_add

def select_artist_names(df_artists, festival):
    app = QApplication(sys.argv)
    window = ArtistChooser(df_artists, festival, names_per_row=3)
    window.setWindowTitle("Spotify Festival Playlist Generator - Artist Selection")
    window.setGeometry(160, 100, 1600, 900)
    window.show()

    app.exec_()

    selected_buttons, new_artist_names = window.get_selected_names_list()
    selected_artist_names = [artist.split("\n")[0] for artist in selected_buttons]

    if __name__ == "__main__":
        print(f"Selected Buttons: {selected_artist_names}")
        print(f"New/Added Artist Names: {new_artist_names}")

    return selected_artist_names, new_artist_names


if __name__ == "__main__":
    artist_names = ['Alanis Morissette', 'Ali Sethi', 'Angel White', 'Arya (Serbia)', 'BLOND:ISH', 'Ben Kweller', 'Breland', 'CVC', 'Calder Allen', 'Celisse',
             'Charlotte Adigéry & Bolis Pupul', 'Cigarettes After Sex', 'Declan McKenna', 'Delacey', 'Eloise', 'Foo Fighters', 'Hozier', 'Katy Kirby',
             'M83', 'Madison Cunningham', 'Maggie Rogers', 'Major Lazer', 'Morgan Wade', 'Mumford & Sons', 'Nemegata', 'Nessa Barrett', 'Noah Kahan',
             'ODESZA', 'Oliver Hazard', 'SIDEPIECE', 'Shania Twain', 'Suki Waterhouse', 'Sunrose', 'The 1975', 'The Breeders', 'The Lumineers',
             'The Mars Volta', 'The Teskey Brothers', 'The Walkmen', 'Tove Lo', 'Yeah Yeah Yeahs', 'corook', 'half•alive']
    genres = [['canadian pop', 'canadian singer-songwriter', 'lilith', 'neo mellow', 'pop rock', 'singer-songwriter'],
              ['classic pakistani pop', 'indian indie', 'pakistani pop', 'sufi'], [], [], ['deep disco house'],
              ['dallas indie', 'pop rock'], ['black americana'], ['cardiff indie'], [], [], ['belgian electronic', 'belgian indie'],
              ['ambient pop', 'dream pop', 'el paso indie', 'shoegaze'], ['pov: indie'], ['modern alternative pop'], ['bedroom soul'],
              ['alternative metal', 'alternative rock', 'modern rock', 'permanent wave', 'post-grunge', 'rock'],
              ['irish singer-songwriter', 'modern rock', 'pov: indie'], ['indie pop'],
              ['french shoegaze', 'french synthpop', 'indietronica', 'metropopolis', 'neo-synthpop'], ['pop folk'], ['indie pop'],
              ['dance pop', 'edm', 'electro house', 'moombahton', 'pop', 'pop dance'], ['modern country pop'],
              ['modern folk rock', 'modern rock', 'neo mellow', 'stomp and holler', 'uk americana'], [], ['social media pop'],
              ['pov: indie'], ['chillwave', 'edm', 'indietronica'], ['stomp and holler'], ['edm', 'house', 'tech house'],
              ['canadian country', 'canadian pop', 'contemporary country', 'country', 'country dawn'], ['indie pop'], [],
              ['modern alternative rock', 'modern rock', 'pop', 'pov: indie', 'rock'], ['alternative rock', 'boston rock'],
              ['folk-pop', 'modern rock', 'stomp and holler'], ['el paso indie', 'garage rock'], ['australian americana'],
              ['chamber pop', 'indie rock', 'noise pop'],
              ['dance pop', 'metropopolis', 'pop', 'swedish electropop', 'swedish pop', 'swedish synthpop'],
              ['alternative dance', 'alternative rock', 'art pop', 'chamber pop', 'dance-punk', 'garage rock', 'indie rock', 'modern rock', 'neo-synthpop', 'new rave'],
              [], ['alt z', 'pov: indie']]
    popularity = [65, 56, 24, 47, 55, 34, 56, 30, 21, 15, 37, 79, 61, 40, 51, 75, 80, 37, 68, 47, 66, 73,
                    53, 69, 7, 66, 82, 67, 50, 59, 70, 63, 10, 74, 50, 76, 47, 62, 44, 71, 63, 45, 56]

    df_artists = pd.DataFrame({'Artist': artist_names,
                               'Artist Genres': genres,
                               'Artist Popularity': popularity,
                               })
    festival = "Austin City Limits Music Festival 2023"
    
    selected_artist_names, new_artist_names = select_artist_names(df_artists, festival)
