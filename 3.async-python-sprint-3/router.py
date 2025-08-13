from datetime import datetime
from http import HTTPStatus
from json.decoder import JSONDecodeError

from aiohttp import web
from aiohttp_session import session_middleware, get_session
from aiohttp_session.cookie_storage import EncryptedCookieStorage
from aiohttp_swagger import setup_swagger

from database import Database
from middleware import authorize
from models import Comment, Dialogue, Message, User


class Router:

    def __init__(self):
        self.db = Database()

    def create_router(self) -> web.Application:
        app = web.Application(middlewares=(
            session_middleware(
                EncryptedCookieStorage(b'Thirty  two  length  bytes  key.')
            ),
            authorize))
        app.add_routes([web.post('/register', self.register)])
        app.add_routes([web.post('/login', self.login)])
        app.add_routes([web.get(
            '/common/messages',
            self.get_common_chat_messages)])
        app.add_routes([web.post(
            '/common/messages',
            self.post_common_chat_message)])
        app.add_routes([web.get('/dialogues', self.get_dialogues)])
        app.add_routes([web.post('/dialogues', self.create_dialogue)])
        app.add_routes([web.get(
            '/dialogues/{id:.*}/messages',
            self.get_dialogue_messages)])
        app.add_routes([web.post('/dialogues/{id:.*}/messages',
                                 self.create_dialogue_message)])
        app.add_routes([web.get(
            '/dialogues/{id:.*}/messages/{id2:.*}/comments',
            self.get_comments)])
        app.add_routes([web.post(
            '/dialogues/{id:.*}/messages/{id2:.*}/comments',
            self.create_comment)])
        setup_swagger(app)
        return app

    async def login(self, request):
        try:
            data = await request.json()
            login = data.get('login', None)
            if login is None:
                raise web.HTTPBadRequest
            password = data.get('password', None)
            if password is None:
                raise web.HTTPBadRequest
            user = User(login, password)
            if self.db.get_user_for_login(user):
                session = await get_session(request)
                user_id = self.db.get_user(login)
                session['user'] = user_id
                return web.HTTPOk()
            return web.Response(text='Пользователь с такими данными не найден',
                                status=HTTPStatus.NOT_FOUND)
        except JSONDecodeError:
            return web.Response(text='Некорректный формат данных',
                                status=HTTPStatus.BAD_REQUEST)

    async def register(self, request):
        """
        ---
        description: Эндпоинт для регистрации пользователя.
        responses:
            "201":
                description: пользователь зарегистрирован
            "400":
                description: неправильный формат данных
        """
        data = await request.json()
        login = data.get('login', None)
        if login is None:
            return web.HTTPBadRequest()
        password = data.get('password', None)
        if password is None:
            return web.HTTPBadRequest()
        user = User(login, password)
        user_id = self.db.create_user(user)
        session = await get_session(request)
        session['user'] = user_id
        session['iwr'] = request.get_extra_info('peername')[1]
        return web.HTTPCreated()

    async def get_common_chat_messages(self, request):
        """
        ---
        description: "Эндпоинт для получения сообщений из общего чата".
        tags:
        - Health check
        produces:
        - application/json
        responses:
            "200":
                description: успешное получение сообщений из общего чата
        """
        session = await get_session(request)
        if session['iwr'] == request.get_extra_info('peername')[1]:
            self.db.get_common_n_messages()
        messages = self.db.get_common_messages()
        messages_list = [Message(message[0], message[1], message[2]).to_dict()
                         for message in messages]
        return web.json_response(messages_list)

    async def post_common_chat_message(self, request):
        """
        ---
        description: Эндпоинт для отправки сообщения в общий чат.
        produces:
        - application/json
        responses:
            "201":
                description: успешная отправка сообщения
            "400":
                description: неверный формат данных
        """
        session = await get_session(request)
        author_id = session.get('user')
        data = await request.json()
        text = data.get('message')
        if text is None:
            return web.Response(text='Сообщение не может быть пустым',
                                status=HTTPStatus.BAD_REQUEST)
        message = Message(text, datetime.now(), author_id, 1)
        self.db.create_common_message(message)
        return web.HTTPCreated()

    async def get_dialogues(self, request):
        """
        ---
        description: Эндпоинт для получения диалогов пользователя.
        produces:
        - application/json
        responses:
            "200":
                description: успешное получение списка диалогов
            "204":
                description: у пользователя нет диалогов
        """
        session = await get_session(request)
        user = session.get('user')
        dialogues = self.db.get_user_dialogues(user)
        if dialogues is None:
            return web.Response(text='Созданных диалогов нет',
                                status=HTTPStatus.NO_CONTENT)
        dialogue_list = [Dialogue(dialogue[1], dialogue[2])
                         for dialogue in dialogues]
        return web.json_response(dialogue_list)

    async def create_dialogue(self, request):
        """
        ---
        description: Эндпоинт для создания диалога с пользователем.
        responses:
            "201":
                description: диалог успешно создан
            "400":
                description: неверный формат данных
        """
        session = await get_session(request)
        user1 = session.get('user')
        data = await request.json()
        user2 = data.get('user_id')
        if user2 is None:
            return web.Response(text='Собеседник не выбран',
                                status=HTTPStatus.BAD_REQUEST)
        already_exists = self.db.get_dialogue(user1, user2)
        if already_exists:
            return web.HTTPOk()
        self.db.create_dialogue(user1, user2)
        return web.HTTPCreated()

    def get_dialogue_messages(self, request):
        """
        ---
        description: Эндпоинт для получения сообщений в диалоге.
        produces:
        - application/json
        responses:
            "200":
                description: успешное получение списка сообщений
            "400":
                description: неверный формат URL
        """
        dialogue_id_str = request.rel_url.parts[2]
        dialogue_id = 0
        try:
            dialogue_id = int(dialogue_id_str)
        except ValueError:
            return web.Response(text='Неверный формат URL',
                                status=HTTPStatus.BAD_REQUEST)
        messages = self.db.get_dialogue_messages(dialogue_id)
        messages_list = [Message(message[0], message[1], message[2]).to_dict()
                         for message in messages]
        return web.json_response(messages_list)

    async def create_dialogue_message(self, request):
        """
        ---
        description: Эндпоинт для отправки сообщения в диалоге.
        responses:
            "201":
                description: сообщение успешно отправлено
            "400":
                description: неверный формат URL
        """
        dialogue_id_str = request.rel_url.parts[2]
        dialogue_id = 0
        try:
            dialogue_id = int(dialogue_id_str)
        except ValueError:
            return web.Response(text='Неверный формат URL',
                                status=HTTPStatus.BAD_REQUEST)
        data = await request.json()
        text = data.get('message')
        if text is None:
            return web.Response(text='Сообщение не может быть пустым',
                                status=HTTPStatus.BAD_REQUEST)
        session = await get_session(request)
        user = session.get('user')
        date = datetime.now()
        message = Message(text, date, user, dialogue_id)
        self.db.create_dialogue_message(message)

    def get_comments(self, request):
        """
        ---
        description: Эндпоинт для получения окмментариев к сообщению.
        produces:
        - application/json
        responses:
            "200":
                description: успешное получение комментариев
            "400":
                description: неверный формат URL
        """
        dialogue_id, message_id = (request.rel_url.parts[2],
                                   request.rel_url.parts[4])
        try:
            dialogue_id = int(dialogue_id)
            message_id = int(message_id)
        except ValueError:
            return web.Response(text='Неверный формат URL',
                                status=HTTPStatus.BAD_REQUEST)
        comments = self.db.get_comments(message_id)
        if comments is None:
            return web.Response(text='У этого сообщения ещё нет комментариев',
                                status=HTTPStatus.NO_CONTENT)
        comments_list = [Comment(comment[0], comment[1], comment[2])
                         for comment in comments]
        return web.json_response(comments_list)

    async def create_comment(self, request):
        """
        ---
        description: Эндпоинт для отправки комментария
        responses:
            "201":
                description: успешная отправка комментария
            "400":
                description: неверный формат URL
        """
        dialogue_id, message_id = (request.rel_url.parts[2],
                                   request.rel_url.parts[4])
        try:
            dialogue_id = int(dialogue_id)
            message_id = int(message_id)
        except ValueError:
            return web.Response(text='Неверный формат URL',
                                status=HTTPStatus.BAD_REQUEST)
        data = await request.json()
        text = data.get('message')
        if text is None:
            return web.Response(text='Комментарий не может быть пустым',
                                status=HTTPStatus.BAD_REQUEST)
        session = await get_session(request)
        user = session.get('user')
        date = datetime.now()
        comment = Comment(text, date, user, message_id)
        self.db.create_comment(comment)
        return web.HTTPCreated()
