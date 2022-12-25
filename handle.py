import re, time, json, hashlib, base64, asyncio
import logging
from coroweb import get, post
from models import User, Comment, Blog, next_id
from errors import *
from aiohttp import web
import markdown2

COOKIE_NAME = 'blogsession'
_COOKIE_KEY = 'blog'

def text2html(text):
  lines = map(lambda s: '<p>%s</p>' % s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'), filter(lambda s: s.strip() != '', text.split('\n')))
  return ''.join(lines)

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

@get('/')
async def index(request):
  summary = 'Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.'
  blogs = [
    Blog(id='1', name='Test Blog', summary=summary, created_at=time.time() - 120),
    Blog(id='2', name='Something New', summary=summary, created_at=time.time() - 3600),
    Blog(id='3', name='Learn Swift', summary=summary, created_at=time.time() - 7200)
  ]
  return {
    '__template__': 'blogs.html',
    'blogs': blogs,
    '__user__' : request.__user__
  }

@get('/blog/{id}')
async def get_blog(id):
  blog = await Blog.find(id)
  comments = await Comment.findAll('blog_id=?', [id], orderBy='created_at desc')
  for c in comments:
    c.html_content = text2html(c.content)
  blog.html_content = markdown2.markdown(blog.content)
  return {
    '__template__' : 'blog.html',
    'blog' : blog,
    'comments' : comments
  }

@get('/api/users')
async def api_get_users():
  users = await User.findAll()
  for u in users:
    u.passwd = '******'
  return dict(users=users)

@get('/register')
async def register():
  return {
    '__template__' : 'register.html'
  }

@get('/signin')
async def signin():
  return {
    '__template__' : 'signin.html'
  }

@get('/manage/blogs/create')
async def manage_create_blog():
  return  {
    '__template__' : 'blog_edit.html',
    'id' : '',
    'action' : '/api/blogs'
  }

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
      image='http://www.gravatar.com/avatar/%s?d=mm&s=120' % hashlib.md5(email.encode('utf-8')).hexdigest())
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

@get('/api/blogs/{id}')
async def api_get_blog(*, id):
  blog = await Blog.find(id)
  return blog

@post('/api/blogs')
async def api_create_blog(request, *, name, summary, content):
  if not name or not name.strip():
    raise APIValueError('name', 'name cannot be empty')
  if not summary or not summary.strip():
    raise APIValueError('summary', 'summary cannot be empty')
  if not content or not content.strip():
    raise APIValueError('content', 'content cannot be empty')
  blog = Blog(user_id = request.__user__.id, user_name = request.__user__.name, 
  user_image = request.__user__.image, name = name.strip(), summary = summary.strip(), 
  content = content.strip())
  await blog.save()
  return blog

handler_list = [index, api_get_users, register, signin, 
                api_register_user, authenticate, api_create_blog,
                manage_create_blog, get_blog
              ]