import random
import logging
import markovify
from textstat.textstat import textstat
from .models import MarkovText


class ProseMaker():

    def __init__(self):
        self._logger = logging.getLogger(__name__)
        self.sentences = []

    def get_prose(self, name):
        return getattr(self, name)()

    def get_sentences(self):
        return [s['text'] for s in self.sentences]

    def syllables(self, sentence):
        syllables = 0
        for word in sentence.split():
           syllables += round(textstat.syllable_count(word))
        return syllables

    def stanza(self):
        return random.sample(self.sentences, 5)

    def haiku(self):
        # 5/7/5 syllable count

        five = [d for d in self.sentences if d['syl'] == 5]

        if len(five) < 2:
            raise Exception('haiku five syllables not found.')

        seven = [d for d in self.sentences if d['syl'] == 7]

        if len(seven) < 1:
            raise Exception('haiku seven syllables not found.')

        return [random.choice(five),
                random.choice(seven),
                random.choice(five)]


class ProseMakerSen(ProseMaker):

    def __init__(self, sendict):
        ProseMaker.__init__(self)
        # arg: sendict = [{'id':id,'text':text},]
        for i in range(len(sendict)):
            self.sentences.append(
                self.analyze_dict(sendict[i])
            )

    def analyze_dict(self, sendict):
        # update the dict with len and syllables
        sendict['len'] = len(sendict['text'])
        sendict['syl'] = self.syllables(sendict['text'])
        return sendict



class ProseMakerText(ProseMaker):

    def __init__(self, text):
        ProseMaker.__init__(self)
        self.generate(text, max_sen=2000)

    def analyze_text(self, id, text):
        return {'id':id,
                'text':text,
                'len':len(text),
                'syl':self.syllables(text)}


    def generate(self, text, max_sen=1000):
        """
        Take text and convert into a
        list of sentences.
        """
        model = markovify.Text(text)
        count = 1
        tries = 5
        while count <= max_sen and tries > 0:
            sen = model.make_short_sentence(100)
            if sen:
                count += 1
                self.sentences.append(
                    self.analyze_text(count, sen)
                )
            else:
                tries -= 1
                self._logger.debug('sen count:%s tries:%s', count, tries)
