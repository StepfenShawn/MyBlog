import asyncio, os, inspect, logging, functools

from urllib import parse
from aiohttp import web
from errors import APIError

'''
A set include all the handler functions (define by @get and @post)
'''
handle_list = set()

'''
Define decorator @get('/path')
'''
def get(path):
  def decorator(func):
    @functools.wraps(func)
    def wrapper(*args, **kw):
      return func(*args, **kw)
    wrapper.__method__ = 'GET'
    wrapper.__route__ = path
    handle_list.add(wrapper)
    return wrapper
  return decorator

'''
Define decorator @post('/path')
'''
def post(path):
  def decorator(func):
    @functools.wraps(func)
    def wrapper(*args, **kw):
      return func(*args, **kw)
    wrapper.__method__ = 'POST'
    wrapper.__route__ = path
    handle_list.add(wrapper)
    return wrapper
  return decorator

def get_required_kw_args(fn):
  args = []
  params = inspect.signature(fn).parameters
  for name, param in params.items():
    # inspect.Parameter.KEYWORD_ONLY : 强制关键子参数
    if param.kind == inspect.Parameter.KEYWORD_ONLY and \
       param.default == inspect.Parameter.empty:
       args.append(name)
  return tuple(args)

def get_named_kw_args(fn):
  args = []
  params = inspect.signature(fn).parameters
  for name, param in params.items():
    if param.kind == inspect.Parameter.KEYWORD_ONLY:
      args.append(name)
  return tuple(args)

def has_named_kw_args(fn):
  params = inspect.signature(fn).parameters
  for name, param in params.items():
    if param.kind == inspect.Parameter.KEYWORD_ONLY:
      return True

def has_var_kw_args(fn):
  params = inspect.signature(fn).parameters
  for name, param in params.items():
    if param.kind == inspect.Parameter.VAR_KEYWORD:
      return True

def has_request_arg(fn):
  sig = inspect.signature(fn)
  params = sig.parameters
  found = False
  for name, param in params.items():
    if name == 'request':
      found = True
      continue
    if found and (param.kind != inspect.Parameter.VAR_POSITIONAL and param.kind != inspect.Parameter.KEYWORD_ONLY and param.kind != inspect.Parameter.VAR_KEYWORD):
      raise ValueError('request parameter must be the last named parameter in function: %s%s' % (fn.__name__, str(sig)))
  return found

class RequestHandler(object):
  def __init__(self, app, fn):
    self.app = app
    self.fn = fn
    self._has_request_arg = has_request_arg(fn)
    self._has_var_kw_arg = has_var_kw_args(fn)
    self._has_named_kw_args = has_named_kw_args(fn)
    self._named_kw_args = get_named_kw_args(fn)
    self._required_kw_args = get_required_kw_args(fn)

  # generated args 'kw' for self.fn
  async def __call__(self, request):
    kw = None
    if self._has_var_kw_arg or self._has_named_kw_args or self._required_kw_args:
      # POST
      if request.method == 'POST':
        if not request.content_type:
          return web.HTTPBadRequest('Missing Content-Type.')
        ct = request.content_type.lower()
        if ct.startswith('application/json'):
          params = await request.json()
          if not isinstance(params, dict):
            return web.HTTPBadRequest('JSON body must be object.')
          kw = params
        elif ct.startswith('application/x-www-form-urlencoded') or ct.startswith('multipart/form-data'):
          params = await request.post()
          kw = dict(**params)
        else:
          return web.HTTPBadRequest('Unsupported Content-Type : %s' % request.content_type)
      
      # GET
      if request.method == 'GET':
        qs = request.query_string
        if qs:
          kw = dict()
          for k,v in parse.parse_qs(qs, True).items():
            kw[k] = v[0]
      
    if kw is None:
      kw = dict(**request.match_info)
    else:
      for k, v in request.match_info.items():
        kw[k] = v

    if self._has_request_arg:
      kw['request'] = request

    if self._required_kw_args:
      for name in self._required_kw_args:
        if not name in kw:
          return web.HTTPBadRequest('Missing argument: %s' % name)
    logging.info('call with args : %s' % str(kw))
    try:
      r = await self.fn(**kw)
      return r
    except APIError as e:
      return dict(error = e.error, data = e.data, message = e.message)

def add_static(app):
  path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
  app.router.add_static('/static/', path)
  logging.info('add static %s => %s' % ('/static/', path))

def add_route(app, fn):
  method = getattr(fn, '__method__', None)
  path = getattr(fn, '__route__', None)
  if path is None or method is None:
    raise ValueError('@get or @post not define in %s.' % str(fn))
  if not asyncio.iscoroutinefunction(fn) and not inspect.isgeneratorfunction(fn):
    fn = asyncio.coroutine(fn)
  logging.info('add route %s %s => %s (%s)' % (method, path, fn.__name__, ' '.join(inspect.signature(fn).parameters.keys())))
  # 注册路由匹配
  app.router.add_route(method, path, RequestHandler(app, fn))