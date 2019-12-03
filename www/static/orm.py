#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio, logging

import aiomysql

# 日志输出函数
def log(sql, args=()):
    logging.info('SQL: %s' % sql)

# 建立一个异步io的连接池
async def creat_pool(loop, **kw):
    # 打印日志, **kw为字典
    logging.info('create database connection pool...')
    # 全局变量
    global __pool
    # 创建的方法就是 aiomysql.create_pool,同时调用了字典的get方法
    __pool = await aiomysql.create_pool(
        host=kw.get('host', 'localhost'),
        port=kw.get('port', 3306),
        user=kw['user'],
        password=kw['password'],
        db=kw['db'],
        charset=kw.get('charset', 'utf-8'),
        autocommit=kw.get('autocommit', True),
        maxsize=kw.get('maxsize', 10),
        minsize=kw.get('minsize', 1),
        loop=loop
    )

# 封装select函数
async def select(sql, args, size=None):
    log(sql)
    global __pool  # 获取全局连接池__pool
    async with __pool.get() as conn:  # 打开连接池，自带关闭功能的with
        async with conn.cursor(aiomysql.DictCursor) as cur:  # 创建游标，DictCursor的作用是使查询返回的结果为字典格式
            # 应该类似于cursor.execute('select * from user where id = %s', ('1',))需要一个参数
            await cur.execute(sql.replace('?', '%s'), args or ())  # 执行SQL语句，将SQL语句的'?'占位符替换成MySQL的'%s'占位符
            # 如果有传入size，则返回对应个数的结果，否则返回全部结果
            if size:
                rs = await cur.fetchmany(size)
            else:
                rs = await cur.fetchall()
        logging.info('rows returned: %s' % len(rs))
        return rs

# 封装insert、update和delete的execute函数
# cursor.execute('insert into user (id, name) values (%s, %s)', ['1', 'Michael'])
async def execute(sql, args, autocommit=True):
    log(sql)  # 日志记录
    async with __pool.get() as conn:  # 打开连接池
        if not autocommit:  # 如果autocommit为False, conn.begin()开始事务
            await conn.begin()
        try:  # 执行sql语句
            async with conn.cursor as cur:
                await cur.execute(sql.replace('?', '%s'), args)
                affected = cur.rowcount()  # 通过rowcount获得sql语句操作影响的行数
            if not autocommit:  # 如果autocommit为False, conn.begin()开始事务
                await conn.begin()
        except BaseException as e:  # 处理出错情况
            if not autocommit:
                await conn.roolback()  # 情况不对就回滚，类似电脑重启包治百病
            raise
        return affected

# insert into 表名[(字段1, ..., 字段n)] values(记录1, ..., 记录n);
# sql

# def fn(self, name='world'):
#     print('Hello, %s' % name)
#
# Hello = type('Hello', (object,), dict(hello=fn))
# Hello1 = type()
#
# class ListMetaclass(type):
#     def __new__(cls, name, bases, attrs):
#         attrs['add'] = lambda self, value: self.append(value)
#         return type.__new__(cls, name, bases, attrs)
#     def __new__():
#
# class Mylist(list, metaclass=ListMetaclass):
#     # class后面紧接着是类名，即Mylist，类名通常是大写开头的单词，紧接着是(object)，表示该类是从哪个类继承下来的，此处是list，因为只有list才成立self.append(value)
#     pass
#
# # 当我们传入关键字参数metaclass时，魔术就生效了，它指示Python解释器在创建MyList时，要通过ListMetaclass.__new__()来创建，在此，我们可以修改类的定义，比如，加上新的方法，然后，返回修改后的定义。
#
# h = Mylist()
# h.add(4)

def create_args_string(num):
    L = []
    for i in range(num):
        L.append('?')
    return ','.join(L)

