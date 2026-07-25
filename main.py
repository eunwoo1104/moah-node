from typing import Optional

from dotenv import load_dotenv
from sanic import Sanic
from sanic.request import Request
from sanic.response import HTTPResponse, text

from util import MoahNodeDB

load_dotenv()

app = Sanic("MoahNode")
database: Optional[MoahNodeDB] = None


@app.before_server_start
async def before_server_start() -> None:
    pass


@app.after_server_stop
async def after_server_stop() -> None:
    if database is not None:
        await database.close()


@app.get("/")
async def hello_world(request: Request) -> HTTPResponse:
    return text("Hello, world.")
