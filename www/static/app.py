# """
# Web App将在9000端口监听HTTP请求，并且对首页/进行响应
# """
# from aiohttp import web
#
# async def index(request):
#     return web.Response(text='awesome')
#
# app = web.Application()
# app.add_routes([web.get('/', index)])
#
# if __name__ == "__main__":
#     web.run_app(app, host='127.0.0.1', port=9090)
#

#!/usr/bin/env python3
# -*- coding: utf-8 -*-


'''
async web application.
'''

import logging; logging.basicConfig(level=logging.INFO)

import asyncio, os, json, time
from datetime import datetime

from aiohttp import web
from jinja2 import Environment, FileSystemLoader

import test_orm
from test_coroweb import add_routes, add_static

# def init_jinja2(app, **kw):
#     logging.info('init jinja2...')
#     options = dict(
#         autoescape = kw.get('autoescape', True),
#         block_start_string = kw.get('block_start_string', '{%'),
#         block_end_string = kw.get('block_end_string', '%}'),
#         variable_start_string = kw.get('variable_start_string', '{{'),
#         variable_end_string = kw.get('variable_end_string', '}}'),
#         auto_reload = kw.get('auto_reload', True)
#     )
#     path = kw.get('path', None)
#     if path is None:
#         path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
#     logging.info('set jinja2 template path: %s' % path)
#     env = Environment(loader=FileSystemLoader(path), **options)
#     filters = kw.get('filters', None)
#     if filters is not None:
#         for name, f in filters.items():
#             env.filters[name] = f
#     app['__templating__'] = env
#
# async def logger_factory(app, handler):
#     async def logger(request):
#         logging.info('Request: %s %s' % (request.method, request.path))
#         # await asyncio.sleep(0.3)
#         return (await handler(request))
#     return logger
#
# async def data_factory(app, handler):
#     async def parse_data(request):
#         if request.method == 'POST':
#             if request.content_type.startswith('application/json'):
#                 request.__data__ = await request.json()
#                 logging.info('request json: %s' % str(request.__data__))
#             elif request.content_type.startswith('application/x-www-form-urlencoded'):
#                 request.__data__ = await request.post()
#                 logging.info('request form: %s' % str(request.__data__))
#         return (await handler(request))
#     return parse_data
#
# async def response_factory(app, handler):
#     async def response(request):
#         logging.info('Response handler...')
#         r = await handler(request)
#         if isinstance(r, web.StreamResponse):
#             return r
#         if isinstance(r, bytes):
#             resp = web.Response(body=r)
#             resp.content_type = 'application/octet-stream'
#             return resp
#         if isinstance(r, str):
#             if r.startswith('redirect:'):
#                 return web.HTTPFound(r[9:])
#             resp = web.Response(body=r.encode('utf-8'))
#             resp.content_type = 'text/html;charset=utf-8'
#             return resp
#         if isinstance(r, dict):
#             template = r.get('__template__')
#             if template is None:
#                 resp = web.Response(body=json.dumps(r, ensure_ascii=False, default=lambda o: o.__dict__).encode('utf-8'))
#                 resp.content_type = 'application/json;charset=utf-8'   # 此处廖老师相比别人的多写了一句
#                 return resp
#             else:
#                 resp = web.Response(body=app['__templating__'].get_template(template).render(**r).encode('utf-8'))
#                 resp.content_type = 'text/html;charset=utf-8'
#                 return resp
#         if isinstance(r, int) and r >= 100 and r < 600:
#             return web.Response(r)
#         if isinstance(r, tuple) and len(r) == 2:
#             t, m = r
#             if isinstance(t, int) and t >= 100 and t < 600:
#                 return web.Response(t, str(m))
#         # default:
#         resp = web.Response(body=str(r).encode('utf-8'))
#         resp.content_type = 'text/plain;charset=utf-8'
#         return resp
#     return response
#
# def datetime_filter(t):
#     delta = int(time.time() - t)
#     if delta < 60:
#         return u'1分钟前'
#     if delta < 3600:
#         return u'%s分钟前' % (delta // 60)
#     if delta < 86400:
#         return u'%s小时前' % (delta // 3600)
#     if delta < 604800:
#         return u'%s天前' % (delta // 86400)
#     dt = datetime.fromtimestamp(t)
#     return u'%s年%s月%s日' % (dt.year, dt.month, dt.day)
#
# async def init(loop):
#     await test_orm.create_pool(loop=loop, host='127.0.0.1', port=3306, user='www', password='www', db='awesome')
#     app = web.Application(loop=loop, middlewares=[
#         logger_factory, response_factory
#     ])
#     init_jinja2(app, filters=dict(datetime=datetime_filter))
#     add_routes(app, 'handlers')
#     add_static(app)
#     srv = await loop.create_server(app.make_handler(), '127.0.0.1', 9000)
#     logging.info('server started at http://127.0.0.1:9000...')
#     return srv
#
# loop = asyncio.get_event_loop()
# loop.run_until_complete(init(loop))
# loop.run_forever()

