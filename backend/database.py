import certifi
from pymongo import MongoClient
from pymongo.errors import PyMongoError

from config import Config


client = None
database = None


def connect_database():
    global client, database

    if not Config.MONGODB_URI:
        raise ValueError("MONGODB_URI is missing from the .env file")

    client = MongoClient(
        Config.MONGODB_URI,
        tls=True,
        tlsCAFile=certifi.where(),
        serverSelectionTimeoutMS=10000,
        connectTimeoutMS=10000,
    )

    client.admin.command("ping")
    database = client[Config.DATABASE_NAME]

    return database


def get_database():
    if database is None:
        return connect_database()

    return database


def check_database_connection():
    try:
        connect_database()
        return True, "MongoDB Atlas connection successful"
    except (PyMongoError, ValueError) as error:
        return False, str(error)