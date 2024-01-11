## Concept

<img src="https://github.com/AustinLowey/SpotifyFestivalPlaylistGenerator/assets/49540411/f8155adc-c98e-47e9-90dd-6dfd8b770bd9" width="700">

---

## Top-Level Overview

#### _Demo Video:_

<a href="https://youtu.be/xa2-pl23kBE" target="_blank">
  <img src="https://github.com/AustinLowey/SpotifyFestivalPlaylistGenerator/assets/49540411/e9c5905b-9d67-4118-a7e8-38f6da1d098c" width="500">
</a>

#### _Key Features:_

- Generates a Spotify playlist by curating top tracks from either a user-inputted music festival's artist lineup and/or manually entered artists' names.
- Can create a playlist with dozens of hours of songs in 1-2 minutes.
- Scrapes and extracts a specific music festival's lineup using Beautiful Soup.
- Guides users through the process with a set of PyQt GUI screens, facilitating artist selection from the imported festival lineup.
- Leverages Spotipy to retrieve top tracks for each artist and create a playlist in Spotify.
- Delivers automated track feature analytics using track metadata and by providing the user with an HTML/CSS playlist summary dashboard.

#### _Main User Interface:_

<img src="https://github.com/AustinLowey/SpotifyFestivalPlaylistGenerator/assets/49540411/b840de90-a4f6-4662-8a11-ff38cf617a18">

---

## Main Python Libraries Used
- pandas
- Spotipy (Python library for the Spotify Web API)
- PyQt5
- Beautiful Soup
- Plotly

Note: To use the Spotipy API, you need to setup an API client key and secret key (https://developer.spotify.com/documentation/web-api). In this application, 3 environment variables were setup: SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, and SPOTIFY_USER. The first and second are used for retrieving artist top tracks and track metadata. The third, SPOTIFY_USER, links to a Spotify account.

---

## Walkthrough

Running run_playlist_generator.py launches the below GUI, which asks the user if they'd like to create a playlist for a specific music festival or create a playlist by manually entering artist names.

<img src="https://github.com/AustinLowey/SpotifyFestivalPlaylistGenerator/assets/49540411/704ef100-d016-45a6-9c3c-b2219be24e39" width="400">

If the user picks the "From Music Festival" option, they are taken to the below screen, where they are asked to get a songkick.com link for a specific music festival. The second option, "Enter Artist Names," offers an alternative approach by bringing the user to a screen where they can type-in multiple artists' names that will be used to make a playlist.

<img src="https://github.com/AustinLowey/SpotifyFestivalPlaylistGenerator/assets/49540411/33706e43-b682-4e2d-aeb4-1bf33bf791da" width="500">

The artist lineup is obtained using the user-provided link. Each artist in the lineup is then searched for in Spotify and the artists' popularities and genres (if there are any published), are shown in the below GUI. The user can scroll through the GUI and select which artists they want to include. They can also manually enter other artists to add.

<img src="https://github.com/AustinLowey/SpotifyFestivalPlaylistGenerator/assets/49540411/638d885b-2b70-4b72-9e4d-fa08bd620a38" width="700">

The next GUI screen shows some info about the to-be-created playlist, as well as allows the user to customize the playlist using the following inputs:
1) Playlist name.
2) Number of songs from each artist.
3) If the user wants less songs for less popular artists. If this option is selected, the amount of songs per artist scales with that artist's popularity. For example, if the user selects 8 songs per artist in step 1 and the highest and lowest artist popularities are 80 and 15, respectively, then the created playlist will have 8 songs for the more popular artist and 3 songs for the less popular artist. Other artists in the middle of that range will have a varying number of songs, linearly scaling with popularity.
4) If the user wants to include multiple versions (i.e., remixes or edits) of the same song. If "no" is selected for this option, only the song with the highest popularity will be retained. Exact duplicates are already automatically removed, regardless of what is selected for this step.

<img src="https://github.com/AustinLowey/SpotifyFestivalPlaylistGenerator/assets/49540411/3ff69b2f-f24a-4376-bf16-ab4b8b259a07" width="500">

Finally, the playlist is created. For each artist, the top tracks per artist and their metadata, including track popularities and track features like tempo and danceability, are pulled using the Spotipy API. This playlist included the top (up to) 10 songs from 53 different artists, for a total of 342 songs (not 530 songs, as multiple remixes and repeats were removed and less songs were included for less popular artists), with a runtime of 19 hours and 11 minutes.

<img src="https://github.com/AustinLowey/SpotifyFestivalPlaylistGenerator/assets/49540411/4e085e58-5f7d-40a8-a224-306b1241361f" width="700">

The artist and song metadata are also saved as a .csv file.

<img src="https://github.com/AustinLowey/SpotifyFestivalPlaylistGenerator/assets/49540411/d44c566d-3d56-4d0d-907f-877543f682c1" width="700">

A dashboard is also created in HTML/CSS, providing multiple capabilities:
1) Automated trend analysis on playlist song features (Tempo, Danceability, Energy and Speechiness) to identify the strongest trends present in the playlist data. This is especially useful if your playlist already fits specific qualities and you want to prune outliers to further strengthen those qualities.
2) Interactive feature plots for all 4 song features (all plotted vs. Song Popularity), where you can hover over any data point to see to which song and artist it belongs, as well as hide artists using the plot's interactive legend. Useful for finding outliers and further exploring playlist trends.
3) Summary information on the playlist and artists, including top playlist genres, similar artist recommendations, total runtime, number of songs, etc.

<img src="https://github.com/AustinLowey/SpotifyFestivalPlaylistGenerator/assets/49540411/e9e71e88-8f1d-4502-8eb3-5e93f4bc24a3" width="700">

Interactive hover and artist isolation functionalities of Feature Plots:

<img src="https://github.com/AustinLowey/SpotifyFestivalPlaylistGenerator/assets/49540411/e4ffc2da-2f8e-4a0f-ac51-e9924f969dc8" width="500">
