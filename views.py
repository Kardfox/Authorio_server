#flask
from main import app
from flask import abort, request

#sql
from sql.sql import SQL
import pymysql
from sql.models import*

#date
import datetime
from time import time

#crypto
from hashlib import sha256
import base64
from werkzeug.security import generate_password_hash, check_password_hash

#json
import json

#threads
from threading import Thread


sql = SQL()

def generate_token(user_id, device):
    today = str(datetime.datetime.today())
    user = user_id
    
    hash = f"{today}-{user}-{device}".encode("utf-8")

    return sha256(hash).hexdigest()

def fnow():
    return "{:%d.%m.%Y, %H:%M}".format(datetime.datetime.now())

def generate_user_id():
    return str(time() % 1)[2:9]

def generate_object_id():
    return str(time() % 1)[2:12]

def encode_image(image):
    return base64.b64encode(image)

#===================================================== V I E W S =====================================================
#===================================================== N O T I F I C A T I O N S =====================================================
class MassNotification(Thread):
    def __init__(
            self,
            type,
            from_author,
            for_object,
            ru=True,
            text="",
            **format):
        super().__init__()

        self.type = type
        self.author = from_author
        self.object_id = for_object
        self.ru = ru
        self.text = text
        self.format = format

        self.run()
    
    def run(self):
        author_lovers = sql.select(Love_authors, author_id=self.author.id)

        for author_lover in author_lovers:
            add_notification(
                self.type,
                for_user=author_lover["user_id"],
                object_id=self.object_id,
                datetime=fnow(),
                author_name=f"{self.author.name} {self.author.surname}",
                author_photo=self.author.photo,
                ru=self.ru,
                text=self.text,
                author_id=self.author.id,
                **self.format
            )

def add_notification(_type,
                     for_user,
                     object_id,
                     author_name,
                     author_photo,
                     ru=True,
                     text="",
                     author_id=None,
                     **format):
    if ru:
        titles = NotificationTypes.TITLES_RU
    else:
        pass #TODO: сделать инглиш

    new_notification = Notifications(
                        user_id=for_user,
                        title = titles[_type].format(**format),
                        text=text,
                        object_id=object_id,
                        object_type=_type,
                        datetime=fnow(),
                        author_name=author_name,
                        author_photo=author_photo
    )

    sql.add(new_notification)

    if author_id:
        notification_long = Notifications_long(new_notification, author_id)

        try:
            sql.add(notification_long)
        except pymysql.err.IntegrityError: pass

@app.route("/notifications/long/get", methods=["POST"])
def get_notifications_long():
    """
        needs:
            author_id
    """
    try:
        author_id = request.get_json()["author_id"]

        notificaitons_long = sql.select(Notifications_long, user_id=author_id)

        return json.dumps(notificaitons_long), 200

    except Exception as ex:
        print(ex)

@app.route("/notifications/read/<token>", methods=["POST"])
def read_noification(token):
    """
        needs:
            token in url
        
        404 - token is dead /
    """
    try:
        token = sql.select_one(Tokens, token=token) or abort(404)
        user_id = token.user_id

        notifications = sql.select(Notifications, user_id=user_id)
        sql.delete(Notifications, user_id=user_id)

        return json.dumps(notifications), 200

    except Exception as ex:
        print(ex)


#===================================================== B O O K S =====================================================
@app.route("/books/add/<token>", methods=["POST"])
def add_book(token):
    """
        needs:
            token in url

            title /
            tags
        404 - token is dead
        400 - wrong json
    """
    try:
        data = request.get_json()

        token = sql.select_one(Tokens, token=token) or abort(404)
        author = sql.select_one(Users, id=token.user_id)

        data["id"] = generate_object_id()
        data["user_id"] = token.user_id
        data["upload_date"] = str(datetime.datetime.today())

        new_book = Books(**data)
        sql.add(new_book)

        MassNotification(
            NotificationTypes.NEW_BOOK,
            from_author=author,
            for_object=new_book.id,
            #format for title
            author=f"{author.name} {author.surname}"
        )

        return "", 200
    except KeyError as ex:
        abort(400)

