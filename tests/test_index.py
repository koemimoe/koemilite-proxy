# mediaproxy: mediaproxy component of litecord
# Copyright 2018-2019, Luna Mendes and the mediaproxy contributors
# SPDX-License-Identifier: AGPL-3.0-only

import pytest


@pytest.mark.asyncio
async def test_index(test_cli):
    """Test index page"""
    resp = await test_cli.get("/")
    assert resp.status_code == 200
