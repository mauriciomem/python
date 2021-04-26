from flask import render_template, redirect, url_for, request, session
from flask import current_app as app
from app import db, Config
from bs4 import BeautifulSoup as bs
from datetime import datetime
from app.forms import RegistrationForm, LoginForm
from app.models import Users, Books, Reviews
import csv, requests

@app.route("/index")
@app.route("/", methods=["GET"])
def index():
    """Home site. Latest reviews"""
    # Get last two reviews
    posts = Reviews().get_reviews(2)

    # Get latest reviews
    latests = Reviews().get_reviews(5)

    if 'username' in session:
        return render_template("index.html", title='Wellcome!', user=session['username'], posts=posts, latests=latests)
    
    # Default page
    return render_template("index.html", title='Wellcome!', posts=posts, latests=latests)

@app.route("/login", methods=["GET", "POST"])
def login():
    """Login signed user"""
    # Form validation Class
    auth = LoginForm()

    if request.method == 'POST':
        # Password Validation
        auth.val_user_passwd = [request.form.get("username"), request.form.get("password")]

        # If there is no error in validation create user session
        if auth.val_error is None:
            session['username'] = request.form.get("username")
            session['logindate'] = datetime.now()
            return redirect(url_for('index'))
    
    # Default page
    return render_template("login.html", auth=auth)

@app.route("/logout", methods=["GET"])
def logout():
    """Logout signed user"""
    session.pop('username', None)
    session.pop('logindate', None)
    return render_template("index.html", rtdo='user logout')

@app.route("/register", methods=["GET", "POST"])
def register(): 
    """New user registration"""

    # New instance of user identity: username u, mail m, password p
    u = RegistrationForm()
    m = RegistrationForm()
    p = RegistrationForm()

    # if POST validate user input in form
    if request.method == 'POST':
        u.val_username = request.form.get("username")
        m.val_email = request.form.get("email")
        p.val_passwd = [request.form.get("password"),request.form.get("password2")]

        # if val_error is empty (None): User can be registered
        if u.val_error is None and m.val_error is None and p.val_error is None:

            # add new user
            nu = Users().set_new_user(username=u.val_username, name=request.form.get("name"), lastname=request.form.get("surname"), email=m.val_email, password=request.form.get("password"))
            return render_template('register.html', u=u, m=m, p=p, rtdo=nu)

        else:
            return render_template("register.html", u=u, m=m, p=p)

    return render_template("register.html", u=u, m=m, p=p)
        

@app.route("/search", methods=["GET", "POST"])
def search():
    """Search for books by ISBN, Author, Title or Release date"""

    if 'username' in session:

        # If POST search book from ISBN, Author, Title OR Release year.
        if request.method == 'POST':
            srch = Books().search_book(search=request.form.get("search"))

            return render_template("search.html", search=srch, user=session['username'])
        
        return render_template("search.html", user=session['username'])

    return render_template("search.html")

@app.route("/book/<int:book_id>")
def book(book_id):
    """List details about a single book."""

    # Make sure book exists.
    book = Books.query.get(book_id)
    if book is None:
        return render_template("error.html", message="No book in our database.")
    
    # Get last 3 reviews
    rev = Reviews().get_reviews(3)

    # goodreads review from book.isdn
    gr = requests.get(Config.GOODREADS_URL_STATS, params={"key": Config.GOODREADS_KEY, "isbns": book.isbn })

    if gr.status_code != 200:
        # Return render_template
        raise Exception("BOOK not found in goodreads database")
    else:
        # Filter json info
        grapi = { k: gr.json()['books'][0][k] for k in ('id', 'isbn', 'isbn13', 'work_ratings_count', 'work_text_reviews_count', 'average_rating')}
        grapi['bookurl'] = Config.GOODREADS_URL_BOOKS + str(grapi['id'])

    # If user is logged in can write a review
    if 'username' in session:
        return render_template("book.html", book=book, reviews=rev, grinfo=grapi, user=session['username'])

    return render_template("book.html", book=book, reviews=rev, grinfo=grapi)

@app.route("/reviews", methods=["GET"])
def reviews():
    """ Show latest reviews from site and Goodreads"""
    
    # Get latest reviews
    rev = Reviews().get_reviews(3)

    if 'username' in session:
        # falta agregar que si estas logueado te permita dejar un review
        return render_template("reviews.html", title='reviews', user=session['username'], reviews=rev)
    return render_template("reviews.html", title='reviews', reviews=rev)

@app.route("/review/<int:review_id>")
def review(review_id):
    """Show last review made by user"""

    rev = Reviews.query.get(review_id)
    if rev is None:
        return render_template("error.html", message="No review in our database.")

    # Get last review by review_id
    rev = Reviews().get_reviews(numbers=1, review_id=review_id)

    res = requests.get(Config.GOODREADS_URL_BISBN + rev[-1].isbn, params={'format': 'json', 'key': Config.GOODREADS_KEY})
    grreview = res.json()['reviews_widget']
    grwidget = bs(grreview, 'html.parser')

    if 'username' in session:
        return render_template("review.html", title='review', user=session['username'], reviews=rev, grreview=grwidget)

    return render_template("review.html", title='review', reviews=rev, grreview=grwidget)