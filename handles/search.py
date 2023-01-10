from coroweb import get, post
from models import Blog
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
  rs = await Blog.find_use_like('content', content)
  return {
    'result_list' : rs,
    '__template__' : "search_result.html",
    '__user__' : request.__user__
  }