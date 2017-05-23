import unittest
import os
import json
from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from flask_prose import FSQLAStorage, ProseEngine
from flask_jsontools import FlaskJsonClient, JsonResponse


class ApiTest(unittest.TestCase):

    def setUp(self):
        self.app = app = Flask(__name__)
        self.app.test_client_class = FlaskJsonClient
        self.app.debug = self.app.testing = True
        self.app.config['SECRET_KEY'] = os.urandom(24)

        #config sqlalchemy
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['DATABASE_URI'] = 'sqlite://'
        app.config['SQLALCHEMY_BINDS'] = {'prose':'sqlite://'}
        self.db = db = SQLAlchemy(app)

        # config flask-prose
        self.storage = FSQLAStorage(db=db, bind_key='prose')
        self.prose = ProseEngine(app=app, storage=self.storage)

        #print(app.url_map)

        self.xray = os.path.join(os.path.dirname(__file__), 'little_shak')

        with open(self.xray, 'r') as myfile:
            text = myfile.read()
            self.storage.corpora_save(label='setup1', text=text)
            self.storage.corpora_save(label='setup2', text=text)


        @app.before_first_request
        def create_user():
            self.db.create_all()

    def test_upload(self):
        with open(self.xray, 'rb') as myfile:
            with self.app.test_client() as c:
                rv = c.post('/v1/corpora',
                            data = {'file': (myfile,'shatit_now')})
                self.assertEqual(rv.status_code, 200)
                self.assertIsInstance(rv, JsonResponse)


                print('get_json', type(rv.get_json()), rv.get_json())
                rv_dict = json.loads(rv.get_json())
                print('rv_dict', type(rv_dict), rv_dict)

                rl = c.get('/v1/corpora/{0}'.format(rv_dict[0]['id']))
                self.assertEqual(rl.status_code, 200)
                self.assertIsInstance(rl, JsonResponse)
                print(str(rl.get_json()))

                rp = c.get('/v1/prose')
                print(rp.get_json())

    def test_corpora_list(self):
        with self.app.test_client() as c:
            # get all corpora
            rv = c.get('/v1/corpora')
            corpora = json.loads(rv.get_json())
            print(rv.get_json(), corpora)
            self.assertEqual(rv.status_code, 200)
            self.assertIsInstance(rv, JsonResponse)
            self.assertGreaterEqual(len(corpora), 1)

            # get one corpora by id
            rv = c.get('/v1/corpora/' + corpora[0]['id'])
            self.assertEqual(rv.status_code, 200)
            self.assertIsInstance(rv, JsonResponse)

    def test_prose(self):
         with self.app.test_client() as c:
            # get a prose  = random
            rv = c.get('/v1/prose')
            prose = json.loads(rv.get_json())
            print('@@@', type(prose), prose)
            self.assertEqual(rv.status_code, 200)
            self.assertIsInstance(rv, JsonResponse)

            # get the prose by id
            rv = c.get('/v1/prose/' + prose['id'])
            self.assertEqual(rv.status_code, 200)
            self.assertIsInstance(rv, JsonResponse)

    def test_grock(self):
        with self.app.test_client() as c:
            # get a prose
            rv = c.get('/v1/prose')
            prose = json.loads(rv.get_json())

            print('####',type(rv.get_json()), type(prose), prose)
            rv = c.post('/v1/prose', data={'prose_id':prose['id'], 'reaction':'omg'})
            self.assertEqual(rv.status_code, 200)
            self.assertIsInstance(rv, JsonResponse)
