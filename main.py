from os import getenv

from dotenv import load_dotenv
from sanic import Sanic, json
from sanic.request import Request
from sanic.response import HTTPResponse, text

from util import (
    MediaSaveHandler,
    MediaUploadSessionManager,
    MoAhNodeCTX,
    MoAhNodeDB,
    PartialMedia,
    create_response,
)

load_dotenv()

app = Sanic("MoAhNode", ctx=MoAhNodeCTX())


@app.before_server_start
async def before_server_start(app_: Sanic) -> None:
    # TODO: handle getenv type
    app_.ctx.database = await MoAhNodeDB.acquire(
        host=getenv("MARIADB_HOST"),
        port=int(getenv("MARIADB_PORT")),
        user=getenv("MARIADB_USER"),
        password=getenv("MARIADB_PASSWORD"),
        db=getenv("MARIADB_DB"),
    )
    app_.ctx.session = MediaUploadSessionManager()


@app.after_server_stop
async def after_server_stop(app_: Sanic) -> None:
    if app_.ctx.database is not None:
        await app_.ctx.database.close()

    if app_.ctx.session is not None:
        await app_.ctx.session.close()


@app.get("/")
async def hello_world(request: Request) -> HTTPResponse:
    return text("Hello, world.")


@app.get("/media")
async def get_media(request: Request) -> HTTPResponse:
    media_id = request.args.get("id")
    if media_id is None:
        return text("Parameter 'id' is required.", status=400)

    media = await app.ctx.database.get_media(media_id)
    if media is None:
        return text("Media not found.", status=404)

    # TODO: gracefully handle datetime
    resp = media.copy()
    resp["created_at"] = str(media["created_at"])

    # TODO: get media object

    return json(resp)


@app.post("/media")
async def post_media(request: Request) -> HTTPResponse:
    # TODO: rate limiting

    key = request.json.get("key")
    core_id = await app.ctx.session.get_session(key)
    if core_id is None:
        return json(
            create_response("SESSION_INVALID", msg="Session not found"), status=401
        )

    file = request.files.get("file")
    if file is None:
        return json(create_response("VALIDATION_ERROR", msg="Missing file"), status=400)

    ext: str = file.name.split(".")[-1]

    if len(ext) > 7:
        return json(
            create_response("VALIDATION_ERROR", msg="File extension too long"),
            status=400,
        )

    with MediaSaveHandler(file.body, ext) as handler:
        media_data: PartialMedia = {
            "dir": handler.dir,
            "uploaded_from": int(core_id),
        }
        file_id = await app.ctx.database.insert_media(media_data)
        handler.mark_safe()

    # TODO: error handling and better response data
    return json(create_response("OK", content={"id": file_id}), status=200)


@app.post("/session")
async def create_session(request: Request) -> HTTPResponse:
    # TODO: better auth method (maybe HMAC?)
    # current implementation is temporary
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Basic "):
        return json(create_response("SESSION_INVALID"), status=401)

    key = auth.lstrip("Basic ")
    core_id = await app.ctx.database.get_core_id(key)
    if core_id is None:
        return json(create_response("SESSION_INVALID"), status=401)

    session = await app.ctx.session.create_session(core_id)
    return json(create_response("OK", content={"session": session}), status=200)


if __name__ == "__main__":
    app.run(dev=True)
