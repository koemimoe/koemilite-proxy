# mediaproxy: mediaproxy component of litecord
# Copyright 2018-2019, Luna Mendes and the mediaproxy contributors
# SPDX-License-Identifier: AGPL-3.0-only

import re

from logbook import Logger
import urllib.request
import urllib.parse
import json

from mediaproxy.utils import embed_image
from mediaproxy.outgoing import fetch

SPOTIFY_REGEX = re.compile(r"^(?:spotify:|https:\/\/[a-z]+\.spotify\.com\/(track\/|playlist\/|album\/))(.*)$")
log = Logger(__name__)


async def gen_embed(url: str):
    """Generate an embed out of a SPOTIFY url."""
    match = SPOTIFY_REGEX.match(url)

    if not match:
        return
    
    spotify_lurl = "https://accounts.spotify.com/api/token"
    sld = dict(grant_type="client_credentials")
    sdata = urllib.parse.urlencode(sld).encode("utf-8")
    sreq = urllib.request.Request(spotify_lurl, headers={"Authorization": "Basic token"}, data=sdata)
    sres = urllib.request.urlopen(sreq).read()
    spotify_login = json.loads(sres);
    
    if match.group(1) == "playlist/":
        spotify_id = match.group(2)
        spotify_url = f"https://api.spotify.com/v1/playlists/{spotify_id}"
    
        spotify_data = await fetch(spotify_url, json=True, headers={"Authorization": "Bearer "+spotify_login["access_token"]})
    
        embed = {
            "title": spotify_data["name"],
            "description": f'{spotify_data["owner"]["display_name"]} · Playlist',
            "type": "link",
            "provider": {
    			"name": "Spotify",
    			"url": "https://spotify.com/"
    		},
            "url": url,
            "thumbnail": await embed_image(spotify_data["images"][0]["url"])
        }
    elif match.group(1) == "track/":
        spotify_id = match.group(2)
        spotify_url = f"https://api.spotify.com/v1/tracks/{spotify_id}"
    
        spotify_data = await fetch(spotify_url, json=True, headers={"Authorization": "Bearer "+spotify_login["access_token"]})
    
        embed = {
            "title": spotify_data["album"]["name"],
            "description": f'{spotify_data["album"]["artists"][0]["name"]} · Song',
            "type": "link",
            "provider": {
    			"name": "Spotify",
    			"url": "https://spotify.com/"
    		},
            "url": url,
            "thumbnail": await embed_image(spotify_data["album"]["images"][0]["url"])
        }
    elif match.group(1) == "album/":
        spotify_id = match.group(2)
        spotify_url = f"https://api.spotify.com/v1/albums/{spotify_id}"
    
        spotify_data = await fetch(spotify_url, json=True, headers={"Authorization": "Bearer "+spotify_login["access_token"]})
    
        embed = {
            "title": spotify_data["name"],
            "description": f'{spotify_data["artists"][0]["name"]} · Album',
            "type": "link",
            "provider": {
    			"name": "Spotify",
    			"url": "https://spotify.com/"
    		},
            "url": url,
            "thumbnail": await embed_image(spotify_data["images"][0]["url"])
        }

    return embed
