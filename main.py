from datetime import UTC, datetime
from os import getenv

from dotenv import load_dotenv
from sanic import Sanic, json
from sanic.request import Request
from sanic.response import HTTPResponse, text

from util import MediaSaveHandler, MoahNodeDB, PartialMedia

load_dotenv()

app = Sanic("MoahNode")


@app.before_server_start
async def before_server_start(app_: Sanic) -> None:
    # TODO: handle getenv type
    app_.ctx.database = await MoahNodeDB.acquire(
        host=getenv("MARIADB_HOST"),
        port=int(getenv("MARIADB_PORT")),
        user=getenv("MARIADB_USER"),
        password=getenv("MARIADB_PASSWORD"),
        db=getenv("MARIADB_DB"),
    )


@app.after_server_stop
async def after_server_stop(app_: Sanic) -> None:
    if app.ctx.database is not None:
        await app_.ctx.database.close()


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
    media["created_at"] = str(media["created_at"])

    return json(media)


@app.post("/media")
async def post_media(request: Request) -> HTTPResponse:
    # TODO: rate limiting

    file = request.files.get("file")
    if file is None:
        return text("Missing file.", status=400)

    ext: str = file.name.split(".")[-1]

    if len(ext) > 7:
        return text("File extension too long. (Max 7)", status=400)

    with MediaSaveHandler(file.body, ext) as handler:
        media_data: PartialMedia = {
            "dir": handler.dir,
            "created_at": datetime.now(UTC),
            "uploader": 1,  # TODO: get uploader
        }
        await app.ctx.database.insert_media(media_data)
        handler.mark_safe()

    # TODO: error handling and better response data
    return text("Media saved successfully.", status=200)


if __name__ == "__main__":
    app.run(dev=True)
