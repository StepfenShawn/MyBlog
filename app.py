import logging
logging.basicConfig(level=logging.INFO)
import asyncio, os, json, time
from datetime import datetime

import inspect
from aiohttp import web, web_request
from jinja2 import Environment, FileSystemLoader
import orm
from coroweb import add_route, add_static
from handle import COOKIE_NAME, cookie2user, handler_list  

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
  async def logger(request : web_request.Request):
    logging.info('Request: %s %s' % (request.method, request.path))
    return (await handler(request))
  return logger

async def auto_factory(app, handler):
  async def auto(request : web_request.Request):
    logging.info('check user: %s %s' % (request.method, request.path))
    request.__user__ = None
    cookie_str = request.cookies.get(COOKIE_NAME)
    if cookie_str:
      user = await cookie2user(cookie_str)
      if user:
        logging.info('set current user: %s' % user.email)
        request.__user__ = user
    return await handler(request)
  return auto

# uri 处理
# 将响应信息转化为 web.Response类型
async def response_factory(app, handler):
  async def response(request : web_request.Request):
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
      if template is None:
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

def datetime_filter(t):
  delta = int(time.time() - t)
  if delta < 60:
    return "1 mins ago"
  if delta < 3600:
    return '%s mins ago' % (delta // 60)
  if delta < 86400:
    return '%s hours ago' % (delta // 3600)
  if delta < 604800:
    return '%s days ago' % (delta // 86400)
  dt = datetime.fromtimestamp(t)
  return '%s-%s-%s' % (dt.year, dt.month, dt.day)

async def init(loop):
  await orm.create_pool(loop=loop, host='127.0.0.1', port=3306, user='root', password='root', db='awesome')
  app = web.Application(middlewares=[
    logger_factory,  auto_factory, response_factory
  ])
  init_jinja2(app, filters = dict(datetime = datetime_filter))
  for item in handler_list:
    add_route(app, item)
  add_static(app)

  app_runner = web.AppRunner(app)
  await app_runner.setup()
  site = web.TCPSite(app_runner, '127.0.0.1', '9000')
  logging.info('server started at http://127.0.0.1:9000')
  await site.start()

loop = asyncio.get_event_loop()
loop.run_until_complete(init(loop))
loop.run_forever()