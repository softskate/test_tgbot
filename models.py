from datetime import datetime
from peewee import *


# Инициализация базы данных SQLite
db = SqliteDatabase('database.db')

# Определение моделей базы данных
class BaseModel(Model):
    class Meta:
        database = db

class User(BaseModel):
    user_id = IntegerField(primary_key=True)
    first_name = CharField()
    last_name = CharField(null=True)
    username = CharField(null=True)
    phone = CharField(null=True)
    next_step = CharField(null=True)
    language_code = CharField()
    last_activity = DateTimeField(default=datetime.now)

class Example(BaseModel):
    description = TextField()
    photo = CharField(null=True)

class ButtonStat(BaseModel):
    button_text = CharField()
    click_count = IntegerField(default=0)

db.create_tables(BaseModel.__subclasses__())
