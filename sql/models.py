import json


class LibTypes:
    PRIVATE          = -1
    PUBLIC           =  1
    FAVORITES        =  2
    PUBLIC_FAVORITES =  3

class NotificationTypes:
    TITLES_RU = (
        "ашипка",
        "Новая запись! Автор: {author}",
        "Новая книга выложена! Автор: {author}",
        "Новая глава у {book}!",
        "У вас новый поклонник {lover}!",
        "Новый комментарий к {object}. Автор: {user}",
        "У вас новый завистник {user}!"
    )

    NEW_NOTE       =  1
    NEW_BOOK       =  2#
    NEW_CHAPTER    =  3#
    NEW_LOVER      =  4#
    NEW_COMMENTARY =  5##
    NEW_HATER      =  6#


class Model:
    @property
    def table(self):
        return self.__class__.__name__.lower()

    @property
    def values(self):
        return tuple(self.__dict__.values())

    @property
    def columns(self):
        return tuple(self.__dict__.keys())
    
    def json(self, *delete, **new):
        data = self.__dict__

        data.update(new)
        for d in delete:
            del data[d]

        return data


class Users(Model):
    id: str
    name: str
    surname: str
    description: str
    email: str
    photo: str
    password: str

    def __init__(self,
                 id="null",
                 name="null",
                 surname="null",
                 description="",
                 email="null",
                 photo="null",
                 password="null"):

        self.id          = id
        self.name        = name
        self.surname     = surname
        self.description = description
        self.email       = email
        self.photo       = photo
        self.password    = password

class Books(Model):
    id: str
    title: str
    user_id: str
    username: str
    tags: str
    raiting: str
    upload_date: str
    description: str

    def __init__(self,
                 id="null",
                 title="null",
                 user_id="null",
                 username="null",
                 tags="null",
                 raiting=0,
                 upload_date="null",
                 description="null"):
        self.id = id
        self.title = title
        self.user_id = user_id
        self.username = username
        self.tags = tags
        self.raiting = raiting
        self.upload_date = upload_date
        self.description = description

class Commentaries(Model):
    object_id: str
    user_id: str
    text: str
    likes: int
    raiting: int
    datetime: str

    def __init__(self,
                 object_id="null",
                 user_id="null",
                 text="null",
                 likes=0,
                 raiting=10,
                 datetime="null"):
        self.object_id = object_id
        self.user_id = user_id
        self.text = text
        self.likes = likes
        self.raiting = raiting
        self.datetime = datetime

class Libraries(Model):
    id: str
    type: int
    title: str
    user_id: str

    def __init__(self,
                 id="null",
                 type=LibTypes.PRIVATE,
                 user_id="null"):
        self.id = id
        self.type = type
        self.user_id = user_id

class Notes(Model):
    id: str
    user_id: str
    text: str
    authorname: str
    upload_date: str

    def __init__(self,
                 id="null",
                 user_id="null",
                 text="null",
                 authorname="null",
                 datetime="12.12.2000, 00:00"):
        self.id = id
        self.user_id = user_id
        self.text = text
        self.authorname = authorname
        self.datetime = datetime

class Tokens(Model):
    user_id: str
    token: str

    def __init__(self,
                 user_id="null",
                 token="null"):

        self.user_id = user_id
        self.token   = token

class Love_authors(Model):
    user_id: str
    author_id: str

    def __init__(self,
                 user_id="null",
                 author_id="null"):
        self.author_id = author_id
        self.user_id = user_id

class Notifications(Model):
    user_id: str
    title: str
    text: str
    object_id: str
    object_type: int
    datetime: str
    author_name: str
    author_photo: str

    def __init__(self,
                 user_id="null",
                 title="null",
                 text="null",
                 object_id="null",
                 object_type=0,
                 datetime="12.12.2000, 00:00",
                 author_name="null",
                 author_photo="null"):
        self.user_id = user_id
        self.title = title
        self.text = text
        self.object_id = object_id
        self.object_type = object_type
        self.datetime = datetime
        self.author_name = author_name
        self.author_photo = author_photo

class Chapters(Model):
    book_id: str
    title: str
    text: str
    upload_date: str

    def __init__(self,
                 book_id="null",
                 title="null",
                 text="null",
                 upload_date="12.12.2000, 00:00"):
        self.book_id = book_id
        self.title = title
        self.text = text
        self.upload_date = upload_date

class Notifications_long(Model):
    def __init__(self, notification=None, author_id=None):
        if notification and author_id:
            self.__dict__ = notification.__dict__
            self.__dict__["user_id"] = author_id