@app.route("/books/get", methods=["POST"])
def get_books():
    """
        needs:
            params in json
        400 - worng json
    """
    try:
        data = request.get_json() or abort(400)

        users = sql.select(Users, sep=" OR ", comp="LIKE", **data)

        return json.dumps(users, default=str), 200

    except json.JSONDecodeError:
        abort(400)

#===================================================== C H A P T E R S =====================================================
@app.route("/books/chapters/add/<token>", methods=["POST"])
def add_chapter(token):
    """
        needs:
            token in url

            book_id /
            title /
            text
        404 - token is dead
        403 - access denided
        400 - wrong json
    """
    try:
        data = request.get_json() or abort(400)

        token = sql.select_one(Tokens, token=token) or abort(404)
        author = sql.select_one(Users, id=token.user_id)

        book = sql.select_one(Books, id=data["book_id"])

        if book.user_id == token.user_id:
            new_chapter = Chapters(book_id=book.id, title=data["title"], text=data["text"])
            sql.add(new_chapter)

            MassNotification(NotificationTypes.NEW_CHAPTER,
                            from_author=author,
                            for_object=book.id,
                            ru=True,
                            #format for title
                            book=f"{book.title}"
            )

            return "", 200
        else:
            abort(403)
    except Exception as ex:
        print(ex)

#===================================================== N O T E S =====================================================
@app.route("/notes/add/<token>", methods=["POST"])
def add_note(token):
    """
        needs:
            token in url

            text
        400 - JSON wrong
    """
    try:
        text = request.get_json()["text"]
        token = sql.select_one(Tokens, token=token) or abort(404)
        
        new_note = Notes(id=generate_object_id(), user_id=token.user_id, text=text, datetime=fnow())
        sql.add(new_note)

        author = sql.select_one(Users, id=token.user_id)

        MassNotification(
            NotificationTypes.NEW_NOTE,
            from_author=author,
            for_object=new_note.id,
            ru=True,
            text=text,
            #format for title
            author=f"{author.name} {author.surname}"
        )

        return "", 200
    except KeyError as ex:
        abort(400)


#===================================================== U S E R =====================================================
@app.route("/users/add/love_author/<token>", methods=["POST"])
def add_love_author(token):
    """
        needs:
            token in url /
            author_id
        
        404 - token is dead
    """
    try:
        token = sql.select_one(Tokens, token=token) or abort(404)
        user = sql.select_one(Users, id=token.user_id)

        author_id = request.get_json()["author_id"]

        new_lover = Love_authors(user_id=token.user_id, author_id=author_id)
        sql.add(new_lover)

        add_notification(
            NotificationTypes.NEW_LOVER,
            for_user=author_id,
            object_id=user.id,
            lover=user.name
        )

        return "", 200
    except Exception as ex:
        print(ex)

        return "", 500

@app.route("/users/delete/love_author/<token>", methods=["POST"])
def delete_love_authors(token):
    """
        needs:
            token in url /
            author_id
        
        404 - token is dead
    """
    try:
        token = sql.select_one(Tokens, token=token) or abort(404)
        author_id = request.get_json()["author_id"]

        sql.delete(Love_authors, user_id=token.user_id, author_id=author_id)

        return "", 200
    except Exception as ex:
        print(ex)

@app.route("/users/get/love_authors/<token>", methods=["POST"])
def get_love_authors(token):
    """
        needs:
            token in url /
            user id
        
        404 - token is dead
    """
    try:
        token = sql.select_one(Tokens, token=token) or abort(404)

        user_id = request.get_json()["user_id"]

        love_authors = [
            sql.select(Users, cols=("id", "name", "photo"), id=love_author["author_id"])
            for love_author in sql.select(Love_authors, cols=("author_id",), user_id=user_id)
        ]

        return json.dumps(love_authors[0]), 200

    except json.JSONDecodeError:
        abort(400)


