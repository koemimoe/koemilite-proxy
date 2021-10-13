# mediaproxy: mediaproxy component of litecord
# Copyright 2018-2019, Luna Mendes and the mediaproxy contributors
# SPDX-License-Identifier: AGPL-3.0-only

from quart import Blueprint, send_file, current_app as app
from logbook import Logger

from mediaproxy.cache import url_tuple
from mediaproxy.insertr.processor import process_url

bp = Blueprint("insertr", __name__)
log = Logger(__name__)


async def cache_or_process(url, url_id):
    """Request a discord embed's JSON from cache, or generate it."""
    try:
        log.debug("searching cache for {}", url_id)
        return next(app.cache_dir.glob(f"{url_id}.json"))
    except StopIteration:
        log.debug("cache failed, processing for {!r}", url)
        return await process_url(url, url_id)


@bp.route("/embed/<scheme>/<path:input_url>")
async def _embed(scheme: str, input_url: str):
    url, url_id = url_tuple(scheme, input_url)

    # we prepend "embed-" to the url id so that we only work on
    # embeds and .json files, etc.
    url_id = f"embed-{url_id}"

    # first, we need to check if anything's on cache_dir

    # NOTE: this is relatively inefficient since process_url will
    # write to the cache, then send_file will have to read it again.
    path = await cache_or_process(url, url_id)

    return await send_file(str(path))
