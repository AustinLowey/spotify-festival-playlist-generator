from typing import Tuple, List

import requests
from bs4 import BeautifulSoup


def get_artist_names(songkick_url: str) -> Tuple[str, List[str]]:
    """
    Retrieves a list of artists performing in a specific music festival.

    Parameters:
        songkick_url (str): The URL of the music festival page on Songkick.com.

    Returns:
        str: Festival name, extracted from the URL.
        List[str]: Sorted list of artist names in festival lineup, extracted
            from the user-provided festival web page.
    """

    # Get web page and its html contents using bs4
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) '
        'Gecko/20100101 Firefox/52.0'
    }
    req = requests.get(songkick_url, headers)
    soup = BeautifulSoup(req.content, 'html.parser')

    # Extract artist names from html
    html_ul_tag = soup.find("ul", class_="festival") # Tag with all artists
    artist_names = [
        html_a_tag.contents[0] for html_a_tag in html_ul_tag.find_all("a")
    ] # List of every artist in the web page's lineup

    # html_a_tag sample: <a href="/artists/29315-foo-fighters">Foo Fighters</a>

    # Extract and format festival name from URL
    try:
        festival_name = (songkick_url
        .split("id/")[1].split("-", 1)[1]
        .replace("-", " ").title()
        )
    except IndexError:
        festival_name = "your music festival"
        
    return festival_name, sorted(artist_names)


def test_get_artist_names(test_url=None):
    """
    Tests the get_artist_names function by fetching artist names and festival
    name from the specified or default test URL(s) and printing the results.

    Parameters:
        test_url (str, optional): URL of the festival to test. Default is None.
            If None, sample/test URLs for ACL and EDC festivals are used.

    Returns:
        None
    """
    
    if test_url: # If test URL provided
        festival_name, artist_names = get_artist_names(test_url)
        print(f"Festival name is: {festival_name}\n")
        print(f"List of artist names in lineup is:\n{artist_names}")
    else:
        # Sample/test URLs if one isn't entered
        acl_url = (
            "https://www.songkick.com/festivals/129-austin-city-limits-music"
            "/id/41123551-austin-city-limits-music-festival-2023"
        )
        edc_url = (
            "https://www.songkick.com/festivals/562824-edc-orlando"
            "/id/40754508-edc-orlando-2023"
        )

        # Test the get_artist_names function with Austin City Limits 2023 URL
        festival_name_acl, artist_names_acl = get_artist_names(acl_url)
        print(f"Festival name is: {festival_name_acl}\n")
        print(f"List of artist names in lineup is:\n{artist_names_acl}\n")
        print("--------------------------------\n")

        # Test the get_artist_names function with EDC Orlando 2023 URL
        festival_name_edc, artist_names_edc = get_artist_names(edc_url)
        print(f"Festival name is: {festival_name_edc}\n")
        print(f"List of artist names in lineup is:\n{artist_names_edc}\n")


if __name__ == "__main__":
    test_get_artist_names()


"""
Austin City Limits 2023 Lineup (from songkick.com, for quick reference):
['Alanis Morissette', 'Ali Sethi', 'Angel White', 'Arya (Serbia)', 'BLOND:ISH','Ben Kweller',
'Breland', 'CVC', 'Calder Allen', 'Celisse', 'Charlotte Adigéry & Bolis Pupul',
'Cigarettes After Sex', 'Declan McKenna', 'Delacey', 'Eloise', 'Foo Fighters', 'Hozier',
'Katy Kirby', 'M83', 'Madison Cunningham', 'Maggie Rogers', 'Major Lazer', 'Morgan Wade',
'Mumford & Sons', 'Nemegata', 'Nessa Barrett', 'Noah Kahan', 'ODESZA', 'Oliver Hazard',
'SIDEPIECE', 'Shania Twain', 'Suki Waterhouse', 'Sunrose', 'The 1975', 'The Breeders',
'The Lumineers', 'The Mars Volta', 'The Teskey Brothers', 'The Walkmen', 'Tove Lo',
'Yeah Yeah Yeahs', 'corook', 'half•alive']

EDC Orlando 2023 Lineup (from songkick.com, for quick reference):
['2AR', 'ATLiens', 'AVELLO', 'Afrojack', 'Alan Walker', 'Alesso', 'Alison Wonderland',
'Alok', 'Anabel Englund', 'Anfisa Letyago', 'Armin van Buuren', 'Armnhmr', 'Azzecca',
'BAGGI', 'BARELY ALIVE', 'BEN STERLING', 'BENDA', 'BLOND:ISH', 'BONNIE X CLYDE',
'Baby Weight', 'Bassrush', 'Ben Nicky', 'Billy Gillies', 'Black Carl!', 'Blastoyz', 'CID',
'Carlita', 'Carola', 'Celo', 'Chelina Manuhutu', 'Chris Stussy', 'Crankdat', 'DJ Icey',
'Deadmau5', 'Deathpact', 'Dennis Cruz', 'Deorro', 'Dillon Francis', 'Dirt Monkey',
'Disco Lines', 'Discovery Project', 'Dom Dolla', 'Dombresky', 'Dreamstate',
'Eats Everything', 'Edgar V.', 'Eli Brown', 'Excision', 'Factory 93', 'Fisher',
'Franky Rizardo', 'Franky Wah', 'Gem & Tauri', 'Gorgon City', 'GorillaT', 'Gryffin', 'HUGEL',
'Hairitage', 'HoneyLuv', 'Insomniac Records', 'James Hype', 'Jamie Jones', 'Jantsen', 'Jorza',
'Joshwa', 'Joyryde', 'KAYZO', 'KREAM', 'Kaskade', 'Korolova', 'LEVEL UP', 'LF SYSTEM',
'Liquid Stranger', 'Loco Dice', 'Loud Luxury', 'Luccio', 'MC Dino', 'MEDUZA', 'Maddix',
'Majestic', 'Malaa', 'Malone', 'Marco Carola', 'Marlo', 'Matt Sassari', 'Mau P',
'Miguelle & Tons', 'Miss Monique', 'Modapit', 'Nia Archives', 'Nitepunk', 'Noizu',
'Paco Osuna', 'Paul van Dyk', 'Pretty Pink', 'Robbie Rivera', 'SLUGG', 'San Holo',
'San Pacho', 'Sara Benyo', 'Seven Lions', 'Ship Wrek', 'Steve Aoki', 'SubDocta', 'Subtronics',
'The Chainsmokers', 'Thunderpony', 'Tini Gessler', 'Todd Terry', 'Valentino Khan',
'Virtual Riot', 'WYLLO', 'Wax Motif', 'Westend', 'Wilkinson', 'Yotto', 'Zedd']
"""
