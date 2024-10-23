## <img src="https://github.com/AustinLowey/SpotifyFestivalPlaylistGenerator/assets/49540411/c033cd7c-81f4-4056-8b32-8ae0da13d583" width="25"> Festival Playlist Generator

<img src="https://github.com/AustinLowey/SpotifyFestivalPlaylistGenerator/assets/49540411/6583aec8-39af-4314-97d7-2a84f4c25e21" width="700">

One of the main features of this application: Simply enter a specific music festival, click which artists you want from the lineup, and a playlist will automatically be generated for you.

## <img src="https://github.com/AustinLowey/SpotifyFestivalPlaylistGenerator/assets/49540411/f97c5ed9-acf1-4d53-8520-6052b52d954c" width="25"> Top-Level Overview

#### _Demo Video:_

<a href="https://youtu.be/xa2-pl23kBE" target="_blank">
  <img src="https://github.com/AustinLowey/SpotifyFestivalPlaylistGenerator/assets/49540411/e9c5905b-9d67-4118-a7e8-38f6da1d098c" width="500">
</a>

#### _Key Features:_

- Generates a Spotify playlist by curating top tracks from the lineup of a user-inputted music festival and/or manually-entered artists' names.
- Can create a playlist with dozens of hours of songs in <1 minute.
- Scrapes and extracts a specific music festival's lineup using Beautiful Soup.
- Guides users through the process with a set of PyQt GUI screens, facilitating artist selection from the imported festival lineup.
- Leverages Spotipy to retrieve top tracks for each artist and create a playlist in Spotify.
- Delivers automated track feature analytics using track metadata and by providing the user with an HTML/CSS playlist summary dashboard.

#### _Main User Interface and Process Flow:_

<img src="https://github.com/AustinLowey/SpotifyFestivalPlaylistGenerator/assets/49540411/b840de90-a4f6-4662-8a11-ff38cf617a18">

---

## <img src="https://github.com/AustinLowey/SpotifyFestivalPlaylistGenerator/assets/49540411/852378b0-d0e5-42a7-a74f-723d2e6fb9d5" width="25"> Getting Started

### _Setup Instructions:_

- Clone the GitHub repository.
- Set up Spotipy Web API client and secret keys (https://developer.spotify.com/documentation/web-api).
- Find your Spotify account's username ID by opening Spotify and navigating to Account -> Edit Profile.
- Set up these 3 IDs as system environment variables with names: SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, and SPOTIFY_USER.
- Note: Using Python 3.8; requirements.txt contains all package/library versions.

### _Main Python Libraries Used:_
- pandas
- Spotipy (Python library for the Spotify Web API)
- PyQt5
- Beautiful Soup
- Plotly

---

## <img src="https://github.com/AustinLowey/SpotifyFestivalPlaylistGenerator/assets/49540411/3d889ec1-e4cd-4c72-94fe-8dd003ade51a" width="25"> Usage

Executing run_playlist_generator.py launches the below GUI, which asks the user if they'd like to create a playlist for a specific music festival or create a playlist by manually entering artists' names.

<img src="https://github.com/AustinLowey/SpotifyFestivalPlaylistGenerator/assets/49540411/e954335b-92be-462a-b6d1-efe30b947c3a" width="400"><br>

Choosing the "From Music Festival" option takes users to the screen below, where they are asked to get a songkick.com link for a specific music festival. The second option, "Enter Artists' Names," offers an alternative approach by bringing the user to a screen where they can type-in multiple artists' names that will be used to make a playlist.

<img src="https://github.com/AustinLowey/SpotifyFestivalPlaylistGenerator/assets/49540411/33706e43-b682-4e2d-aeb4-1bf33bf791da" width="500"><br>

The artist lineup is obtained using the user-provided link. Each artist in the lineup is then searched for in Spotify and the artists' popularities and genres (if there are any published), are shown in the below GUI. The user can scroll through the GUI and select which artists they want to include. They can also manually enter other artists to add.

<img src="https://github.com/AustinLowey/SpotifyFestivalPlaylistGenerator/assets/49540411/638d885b-2b70-4b72-9e4d-fa08bd620a38" width="700"><br>

The next GUI screen shows some info about the to-be-created playlist, as well as allows the user to customize the playlist using the following inputs:
1) Playlist name.
2) Number of songs from each artist.
3) If the user wants less songs for less popular artists. If this option is selected, the amount of songs per artist scales with that artist's popularity. For example, if the user selects 8 songs per artist in step 1 and the highest and lowest artist popularities are 80 and 15, respectively, then the created playlist will have 8 songs for the more popular artist and 3 songs for the less popular artist. Other artists in the middle of that range will have a varying number of songs, linearly scaling with popularity.
4) If the user wants to include multiple versions (i.e., remixes or edits) of the same song. If "no" is selected for this option, only the song with the highest popularity will be retained. Exact duplicates are already automatically removed, regardless of what is selected for this step.

