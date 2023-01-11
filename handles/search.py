from coroweb import get, post
from models import Blog, User, Comment
from aiohttp import web_request

@get('/api/search/{content}')
async def api_search_content(content, request : web_request.Request):
  rs = await Blog.find_use_like('content', content)
  return {
    'result_list' : rs,
    '__user__' : request.__user__
  }

@get('/search/{content}')
async def search_content(content, request : web_request.Request):
  blog_rs = await Blog.find_use_like('content', content)
  user_rs = await User.find_use_like('name', content)
  comment_rs = await Comment.find_use_like('content', content)
  return {
    'blog_rs' : blog_rs,
    'user_rs' : user_rs,
    'comment_rs' : comment_rs,
    '__template__' : "search_result.html",
    '__user__' : request.__user__,
    'content' : content
  }