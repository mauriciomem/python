from werkzeug.security import generate_password_hash, check_password_hash
from app.models import Users
import re

class RegistrationForm():

    def __init__(self, user=None, mail=None, passwd=None, error=None):
        self.user = user
        self.mail = mail
        self.passwd = passwd
        self.error = error

    @property
    def val_username(self):
        return self.user

    @val_username.setter
    def val_username(self, user):
            username = Users.query.filter_by(username=user).first()
            if username is not None:
                self.val_error = 'Already chosen username.'
                return self.val_error
            if not re.match(r'^[a-zA-Z_.-]+$', user):
                self.val_error = 'Bad user name format.'
                return self.val_error
            self.user = user
            return self.user

    @property
    def val_email(self):
        return self.mail
  
    @val_email.setter
    def val_email(self, mail):
            email = Users.query.filter_by(email=mail).first()
            if email is not None:
                self.val_error = 'Please use a different email address.'
                return self.val_error
            if not re.match(r"[^@]+@[^@]+\.[^@]+", mail):
                self.val_error = 'Please insert a correct email address format.'
                return self.val_error
            self.mail = mail
            return self.mail

    @property
    def val_passwd(self):
        return self.passwd

    @val_passwd.setter
    def val_passwd(self, passwd):
        if passwd[0] != passwd[1]:
            self.val_error = 'Passwords don\'t match.'
            return self.val_error
        else:
            self.passwd = True
            return self.passwd

    @property
    def val_error(self):
        return self.error

    @val_error.setter
    def val_error(self, msg):
        self.error = ValidationError(msg)

class LoginForm():

    def __init__(self, auth=None, error=None):
        self.auth = auth
        self.error = error

    @property
    def val_user_passwd(self):
        return self.auth

    @val_user_passwd.setter
    def val_user_passwd(self, auth):
        username = Users.query.filter_by(username=auth[0]).first()
        print(username, auth[0], auth[1])
        if username is None or not username.check_password(auth[1]):
            self.val_error = 'Invalid User name or Password.'
            return self.val_error
        else:
            self.auth = True
            return self.auth

    @property
    def val_error(self):
        return self.error

    @val_error.setter
    def val_error(self, msg):
        self.error = ValidationError(msg)


class SearchForm():
    
    def __init__(self, search):
        self.search = search

class ValidationError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return self.value
