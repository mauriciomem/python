'''
from app import app
'''
from app import new_app


app = new_app()

if __name__ == "__main__":
    app.run(host='0.0.0.0')
