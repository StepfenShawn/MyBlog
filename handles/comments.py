from coroweb import get, post
from models import User, Comment, Blog
from errors import *
from aiohttp import web
from .page import Page, get_page_index

@get('/api/comments')
async def api_comments(*, page = '1'):
  page_index = get_page_index(page)
  num = Comment.findNumber('count(id)')
  p = Page(num, page_index)
  if num == 0:
    return dict(page = p, comments = ())
  comments = await Comment.findAll(orderBy = 'created_at desc', limit=(p.offset, p.limit))
  return dict(page=p, comments=comments)

@post('/api/blogs/{id}/comments')
async def api_create_comment(id, request, *, content):
  user = request.__user__
  if not content or not content.strip():
      raise APIValueError('content')
  blog = await Blog.find(id)
  comment = Comment(blog_id=blog.id, user_id=user.id, user_name=user.name, user_image=user.image, content=content.strip())
  await comment.save()
  return comment