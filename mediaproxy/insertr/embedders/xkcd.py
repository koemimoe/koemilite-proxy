# mediaproxy: mediaproxy component of litecord
# Copyright 2018-2019, Luna Mendes and the mediaproxy contributors
# SPDX-License-Identifier: AGPL-3.0-only

import re

from logbook import Logger

from mediaproxy.utils import embed_image
from mediaproxy.outgoing import fetch

XKCD_REGEX = re.compile(r"https?\:\/\/xkcd.com/(\d+)")
log = Logger(__name__)


async def gen_embed(url: str):
    """Generate an embed out of a XKCD url."""
    match = XKCD_REGEX.match(url)

    if not match:
        return

    xkcd_num = match.group(1)
    xkcd_url = f"https://xkcd.com/{xkcd_num}/info.0.json"

    xkcd_data = await fetch(xkcd_url, json=True)

    embed = {
        "footer": {"text": xkcd_data["alt"]},
        "title": f'xkcd: {xkcd_data["title"]}',
        "type": "rich",
        "url": url,
    }

    xkcd_img_meta = await embed_image(xkcd_data["img"])

    if xkcd_img_meta:
        embed["image"] = xkcd_img_meta

    return embed
