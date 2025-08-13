import sqlite3
import logging
from typing import List

from models import Comment, Message, User


class Database:

    def __init__(self, db_name: str = 'chat_data.db') -> None:
        conn = None
        try:
            conn = sqlite3.connect(db_name)
        except sqlite3.Error as err:
            logging.error('ошибка подключения к базе данных', err)

        self.conn = conn

    def create_tables(self) -> None:
        try:
            cursor = self.conn.cursor()
            logging.info('подключение к базе данных установлено')
            create_users_table = (
                'CREATE TABLE IF NOT EXISTS users ('
                'user_id INTEGER PRIMARY KEY AUTOINCREMENT,'
                'login TEXT NOT NULL UNIQUE,'
                'password TEXT NOT NULL);')
            create_chats_table = (
                'CREATE TABLE IF NOT EXISTS chats ('
                'chat_id INTEGER PRIMARY KEY AUTOINCREMENT,'
                'name TEXT);')
            create_messages_table = (
                'CREATE TABLE IF NOT EXISTS messages ('
                'message_id INTEGER PRIMARY KEY AUTOINCREMENT,'
                'text TEXT NOT NULL,'
                'date_created timestamp,'
                'author INT NOT NULL,'
                'chat INT NOT NULL,'
                'FOREIGN KEY(author) REFERENCES users(user_id),'
                'FOREIGN KEY(chat) REFERENCES chats(chat_id));')
            create_common_messages_table = (
                'CREATE TABLE IF NOT EXISTS common_messages ('
                'message_id INTEGER PRIMARY KEY AUTOINCREMENT,'
                'text TEXT NOT NULL,'
                'date_created timestamp,'
                'author INT NOT NULL,'
                'FOREIGN KEY(author) REFERENCES users(user_id));')
            create_dialogues_table = (
                'CREATE TABLE IF NOT EXISTS dialogues ('
                'dialogue_id INTEGER PRIMARY KEY AUTOINCREMENT,'
                'user1 INTEGER,'
                'user2 INTEGER,'
                'FOREIGN KEY(user1) REFERENCES users(user_id),'
                'FOREIGN KEY(user2) REFERENCES users(user_id));')
            create_comments_table = (
                'CREATE TABLE IF NOT EXISTS comments ('
                'comment_id INTEGER PRIMARY KEY AUTOINCREMENT,'
                'text TEXT,'
                'date_created timestamp,'
                'author INT NOT NULL,'
                'message INT NOT NULL,'
                'FOREIGN KEY(author) REFERENCES users(user_id),'
                'FOREIGN KEY(message) '
                'REFERENCES common_messages(message_id));')
            cursor.execute(create_users_table)
            cursor.execute(create_chats_table)
            cursor.execute(create_messages_table)
            cursor.execute(create_common_messages_table)
            cursor.execute(create_dialogues_table)
            cursor.execute(create_comments_table)
            self.conn.commit()
        except sqlite3.Error as err:
            logging.info('ошибка при подключении к базе данных', err)

    def create_user(self, user: User) -> int:
        insert_user = ('INSERT INTO users(login, password) '
                       'VALUES(:login, :password);')
        cursor = self.conn.cursor()
        try:
            cursor.execute(insert_user,
                           {'login': user.login, 'password': user.password})
            self.conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            logging.info('пользователь уже создан')

    def get_user_for_login(self, user: User) -> bool:
        select_user = ('SELECT login, password FROM users '
                       'WHERE login = :login AND password = :password;')
        cursor = self.conn.cursor()
        cursor.execute(select_user, {'login': user.login,
                                     'password': user.password})
        row = cursor.fetchone()
        if row is None:
            return False
        return True

    def get_user(self, login: str) -> int:
        select_user_id = 'SELECT user_id FROM users WHERE login = :login;'
        cursor = self.conn.cursor()
        cursor.execute(select_user_id, {'login': login})
        row = cursor.fetchone()[0]
        return row

    def create_chat(self, name: str) -> None:
        create_chat = 'INSERT INTO chats(name) VALUES(:name);'
        cursor = self.conn.cursor()
        cursor.execute(create_chat, {'name': name})
        self.conn.commit()

    def create_common_message(self, message: Message):
        create_common_message = (
            'INSERT INTO common_messages(text, date_created, author) '
            'VALUES(:text, :date_created, :author);')
        cursor = self.conn.cursor()
        try:
            cursor.execute(create_common_message, {
                'text': message.text,
                'date_created': message.date_created,
                'author': message.author})
            self.conn.commit()
        except sqlite3.IntegrityError as err:
            logging.info('ошибка при сохранении сообщения', err)

    def get_common_messages(self) -> List:
        select_messages = 'SELECT text, author, date_created ' \
                          'FROM common_messages;'
        cursor = self.conn.cursor()
        cursor.execute(select_messages)
        rows = cursor.fetchall()
        return rows

    def get_common_n_messages(self, limit: int = 20) -> List:
        select_n_messages = ('SELECT text, author, date_created '
                             'FROM common_messages'
                             'ORDER BY date_created DESC'
                             'LIMIT :limit;')
        cursor = self.conn.cursor()
        try:
            cursor.execute(select_n_messages, {'limit': limit})
            rows = cursor.fetchall()
        except sqlite3.OperationalError as err:
            logging.info('ошибка при получении сообщений', err)
            return []
        return rows

    def get_dialogue(self, user1: int, user2: int) -> bool:
        select_dialogue = ('SELECT dialogue_id FROM dialogues'
                           'WHERE (user1 = :user1 AND user2 = :user2)'
                           'OR (user1 = :user2 AND user2 = :user1);')
        cursor = self.conn.cursor()
        row = None
        try:
            cursor.execute(select_dialogue, {'user1': user1, 'user2': user2})
            row = cursor.fetchone()
        except sqlite3.OperationalError as err:
            logging.info('ошибка при получении диалога', err)
        if row is None:
            return False
        return True

    def create_dialogue(self, user1: int, user2: int):
        create_dialogue = ('INSERT INTO dialogues(user1, user2) '
                           'VALUES(:user1, :user2);')
        cursor = self.conn.cursor()
        cursor.execute(create_dialogue, {'user1': user1, 'user2': user2})
        self.conn.commit()

    def get_dialogue_messages(self, dialogue: int):
        select_messages = ('SELECT text, author, date_created '
                           'FROM messages WHERE chat = :dialogue')
        cursor = self.conn.cursor()
        cursor.execute(select_messages, {'dialogue': dialogue})
        rows = cursor.fetchall()
        return rows

    def create_dialogue_message(self, message: Message):
        create_dialogue_message = (
            'INSERT INTO messages(text, date_created, author, chat'
            'VALUES(:text, :date_created, :author, :chat')
        cursor = self.conn.cursor()
        cursor.execute(create_dialogue_message, {
            'text': message.text,
            'date_created': message.date_created,
            'author': message.author,
            'chat': message.chat})
        self.conn.commit()

    def get_user_dialogues(self, user: int) -> List:
        select_user_dialogues = 'SELECT dialogue_id FROM dialogues ' \
                                'WHERE user1 = :user OR user2 = :user;'
        cursor = self.conn.cursor()
        cursor.execute(select_user_dialogues, {'user': user})
        rows = cursor.fetchall()
        return rows

    def get_comments(self, message: int) -> List:
        select_message_comments = ('SELECT text, date_created, author '
                                   'FROM comments '
                                   'WHERE message = :message;')
        cursor = self.conn.cursor()
        cursor.execute(select_message_comments, {'message': message})
        rows = cursor.fetchall()
        return rows

    def create_comment(self, comment: Comment):
        create_comment = ('INSERT INTO comments('
                          'text, date_created, author, message) '
                          'VALUES(:text, :date_created, :author, :message);')
        cursor = self.conn.cursor()
        cursor.execute(create_comment, {'text': comment.text,
                                        'date_created': comment.date_created,
                                        'author': comment.author,
                                        'message': comment.message})
        self.conn.commit()
