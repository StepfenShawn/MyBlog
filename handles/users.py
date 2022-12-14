import re, time, json, hashlib
import logging
from coroweb import get, post
from models import User, next_id
from errors import *
from aiohttp import web, web_request
from .page import get_page_index

COOKIE_NAME = 'blogsession'
_COOKIE_KEY = 'blog'

'''
Generate cookie str by user.
'''
def user2cookie(user, max_age):
  expires = str(int(time.time() + max_age))
  s = '%s-%s-%s-%s' % (user.id, user.passwd, expires, _COOKIE_KEY)
  L = [user.id, expires, hashlib.sha1(s.encode('utf-8')).hexdigest()]
  return '-'.join(L)

async def cookie2user(cookie_str):
  if not cookie_str:
    return None
  try:
    L = cookie_str.split('-')
    if len(L) != 3:
      return None
    uid, expires, sha1 = L
    if int(expires) < time.time():
      return None
    user = await User.find(uid)
    if user is None:
      return None
    s = '%s-%s-%s-%s' % (uid, user.passwd, expires, _COOKIE_KEY)
    if sha1 != hashlib.sha1(s.encode('utf-8')).hexdigest():
      logging.info('invalid sha1')
      return None
    user.passwd = '******'
    return user
  except Exception as e:
    logging.exception(e)
    return None

@get('/register')
async def register(request : web_request.Request):
  return {
    '__template__' : 'register.html'
  }

@get('/signin')
async def signin(request : web_request.Request):
  return {
    '__template__' : 'signin.html'
  }

@get('/signout')
async def signout(request : web_request.Request):
  # remove session cookie (just set the max_age = -1000)
  user = request.__user__
  r = web.Response()
  r.set_cookie(COOKIE_NAME, user2cookie(user, -1000), max_age = -1000, httponly = True)
  user.passwd = '******'
  r.content_type = 'text/html;charset=utf-8'
  r.body = b'<script>location.reload();location.assign("/")</script>'
  return r

@get('/api/users')
async def api_get_users():
  users = await User.findAll()
  for u in users:
    u.passwd = '******'
  return dict(users=users)

@get('/api/users/{id}')
async def api_get_users_by_id(*, id):
  user = await User.find(id)
  return user

@post('/api/users/{id}/edit')
async def api_edit_users(id, location, image, name, request, **kw):
  user = await User.find(id)
  user.location = location
  user.image = image
  user.name = name
  await user.update()
  return user

_RE_EMAIL = re.compile(r'^[a-z0-9\.\-\_]+\@[a-z0-9\-\_]+(\.[a-z0-9\-\_]+){1,4}$')
_RE_SHA1 = re.compile(r'^[0-9a-f]{40}$')

@post('/api/users')
async def api_register_user(*, email, name, passwd):
  if not name or not name.strip():
    raise APIValueError('name')
  if not email or not _RE_EMAIL.match(email):
    raise APIValueError('email')
  if not passwd or not _RE_SHA1.match(passwd):
    raise APIValueError('passwd')
  users = await User.findAll('email=?', [email])
  if len(users) > 0:
    raise APIError('register:failed', 'email', 'Email is already in use.')
  uid = next_id()
  sha1_passwd = '%s:%s' % (uid, passwd)
  user = User(id = uid, name = name.strip(), email = email, passwd=hashlib.sha1(sha1_passwd.encode('utf-8')).hexdigest(), 
      image='/static/img/defalut_avatar.png')
  await user.save()
  # make session cookie
  r = web.Response()
  r.set_cookie(COOKIE_NAME, user2cookie(user, 86400), max_age = 86400, httponly = True)
  user.passwd = '******'
  r.content_type = 'application/json'
  r.body = json.dumps(user, ensure_ascii = False).encode('utf-8')
  return r

@post('/api/authenticate')
async def authenticate(*, email, passwd):
  if not email:
    raise APIValueError('email', 'Invalid email.')
  if not passwd:
    raise APIValueError('passwd', 'Invalid password.')
  users = await User.findAll('email=?', [email])
  if len(users) == 0:
    raise APIValueError('email', 'Email not exist.')
  user = users[0]
  # check password
  sha1 = hashlib.sha1()
  sha1.update(user.id.encode('utf-8'))
  sha1.update(b':')
  sha1.update(passwd.encode('utf-8'))
  if user.passwd != sha1.hexdigest():
    raise APIValueError('passwd', 'Invalid password.')
  # authenticate ok, set cookie:
  r = web.Response()
  r.set_cookie(COOKIE_NAME, user2cookie(user, 86400), max_age = 86400, httponly = True)
  user.passwd = '******'
  r.content_type = 'application/json'
  r.body = json.dumps(user, ensure_ascii = False).encode('utf-8')
  return r

@get('/user/{id}')
async def get_user(id, request, **kw):
  user = await User.find(id)
  return {
    '__template__' : 'user.html',
    'user' : user,
    '__user__' : request.__user__
  }

@get('/manage/users')
async def manage_users(request, *, page = '1', **kw):
  return {
    '__template__' : 'manage_user.html',
    'page_index' : get_page_index(page),
    '__user__' : request.__user__
  }

@get('/user/{id}/edit')
async def user_setting(id, request, **kw):
  return {
    '__template__' : 'user_setting.html',
    '__user__' : request.__user__,
    'id' : id,
    'action' : '/api/users/'
  }