<img src="https://github.com/AustinLowey/SpotifyFestivalPlaylistGenerator/assets/49540411/3ff69b2f-f24a-4376-bf16-ab4b8b259a07" width="500"><br>

Finally, the playlist is created. For each artist, the top tracks per artist and their metadata, including track popularities and track features like tempo and danceability, are pulled using the Spotipy API. This playlist included the top (up to) 10 songs from 53 different artists, for a total of 342 songs (not 530 songs, as multiple remixes and repeats were removed and less songs were included for less popular artists), with a runtime of 19 hours and 11 minutes.

<img src="https://github.com/AustinLowey/SpotifyFestivalPlaylistGenerator/assets/49540411/4e085e58-5f7d-40a8-a224-306b1241361f" width="600"><br>

The artist and song metadata are also saved as a .csv file.

<img src="https://github.com/AustinLowey/SpotifyFestivalPlaylistGenerator/assets/49540411/d44c566d-3d56-4d0d-907f-877543f682c1" width="600"><br>

A dashboard is also created in HTML/CSS, providing multiple capabilities:
1) Automated trend analysis on playlist song features (Tempo, Danceability, Energy and Speechiness) to identify the strongest trends present in the playlist data. This is especially useful if your playlist already has specific qualities and you want to prune outliers to further strengthen those qualities.
2) Interactive feature plots for all 4 song features (all plotted vs. Song Popularity), where you can hover over any data point to see to which song and artist it belongs, as well as hide artists using the plot's interactive legend. Useful for finding outliers and further exploring playlist trends.
3) Summary information on the playlist and artists, including top playlist genres, similar artist recommendations, total runtime, number of songs, etc.

<img src="https://github.com/AustinLowey/SpotifyFestivalPlaylistGenerator/assets/49540411/b5281198-e7ef-4164-bc78-dbb89f0a4d34" width="700"><br>

Interactive hover and artist isolation functionalities of Feature Plots:

<img src="https://github.com/AustinLowey/SpotifyFestivalPlaylistGenerator/assets/49540411/e4ffc2da-2f8e-4a0f-ac51-e9924f969dc8" width="500">

---

## <img src="https://github.com/AustinLowey/SpotifyFestivalPlaylistGenerator/assets/49540411/a6e5d2f2-7dcb-4f38-bf78-fe27cd0c2957" width="25"> Roadmap

