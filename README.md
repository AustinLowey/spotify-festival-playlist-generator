# Spotify Festival Playlist Generator

## Top-Level Overview
- Generates a Spotify playlist by curating top tracks from either a user-inputted music festival's artist lineup and/or manually entered artists' names.
- Can create a playlist with dozens of hours of songs in 1-2 minutes.
- Scrapes and extracts a specific music festival's lineup using Beautiful Soup.
- Guides users through the process with a set of PyQt GUI screens, facilitating artist selection from the imported festival lineup.
- Leverages Spotipy to retrieve top tracks for each artist and create a playlist in Spotify.
- Delivers automated track feature analytics using track metadata and presents the user with an HTML/CSS playlist summary dashboard.

### Demo Video:

<a href="https://youtu.be/xa2-pl23kBE" target="_blank">
  <img src="https://github.com/AustinLowey/SpotifyFestivalPlaylistGenerator/assets/49540411/e9c5905b-9d67-4118-a7e8-38f6da1d098c" width="600">
</a>

## Main Python Libraries Used
- pandas
- Spotipy (Python library for the Spotify Web API)
- PyQt5
- Beautiful Soup
- Plotly

Note: To use the Spotipy API, you need to setup an API client key and secret key (https://developer.spotify.com/documentation/web-api). In this application, 3 environment variables were setup: SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, and SPOTIFY_USER. The first and second are used for retrieving artist top tracks and track metadata. The third, SPOTIFY_USER, links to a Spotify account.

## Demo
A video will be added in the coming weeks, once a few more planned GUI features/improvements have been implemented.

Running run_playlist_generator.py launches the below GUI, which asks the user if they'd like to create a playlist for a specific music festival or create a playlist by manually enter artist names.

<img src="https://github.com/AustinLowey/SpotifyFestivalPlaylistGenerator/assets/49540411/704ef100-d016-45a6-9c3c-b2219be24e39" width="600">

If the user picks the "From Music Festival" option, they are taken to the below screen, where they are asked to get a songkick.com link for a specific music festival. The second option, "Enter Artist Names," has not yet been implemented, but will be useful for if the music festival isn't available on songkick.com

<img src="https://github.com/AustinLowey/SpotifyFestivalPlaylistGenerator/assets/49540411/08753f9d-5b72-475e-9d14-0c5b5384c63a" width="600">

The artist lineup is obtained using the user-provided link. Each artist in the lineup is then searched for in Spotify and the artists' popularities and genres (if there are any published), are shown in the below GUI. The user can scroll through the GUI and select which artists they want to include. They can also manually enter other artists to add.

<img src="https://github.com/AustinLowey/SpotifyFestivalPlaylistGenerator/assets/49540411/b376979e-758e-4d51-8f3e-89b3865117a5" width="600">

The next GUI screen shows some info about the to-be-created playlist, as well as allows the user to customize the playlist using the following inputs:
1) Number of songs from each artist.
2) If the user wants less songs for less popular artists. If this option is selected, the amount of songs per artist scales with that artist's popularity. For example, if the user selects 8 songs per artist in step 1 and the highest and lowest artist popularities are 80 and 15, respectively, then the created playlist will have 8 songs for the more popular artist and 3 songs for the less popular artist. Other artists in the middle of that range will have a varying number of songs, linearly scaling with popularity.
3) If the user wants to include multiple versions (i.e., remixes or edits) of the same song. If "no" is selected for this option, only the song with the highest popularity will be retained. Exact duplicates are already automatically removed, regardless of what is selected for this step.

<img src="https://github.com/AustinLowey/SpotifyFestivalPlaylistGenerator/assets/49540411/453541e4-4cab-4fd2-bb3c-82b8a6fe7c99" width="600">

Finally, the playlist is created. For each artist, the top tracks per artist and their metadata, including track popularities and track features like tempo and danceability, are pulled using the Spotipy API. This playlist included the top (up to) 8 songs from 11 different artists, for a total of 70 songs (not 88 songs, as multiple remixes were removed and less songs were included for less popular artists), with a runtime of 3 hours and 50 minutes.

<img src="https://github.com/AustinLowey/SpotifyFestivalPlaylistGenerator/assets/49540411/6b6c26b4-9a43-4383-aee9-8ed3ea5b3b52" width="600">

The artist and song metadata are also saved as a .csv file.

<img src="https://github.com/AustinLowey/SpotifyFestivalPlaylistGenerator/assets/49540411/acc0df46-1cf5-42b4-ba8d-18a30fa9d7d2" width="600">

A dashboard is also created in HTML/CSS, providing multiple capabilities:
1) Automated trend analysis on playlist song features (Tempo, Danceability, Energy and Speechiness) to identify the strongest trends present in the playlist data. This is especially useful if your playlist already fits specific qualities and you want to prune outliers to further strengthen those qualities.
2) Interactive feature plots for all 4 song features (all plotted vs. Song Popularity), where you can hover over any data point to see to which song and artist it belongs, as well as hide artists using the plot's interactive legend. Useful for finding outliers and further exploring playlist trends.
3) Summary information on the playlist and artists, including top playlist genres, similar artist recommendations, total runtime, number of songs, etc.

<img src="https://github.com/AustinLowey/SpotifyFestivalPlaylistGenerator/assets/49540411/99fdbe91-f41c-419d-bc23-07df5c8d8ef8" width="600">

Interactive hover functionality of Feature Plots:

<img src="https://github.com/AustinLowey/SpotifyFestivalPlaylistGenerator/assets/49540411/0c20b474-e08e-4e8c-89d1-249699b6efe3" width="600">

That's the end of the demo! Here's another playlist I made in Sep. 2023 for every artist that was in the Electric Zoo 2023 lineup. 818 songs and over 49 hours. Definitely wouldn't have made that manually!

<img src="https://github.com/AustinLowey/SpotifyFestivalPlaylistGenerator/assets/49540411/6f81ed91-e85b-4280-bb85-08b60b1aa292" width="600">