# 定义Field类，用来保存表的字段名字， 列类型， 主键， 默认值
class Field(object):
    def __init__(self, name, column_type, primary_key, default):
        self.name = name
        self.column_type = column_type
        self.primary_key = primary_key
        self.default = default

    def __str__(self):
        # 实例所属类的名称， 列类型， 字段名字（maybe)
        return '<%s, %s, %s>' % (self.__class__.__name__, self.column_type, self.name)

# 定义数据库的五个存储类型：字符串，布尔， 整数，浮点数， text???
class StringField(Field):
    # 定义StringField实例时，按照自身的__init__方法设置参数，如ccdd = StringField('zhende1', True, '100', 'zhende2')
    # 它会自动给name, primary, default, dd1赋值，如果未赋值，则采用自动赋值为None, False, None, 'varchar(100)'
    # 接下来将name, primary, default, dd1代入父类的__init__方法
    # def __init__(self, name=None, column_type='varchar(100)', primary_key=False, default=None):
    #     super().__init__(name, column_type, primary_key, default)

    def __init__(self, name=None, primary_key=False, default=None, ddl='varchar(100)'):
        super().__init__(name, ddl, primary_key, default)

# 区别为字符串的类列型能变，如'varchar(100)'，而布尔， 整数，浮点数， text的列类型直接给定
# 且布尔、text不能作为主键，所以直接锁定，不让设置
class StringField(Field):

    def __init__(self, name=None, primary_key=False, default=None, ddl='varchar(100)'):
        super().__init__(name, ddl, primary_key, default)

class BooleanField(Field):

    def __init__(self, name=None, default=False):
        super().__init__(name, 'boolean', False, default)

class IntegerField(Field):

    def __init__(self, name=None, primary_key=False, default=0):
        super().__init__(name, 'bigint', primary_key, default)

class FloatField(Field):

    def __init__(self, name=None, primary_key=False, default=0.0):
        super().__init__(name, 'real', primary_key, default)

class TestField(Field):

    def __init__(self, name=None, default=None):
        super().__init__(name, 'text', False, default)


