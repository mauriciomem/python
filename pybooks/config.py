import os


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'SuperPassword'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_PERMANENT = False
    SESSION_TYPE = "filesystem"
    GOODREADS_URL_STATS = 'https://www.goodreads.com/book/review_counts.json'
    GOODREADS_URL_BOOKS = 'https://www.goodreads.com/book/show/'
    GOODREADS_URL_BISBN = 'https://www.goodreads.com/book/isbn/'
    GOODREADS_KEY = '0WhYx9PI8XGqI4v69vDPTw'
    GOODREADS_SECRET = os.environ.get('GOODREADS_SECRET')

