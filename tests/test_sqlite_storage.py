import unittest
from .storage_test_tables import StorageTestTables
from .storage_test_methods import StorageTestMethods
try:
    from builtins import range
except ImportError:
    pass
import tempfile
import os
from sqlalchemy import create_engine, MetaData
import time
from flask_prose import Storage


class StorageTest():

    def _create_storage(self):
        temp_dir = tempfile.gettempdir()
        self._dbfile = os.path.join(temp_dir, "temp.db")
        self.engine = create_engine('sqlite:///'+self._dbfile)
        self.storage = Storage(self.engine)
        self.metadata = MetaData(bind=self.engine, reflect=True)

    def tearDown(self):
        os.remove(self._dbfile)
        pass

class TestSQLiteStorageTables(StorageTest, StorageTestTables, unittest.TestCase):

    def dummy(self):
        pass


class TestSQLiteStorageMethods(StorageTest, StorageTestMethods, unittest.TestCase):

    def dummy(self):
        pass
