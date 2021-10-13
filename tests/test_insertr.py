# mediaproxy: mediaproxy component of litecord
# Copyright 2018-2019, Luna Mendes and the mediaproxy contributors
# SPDX-License-Identifier: AGPL-3.0-only

import pytest


@pytest.mark.asyncio
async def test_embed(test_cli):
    """Test embedding a page."""
    resp = await test_cli.get("/embed/https/example.org")
    assert resp.status_code == 200

    rjson = await resp.json
    assert isinstance(rjson, list)
    assert rjson[0] == {
        "type": "url",
        "title": "Example Domain",
        "url": "https://example.org",
    }
