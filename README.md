# Spotify Festival Playlist Generator
Creates a playlist for a specific music festival by using top songs from artists in the festival's lineup. Alternatively, a user can create a playlist just by entering multiple artists and a playlist will be created for the top songs from those artists. The user can select how many songs to include from each artist.

# Main Python Libraries Used
- Spotipy
- pandas
- PyQt5
- Beautiful Soup
- Plotly

Note: To use the Spotipy API, you need to setup an API client key and secret key (https://developer.spotify.com/documentation/web-api). In this application, 3 environment variables were setup: SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, and SPOTIFY_USER. The first and second are used for retrieving artist top tracks and track metadata. The third, SPOTIFY_USER, links to a Spotify account.

# Demo of Prototype
The below demo will be replaced by a video demo once the GUI has been improved and some planned features have been added.

Running run_playlist_generator.py launches the below GUI, which prompts the user for a songkick.com link for a specific music festival (as well as a couple other questions that will probably be moved to a different GUI screen in a future commit).

<img src="https://github.com/AustinLowey/SpotifyFestivalPlaylistGenerator/assets/49540411/a16681e6-f5dd-46e7-9b04-83a5f7bcb611" width="600">

The artist lineup is found using the user-provided link. The artists are searched for in Spotify and their popularity and genres (if there are any published), are shown in the below GUI. The user can scroll through the GUI and select which artists they want to include. They can also fill in other artists to add.

<img src="https://github.com/AustinLowey/SpotifyFestivalPlaylistGenerator/assets/49540411/4fff5e6c-f828-40ad-8d41-295c382bb583" width="600">

For each artist from the Artist Selection GUI screen, the top 10 (or user-chosen number, so in this example, it's actually 8) songs and their metadata are pulled using the Spotipy API. This includes popularities as well as song features like tempo and danceability. The song and artist data are saved to a .csv file.

<img src="https://github.com/AustinLowey/SpotifyFestivalPlaylistGenerator/assets/49540411/e33e57c6-786e-4de5-96be-1d972a7b2be0" width="600">

Finally, the playlist is created. This one included the top 8 songs from 12 different artists: AFROJACK, Alesso, Alison Wonderland, Armin Van Buuren, Excision, FISHER, Gorgon City, James Hype, Kaskade, Zedd, John Summit, and Hayla for 94 songs (not 96 songs, as 2 repeats were deleted). A total of 5 hours and 22 minutes.

<img src="https://github.com/AustinLowey/SpotifyFestivalPlaylistGenerator/assets/49540411/a493d5f4-941f-4a06-9e4e-70dfe44324a0" width="600">

A dashboard is also created in HTML/CSS, providing multiple capabilities:
1) Automated trend analysis on playlist song features (Tempo, Danceability, Energy and Speechiness) to identify the strongest trends present in the playlist data. This is especially useful if your playlist already fits specific qualities and you want to prune outliers to further strengthen those qualities.
2) Interactive feature plots for all 4 song features (all plotted vs. Song Popularity), where you can hover over any data point to see to which song and artist it belongs. Useful for finding outliers and further exploring playlist trends.
3) Summary information on the playlist and artists, including top playlist genres, similar artist recommendations, total runtime, number of songs, etc.
<img src="https://github.com/AustinLowey/SpotifyFestivalPlaylistGenerator/assets/49540411/d04301c5-f712-4779-99ad-a9d297a726e1" width="600">

Interactive hover functionality of Feature Plots:

<img src="https://github.com/AustinLowey/SpotifyFestivalPlaylistGenerator/assets/49540411/1390a26c-3206-4b23-bc5d-8fa918657d2c" width="600">

That's the end of the demo! Here's another playlist I made a few months ago for every artist that was in the Electric Zoo 2023 lineup. 818 songs and over 49 hours. Definitely wouldn't have made that manually!

<img src="https://github.com/AustinLowey/SpotifyFestivalPlaylistGenerator/assets/49540411/6f81ed91-e85b-4280-bb85-08b60b1aa292" width="600">
