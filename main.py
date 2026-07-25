from sanic import Sanic
from sanic.response import text

app = Sanic("MoahNode")

@app.get("/")
async def hello_world(request):
    return text("Hello, world.")
