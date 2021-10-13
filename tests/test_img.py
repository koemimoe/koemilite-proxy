# mediaproxy: mediaproxy component of litecord
# Copyright 2018-2019, Luna Mendes and the mediaproxy contributors
# SPDX-License-Identifier: AGPL-3.0-only

import pytest


@pytest.mark.asyncio
async def test_invalid_image(test_cli):
    """Test a URL pointing to an html page."""
    resp = await test_cli.get("/img/https/example.com")
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_valid_image(test_cli):
    """Test a URL pointing to an image. Then do it again to ensure cache
    path goes through."""
    resp = await test_cli.get("/img/https/elixi.re/i/mp9.png")
    assert resp.status_code == 200

    resp = await test_cli.get("/img/https/elixi.re/i/mp9.png")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_invalid_scheme(test_cli):
    """Test invalid scheme"""
    resp = await test_cli.get("/img/ftp/example.com")
    assert resp.status_code == 422

    resp = await test_cli.get("/meta/ftp/example.com")
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_invalid_image_meta(test_cli):
    """Test a URL pointing to an html page."""
    resp = await test_cli.get("/meta/https/example.com")
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_valid_image_meta(test_cli):
    """Test a URL pointing to an image."""
    resp = await test_cli.get("/meta/https/elixi.re/i/mp9.png")
    assert resp.status_code == 200

    rjson = await resp.json
    assert isinstance(rjson["width"], int)
    assert isinstance(rjson["height"], int)
