# mediaproxy: mediaproxy component of litecord
# Copyright 2018-2019, Luna Mendes and the mediaproxy contributors
# SPDX-License-Identifier: AGPL-3.0-only

from .proxy import bp as proxy
from .insertr import bp as insertr
from .url_cache import bp as url_cache

__all__ = ["proxy", "insertr", "url_cache"]
