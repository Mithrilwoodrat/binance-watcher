from peewee import *
import os
import datetime

CURDIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH =  os.path.join(CURDIR, 'binance.db')

# SQLite database using WAL journal mode and 64MB cache.
sqlite_db = SqliteDatabase(DB_PATH, pragmas={
    'journal_mode': 'wal',
    'cache_size': -1024 * 64})


class BaseModel(Model):
    """A base model that will use our Postgresql database"""
    class Meta:
        database = sqlite_db


class Announcement(BaseModel):
    id = AutoField()
    title = CharField()
    coin_name = CharField()
    announcement_time = BigIntegerField()
    found_coin = SmallIntegerField(default=0)
    created_at = TimeField(constraints=[SQL("DEFAULT CURRENT_TIMESTAMP")])
    updated_at = TimeField(constraints=[SQL("DEFAULT CURRENT_TIMESTAMP")])


sqlite_db.create_tables([Announcement])


def get_last_announcement():
    announcement = Announcement.select().where(Announcement.found_coin==1).order_by(Announcement.announcement_time.desc()).get()
    return announcement

print("title: {}, time:{}".format(get_last_announcement().title, datetime.datetime.fromtimestamp(int(get_last_announcement().announcement_time/1000))))