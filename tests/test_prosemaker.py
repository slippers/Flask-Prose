import unittest
import os
from flask_prose import (
ProseMakerText,
ProseMakerSen
)


class TestProseMaker(unittest.TestCase):

    def setUp(self):
        xray = os.path.join(os.path.dirname(__file__), 'shatit')
        with open(xray, 'r') as myfile:
            data = myfile.read()
            self.pm = ProseMakerText(text=data)

    def test_sentences(self):
        sentences = self.pm.get_sentences()
        print(sentences[1])
        self.assertIsNotNone(sentences)

    def test_stanza(self):
        stanza = self.pm.stanza()
        print(stanza)
        self.assertIsNotNone(stanza)
        self.assertEquals(len(stanza), 5)

    def test_haiku(self):
        haiku = self.pm.haiku()
        print(haiku)
        self.assertEquals(len(haiku), 3)

    def test_ProseMakerSen(self):
        ps = ProseMakerSen(self.pm.sentences)
        self.assertListEqual(ps.sentences, self.pm.sentences)
