# mediaproxy: mediaproxy component of litecord
# Copyright 2018-2019, Luna Mendes and the mediaproxy contributors
# SPDX-License-Identifier: AGPL-3.0-only

import pytest

from mediaproxy.insertr.embedders.opengraph import from_html


@pytest.mark.asyncio
async def test_empty():
    """Test empty string against ogp parser"""
    assert not await from_html("")


@pytest.mark.asyncio
async def test_title():
    """test embed.title from ogp"""
    embed = await from_html(
        """
    <html>
    <head>
        <meta property="og:title" content="some title">
    </head>
    <body>
        blah.
    </body>
    </html>
    """
    )

    assert embed["title"] == "some title"


@pytest.mark.asyncio
async def test_description():
    """test embed.description from ogp"""
    embed = await from_html(
        """
    <html>
    <head>
        <meta property="og:title" content="some title">
        <meta property="og:description" content="some desc">
    </head>
    <body>
        blah.
    </body>
    </html>
    """
    )

    assert embed["title"] == "some title"
    assert embed["description"] == "some desc"

    assert embed["title"] == "some title"
