import os

from datetime import timedelta
from flask import Flask, jsonify
from flask_restful import Api
from flask_jwt import JWT


from security import authenticate, identity
from resources.user import UserRegister
from resources.item import Item, ItemList
from resources.store import Store, StoreList
from db import db


# Get the postgre url which get from Heroku, so replace some header
uri = os.environ.get('DATABASE_URL', 'sqlite:///data.db')
if uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'jose'
api = Api(app)


# Ask SQLAlchemy to automatically create table for us
@app.before_first_request
def create_tables():
    db.create_all()


# change the login endpoint from '/auth' to '/login'
app.config['JWT_AUTH_URL_RULE'] = '/login'

app.config['JWT_EXPIRATION_DELTA'] = timedelta(seconds=18000)

jwt = JWT(app, authenticate, identity)  # /auth


# customize what to return after authenticated. Not only access_token
@jwt.auth_response_handler
def customized_response_handler(access_token, identity):
    return jsonify({
        'access_token': access_token.decode('utf-8'),
        'user_id': identity.id
    })


api.add_resource(Store, '/store/<string:name>')
api.add_resource(Item, '/item/<string:name>')
api.add_resource(ItemList, '/items')
api.add_resource(StoreList, '/stores')
api.add_resource(UserRegister, '/register')


# '__main__' is the name assigned to the file which is actually ran by Python
# here we use '__name__ == __main__' to make sure the app only run when the app.py
# is the the file which ran by Python. This line of app.run will not happen when
# "app.py" file is imported by other files. So '__name__ == __main__' is a guard
if __name__ == '__main__':
    db.init_app(app)
    app.run(port=5000, debug=True)
