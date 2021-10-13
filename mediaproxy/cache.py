# mediaproxy: mediaproxy component of litecord
# Copyright 2018-2019, Luna Mendes and the mediaproxy contributors
# SPDX-License-Identifier: AGPL-3.0-only

import urllib.parse

import mmh3

from quart import current_app as app, request

from mediaproxy.errors import InvalidResponse
from mediaproxy.mimes import check_mime, get_extension


async def _request_and_cache(url: str, url_hash: int) -> str:
    # there is too much custom response logic for this
    # that it can't be moved to mediaproxy.outgoing.
    
    async with app.session.get(url) as resp:
        if resp.status != 200:
            raise InvalidResponse("outgoing url did not respond with 200")

        # determine a file extension off Content-Type
        content_type = resp.headers["Content-Type"]

        # make sure we dont relay some shit like text/html
        check_mime(content_type)

        extension = get_extension(content_type)

        # construct filepath based off url hash
        file_path = app.cache_dir / f"{url_hash}.{extension}"

        # buffered writes to file
        with file_path.open("wb") as target:
            while True:
                chunk = await resp.content.read(4096)

                if not chunk:
                    break

                target.write(chunk)

    return file_path


async def request_and_cache(url: str, url_hash: int):
    """Request a file on a website, save it
    to the cache folder and return the resulting
    path."""

    async with app.outgoing_semaphore:
        return await _request_and_cache(url, url_hash)


async def path_or_request(url: str, url_hash: int):
    """Get the cached path for a given url or request it."""
    try:
        cached = next(app.cache_dir.glob(f"{url_hash}.*"))
        return cached
    except StopIteration:
        return await request_and_cache(url, url_hash)


def url_tuple(scheme: str, input_url: str) -> tuple:
    """Generate a url tuple, containing the full url, and the UrlID."""
    # construct the url and check its validity with urllib.parse
    # TODO: maybe ignore the ones we use (or will use),
    # such as width and height?
    args = urllib.parse.urlencode(request.args)
    constructed = f"{scheme}://{input_url}"
    parsed = urllib.parse.urlparse(constructed)

    # unparse to make sure we use proper validated data
    url = urllib.parse.urlunparse(parsed)

    # from there we can hash and give a file in cache
    url_hash = mmh3.hash128(url, signed=False)

    return url, url_hash
