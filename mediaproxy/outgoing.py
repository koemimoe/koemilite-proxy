# mediaproxy: mediaproxy component of litecord
# Copyright 2018-2019, Luna Mendes and the mediaproxy contributors
# SPDX-License-Identifier: AGPL-3.0-only

import time
from json import loads as json_loads
from typing import Optional, Any, Union

from quart import current_app as app

# TODO rename to InvalidUpstreamResponse
from mediaproxy.errors import InvalidResponse

CACHE_INVALIDATE = 60


def _get_from_cache(url, *, json=False) -> Optional[Union[str, Any]]:
    now = time.monotonic()

    try:
        invalid_ts, data = app.url_cache[url]
    except KeyError:
        return None

    if now > invalid_ts:
        app.url_cache.pop(url)
        return None

    if isinstance(data, Exception):
        raise data

    return json_loads(data) if json and isinstance(data, str) else data


async def do_request(
    url: str,
    *,
    wanted_mime: str = "text/html",
    wanted_status: int = 200,
    do_json: bool = False,
    headers=None,
):
    async with app.outgoing_semaphore:
        async with app.session.get(url, headers=headers) as resp:
            ctype = resp.headers["content-type"]
            if not ctype.startswith(wanted_mime):
                raise InvalidResponse(f"outgoing url did not give {wanted_mime!r}")

            if resp.status != wanted_status:
                raise InvalidResponse(f"got {resp.status}, not {wanted_status}")

            return await resp.json() if do_json else await resp.text()


async def request_and_cache(
    url: str,
    *,
    wanted_mime: str = "text/html",
    wanted_status: int = 200,
    do_json: bool = False,
    headers=None,
) -> str:
    """Request a given URL and automatically put it in cache."""
    try:
        data = await do_request(
            url,
            wanted_mime=wanted_mime,
            wanted_status=wanted_status,
            do_json=do_json,
            headers=headers,
        )
    except InvalidResponse as exc:
        now = time.monotonic()
        app.url_cache[url] = (now + CACHE_INVALIDATE, exc)
        raise exc

    now = time.monotonic()
    app.url_cache[url] = (now + CACHE_INVALIDATE, data)
    return data


async def fetch(url: str, *, json=False, headers=None, mime=None):
    """Fetch a URL. Has caching."""
    mime = mime or ("application/json" if json else "text/html")

    data = _get_from_cache(url, json=json)
    if data is not None:
        return data

    return await request_and_cache(url, wanted_mime=mime, do_json=json, headers=headers)
