"""
Web App将在9000端口监听HTTP请求，并且对首页/进行响应
"""
from aiohttp import web

async def index(request):
    return web.Response(text='awesome')

app = web.Application()
app.add_routes([web.get('/', index)])

if __name__ == "__main__":
    web.run_app(app, host='127.0.0.1', port=9090)