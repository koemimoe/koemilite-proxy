# mediaproxy: mediaproxy component of litecord
# Copyright 2018-2019, Luna Mendes and the mediaproxy contributors
# SPDX-License-Identifier: AGPL-3.0-only

import re
import json
from typing import Union, List, Dict

from quart import current_app as app
from logbook import Logger

from mediaproxy.insertr.embedders import (
    xkcd_embed,
    opengraph_embed,
    meta_embed,
    activitypub_embed,
    twitter_embed,
    spotify_embed,
)

log = Logger(__name__)

# embedder mapping for mediaproxy.
# this maps regexes for the url into embedders that match.
# the empty string is served as a fallback for all urls.
EMBEDDERS = {
    re.compile(r"xkcd.com\/\d+"): xkcd_embed,
    re.compile(r"https?:\/\/twitter.com\/[0-9a-zA-Z_]{1,20}\/status\/([0-9]*)"): twitter_embed,
    re.compile(r"^(?:spotify:|https:\/\/[a-z]+\.spotify\.com\/(track\/|playlist\/|album\/))(.*)$"): spotify_embed,
    re.compile(
        r"https?:\/\/([^:\/\s]+)\/(notes|objects|notice)\/([a-zA-Z0-9-_/]*)"
    ): activitypub_embed,
    re.compile(
        r"https?:\/\/([^:\/\s]+)\/users\/([a-zA-Z0-9-_/]*)\/statuses\/([0-9]{17,21})"
    ): activitypub_embed,
    re.compile(
        r"https?:\/\/([^:\/\s]+)\/@([a-zA-Z0-9-_/]*)\/([a-zA-Z0-9-_/]*)"
    ): activitypub_embed,
    "": [opengraph_embed, meta_embed],
}


async def _multi_embedders(embedders: list, url: str):
    """Call the given list of embedders and return a result for the first
    one that works."""
    if not isinstance(embedders, list):
        return await embedders(url)

    # iterate over all embedders and return the
    # first one that has a good embed
    for embedder in embedders:
        log.debug("processing {!r} with {!r}", url, embedder)
        embed = await embedder(url)

        if not embed:
            continue

        keys = embed.keys()

        # invalid when the embed only has a single key,
        # and that key is the type key.
        invalid = len(keys) == 1 and "type" in keys

        if embed and not invalid:
            return embed

    return None


async def _process_url(url):
    for regex, embedders in EMBEDDERS.items():
        # if regex is empty, then we are on a fallback for
        # any kind of url.
        if not regex:
            log.debug("using fallback embedders")
            return await _multi_embedders(embedders, url)

        # if it is a regex, check if it matches (anywhere in the string,
        # with re.search)
        if regex.search(url):
            log.debug("matched on embedder regex {!r}", regex)
            return await embedders(url)


async def process_url(url: str, url_id: str):
    """Process the given url's embed and store it in the given urlid as a
    JSON file."""

    embeds: Union[List, Dict] = await _process_url(url)
    if isinstance(embeds, dict):
        embeds = [embeds]

    embed_path = app.cache_dir / f"{url_id}.json"

    # null is sentinel value to signal no embeds were made
    embed_path.write_text(json.dumps(embeds or None))

    return embed_path
