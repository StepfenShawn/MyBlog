import time, uuid
from orm import Model, StringField, BooleanField, FloatField, TextField, IntegerField, MediumBlobField 

def next_id():
  return '%015d%s000' % (int(time.time() * 1000), uuid.uuid4().hex)

class User(Model):
  __table__ = 'users'

  id = StringField(primary_key=True, default=next_id, ddl = 'varchar(50)')
  email = StringField(ddl='varchar(50)')
  passwd = StringField(ddl='varchar(50)')
  admin = BooleanField()
  name = StringField(ddl='varchar(50)')
  image = StringField(ddl='varchar(500)')
  created_at = FloatField(default=time.time)
  location = StringField(ddl='varchar(50)')

class PersonPhoto(Model):
  __table__ = 'preson_photoes'
  
  user_id = StringField(primary_key=True, default=next_id, ddl='vrchar(50)')
  image = MediumBlobField()

class Blog(Model):
  __table__ = 'blogs'

  id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
  user_id = StringField(ddl='varchar(50)')
  user_name = StringField(ddl='varchar(50)')
  user_image = StringField(ddl='varchar(500)')
  name = StringField(ddl='varchar(50)')
  summary = StringField(ddl='varchar(200)')
  content = TextField()
  created_at = FloatField(default=time.time)
  vistors = IntegerField(default=0)
  likes = IntegerField(default=0)

class Comment(Model):
  __table__ = 'comments'

  id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
  blog_id = StringField(ddl='varchar(50)')
  user_id = StringField(ddl='varchar(50)')
  user_name = StringField(ddl='varchar(50)')
  user_image = StringField(ddl='varchar(500)')
  content = TextField()
  created_at = FloatField(default=time.time)
  likes = IntegerField(default=0)

class Website(Model):
  __table__ = 'website'

  id = StringField(primary_key=True, default=next_id)
  vistors = IntegerField(default=0)