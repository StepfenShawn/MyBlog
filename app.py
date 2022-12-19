import logging
logging.basicConfig(level=logging.INFO)
import asyncio, os, json, time
from datetime import datetime

from aiohttp import web
from jinja2 import Environment, FileSystemLoader
import orm
from coroweb import add_route, add_static

def init_jinja2(app, **kw):
  logging.info('init jinja2...')
  options = dict(
    autoescape = kw.get('autoescape', True),
    block_start_string = kw.get('block_start_string', '{%'),
    block_end_string = kw.get('block_end_string', '%}'),
    variable_start_string = kw.get('variable_start_string', '{{'),
    variable_end_string = kw.get('variable_end_string', '}}'),
    auto_reload = kw.get('auto_reload', True)
  )
  path = kw.get('path', None)
  if path is None:
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
  logging.info('set jinja2 template path: %s' % path)
  env = Environment(loader=FileSystemLoader(path), **options)
  filters = kw.get('filters', None)
  if filters is not None:
    for name, f in filters.items():
      env.filters[name] = f
  app['__templating__'] = env

async def logger_factory(app, handler):
  async def logger(request):
    logging.info('Request: %s %s' % (request.method, request.path))
    return (await handler(request))
  return logger

# uri 处理
# 将响应信息转化为 web.Response类型
async def response_factory(app, handler):
  async def response(request):
    logging.info('Response handler...')
    r = await handler(request)
    if (isinstance(r, web.StreamResponse)):
      return r
    if isinstance(r, bytes):
      resp = web.Response(body = r)
      resp.content_type = 'application/octet-stream'
      return resp
    if isinstance(r, str):
      if r.startswith('redirect:'):
        return web.HTTPFound(r[9:])
      resp = web.Response(body=r.encode('utf-8'))
      resp.content_type = 'text/html;charset=utf-8'
      return resp
    if isinstance(r, dict):
      template = r.get('__template__')
      # json type
      if template is not None:
        resp = web.Response(body=json.dumps(r, ensure_ascii=False, default=lambda o : o.__dict__).encode('utf-8'))
        resp.content_type = 'application/json;charset=utf-8'
        return resp
      else:
        resp = web.Response(body=app['__templating__'].get_template(template).render(**r).encode('utf-8'))
        resp.content_type = 'text/html;charset=utf-8'
        return resp
    # status
    if isinstance(r, int) and r >= 100 and r < 600:
      return web.Response(r)
    # status with reason
    if isinstance(r, tuple) and len(r) == 2:
      status, reason = r
      if isinstance(status, int) and status >= 100 and status < 600:
        return web.Response(status, str(reason))
    # default
    resp = web.Response(body=str(r).encode('utf-8'))
    resp.content_type = 'text/plain;charset=utf-8'
    return resp
  return response


@asyncio.coroutine
async def init(loop):
  await orm.create_pool(loop=loop, host='127.0.0.1', port=3306, user='root', password='root', db='awesome')
  app = web.Application(loop=loop, middlewares=[
    logger_factory, response_factory
  ])
  init_jinja2(app)
  add_static(app)
  srv = await loop.create_server(app.make_handler(), '127.0.0.1', '9000')
  logging.info('server started at http://127.0.0.1:9000')
  return srv

loop = asyncio.get_event_loop()
loop.run_until_complete(init(loop))
loop.run_forever()