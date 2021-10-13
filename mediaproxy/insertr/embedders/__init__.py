# mediaproxy: mediaproxy component of litecord
# Copyright 2018-2019, Luna Mendes and the mediaproxy contributors
# SPDX-License-Identifier: AGPL-3.0-only

from .opengraph import gen_embed as opengraph_embed
from .xkcd import gen_embed as xkcd_embed
from .activitypub import gen_embed as activitypub_embed
from .meta import gen_embed as meta_embed
from .twitter import gen_embed as twitter_embed
from .spotify import gen_embed as spotify_embed

__all__ = ["xkcd_embed", "opengraph_embed", "meta_embed", "activitypub_embed", "twitter_embed", "spotify_embed"]
