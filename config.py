import os

class Development():
    DEBUG = True
    #MONGO_DATABASE_SERVER = os.environ.get('DEV_DATABASE_SERVER') or 'localhost'
    MONGO_DATABASE_SERVER = os.environ.get('DEV_DATABASE_SERVER') or '118.107.88.35'
    MONGO_DATABASE_PORT = os.environ.get('DEV_DATABASE_PORT') or 27017
    MONGO_DATABASE_NAME = os.environ.get('DEV_DATABASE_NAME') or 'DEV_BLANKSPIDER'

class Production():
    DEBUG = False
    #MONGO_DATABASE_SERVER = os.environ.get('PROD_DATABASE_SERVER') or 'localhost'
    MONGO_DATABASE_SERVER = os.environ.get('PROD_DATABASE_SERVER') or '118.107.88.35'
    MONGO_DATABASE_PORT = os.environ.get('PROD_DATABASE_PORT') or 27017
    MONGO_DATABASE_NAME = os.environ.get('PROD_DATABASE_NAME') or 'BLANKSPIDER'


config = {
    'development': Development,
    'production': Production,
    'default': Development
}