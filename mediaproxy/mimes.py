# mediaproxy: mediaproxy component of litecord
# Copyright 2018-2019, Luna Mendes and the mediaproxy contributors
# SPDX-License-Identifier: AGPL-3.0-only

import mimetypes
from mediaproxy.errors import MimeError

WHITELIST = [
    "image/gif",
    "image/png",
    "image/jpeg",
    "image/webp",
    "video/webm",
    "image/x-icon",
]


EXTENSIONS = {
    "image/jpeg": "jpeg",
    "image/webp": "webp",
    "image/vnd.microsoft.icon": "ico",
    "image/x-icon": "ico",
}


MIMES = {
    "jpg": "image/jpeg",
    "jpe": "image/jpeg",
    "webp": "image/webp",
    "ico": "image/x-icon",
}


def get_extension(mime: str) -> str:
    """Get an extension for a mimetype."""
    if mime in EXTENSIONS:
        return EXTENSIONS[mime]

    extensions = mimetypes.guess_all_extensions(mime)

    try:
        return extensions[0].strip(".")
    except IndexError:
        raise ValueError(f"No extension found for mime {mime!r}")


def get_mimetype(ext: str) -> str:
    """Get a mimetype for an extension."""
    if ext in MIMES:
        return MIMES[ext]

    return mimetypes.types_map[f".{ext}"]


def check_mime(mime: str):
    """Make sure we pass things that make sense."""
    if mime not in WHITELIST:
        raise MimeError("Unwhitelisted MIME type")
