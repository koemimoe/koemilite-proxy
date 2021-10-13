# mediaproxy: mediaproxy component of litecord
# Copyright 2018-2019, Luna Mendes and the mediaproxy contributors
# SPDX-License-Identifier: AGPL-3.0-only

import sys
import os

import pytest

# this is very hacky.
sys.path.append(os.getcwd())

from run import app as main_app


@pytest.fixture(name="app")
def _test_app(event_loop):
    main_app.testing = True

    # hardcode that for all tests
    main_app.cfg["mediaproxy"]["tls"] = ""
    main_app.cfg["mediaproxy"]["domain"] = "images.discordapp.io"
    main_app.cfg["mediaproxy"]["ratelimit"] = "100/1"

    # make sure we're calling the before_serving hooks
    # NOTE: startup() is something internal from Quart.
    event_loop.run_until_complete(main_app.startup())

    return main_app


@pytest.fixture(name="test_cli")
def _test_cli(app):
    """Give a test client."""
    return app.test_client()
