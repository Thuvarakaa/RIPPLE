# web_routes.py
import picoweb

def index(req, resp):
    yield from picoweb.start_response(resp, "text/html")
    with open("index.html", "r") as f:
        yield from resp.awrite(f.read())

ROUTES = [
    ("/", index),
]
