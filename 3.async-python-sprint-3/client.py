import asyncio
import json
import logging

import aiohttp


class Client:
    def __init__(self, server_host="0.0.0.0", server_port=8080):
        self.url = f'http://{server_host}:{server_port}'
        self.cookie = None

    def send(self, message=""):
        pass

    async def register_user(self, session: aiohttp.ClientSession):
        login = input('введите логин: ')
        password = input('введите пароль: ')
        data = {'login': login, 'password': password}
        data = json.dumps(data)
        url = self.url + '/register'
        async with session.post(url, data=data) as resp:
            logging.info(resp.status)
            if resp.status == 201:
                self.cookie = resp.cookies

    async def login_user(self, session: aiohttp.ClientSession):
        login = input('введите логин: ')
        password = input('введите пароль: ')
        data = {'login': login, 'password': password}
        data = json.dumps(data)
        url = self.url + '/login'
        async with session.post(url, data=data) as resp:
            logging.info(resp.status)
            if resp.status == 200:
                self.cookie = resp.cookies

    async def get_common_chat(self, session: aiohttp.ClientSession):
        session.cookie_jar.update_cookies(self.cookie)
        url = self.url + '/common/messages'
        async with session.get(url) as resp:
            logging.info(await resp.text())

    async def create_dialogue(self, session: aiohttp.ClientSession):
        session.cookie_jar.update_cookies(self.cookie)
        url = self.url + '/dialogues'
        data = {'user_id': 1}
        data = json.dumps(data)
        async with session.post(url, data=data) as resp:
            logging.info(resp.status)

    async def create_dialogue_message(self, session: aiohttp.ClientSession):
        session.cookie_jar.update_cookies(self.cookie)
        url = self.url + '/dialogues/1/messages'
        data = {'message': 'message for a dialogue'}
        data = json.dumps(data)
        async with session.post(url, data=data) as resp:
            logging.info(resp.status)

    async def session(self):
        async with aiohttp.ClientSession() as session:
            await self.register_user(session)
            await self.get_common_chat(session)
            await self.create_dialogue(session)
            await self.create_dialogue_message(session)

    def run(self):
        asyncio.run(self.session())
