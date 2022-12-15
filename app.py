import logging
logging.basicConfig(level=logging.INFO)
import asyncio, os, json, time
from datetime import datetime

from aiohttp import web

html = ""
with open("index.html", encoding='utf-8') as f:
  html = f.read()

def index(request):
  global html
  return web.Response(body=html, headers = {"content-type": "text/html"})

@asyncio.coroutine
def init(loop):
  app = web.Application(loop=loop)
  app.router.add_route('GET', '/', index)
  srv = yield from loop.create_server(app.make_handler(), '127.0.0.1', '9000')
  logging.info('server started at http://127.0.0.1:9000')
  return srv

loop = asyncio.get_event_loop()
loop.run_until_complete(init(loop))
loop.run_forever()