@app.route("/users/get", methods=["POST"])
def get_user():
    """
        needs:
            user data in json
        
        400 - wrong json
    """
    try:
        data = request.get_json()

        users = sql.select(Users, sep=" OR ", comp="LIKE", **data)

        return json.dumps(users, default=str), 200

    except json.JSONDecodeError:
        abort(400)

@app.route("/user/change/<token>", methods=["POST"])
def change_user(token):
    """
        needs:
            token in URL /
            changes in json

        404 - token is dead /
        400 - wrong json
    """
    token = sql.select_one(Tokens, token=token) or abort(404)

    try:
        changes = request.get_json()
        if "password" in changes:
            abort(403)

        user = sql.select_one(Users, id=token.user_id)

        sql.update(user, **changes)

        return "", 200
    
    except json.JSONDecodeError:
        abort(400)

@app.route("/user/change_password/<token>", methods=["POST"])
def change_user_password(token):
    """
        needs:
            token in URL /
            old_password /
            new_password

        404 - token is dead /
        400 - passwords are the same or json wrong /
        403 - wrong password
    """
    token = sql.select_one(Tokens, token=token) or abort(404)

    try:
        data = request.get_json()
        data = json.loads(data)

        new_password = data["new_password"]
        old_password = data["old_password"]

        user = sql.select_one(Users, id=token.user_id)

        if check_password_hash(user.password, old_password):
            if check_password_hash(user.password, new_password):
                abort(400)

            sql.update(user, password=generate_password_hash(new_password, method="sha256"))

            return "", 200
        abort(403)
    
    except json.JSONDecodeError:
        abort(400)

@app.route("/user/delete/<token>", methods=["POST"])
def delete_user(token):
    """
        needs:
            token in URL /
            password
        
        404 - token is dead /
        403 - wrong password /
        400 - wrong json
    """
    db_token = sql.select_one(Tokens, token=token) or abort(404)

    try:
        user = sql.select_one(Users, id=db_token.user_id)

        password = request.get_json()["password"]

        if check_password_hash(user.password, password):
            sql.delete(Users, id=user.id)

            return "", 200
        abort(403)
    
    except (json.JSONDecodeError, KeyError):
        abort(400)

#===================================================== A U T H =====================================================
@app.route("/login", methods=["POST"])
def login():
    """
        neeeds:
            email /
            device /
            password
            
        404 - user not found /
        400 - wrong json /
        403 - wrong password /
    """
    new_login = request.get_json()

    try:
        user = sql.select_one(Users, email=new_login["email"]) or abort(404)

        if check_password_hash(user.password, new_login["password"]):

            new_token = generate_token(user.id, new_login["device"])
            token_values = {"user_id": user.id, "token": new_token}
            
            sql.add(Tokens(**token_values))

            return user.json("password", token=new_token), 200
        abort(403)

    except (json.JSONDecodeError, KeyError):
        abort(400)

@app.route("/signup", methods=["POST"])
def signup():
    """
        needs:
            name /
            surname /
            email /
            password /

        400 - wrong json /
        403 - email is exist
    """
    json_data = request.get_json()

    try:
        json_data["name"]
        json_data["surname"]

        new_user = Users(**json_data)

        new_user.id = generate_user_id()
        with open("default.png", "rb") as photo : photo = photo.read()
        new_user.photo = encode_image(photo).decode("utf-8")
        new_user.password = generate_password_hash(new_user.password, method="sha256")

        sql.add(new_user)

        return "", 200
    
    except (json.JSONDecodeError, KeyError):
        abort(400)
    
    except pymysql.err.IntegrityError:
        abort(403)

@app.route("/logout/<token>", methods=["GET"])
def logout(token):
    """
        needs:
            token in URL
        
        400 - wrong url /
        404 - token is dead
    """
    sql.select(Tokens, token=token) or abort(404)

    sql.delete(Tokens, token=token)

    return "", 200
