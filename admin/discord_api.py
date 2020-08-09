from collections import defaultdict
from os import environ

import httpx

DISCORD_API_TOKEN = environ.get("BOT_TOKEN")

RATELIMITS = defaultdict(dict)

USER_CACHE = {}

DISCORD_API_BASE = "https://discord.com/api/v7"

class RateLimitException(Exception):
    pass

async def upstream_get_user(user_id):
    if RATELIMITS["users"].get("remaining") == 0:
        raise RateLimitException(RATELIMITS["users"]["reset_after"])

    async with httpx.AsyncClient() as client:
        user = await client.get(f"{DISCORD_API_BASE}/users/{user_id}", headers={
            "Authorization": f"Bot {DISCORD_API_TOKEN}"
        })

    RATELIMITS["users"]["reset_after"] = user.headers["x-ratelimit-reset-after"]
    RATELIMITS["users"]["remaining"] = user.headers["x-ratelimit-remaining"]

    if user.status_code == 429:
        # R A T E L I M I T S !
        raise RateLimitException(RATELIMITS["users"]["reset_after"])
    else:
        user_data = user.json()
        USER_CACHE[user_data["id"]] = user_data
        return user_data, user.status_code

async def get_user(user_id):
    if user := USER_CACHE.get(str(user_id)):
        return user, 200
    else:
        return await upstream_get_user(user_id)