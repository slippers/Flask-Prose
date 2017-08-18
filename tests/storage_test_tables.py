import unittest
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



class StorageTestTables(ProseTestCase):

    def setUp(self):
        ProseTestCase.setUp(self)
        self._create_storage()

    def check_table(self, table_name, expected_columns):
        table = self.metadata.tables[table_name]
        columns = [t.name for t in table.columns]
        self.assertListEqual(columns, expected_columns)

    def test_corpora_table_exists(self):
        table_name = "corpora"
        expected_columns = ['id', 'label', 'source', 'text', 'post_date']
        self.check_table(table_name, expected_columns)

    def test_markovtext(self):
        table_name = "markovtext"
        expected_columns = ['id', 'corpora_id', 'text', 'used', 'created_date']
        self.check_table(table_name, expected_columns)

    def test_prose_table_exists(self):
        table_name = "prose"
        expected_columns = ['id', 'prosetype_id','title', 'text', 'created_date']
        self.check_table(table_name, expected_columns)

    def test_prosetype_table_exists(self):
        table_name = "prosetype"
        expected_columns = ['id', 'label']
        self.check_table(table_name, expected_columns)

    def test_grock_table_exists(self):
        table_name = "grock"
        expected_columns = ['id', 'prose_id', 'reaction', 'created_date']
        self.check_table(table_name, expected_columns)

    def test_prosecorpora_table_exists(self):
        table_name = "prosecorpora"
        expected_columns = ['prose_id', 'corpora_id']
        self.check_table(table_name, expected_columns)