### _Planned Features:_
- [Advanced playlist sorting options](https://github.com/AustinLowey/SpotifyFestivalPlaylistGenerator/issues/14)
- [Playlist summary dashboard and automated metadata analysis for existing playlists](https://github.com/AustinLowey/SpotifyFestivalPlaylistGenerator/issues/15)
- [Add loading screens, bars, and/or messages](https://github.com/AustinLowey/SpotifyFestivalPlaylistGenerator/issues/16)
- [Genre-filter buttons on Artist Selection screen](https://github.com/AustinLowey/SpotifyFestivalPlaylistGenerator/issues/17)
- [Song metadata retrieval during Playlist Customization screen to reduce user wait time](https://github.com/AustinLowey/SpotifyFestivalPlaylistGenerator/issues/18)
- ["Add to playlist" button for each recommended artist on Playlist Customization screen](https://github.com/AustinLowey/SpotifyFestivalPlaylistGenerator/issues/19)
- [Re-implement "offline_main()" function in run_playlist_generator.py](https://github.com/AustinLowey/SpotifyFestivalPlaylistGenerator/issues/21)
- [Auto-pruning capabilities to remove songs above/below certain feature thresholds](https://github.com/AustinLowey/SpotifyFestivalPlaylistGenerator/issues/22)
- [Update artist logos to have a straight line on the right side](https://github.com/AustinLowey/SpotifyFestivalPlaylistGenerator/issues/28)
- [Dashboard feature plots - Cap feature_range lower and upper bounds if all data within range](https://github.com/AustinLowey/SpotifyFestivalPlaylistGenerator/issues/31)
- [Spotify jams, mobile capability, and/or browser-usage](https://github.com/AustinLowey/SpotifyFestivalPlaylistGenerator/issues/25)

### _Open Issues:_
- [Improve artist search query](https://github.com/AustinLowey/SpotifyFestivalPlaylistGenerator/issues/26)
- [Improve artist logo scaling on Artist Selection screen](https://github.com/AustinLowey/SpotifyFestivalPlaylistGenerator/issues/27)
- [Improve Festival Link screen (general interface)](https://github.com/AustinLowey/SpotifyFestivalPlaylistGenerator/issues/29)
- [Error handling if no artist selected or entered on Artist Selection screen](https://github.com/AustinLowey/SpotifyFestivalPlaylistGenerator/issues/30)
- [Negative runtime in Playlist Customization screen (update regression model)](https://github.com/AustinLowey/SpotifyFestivalPlaylistGenerator/issues/32)
- [Bad festival link (additional) error handling](https://github.com/AustinLowey/SpotifyFestivalPlaylistGenerator/issues/33)
- [Single artist selection/entry leads to a crash](https://github.com/AustinLowey/SpotifyFestivalPlaylistGenerator/issues/34)

### _Other Changes:_
- [Reorganize PyQt styles into an init_widget_styles() method](https://github.com/AustinLowey/SpotifyFestivalPlaylistGenerator/issues/36)
- [Record new demo video for documentation with most recent (minor) GUI updates](https://github.com/AustinLowey/SpotifyFestivalPlaylistGenerator/issues/23)
- [Add unit testing](https://github.com/AustinLowey/SpotifyFestivalPlaylistGenerator/issues/20)
- [(Maybe) Rename all column names in all DataFrames to remove spaces](https://github.com/AustinLowey/SpotifyFestivalPlaylistGenerator/issues/37)
- [Add .gitignore and .gitattributes](https://github.com/AustinLowey/SpotifyFestivalPlaylistGenerator/issues/24)

---

## Sample Playlists by Music Genre/Festival Type

### Rock
- [Sea.Hear.Now 2024 (Rock, Alternative, Indie, Pop) - 169 songs, 10 hr 36 min](https://open.spotify.com/playlist/2r6J67ohr4xzgHRvmpwAY3?si=a57f2431c46b4da9)
- [Austin City Limits 2023 (Rock artists only) - 130 songs, 8hr 16min](https://open.spotify.com/playlist/4ZmRXoFPo7Vg8wn9SkRW4P?si=c219d4e3c6c14613)

### Electronic
- [Electric Zoo 2023 - 818 songs, 49 hr 7 min](https://open.spotify.com/playlist/6HfL8jbc4Fg8UVda0mD61U?si=8c37fa86729c4450)
- [Electric Daisy Carnival 2023 (House artists only) - 342 songs, 19 hr 11 min](https://open.spotify.com/playlist/3G5t70d2U5XX2NahtPjh81?si=62244a4cace1441a)

### Pop
- [Coachella 2024 (Pop artists only) - 183 songs, 10 hr 31 min](https://open.spotify.com/playlist/1z6imiEKV9Y2SSFCeXoIrJ?si=cdfb0f8274dd4c67)

### Folk
- [Newport Folk Festival - 106 songs, 6 hr 32 min](https://open.spotify.com/playlist/2vrWh0r0OApjiyJZpVdsPu?si=87d201370cf34fb3)

### Country
- [CMA Music Festival - 245 songs, 13 hr 47 min](https://open.spotify.com/playlist/1sQvtjGKAj5yvsDB5yKNF7?si=c748b93424e5464a)

### Rap / Hip-Hop
- [Rolling Loud 2024 - 237 songs, 11 hr 35 min](https://open.spotify.com/playlist/6XRzy10I1b9HSZ8IhW9hWk?si=445437c49d6c42fb)

### Jazz
- [Newport Jazz Festival - 178 songs, 13 hr 23 min](https://open.spotify.com/playlist/44ZHAa6fVzLSWitf6mc6Cd?si=88846fd5814a4695)

