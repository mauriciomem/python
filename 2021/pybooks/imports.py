import csv
import os

from flask import Flask
from app.models import *

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

def main():
    f = open('books.csv')
    read = csv.reader(f)
    for isbn, title, author, year in read:
        book = Books(isbn=isbn, title=title, author=author, year=year)
        db.session.add(book)
    print(f"Added info from book {title}.")
    db.session.commit()

if __name__ == "__main__":
    with app.app_context():
        main()
