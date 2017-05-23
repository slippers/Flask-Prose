import unittest
import os
import json
from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from flask_prose import FSQLAStorage, ProseEngine
from flask_jsontools import FlaskJsonClient, JsonResponse
from flask_security import (
    Security,
    auth_token_required,
    roles_required
)
from .security_models import SetupModels, SetupUsers

class ApiTest(unittest.TestCase):

    def setUp(self):
        print('setUp')
        self.app = app = Flask(__name__)
        self.app.test_client_class = FlaskJsonClient
        self.app.debug = self.app.testing = True
        self.app.config['SECRET_KEY'] = os.urandom(24)

        #config sqlalchemy
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['DATABASE_URI'] = 'sqlite://'
        app.config['SQLALCHEMY_BINDS'] = {'prose':'sqlite://'}
        self.db = db = SQLAlchemy(app)

        #config flask-security
        app.config['WTF_CSRF_ENABLED'] = False
        user_datastore = SetupModels(db)
        security = Security(app, user_datastore)

        # config flask-prose
        self.storage = FSQLAStorage(db=db, bind_key='prose')
        self.prose = ProseEngine()
        self.prose.viewmethod_decorators(
            corpora=(auth_token_required, roles_required('prose_admin'),)
        )
        self.prose.init_app(app=app, storage=self.storage)

        self.xray = os.path.join(os.path.dirname(__file__), 'little_shak')

        with open(self.xray, 'r') as myfile:
            self.storage.corpora_save(label='setup', text=myfile.read())


        #print(app.url_map)

        @app.before_first_request
        def create_user():
            self.db.create_all()
            SetupUsers(user_datastore)
            self.db.session.commit()

    def getAuthToken(self, test_client, user):
        """
            flask-security contains the /login endpoint
            that when posed to will return the json auth_token

            the flask-security @auth_token_required decorator
            will do the method access checking

            must set this config for token authentication to work.
            app.config['WTF_CSRF_ENABLED'] = False
        """
        user = {'email':user, 'password':'test123'}
        ru = test_client.post('/login', user)
        ru_json = ru.get_json()
        print('getAuthToken:token', ru_json)
        return {'authentication-token': ru_json['response']['user']['authentication_token']}

    def test_upload(self):
        with open(self.xray, 'rb') as myfile:
            with self.app.test_client() as c:
                auth_token = self.getAuthToken(c, 'test@example.com')
                rv = c.post('/v1/corpora',
                            data = {'file': (myfile,'shatit_now')},
                            headers=auth_token)

                self.assertEqual(rv.status_code, 200)

                rv_dict = json.loads(rv.get_json())

                rl = c.get('/v1/corpora/{0}'.format(rv_dict[0]['id']),
                           headers=auth_token)
                self.assertEqual(rl.status_code, 200)
                self.assertIsInstance(rl, JsonResponse)
                print(rl.get_json())

                rp = c.get('/v1/prose')
                print(rp.get_json())

    def test_no_token(self):
        with self.app.test_client() as c:
            rv = c.get('/v1/prose')
            print(rv.get_json())

    def test_corpora_list(self):
        with self.app.test_client() as c:
            auth_token = self.getAuthToken(c, 'test@example.com')

            rv = c.get('/v1/corpora', headers=auth_token)
            print(rv)
            self.assertEqual(rv.status_code, 200)
            self.assertIsInstance(rv, JsonResponse)

    def test_prose(self):
         with self.app.test_client() as c:
            rv = c.get('/v1/prose')
            print(rv.get_json())
            self.assertEqual(rv.status_code, 200)
            self.assertIsInstance(rv, JsonResponse)
