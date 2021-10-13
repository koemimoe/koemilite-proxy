# mediaproxy

Proxy Images and other files through itself. Also can generate Discord Embeds
out of given websites, via OpenGraph or `<meta>` tags or other embedders.

This is an optional component of [Litecord].

[litecord]: https://gitlab.com/litecord/litecord

This is designed to run on a separate machine, so the server running the
litecord instance does not have to deal with other websites.

Discord does not use this software.

## Installation

Requirements:
 - **Python 3.7+**
 - [pipenv]

`mediaproxy` does not require a database. The filesystem is used as cache.

[pipenv]: https://github.com/pypa/pipenv

### Download the code

```sh
$ git clone https://gitlab.com/litecord/mediaproxy.git && cd mediaproxy
```

### Install packages

```sh
$ pipenv install
```

### Configuration

```sh
$ cp config.example.ini config.ini
# edit config.ini as wanted
```

### Running

It is preferred to run mediaproxy on the port `5002`,
while Litecord and its websocket run on ports 5000 and 5001 respectively.

```sh
$ pipenv run hypercorn run:app --bind 0.0.0.0:5002
```

**It is recommended to run mediaproxy behind [NGINX].** You can use the
`nginx.conf` file at the root of the repository as a template.

[nginx]: https://www.nginx.com

## Usage

external websites use the following syntax in paths:

```
/<scheme>/<path>
```

`path` is composed of `<host>/<url_path>`.
`scheme` can only be `http` or `https`.

 - the `/img/` scope proxies an external HTTP website's **multimedia** resource.
 - the `/meta` scope gives metadata about an external image, such as width
    and height, used for embed generation in litecord
 - the `/embed/` scope gives a discord embed representing the url. depending
    of the url's format it can be routed to a different embedder, such as
    the OGP (OpenGraph Protocol) embedder, `<meta>` embedder, or XKCD embedder,
    etc.

### Errors

 - Requesting images or metadata from URLs that aren't images will return a
    405 Method Not Allowed response.
 - Embeds that fail to be generated will return `null`.

### Example

if you want to get a certain image's raw data as a response body,
`http://blah.com/img/http/website.com/photo.png`

replace `img` with `meta` for image metadata, and `img` with `embed` to generate
an embed.
