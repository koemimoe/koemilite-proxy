# mediaproxy: mediaproxy component of litecord
# Copyright 2018-2019, Luna Mendes and the mediaproxy contributors
# SPDX-License-Identifier: AGPL-3.0-only

import time
from typing import Optional

from quart import current_app as app, request

from mediaproxy.errors import Ratelimited


class RatelimitBucket:
    """Main ratelimit bucket class.

    Code extracted from litecord, which was extracted from elixire,
    which is work on top of discord.py.
    """

    def __init__(self, tokens, second):
        self.requests = tokens
        self.second = second

        self._window = 0.0
        self._tokens = self.requests
        self.retries = 0
        self._last = 0.0

    def get_tokens(self, current):
        """Get the current amount of available tokens."""
        if not current:
            current = time.time()

        # by default, use _tokens
        tokens = self._tokens

        # if current timestamp is above _window + seconds
        # reset tokens to self.requests (default)
        if current > self._window + self.second:
            tokens = self.requests

        return tokens

    def update_rate_limit(self):
        """Update current ratelimit state."""
        current = time.time()
        self._last = current
        self._tokens = self.get_tokens(current)

        # we are using the ratelimit for the first time
        # so set current ratelimit window to right now
        if self._tokens == self.requests:
            self._window = current

        # Are we currently ratelimited?
        if self._tokens == 0:
            self.retries += 1
            return self.second - (current - self._window)

        # if not ratelimited, remove a token
        self.retries = 0
        self._tokens -= 1

        # if we got ratelimited after that token removal,
        # set window to now
        if self._tokens == 0:
            self._window = current

        return None

    def reset(self):
        """Reset current ratelimit to default state."""
        self._tokens = self.requests
        self._last = 0.0
        self.retries = 0

    def copy(self):
        """Create a copy of this ratelimit.

        Used to manage multiple ratelimits to users.
        """
        return RatelimitBucket(self.requests, self.second)

    def __repr__(self):
        return (
            f"<RatelimitBucket requests={self.requests} "
            f"second={self.second} window: {self._window} "
            f"tokens={self._tokens}>"
        )


class Ratelimit:
    """Manages buckets."""

    def __init__(self, tokens, second, keys=None):
        self._cache = {}
        if keys is None:
            keys = tuple()
        self.keys = keys
        self._cooldown = RatelimitBucket(tokens, second)

    def __repr__(self):
        return f"<Ratelimit cooldown={self._cooldown}>"

    def _verify_cache(self):
        current = time.time()
        dead_keys = [k for k, v in self._cache.items() if current > v._last + v.second]

        for k in dead_keys:
            del self._cache[k]

    def get_bucket(self, key) -> Optional[RatelimitBucket]:
        if not self._cooldown:
            return None

        self._verify_cache()

        if key not in self._cache:
            bucket = self._cooldown.copy()
            self._cache[key] = bucket
        else:
            bucket = self._cache[key]

        return bucket


def get_ip() -> str:
    """Get the remote address of a request. Supports reverse
    proxies setting X-Forwarded-For."""
    if "X-Forwarded-For" in request.headers:
        return request.headers["X-Forwarded-For"]

    return request.remote_addr


async def rtl_handler():
    """Simple ratelimit handler."""
    ip_addr = get_ip()
    bucket = app.ratelimit.get_bucket(ip_addr)
    retry_after = bucket.update_rate_limit()

    if retry_after:
        raise Ratelimited()
