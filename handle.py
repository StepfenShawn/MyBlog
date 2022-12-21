import re, time, json, hashlib, base64, asyncio
import logging
from coroweb import get, post
from models import User, Comment, Blog, next_id

@get('/')
async def index(request):
  users = await User.findAll()
  return {
    '__template__' : 'test.html',
    'users' : users
  }