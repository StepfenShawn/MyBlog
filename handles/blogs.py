from coroweb import get, post
from models import Comment, Blog, Website
from errors import *
from aiohttp import web
from .page import Page, get_page_index
import markdown

def text2html(text):
  lines = map(lambda s: '<p>%s</p>' % s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'), filter(lambda s: s.strip() != '', text.split('\n')))
  return ''.join(lines)

@get('/')
async def index(request):
  blogs = await Blog.findAll()
  return {
    '__template__': 'blogs.html',
    'blogs': blogs,
    '__user__' : request.__user__
  }

@get('/blog/{id}')
async def get_blog(request, *, id):
  blog = await Blog.find(id)
  blog.vistors += 1
  await blog.update()
  comments = await Comment.findAll('blog_id=?', [id], orderBy='created_at desc')
  for c in comments:
    c.html_content = text2html(c.content)
  blog.html_content = markdown.markdown(blog.content, extensions=['markdown.extensions.codehilite', 
                        'markdown.extensions.fenced_code', 'markdown.extensions.tables'])
  return {
    '__template__' : 'blog_show.html',
    'blog' : blog,
    'comments' : comments,
    '__user__' : request.__user__
  }

@get('/manage/blogs')
async def manage_blogs(*, page = '1'):
  return {
    '__template__' : 'manage_blogs.html',
    'page_index' : get_page_index(page)
  }

@get('/manage/blogs/create')
async def manage_create_blog():
  return  {
    '__template__' : 'blog_edit.html',
    'id' : '',
    'action' : '/api/blogs'
  }

@get('/manage/blogs/edit/{id}')
async def manage_edit_blog(*, id):
  return {
    '__template__' : 'blog_edit.html',
    'id' : id,
    'action' : '/api/blogs'
  }

@get('/api/blogs/{id}')
async def api_get_blog(*, id):
  blog = await Blog.find(id)
  return blog

@get('/api/blogs')
async def api_blogs(*, page = '1'):
  page_index = get_page_index(page)
  # find the numbers of all blags
  num = await Blog.findNumber('count(id)')
  p = Page(num, page_index)
  if num == 0:
    return dict(page = p, blogs = ())
  blogs = await Blog.findAll(orderBy='created_at desc', limit=(p.offset, p.limit))
  return dict(page = p, blogs = blogs)

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

@post('/api/blogs/{id}/delete')
async def api_delate_blog(request, *, id):
  blog = await Blog.find(id)
  await blog.remove()
  return dict(id=id)

@post('/api/blogs/{id}/edit')
async def api_edit_blog(id, name, summary, content, request, **kw):
  blog = await Blog.find(id)
  blog.name = name
  blog.summary = summary
  blog.content = content
  await blog.update()
  return blog