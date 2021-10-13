# mediaproxy: mediaproxy component of litecord
# Copyright 2018-2019, Luna Mendes and the mediaproxy contributors
# SPDX-License-Identifier: AGPL-3.0-only

from bs4 import BeautifulSoup
from logbook import Logger

from mediaproxy.utils import embed_image
from mediaproxy.outgoing import fetch

log = Logger(__name__)


async def inject_opengraph_image(embed, meta_content: str):
    """Inject embed.thumbnail based on an og:image meta tag"""
    image = await embed_image(meta_content)

    if image:
        embed["thumbnail"] = image


async def from_html(html: str) -> dict:
    """Generate an embed out of raw HTML information."""
    # NOTE: the lxml html parser is much better than python's.
    # i was having trouble understanding its meta tags on python.
    soup = BeautifulSoup(html, "lxml")

    embed = {"type": "url"}
    head = soup.head

    if not head:
        return {}
        
    for child in head.children:
        # skip non-<meta>
        if child.name != "meta":
            continue
        
        meta_content = child.get('content')
        meta_prop = child.get('property')
        meta_name = child.get('name')
        
        if "og:title" in (meta_prop, meta_name):
            embed["title"] = meta_content
        elif "title" in (meta_prop, meta_name):
            embed["title"] = meta_content
            
        if "og:description" in (meta_prop, meta_name):
            embed["description"] = meta_content
        elif "description" in (meta_prop, meta_name):
            embed["description"] = meta_content
            
        if "theme-color" in (meta_prop, meta_name):
            embed["color"] = int(meta_content.replace("#", ""), 16)
        
        # change type if present
        if "og:type" in (meta_prop, meta_name):
            if meta_content == "article" or meta_content == "object" or meta_content == "website":
                embed["type"] = "article"

        if meta_prop == "og:image":
            await inject_opengraph_image(embed, meta_content)

    return embed


async def gen_embed(url: str) -> dict:
    """Generate an embed based on OpenGraph data. Requests the HTML off
    the page and feeds to the from_html function."""
    if "instagram.com" in url:
        return
    
    text = await fetch(url)
    embed = await from_html(text)

    if embed:
        # inject embed.url
        embed["url"] = url

    return embed
