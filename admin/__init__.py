from os import environ

from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.cors import CORSMiddleware
from starlette_gino.middleware import DatabaseMiddleware

from admin.models import db
from admin.route_manager import create_route_map

middleware = [
    Middleware(SessionMiddleware, secret_key=environ.get("SECRET_KEY")),
    Middleware(
        CORSMiddleware,
        allow_origins=[
            "https://admin.modpod.live",
            "http://127.0.0.1:3000"
        ],
        allow_headers=[
            "Authorization",
            "Content-Type"
        ],
        allow_methods=["*"]
    ),
    Middleware(
        DatabaseMiddleware,
        db=db,
        database_url=environ.get("DATABASE_URL")
    )
]

app = Starlette(routes=create_route_map(), middleware=middleware)
