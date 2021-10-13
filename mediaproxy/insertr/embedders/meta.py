# mediaproxy: mediaproxy component of litecord
# Copyright 2018-2019, Luna Mendes and the mediaproxy contributors
# SPDX-License-Identifier: AGPL-3.0-only

from bs4 import BeautifulSoup
from logbook import Logger

from mediaproxy.outgoing import fetch

log = Logger(__name__)


async def from_html(text: str) -> dict:
    """Generate a discord embed out of html <meta> tags."""
    soup = BeautifulSoup(text, "lxml")

    embed = {"type": "url"}
    head = soup.head

    if not head:
        return {}

    for child in head.children:
        if child.name == "title":
            embed["title"] = child.string

        if child.name != "meta":
            continue

        try:
            meta_name = child["name"]
            meta_content = child["content"]
        except KeyError:
            continue

        if meta_name == "description":
            embed["description"] = meta_content

    return embed


async def gen_embed(url: str) -> dict:
    """Make an embed out of simple meta tags."""
    if "instagram.com" in url:
        return
    text = await fetch(url)
    embed = await from_html(text)

    if embed:
        # inject embed.url
        embed["url"] = url

    return embed
