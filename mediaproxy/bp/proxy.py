# mediaproxy: mediaproxy component of litecord
# Copyright 2018-2019, Luna Mendes and the mediaproxy contributors
# SPDX-License-Identifier: AGPL-3.0-only

import asyncio
from time import time

from quart import Blueprint, jsonify, send_file, current_app as app
from quart.ctx import copy_current_app_context

from PIL import Image
from logbook import Logger

from mediaproxy.mimes import get_mimetype
from mediaproxy.cache import path_or_request, url_tuple

bp = Blueprint("proxy", __name__)
log = Logger(__name__)


async def janitor_cleanup():
    """Delete all files that have more than 5 minutes lifetime."""
    deleted = 0

    for cached_path in app.cache_dir.glob("*.*"):
        if cached_path.parts[-1] == ".gitkeep":
            continue

        stat = cached_path.stat()
        now = time()

        # last time of modification should suffice.
        life = now - stat.st_mtime

        # if file life is below 30m, keep it living.
        if life < 1800:
            continue

        log.debug("removing {}, life >= 15m", cached_path)

        cached_path.unlink()
        deleted += 1

    return deleted


@bp.route("/img/<scheme>/<path:input_url>")
async def fetch_file(scheme: str, input_url: str):
    """Fetch a single file"""
    if scheme not in ("http", "https"):
        return "invalid scheme for url", 422
        
    url, url_hash = url_tuple(scheme, input_url)
    path = await path_or_request(url, url_hash)
    return await send_file(str(path))


async def get_meta(url, url_id) -> dict:
    """Get simple image metadata about a given URL."""
    path = await path_or_request(url, url_id)
    mime = get_mimetype(path.parts[-1].split(".")[-1])

    meta = {"image": mime.startswith("image/")}

    if meta["image"]:
        # open image with pillow, extract width and height
        image = Image.open(path)
        meta["width"], meta["height"] = image.size

    return meta


@bp.route("/meta/<scheme>/<path:input_url>")
async def _route_get_meta(scheme: str, input_url: str):
    """Fetch a single file"""
    if scheme not in ("http", "https"):
        return "invalid scheme for url", 422

    url, url_hash = url_tuple(scheme, input_url)
    meta = await get_meta(url, url_hash)
    return jsonify(meta)


def _maybe_info(deleted: int):
    # move call to info if there were more than 0 files deleted
    if deleted:
        log.info("janitor: deleted {} files", deleted)
    else:
        log.debug("janitor: deleted {} files", deleted)


@bp.before_app_request
async def proxy_janitor_start():
    """Start cache janitor."""

    @copy_current_app_context
    async def janitor_loop():
        try:
            log.debug("raw cache janitor start")
            while True:
                deleted = await janitor_cleanup()
                _maybe_info(deleted)
                await asyncio.sleep(30)
        except asyncio.CancelledError:
            pass
        except Exception:
            log.exception("error on janitor task")

    if not app.testing and not app._cache_janitor:
        app._cache_janitor = asyncio.get_event_loop().create_task(janitor_loop())
