# mediaproxy: mediaproxy component of litecord
# Copyright 2018-2019, Luna Mendes and the mediaproxy contributors
# SPDX-License-Identifier: AGPL-3.0-only

import pytest

from mediaproxy.insertr.embedders.meta import from_html


@pytest.mark.asyncio
async def test_empty():
    """Test empty string against meta parser"""
    assert not await from_html("")


@pytest.mark.asyncio
async def test_title():
    """test embed.title"""
    embed = await from_html(
        """
    <html>
    <head>
        <title>pee</title>
    </head>
    <body>
        blah.
    </body>
    </html>
    """
    )

    assert embed["title"] == "pee"


@pytest.mark.asyncio
async def test_description():
    """test embed.description"""
    embed = await from_html(
        """
    <html>
    <head>
        <title>pee</title>
        <meta name="description" content="test">
    </head>
    <body>
        blah.
    </body>
    </html>
    """
    )

    assert embed["title"] == "pee"
    assert embed["description"] == "test"
