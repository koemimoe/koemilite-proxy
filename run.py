# mediaproxy: mediaproxy component of litecord
# Copyright 2018-2019, Luna Mendes and the mediaproxy contributors
# SPDX-License-Identifier: AGPL-3.0-only

import sys
import tempfile
import shutil
import asyncio

from configparser import ConfigParser
from pathlib import Path

import logbook

from aiohttp import ClientSession, ClientTimeout
from logbook import StreamHandler, Logger
from logbook.compat import redirect_logging
from quart import Quart

from mediaproxy.bp import proxy, insertr, url_cache
from mediaproxy.errors import InvalidResponse, MimeError, Ratelimited
from mediaproxy.ratelimit import Ratelimit, rtl_handler

app = Quart(__name__)

handler = StreamHandler(sys.stdout, level=logbook.INFO)
handler.push_application()

log = Logger("mediaproxy")
redirect_logging()


def load_blueprints(app_):
    """Load blueprints"""
    blueprints = [proxy, insertr, url_cache]

    for bp in blueprints:
        app_.register_blueprint(bp)


def load_config(app_):
    """Load config file"""
    cfg = ConfigParser()
    cfg.read("./config.ini")

    app_.cfg = cfg
    app_.testing = False

    if cfg["mediaproxy"]["test"]:
        handler.level = logbook.DEBUG


load_blueprints(app)
load_config(app)


@app.before_serving
async def app_before_serving():
    """Before serving handler"""
    timeout = ClientTimeout(total=20, connect=5, sock_connect=10, sock_read=10)

    app.session = ClientSession(timeout=timeout)

    app.cache_dir = Path(tempfile.mkdtemp(prefix="mediaproxy_"))
    log.info("cache dir: {!r}", app.cache_dir)

    # for now, only 5 concurrent outgoing requests at a time
    app.outgoing_semaphore = asyncio.Semaphore(10)

    # global ratelimit
    try:
        ratelimit = app.cfg["mediaproxy"].get("ratelimit", "5/5")
        ratelimit = ratelimit.split("/")
        ratelimit = map(int, ratelimit)
        ratelimit = tuple(ratelimit)
    except ValueError:
        log.error("config error: invalid ratelimit value")

    app.ratelimit = Ratelimit(ratelimit[0], ratelimit[1])
    log.info("ratelimit: {!r}", app.ratelimit)

    # variables to hold things that run on before_app_request hooks
    # since before_app_request may be run multiple times.
    app.url_cache = None
    app._cache_janitor = None
    app._url_janitor = None


@app.after_serving
async def app_after_serving():
    """After serving handler"""
    await app.session.close()
    log.info("removing cache dir {!r}", app.cache_dir)
    shutil.rmtree(app.cache_dir)


@app.before_request
async def app_before_request():
    """Call ratelimit handler"""
    await rtl_handler()


@app.errorhandler(InvalidResponse)
async def invalid_resp_err(err):
    """Handle InvalidResponse errors."""
    log.warning("invalid response: {!r}", err)
    return "", 401


@app.errorhandler(MimeError)
async def invalid_mime_err(_err):
    """Handle MimeError errors."""
    return "", 400


@app.errorhandler(Ratelimited)
async def ratelimited_err(_err):
    """Handle Ratelimited errors."""
    return "You are being rate limited.", 429


@app.route("/", methods=["GET"])
async def index():
    """Main index handler"""
    return "hewwo"
