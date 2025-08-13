from aiohttp import web
from aiohttp_session import get_session


async def authorize(app, handler):
    async def middleware(request):
        rurl = request.rel_url
        if str(rurl) in ('/register', '/login', '/api/doc/swagger.json',
                         '/api/doc'):
            return await handler(request)
        session = await get_session(request)
        if session.get('user'):
            return await handler(request)
        url = 'http://0.0.0.0:8080/login'
        raise web.HTTPFound(url)
        return handler(request)

    return middleware