# 开始定义元类，直接生成sql语句中的SELECT, INSERT, UPDATE和DELETE语句:
# 实现在定义子类model时将元类中的方法定义完成，不必在model类的对象user时调用方法
class ModelMetaclass(type):

    def __new__(cls, name, bases, attrs):  # 四份参数依次为：当前准备创建的类的对象, 类的名字, 类继承的父类集合, 类的方法集合

        tableName = attrs.get('__table__', None) or name  # 表的名字，如果没有的话则取值为类名(name)
        logging.info('found model: %s (table: %s)' % (name, tableName))
        mappings = dict()  # 存储类和表的映射关系
        fields = []  # 保存主键外的属性名字 (如password)    Field类存储了表的字段名字， 列类型， 是否为主键， 默认值
        # 类方法的名字对应
        primaryKey = None
        # k为id, name, password, email   v为IntegerField   StringField等，但是此时未定义，如何出来的？？
        for k, v in attrs.items():
            if isinstance(v, Field):  # 判断类方法集合中是否是Field类
                logging.info('found mapping: %s ==> %s' % (k, v))
                mappings[k] = v  # 存储类方法名字和方法函数  # 存储k, v
                # 找到主键，当第一次找到主键时，primary_key被赋值，当再次出现主键，系统就报错一个表有且只能有一个主键
                if v.primary_key:
                    if primaryKey:  # 由于primaryKey初始定义为None，所以不执行该语句
                        raise NameError('Duplicate primary key for field: %s' % k)  # 一个表有且只能有一个主键
                    primaryKey = k  # 存储主键名字
                else:
                    fields.append(k)  # 保存主键外的列名字：如name, password, email
        # 暂时不知道如何解决，定义元类ModelMetaclass后接着定义Model类时，会执行元类的__new__方法，所以会直接执行下列语句，直接报错
        # if not primaryKey:  # 遍历完发现主键不存在也直接报错
        #     print('hello,这里错了')
        #     raise RuntimeError('Primary key not found.')
        for k in mappings.keys():
            # k, v已存储在字典mappings里。k为id, name, password, email   v为IntegerField   StringField等
            attrs.pop(k)  # 从类属性中删除Field属性，否则容易造成运行时发生错误，因为实例的属性会覆盖类的同名属性
        # 保存主键外的其它列名字为列表形式
        # 除主键外的其它列名字变成['repr(name)', 'repr(email)', 'repr(password)']这种格式
        escaped_fields = list(map(lambda f: 'repr(%s)' % f, fields))  # repr语法代入SQL语句不会报错

        # 定义类属性
        # getattr(attrs, '__mappings__')报错，所以得重新定义函数取得value值
        attrs['__mappings__'] = mappings  # 类属性1：保存属性和列的映射关系, 转存最开始的k, v
        # k为id, name, password, email  v为IntegerField   StringField等
        attrs['__table__'] = tableName  # 类属性2：存储表名字
        attrs['__primary_key__'] = primaryKey  # 类属性3：存储主键名，例如id
        attrs['__fields__'] = fields  # 类属性4：存储除主键外的列名字，例如name, email, password，它为list

        # 类属性5：存储sql select语句   例如select 字段名1,字段名2…… from 表名
        attrs['__select__'] = 'select repr(%s), %s from repr(%s)' % (primaryKey, ','.join(escaped_fields), tableName)
        # 'repr(id)'
        # 'repr(name),repr(email),repr(password)'
        # 'repr(table1)'
        # 形如： 'select repr(id), repr(name), repr(email), repr(password) from repr(table1)'

        # 类属性6
        attrs['__insert__'] = 'insert into repr(%s) (%s, repr(%s)) values (%s) ' % (tableName,
        ','.join(escaped_fields), primaryKey, create_args_string(len(escaped_fields) + 1))
        # 形如： 'insert into repr(table1) (repr(name), repr(email), repr(password), repr(id)) values (?,?,?,?,?)'
        # ？为占位符

        # 类属性7   sql = "UPDATE customers SET address = 'Canyon 123' WHERE address = 'Valley 345'"
        attrs['__update__'] = 'update repr(%s) set %s where repr(%s)=?' % (tableName,
        ','.join(map(lambda f: 'repr(%s)=?' % (mappings.get(f).name or f), fields)), primaryKey)
        # mappings.get(f)用来获得field的属性，
        # mappings.get(f).name可以实现如下功能：获得列名字email对应的StringField类里面定义的name, 一般仍为email
        # 形如： 'update repr(table1) set repr(name)=?,repr(email)=?,repr(password)=? where repr(id)=?'

        # 类属性8
        attrs['__delete__'] = 'delete from repr(%s) where repr(%s)=?' % (tableName, primaryKey)
        # 形如： 'delete from repr(table1) where repr(id)=?'

        return type.__new__(cls, name, bases, attrs)


