# mediaproxy: mediaproxy component of litecord
# Copyright 2018-2019, Luna Mendes and the mediaproxy contributors
# SPDX-License-Identifier: AGPL-3.0-only

import urllib.parse
from typing import Optional, Dict, Any

from quart import current_app as app
from logbook import Logger

from mediaproxy.cache import url_tuple
from mediaproxy.bp.proxy import get_meta

log = Logger(__name__)


async def embed_image(image_url_unparsed: str) -> Optional[Dict[str, Any]]:
    """Generate a Discord Embed image object out of a url."""
    image_url = urllib.parse.urlparse(image_url_unparsed)
    query_append = f"?{image_url.query}" if image_url.query else ""
    img_raw_url = f"{image_url.netloc}{image_url.path}{query_append}"

    img_url, img_id = url_tuple(image_url.scheme, img_raw_url)

    log.debug("querying image {} {}", img_url, img_id)
    meta = await get_meta(img_url, img_id)

    # construct a proxy url based off app.cfg['mediaproxy']['domain']
    md_domain = app.cfg["mediaproxy"]["domain"]
    sec = "s" if app.cfg["mediaproxy"]["tls"] else ""

    img_proxy_url = f"http{sec}://{md_domain}/img/" f"{image_url.scheme}/{img_raw_url}"

    if meta["image"]:
        return {
            "height": meta["height"],
            "width": meta["width"],
            "proxy_url": img_proxy_url,
            "url": img_url,
        }

    return None
