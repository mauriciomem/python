from app import db
from datetime import datetime
from sqlalchemy import cast, String, Integer, SmallInteger
from werkzeug.security import generate_password_hash, check_password_hash

class Books(db.Model):
    __tablename__ = "books"
    id = db.Column(db.Integer, primary_key=True)
    isbn = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String, nullable=False)
    author = db.Column(db.String, nullable=False)
    year = db.Column(db.SmallInteger, nullable=False)
    reviews = db.relationship("Reviews", backref="book", lazy=True)

    def search_book(self, search=None):
        """ Search book ISBN, Author, Title, Release Year from string"""
        return db.session.query(Books) \
            .filter( \
                (Books.author.like(f'%{search}%') | Books.title.like(f'%{search}%') | cast(Books.year, String).like(f'%{search}%') | cast(Books.isbn, String).like(f'%{search}%'))
                )
        # Search in routes.py
        '''
            search = Books.query.filter((Books.author.like(f'%{request.form.get("search")}%') | 
            Books.title.like(f'%{request.form.get("search")}%') | 
            cast(Books.year, String).like(f'%{request.form.get("search")}%') | 
            cast(Books.isbn, String).like(f'%{request.form.get("search")}%')))
        '''

    def __repr__(self):
        return '<Books {}>'.format(self.title)

class Users(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False)
    name = db.Column(db.String, nullable=False)
    surname = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    passwd = db.Column(db.String, nullable=False)
    created = db.Column(db.DateTime, nullable=False)
    reviews = db.relationship("Reviews", backref="user", lazy=True)

    def set_passwd(self, password):
        self.passwd = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.passwd, password)

    def set_new_user(self, username, name, lastname, email, password, created=datetime.now()):
        """ Add new user """
        u = Users(username=username, name=name, surname=lastname, email=email, created=created)
        u.set_passwd(password=password)
        db.session.add(u)
        db.session.commit()
        return 'User successfully added!'

    def __repr__(self):
        return '<Users {}>'.format(self.name)

class Reviews(db.Model):
    __tablename__ = "reviews"
    id = db.Column(db.Integer, primary_key=True)
    score = db.Column(db.SmallInteger, nullable=True)
    review = db.Column(db.String, nullable=True)
    created = db.Column(db.DateTime, nullable=False)
    title = db.Column(db.String, nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey("books.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    def get_reviews(self, numbers=1, review_id=None):
        """ Get review list from lastest review, filter by review limit and/or review id."""
        if review_id:
            return db.session.query(Users.name, Users.surname, Books.title, Books.isbn, Reviews) \
            .filter(Reviews.user_id == Users.id) \
            .filter(Reviews.book_id == Books.id) \
            .filter(Reviews.id == review_id) \
            .order_by(Reviews.created.desc()) \
            .limit(numbers)    
        else:
            return db.session.query(Users.name, Users.surname, Books.title, Books.isbn, Reviews) \
            .filter(Reviews.user_id == Users.id) \
            .filter(Reviews.book_id == Books.id) \
            .order_by(Reviews.created.desc()) \
            .limit(numbers)

    def __repr__(self):
        return '<Review {}>'.format(self.review)