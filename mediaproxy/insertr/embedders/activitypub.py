# mediaproxy: mediaproxy component of litecord
# Copyright 2018-2019, Luna Mendes and the mediaproxy contributors
# SPDX-License-Identifier: AGPL-3.0-only

# This embedder is based off earlier work by Cynthia Foxwell
#  https://gitlab.com/Cynosphere/HiddenPhox/blob/master/events/twimg.js

import re

from logbook import Logger

from mediaproxy.utils import embed_image
from mediaproxy.outgoing import fetch

log = Logger(__name__)

MIME = "application/activity+json"
AS_HEADERS = {"Accept": MIME}

PLUSER_REGEX = r"https?:\/\/([^:\/\s]+)\/users\/([a-zA-Z0-9-_/]*)"


def _cleanup(data: str) -> str:
    assert data is not None
    # some day we may want to put an http parser, but for now, this will work
    data = data.replace("<br>", "\n")
    data = data.replace("<br/>", "\n")
    data = data.replace("<br />", "\n")
    data = re.sub(r"<(?:.|\n)*?>", "", data)
    return data


def _post_content(post: dict) -> str:
    if post["sensitive"] and post.get("summary") is not None:
        return f"Content Warning: {_cleanup(post['summary'])}"

    misskey_content = post.get("_misskey_content")
    if misskey_content:
        return misskey_content

    return _cleanup(post["content"])


async def gen_embed(url: str):
    """Generate an embed out of a Pleroma url."""
    post = await fetch(url, json=True, headers=AS_HEADERS, mime=MIME)
    print(post)

    author_data = await fetch(
        post["attributedTo"], json=True, headers=AS_HEADERS, mime=MIME
    )
    print("author", author_data)

    post_object = post.get("object")
    object_url = post.get("id") or post_object.get("url")
    if object_url:
        log.info("got post.object! {}", object_url)
        post = await fetch(object_url, json=True, headers=AS_HEADERS, mime=MIME)

    match = re.match(PLUSER_REGEX, post["attributedTo"])
    assert match is not None

    attachments = post.get("attachment")

    embed = {
        "type": "rich",
        "author": {"name": author_data["name"], "url": author_data["url"]},
        "title": f'(@{author_data["preferredUsername"]}@{match.group(1)})',
        "url": url,
        "description": _post_content(post),
        "thumbnail": await embed_image(author_data["icon"]["url"]),
        "color": 0x282C37,
        "footer": {"text": "ActivityPub Post"},
    }

    if attachments:
        if post["sensitive"]:
            embed["description"] += "\n(Contains sensitive attachments)"
        else:
            embed["image"] = await embed_image(attachments[0]["url"])

    embeds = [embed]
    for attachment in attachments[1:]:

        # do not process extra attachments if post is sensitive
        if post["sensitive"]:
            break

        embeds.append(
            {"url": url, "type": "rich", "image": await embed_image(attachment["url"])}
        )

    return embeds
