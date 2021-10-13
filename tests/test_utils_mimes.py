# mediaproxy: mediaproxy component of litecord
# Copyright 2018-2019, Luna Mendes and the mediaproxy contributors
# SPDX-License-Identifier: AGPL-3.0-only

from mediaproxy.mimes import get_extension, get_mimetype


def test_extension():
    """Test mimetype -> extension conversion"""
    assert get_extension("image/png") == "png"
    assert get_extension("image/webp") == "webp"


def test_invalid_ext():
    """Test invalid mime"""
    try:
        get_extension("ppppppppppppp")
        assert False
    except ValueError:
        pass


def test_mimetype():
    """Test extension -> mimetype conversion"""
    assert get_mimetype("png") == "image/png"
    assert get_mimetype("webp") == "image/webp"
