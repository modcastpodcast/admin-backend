from asyncpg.exceptions import UniqueViolationError
from starlette.responses import JSONResponse

from admin.route import Route
from admin.models import ShortURL
from admin.utils import is_authorized, is_json


class LinkRoute(Route):
    """
    Route for fetching, creating, updating and deleting links.
    """
    name = "link"
    path = "/link"

    @is_authorized
    async def get(self, request):
        urls = await ShortURL.query.order_by(ShortURL.clicks.desc()).gino.all()

        response = []

        for url in urls:
            if (
                request.query_params.get("mine")
                and url.creator != request.state.api_key.creator
            ):
                continue

            response.append({
                "short_code": url.short_code,
                "long_url": url.long_url,
                "notes": url.notes,
                "creator": str(url.creator),
                "creation_date": url.creation_date.timestamp(),
                "clicks": url.clicks
            })

        return JSONResponse(response)

    @is_authorized
    @is_json
    async def post(self, request):
        data = await request.json()

        if data["short_code"].isspace() or data["short_code"] == "":
            return JSONResponse(
                {
                    "status": "error",
                    "message": "Short code cannot be blank"
                },
                status_code=400
            )

        if data["long_url"].isspace() or data["long_url"] == "":
            return JSONResponse(
                {
                    "status": "error",
                    "message": "Long URL cannot be blank"
                },
                status_code=400
            )

        if request.state.api_key.is_admin and data.get("creator"):
            new_url = ShortURL(
                short_code=data["short_code"],
                long_url=data["long_url"],
                creator=data["creator"],
                notes=data.get("notes", "")
            )
        else:
            new_url = ShortURL(
                short_code=data["short_code"],
                long_url=data["long_url"],
                creator=request.state.api_key.creator,
                notes=data.get("notes", "")
            )

        try:
            await new_url.create()
        except UniqueViolationError:
            return JSONResponse(
                {
                    "status": "error",
                    "message": "Short code already exists"
                },
                status_code=400
            )

        return JSONResponse(
            {
                "status": "success"
            }
        )

    @is_authorized
    @is_json
    async def delete(self, request):
        data = await request.json()

        short_url = await ShortURL.get(data["short_code"])

        if not short_url:
            return JSONResponse({
                "status": "error",
                "message": "Short URL not found"
            }, status_code=404)

        if (
            request.state.api_key.is_admin
            or request.state.api_key.creator == short_url.creator
        ):
            await short_url.delete()
        else:
            return JSONResponse({
                "status": "error",
                "message": "You are not an administrator "
                           "and you do not own this short URL"
            }, status_code=403)

        return JSONResponse({
            "status": "success"
        })

    @is_authorized
    @is_json
    async def patch(self, request):
        data = await request.json()

        short_url = await ShortURL.get(data["old_short_code"])

        if not short_url:
            return JSONResponse({
                "status": "error",
                "message": "Short URL not found"
            }, status_code=404)

        updates = {
            "short_code": data.get("short_code", short_url.short_code),
            "long_url": data.get("long_url", short_url.long_url),
            "notes": data.get("notes", short_url.notes)
        }

        if updates["short_code"].isspace() or updates["short_code"] == "":
            return JSONResponse(
                {
                    "status": "error",
                    "message": "Short code cannot be blank"
                },
                status_code=400
            )

        if updates["long_url"].isspace() or updates["long_url"] == "":
            return JSONResponse(
                {
                    "status": "error",
                    "message": "Long URL cannot be blank"
                },
                status_code=400
            )

        if request.state.api_key.is_admin:
            updates["creator"] = int(data.get("creator", short_url.creator))

        try:
            await short_url.update(**updates).apply()
        except UniqueViolationError:
            return JSONResponse({
                "status": "error",
                "message": "New short URL already exists"
            }, status_code=400)

        return JSONResponse({
            "status": "success"
        })
