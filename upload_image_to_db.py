import base64
from sql.sql import SQL
from sql.models import User





with open("default.png", "rb") as file: photo = file.read()


photo = base64.b64encode(photo)
print(photo.decode())

#with open("default.jpeg", "wb") as file : file.write(photo)