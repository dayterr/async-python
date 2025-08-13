class User:
    def __init__(self, login: str, password: str):
        self.login = login
        self.password = password


class Message:
    def __init__(self, text: str, date_created, author: int, chat: int = None):
        self.text = text
        self.date_created = date_created
        self.author = author
        self.chat = chat

    def to_dict(self) -> dict:
        dict = {'message': self.text, 'date_created': self.date_created,
                'author': self.author}
        if self.chat is not None:
            dict['chat'] = self.chat
        return dict


class Dialogue:
    def __init__(self, user1: int, user2: int):
        self.user1 = user1
        self.user2 = user2

    def to_dict(self) -> dict:
        dict = {'user1': self.user1, 'user2': self.user2}
        return dict


class Comment:
    def __init__(self, text: str, date_created, author: int,
                 message: int = None):
        self.text = text
        self.date_created = date_created
        self.author = author
        self.message = message

    def to_dict(self) -> dict:
        dict = {'text': self.text, 'date_created': self.date_created,
                'author': self.author}
        return dict
