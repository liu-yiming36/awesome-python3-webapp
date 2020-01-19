# 完整检查了
import asyncio, os, inspect, logging, functools
from urllib import parse
from aiohttp import web
# from apis import APIError

# 装饰器功能：这样，一个函数通过@get()的装饰就附带了URL信息。
def get(path):
    """
    Define decorator @get('/path')
    """
    def decorator(func):
        logging.info('@get init')
        @functools.wraps(func)  # 用来保留被装饰函数的元信息，如注释、名字
        # 拓展的函数参数未定
        def wrapper(*args, **kw):
            return func(*args, **kw)
        wrapper.__method__ = 'GET'
        wrapper.__route__ = path
        logging.info('@get finish')
        return wrapper
    return decorator

# 这样，一个函数通过@post()的装饰就附带了URL信息。
def post(path):
    """
    Define decorator @post('/path')
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kw):
            return func(*args, **kw)
        wrapper.__method__ = 'POST'
        wrapper.__route__ = path
        return wrapper
    return decorator

# 处理url信息,获得无默认值的命名关键字参数的名字
def get_required_kw_args(fn):
    logging.info('get_required_kw_args init')
    args = []
    params = inspect.signature(fn).parameters  # 获取类或函数的参数的信息, 值为一个有序字典
    for name, param in params.items():
        # 如果param是关键字参数，且无默认值，则
        if param.kind == inspect.Parameter.KEYWORD_ONLY and param.default == inspect.Parameter.empty:
            args.append(name)
    logging.info('get_required_kw_args finish')
    return tuple(args)

# 处理url信息，获得命名关键字参数的名字
def get_named_kw_args(fn):
    logging.info('get_named_kw_args init')
    args = []
    params = inspect.signature(fn).parameters
    for name, param in params.items():
        if param.kind == inspect.Parameter.KEYWORD_ONLY:
            args.append(name)
    logging.info('get_named_kw_args finish')
    return tuple(args)

# 判断是否有命名关键字参数
def has_named_kw_args(fn):
    logging.info('has_named_kw_args init')
    params = inspect.signature(fn).parameters
    for name, param in params.items():
        logging.info('has_named_kw_args finish')
        if param.kind == inspect.Parameter.KEYWORD_ONLY:
            return True

# 判断是否有可变关键字参数: 即**kwargs 参数
def has_var_kw_arg(fn):
    logging.info('has_var_kw_arg init')
    params = inspect.signature(fn).parameters
    for name, param in params.items():
        logging.info('has_var_kw_arg finish')
        if param.kind == inspect.Parameter.VAR_KEYWORD:
            return True

# 寻找名字为request的参数，且该参数为最后一个参数，有则返回True，返回False
def has_request_arg(fn):
    logging.info('has_request_arg init')
    sig = inspect.signature(fn)
    params = sig.parameters
    found = False
    for name, param in params.items():
        if name == 'request':
            found = True
            continue
        # 不是VAR_POSITIONAL、KEYWORD_ONLY、VAR_KEYWORD
        if found and (param.kind != inspect.Parameter.VAR_POSITIONAL and param.kind != inspect.Parameter.KEYWORD_ONLY and param.kind != inspect.Parameter.VAR_KEYWORD):
            raise ValueError('request parameter must be the last named parameter in function: %s%s' % (fn.__name__, str(sig)))
    logging.info('has_request_arg finish')
    return found

# 封装一个URL处理函数,用来从url函数中分析其需要接收的参数，从request中获取必要的参数
# 调用url函数，然后把结果转换成web.response
# RequestHandler的主要作用就是构成标准的app.router.add_route第三个参数，还有就是获取不同的函数的对应的参数，
class RequestHandler(object):

    def __init__(self, app, fn):  #接受app参数
        logging.info('start RequestHandle...')
        # 没弄懂此处为什么arg有的加复数有的不加复数
        self._app = app
        self._func = fn
        self._has_request_arg = has_request_arg(fn)
        self._has_var_kw_arg = has_var_kw_arg(fn)
        self._has_named_kw_args = has_named_kw_args(fn)
        self._named_kw_args = get_named_kw_args(fn)
        self._required_kw_args = get_required_kw_args(fn)
        logging.info('finish RequestHandle...')

    async def __call__(self, request):  # day5未用到RequestHandle(request),所以以下未运行
        logging.info('start to call RequestHandle...')
        print('Request is %s' % request)
        kw = None
        # 如果包含可变关键字参数或者命名关键字参数或者无默认值的命名关键字参数，个人觉得第三个从属于第二个
        if self._has_var_kw_arg or self._has_named_kw_args or self._required_kw_args:
            if request.method == 'POST':  # 如果客户端发来的方法是POST
                if not request.content_type:  # 查询有无提交数据的格式（EncType)
                    return web.HTTPBadRequest(text='Missing Content Type')
                ct = request.content_type.lower()  # 将content type小写
                if ct.startswith('application/json'):  # 如果ct以字符串'application/json'开头
                    params = await request.json()  # Read request body decoded as json.
                    if not isinstance(params, dict):  # 如果param不是字典
                        return web.HTTPBadRequest(text='JSON body must be object.')
                    kw = params
                elif ct.startswith('application/x-www-form-urlencoded') or ct.startswith('multipart/form-data'):
                    params = await request.post()
                    kw = dict(**params)
                else:
                    return web.HTTPBadRequest('unsupported Content-Type: %s' % request.content_type)
            if request.method == 'GET':  # 如果客户端发来的方法是GET
                qs = request.query_string
                if qs:
                    kw = dict()
                    for k, v in parse.parse_qs(qs, True).items():  # parse.parse_qs解析url返回字典形式
                        # Parse a query string given as a string argument.Data are returned as a dictionary. The dictionary keys are the unique query variable names and the values are lists of values for each name
                        kw[k] = v[0]
        if kw is None:
            # request.match_info返回dict对象。可变路由中的可变字段{variable}为参数名，传入request请求的path为值
            # 若存在可变路由：/a/{name}/c，可匹配path为：/a/jack/c的request
            # 则request.match_info返回{name = jack}
            kw = dict(**request.match_info)
        else:
            if not self._has_var_kw_arg and self._named_kw_args:  # 当函数参数没有关键字参数时，移去request除命名关键字参数所有的参数信息
                # 将self._named_kw_args写成了self._has_named_kw_args，这两者有什么区别
                # 前者为逻辑值，后者为tuple，默认是空tuple，所以理论上效果是一样的
                # remove all unamed kw
                copy = dict()
                for name in self._named_kw_args:
                    if name in kw:
                        copy[name] = kw[name]
                kw = copy
            # check named arg
            for k, v in request.match_info.items():
                if k in kw:
                    logging.warning('Duplicate arg name in named arg and kw args: %s' % k)
                kw[k] = v
        if self._has_request_arg:
            kw['request'] = request
        # check required kw:
        if self._required_kw_args:  # 假如有无默认值的命名关键字参数
            for name in self._required_kw_args:
                if not name in kw:  # 但是request没有提供相应的数值，则报错
                    return web.HTTPBadRequest(text='Missing argument: %s' % name)
        logging.info('call with args: %s' % str(kw))
        try:
            r = await self._func(**kw)
            return r
        except APIError as e:
            return dict(error=e.error, data=e.data, message=e.message)
        logging.info('finish calling RequestHandler...')


# 添加静态文件夹路径
def add_static(app):
    # os.path.abspath(__file__)当前.py文件所在文件夹的绝对路径  os.path.dirname去掉文件名，返回目录
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
    app.router.add_static('/static/', path)
    logging.info('add static %s => %s' % ('/static/', path))

# 用来注册一个URL处理函数，主要起验证函数是否有包含URL的响应方法与路径信息，以及将函数变为协程。
def add_route(app, fn):
    logging.info('start to add_route...app is %s and fn is %s' % (app, fn))
    method = getattr(fn, '__method__', None)
    path = getattr(fn, '__route__', None)
    if path is None or method is None:
        raise ValueError('@get or @post not defined in %s.' % str(fn))
    if not asyncio.iscoroutinefunction(fn) and not inspect.isgeneratorfunction(fn):  # 判断是否是协程函数且是生成器函数
        fn = asyncio.coroutine(fn)
    logging.info('add route %s %s => %s(%s)' % (method, path, fn.__name__, ', '.join(inspect.signature(fn).parameters.keys())))
    print('app is %s and path is %s and fn is %s' % (method, path, fn))
    app.router.add_route(method, path, RequestHandler(app, fn))
    logging.info('finish add_route...')

# 批量注册：只需向这个函数提供要批量注册函数的文件路径，新编写的函数就会筛选，注册文件内所有符合注册条件的函数
# 自动把handle的所有符合条件的函数注册了
def add_routes(app, module_name):
    logging.info('start to add_routes...')
    print('app is %s and module_name is %s '% (app, module_name))
    n = module_name.rfind('.')  # 找到字符串中'.'最后一次出现的位置，无则返回-1
    if n == (-1):
        mod = __import__(module_name, globals(), locals())  # 用于动态加载类和函数
    else:
        name = module_name[n+1:]  # 字符串切片
        mod = getattr(__import__(module_name[:n], globals(), locals(), [name]), name)  # 导入名字为name（'.'后面的字符串）的子模块
    for attr in dir(mod):  # 模块中定义的名字列表
        if attr.startswith('_'):
            continue
        fn = getattr(mod, attr)
        if callable(fn):
            method = getattr(fn, '__method__', None)
            path = getattr(fn, '__route__', None)
            if method and path:
                add_route(app, fn)
    logging.info('finish add_routes...')







