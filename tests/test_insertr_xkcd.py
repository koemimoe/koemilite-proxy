# mediaproxy: mediaproxy component of litecord
# Copyright 2018-2019, Luna Mendes and the mediaproxy contributors
# SPDX-License-Identifier: AGPL-3.0-only

import pytest


@pytest.mark.asyncio
async def test_xkcd_embed(test_cli):
    """Test a XKCD url."""
    resp = await test_cli.get("/embed/https/xkcd.com/1")
    assert resp.status_code == 200

    rjson = await resp.json
    assert isinstance(rjson, list)
    assert rjson[0] == {
        "footer": {"text": "Don't we all."},
        "image": {
            "height": 311,
            "proxy_url": (
                "http://images.discordapp.io/img/https/imgs.xkcd.com"
                "/comics/barrel_cropped_(1).jpg"
            ),
            "url": "https://imgs.xkcd.com/comics/barrel_cropped_(1).jpg",
            "width": 577,
        },
        "title": "xkcd: Barrel - Part 1",
        "type": "rich",
        "url": "https://xkcd.com/1",
    }
