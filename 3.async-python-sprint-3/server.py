from aiohttp import web

from router import Router
from settings import settings


class Server:
    def __init__(self, host=settings.host, port=settings.port):
        self.host = host
        self.port = port
        self.router = Router()
        self.app = self.router.create_router()

    def listen(self):
        pass

    def run(self):
        self.router.db.create_tables()
        web.run_app(self.app)
