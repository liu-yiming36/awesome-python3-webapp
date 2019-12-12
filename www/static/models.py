import time, uuid

from test_orm import Model, StringField, BooleanField, FloatField, TextField


def next_id():  # 检查了
    # time time() 返回当前时间的时间戳（1970纪元后经过的浮点秒数）
    # UUID: 通用唯一标识符 ( Universally Unique Identifier )
    # 通过随机数来生成UUID. 使用的是伪随机数有一定的重复概率.  .hex将uuid字符串中的 - 删除
    return '%015d%s000' % (int(time.time() * 1000), uuid.uuid4().hex)



# 存储用户信息
class User(Model):  # 检查了
    __table__ = 'users'

    id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
    email = StringField(ddl='varchar(50)')
    password = StringField(ddl='varchar(50)')   # 此处passwd改成了password
    admin = BooleanField()
    name = StringField(ddl='varchar(50)')
    image = StringField(ddl='varchar(500)')
    created_at = FloatField(default=time.time)

class Blog(Model):  # 检查了
    __table__ = 'blogs'

    id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
    user_id = StringField(ddl='varchar(50)')
    user_name = StringField(ddl='varchar(50)')
    user_image = StringField(ddl='varchar(500)')
    name = StringField(ddl='varchar(50)')
    summary = StringField(ddl='varchar(200)')
    content = TextField()
    created_at = FloatField(default=time.time)

class Comment(Model):  # 检查了
    __table__ = 'comments'

    id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
    blog_id = StringField(ddl='varchar(50)')
    user_id = StringField(ddl='varchar(50)')
    user_name = StringField(ddl='varchar(50)')
    user_image = StringField(ddl='varchar(500)')
    content = TextField()
    created_at = FloatField(default=time.time)