class Model(dict, metaclass=ModelMetaclass):

    def __init__(self, **kw):
        super(Model, self).__init__(**kw)

    # 通过__getattr__和__serattr__可以实现“.”调用
    # 以下key一般为id, name, email, password
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(r"'Model' object has no attribute '%s'" % key)

    # object.__setattr__(self, name, value)
    def __setattr__(self, key, value):
        self[key] = value

    def getValue(self, key):
        return getattr(self, key, None)  # 调用内置函数getattr       getattr(object, name, default)

    def getValueOrDefault(self, key):
        value = getattr(self, key, None)
        if value is None:
            field = self.__mappings__[key]
            if field.default is not None:
                # 如果field的default是一个方法，则value赋值为default()被调用后返回的值，如果不是方法的话，value赋值为default值本身
                # 举例：password的默认值可能是一个值，也可能是一个函数。如果默认值是值，则取这个值，如果是函数，就去调用它，取值为调用后返回的结果
                value = field.default() if callable(field.default) else field.default
                logging.debug('using default value for %s: %s' % (key, str(value)))
                setattr(self, key, value)  # 调用内置函数
        return value

    # 定义类方法，第一个参数为当前调用类名cls，而实例方法第一个参数为self
    @staticmethod
    async def findAll(cls, where=None, args=None, **kw):
        """find object by where clause."""
        sql = [cls.__select__]
        if where:
            # sql最终会等于 "select repr(id), repr(name), repr(email), repr(password) from repr(table1)where email ='xxx'"
            # ?  这里输入的参数是where=email=？ 这样的吗
            sql.append('where')
            sql.append(where)
        if args is None:
            args = []
        orderBy = kw.get('orderBy', None)  # 字典获取key 'orderBy'对应的value，如没有则返回None
        if orderBy:  # 如果非空
            sql.append('order by')
            sql.append(orderBy)
        limit = kw.get('limit', None)
        if limit is not None:  # 如果非空
            sql.append('limit')
            if isinstance(limit, int):  # limit m 表示取前m条记录
                sql.append('?')
                args.append(limit)
            elif isinstance(limit, tuple) and len(limit) == 2:  # limit n,m 表示从第n条记录开始选择m条记录
                sql.append('?, ?')
                args.extend(limit)  # 将limit(此时是元组)扩充进args(列表)里
            else:  # 如果limit既不是整数，也不是元组，则报错“非法的限制值”
                raise ValueError('Invaild limit value: %s' % str(limit))
        rs = await select(' '.join(sql), args)  # select函数内执行了cursor.execute(sql, args)，rs为select找到的记录
        # 每条记录对应的类实例，**r是关键字参数，构成了一个cls类的列表
        return [cls(**r) for r in rs]

    # 类方法
    @classmethod
    async def findNumber(cls, selectField, where=None, args=None):
        """find number by select and where."""
        sql = ['select %s _num_ from repr(%s)' % (selectField, cls.__table__)]  # __table__类属性：存储表名字， _num_不知道有啥用
        if where:
            sql.append('where')
            sql.append(where)
        rs = await select(' '.join(sql), args, 1)  # select找一条记录
        if len(rs) == 0:
            return None
        return rs[0]['_num_']

    @classmethod
    async def find(cls, pk):
        """find object by primary key."""
        rs = await select('%s where repr(%s)=?' % (cls.__select__, cls.__primary_key__), [pk], 1)
        if len(rs) == 0:
            return None
        return cls(**rs[0])

    # 实例方法，参数为self, 即类实例
    async def save(self):
        args = list(map(self.getValueOrDefault, self.__fields__))
        args.append(self.getValueOrDefault(self.__primary_key__))  # __primary_key__存储主键名
        rows = await execute(self.__insert__, args)  # 调用了封装insert、update和delete的execute函数，执行了cursor.execute(sql, args)
        if rows != 1:
            logging.warning('failed to insert record: affected rows: %s' % rows)

    async def update(self):
        args = list(map(self.getValue, self.__fields__))  # __fields__存储除主键外的列名字
        args.appenf(self.getValue(self.__primary_key__))
        rows = await execute(self.__update__, args)
        if rows != 1:
            logging.warning('failed to update by primary key: affected rows: %s' % rows)

    async def remove(self):
        args = [self.getValue(self.__primary_key__)]
        rows = await execute(self.__delete__, args)
        if rows != 1:
            logging.warning('failed to remove by primary key: affected rows: %s' % rows)


if __name__ == '__main__':
    class User(Model):
        # 定义类的属性到列的映射：
        id = IntegerField('id', primary_key=True)
        name = StringField('username')
        email = StringField('email')
        password = StringField('password')

        # 创建一个实例：


    u = User(id=12345, name='peic', email='peic@python.org', password='password')
    print(u)
    # 保存到数据库：
    # await u.save()  # SyntaxError: 'await' outside function
    print(u)







