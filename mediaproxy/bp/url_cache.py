# mediaproxy: mediaproxy component of litecord
# Copyright 2018-2019, Luna Mendes and the mediaproxy contributors
# SPDX-License-Identifier: AGPL-3.0-only

import asyncio
import time

from quart import Blueprint, current_app as app
from quart.ctx import copy_current_app_context

from logbook import Logger


bp = Blueprint("url_cache", __name__)
log = Logger(__name__)


async def cache_janitor_tick(app_):
    """url cache janitor tick."""
    now = time.monotonic()

    for key in list(app_.url_cache):
        invalid_ts, _ = app_.url_cache[key]

        if invalid_ts > now:
            continue

        log.debug("removed {!r} from url cache", key)
        app_.url_cache.pop(key)


@bp.before_app_request
async def url_cache_start():
    """Start the url cache."""
    if not app.url_cache:
        app.url_cache = {}

    loop = asyncio.get_event_loop()

    @copy_current_app_context
    async def cache_janitor():
        """cache janitor loop"""
        try:
            log.info("url cache janitor start")
            while True:
                log.debug("url cache janitor tick")
                await cache_janitor_tick(app)
                await asyncio.sleep(30)
        except asyncio.CancelledError:
            log.info("url cache janitor cancel")
        except Exception:
            log.exception("url cache janitor fail")

    if not app.testing and not app._url_janitor:
        log.info("url cache start")
        app._url_janitor = loop.create_task(cache_janitor())
