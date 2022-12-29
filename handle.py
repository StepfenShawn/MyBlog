from handles.users import *
from handles.blogs import *
from handles.comments import *


handler_list = [index, api_get_users, register, signin, signout,
                api_register_user, authenticate, get_user, api_create_blog,
                manage_create_blog, manage_edit_blog, get_blog, manage_blogs, api_blogs,
                api_delate_blog, api_create_comment, api_get_blog, api_edit_blog
              ]