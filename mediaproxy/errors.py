# mediaproxy: mediaproxy component of litecord
# Copyright 2018-2019, Luna Mendes and the mediaproxy contributors
# SPDX-License-Identifier: AGPL-3.0-only


class InvalidResponse(Exception):
    pass


class MimeError(Exception):
    pass


class Ratelimited(Exception):
    pass
