import asyncio
from os import environ
from enum import Enum
from typing import Any, Dict, Optional

import httpx

WEBHOOK_URL = environ.get("AUDIT_LOG_WEBHOOK")

class AuditColour(Enum):
    DEFAULT = 0xE70B71
    SUCCESS = 0x43B581
    ERROR = 0xF04747
    BLURPLE = 0x7289DA

async def send_audit_log(
    title: Optional[str] = None,
    body: Optional[str] = None,
    inline_fields: Optional[Dict[str, Any]] = {},
    newline_fields: Optional[Dict[str, Any]] = {},
    colour: AuditColour = AuditColour.DEFAULT
):
    """
    Send an audit log to the Discord webhook.
    """
    inline_fields = [{"name": k, "value": v, "inline": True} for k, v in inline_fields.items()]
    newline_fields = [{"name": k, "value": v, "inline": False} for k, v in newline_fields.items()]

    fields = inline_fields + newline_fields

    async with httpx.AsyncClient() as client:
        resp = await client.post(WEBHOOK_URL, json={
            "username": "Modcast Podcast Admin",
            "icon_url": "https://cdn.discordapp.com/team-icons/755212236242288640/69496a2e8be6eccfee1fbc0fce476ae8.png",
            "embeds": [{
                "title": title,
                "description": body,
                "fields": fields,
                "color": colour.value
            }]
        })

        if resp.status_code == 204:
            # Success
            return
        elif resp.status_code == 429:
            # Ratelimited
            ratelimit = await resp.json()
            
            try_after = ratelimit["retry_after"]
            await asyncio.sleep(try_after)
        else:
            # Unknown error
            return
