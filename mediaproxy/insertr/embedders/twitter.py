# mediaproxy: mediaproxy component of litecord
# Copyright 2018-2019, Luna Mendes and the mediaproxy contributors
# SPDX-License-Identifier: AGPL-3.0-only

import re

from logbook import Logger
import json

from mediaproxy.utils import embed_image
from mediaproxy.outgoing import fetch

TWITTER_REGEX = re.compile(r"https?:\/\/twitter.com\/[0-9a-zA-Z_]{1,20}\/status\/([0-9]*)")
log = Logger(__name__)


async def gen_embed(url: str) -> dict:
    """Generate an embed out of a TWITTER url."""
    match = TWITTER_REGEX.match(url)

    if not match:
        return

    tweet_id = match.group(1)
    tweet_url = f"https://api.twitter.com/2/tweets/{tweet_id}?expansions=attachments.media_keys,author_id&tweet.fields=attachments,author_id,id,created_at,text,public_metrics&media.fields=height,width,url,preview_image_url,type&user.fields=name,username,url,profile_image_url"

    tweet_data = await fetch(tweet_url, json=True, headers={"Authorization": "Bearer AAAAAAAAAAAAAAAAAAAAAERjCQEAAAAASrbwd9qiQwqpq0rxDycwl2XRFL8%3DhxXe9SZGw2pFq5K74oNXlHgcN6SzG9uIUGw7PMTLVaeGEnfOly"})
    
    tweet_uimg_meta = await embed_image(tweet_data["includes"]["users"][0]["profile_image_url"].replace("normal", "bigger"))
    tweet_fimg_meta = await embed_image("https://abs.twimg.com/icons/apple-touch-icon-192x192.png")

    embed = {
        "type": "rich",
		"url": url,
		"description": tweet_data["data"]["text"],
		"color": 1942002,
		"timestamp": tweet_data["data"]["created_at"],
		"fields": [
			{
				"name": "Retweets",
				"value": str(tweet_data["data"]["public_metrics"]["retweet_count"]),
				"inline": True
			},
			{
				"name": "Likes",
				"value": str(tweet_data["data"]["public_metrics"]["like_count"]),
				"inline": True
			}
		],
		"author": {
			"name": tweet_data["includes"]["users"][0]["name"]+" (@"+tweet_data["includes"]["users"][0]["username"]+")",
			"url": "https://twitter.com/"+tweet_data["includes"]["users"][0]["username"],
			"icon_url": tweet_uimg_meta["url"],
			"proxy_icon_url": tweet_uimg_meta["proxy_url"]
		},
		"footer": {
			"text": "Twitter",
			"icon_url": "https://abs.twimg.com/icons/apple-touch-icon-192x192.png",
			"proxy_icon_url": tweet_fimg_meta["proxy_url"]
		}
    }
    
    if "attachments" in tweet_data["data"]:
        if tweet_data["includes"]["media"][0]["type"] == "photo":
            embed["image"] = await embed_image(tweet_data["includes"]["media"][0]["url"])
        elif tweet_data["includes"]["media"][0]["type"] == "animated_gif":
            embed_t = await embed_image(tweet_data["includes"]["media"][0]["preview_image_url"])
            embed["thumbnail"] = embed_t
            embed["video"] = {"url": "https://twitter.com/i/videos/tweet/"+tweet_id, "width": embed_t["width"], "height": embed_t["height"]}
        elif tweet_data["includes"]["media"][0]["type"] == "video":
            embed_t = await embed_image(tweet_data["includes"]["media"][0]["preview_image_url"])
            embed["thumbnail"] = embed_t
            embed["video"] = {"url": "https://twitter.com/i/videos/tweet/"+tweet_id, "width": embed_t["width"], "height": embed_t["height"]}
        
        embedadd = []
        
        for mediac in tweet_data["includes"]["media"][1:4]:
            if mediac["type"] == "photo":
                embedadd.append(
                    {"url": url, "type": "rich", "image": await embed_image(mediac["url"])}
                )
            elif mediac["type"] == "animated_gif":
                embed_t = await embed_image(mediac["preview_image_url"])
                embedadd.append(
                    {"url": url, "type": "rich", "thumbnail": embed_t, "video": {"url": "https://twitter.com/i/videos/tweet/"+tweet_id, "width": embed_t["width"], "height": embed_t["height"]}}
                )
            elif mediac["type"] == "video":
                embed_t = await embed_image(mediac["preview_image_url"])
                embedadd.append(
                    {"url": url, "type": "rich", "thumbnail": embed_t, "video": {"url": "https://twitter.com/i/videos/tweet/"+tweet_id, "width": embed_t["width"], "height": embed_t["height"]}}
                )
                
        embedadd = json.loads(json.dumps(embedadd))
        
        if not embedadd:
            return embed
        elif embedadd[0] and not 1 < len(embedadd):
            return embed, embedadd[0]
        elif embedadd[0] and embedadd[1] and not 2 < len(embedadd):
            return embed, embedadd[0], embedadd[1]
        else:
            return embed, embedadd[0], embedadd[1], embedadd[2]
    else:
        return embed