# 初始化jinja2模板
def init_jinja2(app, **kw):
    logging.info('init jinja2...')
    print('kw is %s' % kw)
    # 对Environment类的参数options进行配置
    options = dict(
        # 字典的get()方法返回指定键的值，如果值不存在则返回默认值
        autoescape = kw.get('autoescape', True),
        # 代码块的开始、结束标志
        block_start_string = kw.get('block_start_string', '{%'),
        block_end_string = kw.get('block_end_string', '%}'),
        # 变量的开始、结束标志
        variable_start_string = kw.get('variable_start_string', '{{'),
        variable_end_string = kw.get('variable_end_string', '}}'),
        # 自动加载修改后的模板文件
        auto_reload = kw.get('auto_reload', True)
    )
    # 获取模板文件夹路径
    path = kw.get('path', None)
    if path is None:
        # 如果未指定的话，则找到当前运行.py文件的文件夹下的templates文件夹
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
    logging.info('set jinja2 template path: %s' % path)
    # Environment类是jinja2的核心类，用来保存配置、全局对象和模板文件的路径
    # FileSystemLoader类可以用来加载path路径的模板文件。先定义路径，后加载模板
    env = Environment(loader=FileSystemLoader(path), **options)  # 把字典option代入
    # 过滤器集合
    filters = kw.get('filters', None)
    if filters is not None:
        for name, f in filters.items():
            env.filters[name] = f
    # 至此，完成jinja2的初始化需要定义Environment类，需要定义模板加载器FileSystemLoader，过滤器以及option内的参数
    app['__templating__'] = env
    logging.info('finish initializing jinja2...')

# 一个记录URL日志的logger_middleware
async def logger_factory(app, handler):  # 协程，两个参数
    async def logger_middleware(request):
        logging.info('Request: %s %s' % (request.method, request.path))
        return await handler(request)
    return logger_middleware

# 一个存储数据的middleware
async def data_factory(app, handler):
    async def parse_data(request):
        if request.method == 'POST':
            if request.content_type.startswith('application/json'):
                request.__data__ = await request.json()
                logging.info('request json: %s' % str(request.__data__))
            elif request.content_type.startswith('application/x-www-form-urlencoded'):
                request.__data__ = await request.post()
                logging.info('request form: %s' % str(request.__data__))
        return await handler(request)
    return parse_data

# 函数返回值转化为'web.response'
async def response_factory(app, handler):
    async def response_middleware(request):
        logging.info('Response handler...')
        r = await handler(request)
        if isinstance(r, web.StreamResponse):
            return r
        if isinstance(r, bytes):
            resp = web.Response(body=r)
            resp.content_type = 'application/octet-stream'
            return resp
        if isinstance(r, str):
            if r.startswith('redirect:'):  # 重定向
                return web.HTTPFound(r[9:])  # 转入别的网站
            resp = web.Response(body=r.encode('utf-8'))
            resp.content_type = 'text/html;charset=utf-8'
            return resp
        if isinstance(r, dict):
            template = r.get('__template__')
            if template is None:
                resp = web.Response(body=json.dumps(r, ensure_ascii=False, default=lambda o: o.__dict__).encode('utf-8'))
                # https://docs.python.org/2/library/json.html#basic-usage
                resp.content_type = 'application/json;charset=utf-8'
                return resp
            else:  # jinja2模板
                resp = web.Response(body=app['__templating__'].get_template(template).render(**r).encode('utf-8'))
                resp.content_type = 'text/html;charset=utf-8'
                return resp
        if isinstance(r, int) and r >= 100 and r < 600:
             return web.Response(r)
        if isinstance(r, tuple) and len(r) == 2:
            t, m = r
            if isinstance(t, int) and t >= 100 and t < 600:
                 return web.Response(t, str(m))
        # 默认情况
        resp = web.Response(body=str(r).encode('utf-8'))
        resp.content_type = 'text/plain;charset=utf-8'
        return resp
    return response_middleware

def datetime_filter(t):
    delta = int(time.time() - t)
    if delta < 60:
        return u'1分钟前'
    if delta < 3600:
        return u'%s分钟前' % (delta // 60)  # 取整
    if delta < 86400:
        return u'%s小时前' % (delta // 3600)
    if delta < 604800:
        return u'%s天前' % (delta // 86400)
    dt = datetime.fromtimestamp(t)  # 将时间戳转换为datetime
    return u'%s年%s月%s日' % (dt.year, dt.month, dt.day)

async def init(loop):
    # await test_orm.create_pool(loop=loop, host='127.0.0.1', port=3306, user='www', password='www', db='awesome')
    await test_orm.create_pool(loop=loop, host='127.0.0.1', port=3306, user='root', password='uu888888', db='awesome')
    # 下条语句报错，提示loop参数被弃用
    # app = web.Application(loop=loop, middlewares=[logger_factory, response_factory])
    # 改成
    app = web.Application(middlewares=[logger_factory, response_factory])
    init_jinja2(app, filters=dict(datetime=datetime_filter),
                path=r'D:\python_project\awesome-python3-webapp\www\templates')
    # init_jinja2(app, filters=dict(datetime=datetime_filter))  # 不设置路径的话，默认路径是当前.py文件的文件夹下的template文件夹
    print('app is %s ' % app)
    add_routes(app, 'test_handlers')
    add_static(app)
    # 下条语句报错，提示make_handler()被弃用
    # srv = await loop.create_server(app.make_handler(), '127.0.0.1', 9000)
    # logging.info('Server started at http://127.0.0.1:9000...')
    # return srv
    # 改成
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '127.0.0.1', 9000)
    await site.start()
    logging.info('Server started at http://127.0.0.1:9000...')


loop = asyncio.get_event_loop()
loop.run_until_complete(init(loop))
loop.run_forever()


