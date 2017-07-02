import unittest
import pytest
import random
import uuid
try:
    from builtins import range
except ImportError:
    pass
import unittest
import os
from .prosetestcase import ProseTestCase
import time

class StorageTestMethods(ProseTestCase):

    def setUp(self):
        ProseTestCase.setUp(self)
        self._create_storage()

    def test_new_corpora(self):
        with pytest.raises(Exception) as excinfo:
            corpora = self.storage.corpora_save(label='test', text='hoorah')
        assert str(excinfo.value).startswith('MarkovText not found for corpora:')

    def test_prose(self):
        xray = os.path.join(os.path.dirname(__file__), 'shatit')
        with open(xray, 'r') as myfile:
            data = myfile.read()
            corpora1 = self.storage.corpora_save(label='data1', text=data)

            print('corpora1:', corpora1)

            self.assertIsNotNone(corpora1)
            prose1 = self.storage.prose()

            self.assertIsNotNone(prose1)
            print('prose1:', prose1)
            assert(prose1['id'])
            assert(prose1['corporas'])
            assert(prose1['prosetype'])

            prose2 = self.storage.prose(corpora=set().add(corpora1))
            self.assertIsNotNone(prose2)
            prose3 = self.storage.prose(uuid=prose1['id'])
            self.assertIsNotNone(prose3)

    def test_corpora_list(self):
        xray = os.path.join(os.path.dirname(__file__), 'shatit')
        with open(xray, 'r') as myfile:
            data = myfile.read()
            corpora1 = self.storage.corpora_save(label='data1', text=data)
            self.assertIsNotNone(corpora1)
            corpora2 = self.storage.corpora_save(label='data2', text=data)
            self.assertIsNotNone(corpora2)
            clist = self.storage.corpora_list()
            assert(len(clist) == 2)
            clist1 = self.storage.corpora_list(uuid=corpora1)
            assert(len(clist1) == 1)

    def test_corpora_generate_prose(self):
        xray = os.path.join(os.path.dirname(__file__), 'shatit')
        with open(xray, 'r') as myfile:
            data = myfile.read()
            corpora = self.storage.corpora_save(label='data', text=data)
            corpora_clone = self.storage.corpora_save(label='data clone', text=data)
            self.assertIsNotNone(corpora)
            self.storage.corpora_generate_prose(set([corpora]))
            p = self.storage.prose()
            print('prose:', p)
            self.assertIsNotNone(p)

            cp = self.storage.prose(corpora=corpora)
            print('cp:', corpora, cp)

    def test_multiple_corpora_prose(self):
        xray = os.path.join(os.path.dirname(__file__), 'shatit')
        with open(xray, 'r') as myfile:
            data = myfile.read()
            corpora1 = self.storage.corpora_save(label='data1', text=data)
            self.assertIsNotNone(corpora1)
            corpora2 = self.storage.corpora_save(label='data2', text=data)
            self.assertIsNotNone(corpora2)
            corpora3 = self.storage.corpora_save(label='data3', text=data)
            self.assertIsNotNone(corpora3)
            corpora4 = self.storage.corpora_save(label='data4', text=data)
            self.assertIsNotNone(corpora4)

            corpora_set = set([corpora1, corpora2, corpora3, corpora4])

            self.storage.corpora_generate_prose(corpora_set)
            p = self.storage.prose()
            self.assertIsNotNone(p)

    def test_rating(self):

        xray = self.storage.ratings()
        xray = self.storage.ratings(prose_id=uuid.uuid1())

        xray = os.path.join(os.path.dirname(__file__), 'shatit')
        with open(xray, 'r') as myfile:
            data = myfile.read()
            corpora1 = self.storage.corpora_save(label='data1', text=data)
            self.assertIsNotNone(corpora1)

            prose1 = self.storage.prose()
            prose2 = self.storage.prose()
            prose3 = self.storage.prose()

            # create saw grock
            for x in range(100):
                self.storage.prose()

            self.storage.grock(prose_id=prose3['id'], reaction='meh')
            self.storage.grock(prose_id=prose3['id'], reaction='omg')
            self.storage.grock(prose_id=prose3['id'], reaction='omg')

            self.storage.grock(prose_id=prose1['id'], reaction='meh')
            self.storage.grock(prose_id=prose1['id'], reaction='meh')

            self.storage.grock(prose_id=prose2['id'], reaction='omg')
            self.storage.grock(prose_id=prose2['id'], reaction='omg')

            xray = self.storage.ratings()

            delta = self.storage.ratings(prose_id=prose3['id'])

            assert(len(delta) == 1)

            meh = self.storage.ratings(rate_type='meh')


    def test_grock_rating(self):
        xray = os.path.join(os.path.dirname(__file__), 'shatit')
        with open(xray, 'r') as myfile:
            data = myfile.read()
            corpora1 = self.storage.corpora_save(label='data1', text=data)
            self.assertIsNotNone(corpora1)

            prose1 = self.storage.prose()
            prose2 = self.storage.prose()

            # create saw grock
            for x in range(100):
                self.storage.prose()

            for x in range(20):
                self.storage.grock(prose_id=prose1['id'], reaction='omg')
                self.storage.grock(prose_id=prose2['id'], reaction='omg')

            for x in range(10):
                self.storage.grock(prose_id=prose1['id'], reaction='meh')
                self.storage.grock(prose_id=prose2['id'], reaction='meh')

            xray = self.storage.ratings()

            assert(len(xray) == 2)


    def test_grock_rating_rand(self):
        xray = os.path.join(os.path.dirname(__file__), 'shatit')
        with open(xray, 'r') as myfile:
            data = myfile.read()
            corpora1 = self.storage.corpora_save(label='data1', text=data)
            self.assertIsNotNone(corpora1)

            for x in range(1000):
                reaction = random.choice(['omg','meh'])
                p = self.storage.prose()
                self.storage.grock(prose_id=p['id'], reaction=reaction)

            xray = self.storage.ratings(limit=50)
