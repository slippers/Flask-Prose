import random
import math
import re
import logging
import markovify
from textstat.textstat import textstat
from .models import MarkovText
import pdb

class ProseMaker():

    NOISE_WORDS = set([
        "a","about","above","all","along","also","although","am","an","and","any","are","aren't",
        "as","at","be","because","been","but","by","can","cannot","could","couldn't",
        "did","didn't","do","does","doesn't","e.g.","either","etc","etc.","even","ever",
        "for","from","further","get","gets","got","had","hardly","has","hasn't","having","he",
        "hence","her","here","hereby","herein","hereof","hereon","hereto","herewith","him",
        "his","how","however","i","i.e.","if","in","into","is","it","it's","its","me","more",
        "most","mr","my","near","nor","not","now","of","on","onto","other","our","out","over",
        "really",
        "said","same","she","should","shouldn't","since","so","some","such","than","that",
        "the","their","them","then","there","thereby","therefore","therefrom","therein",
        "thereof","thereon","thereto","therewith","these","they","this","those","through",
        "thus","to","too","under","until","unto","upon","us","very","viz","was","wasn't",
        "we","were","what","when","where","whereby","wherein","whether","which","while",
        "who","whom","whose","why","with","without","would","you","your"
    ])


    def __init__(self):
        self._logger = logging.getLogger(__name__)
        self.sentences = []

    def get_prose(self, name):
        return getattr(self, name)()

    def clean_words(self, sentences):
        # flatten sentences into a list of words
        words = [item for sublist in sentences for item in sublist['text'].split()]
        if not words:
            return
        # extract all the noise words
        clean = [x for x in words if re.sub(r'\W+', '', x.lower()) not in ProseMaker.NOISE_WORDS]
        return clean

    def title(self, sentences):
        clean = self.clean_words(sentences)
        if not clean:
            return
        count = math.ceil(math.log(len(clean), 3))
        title = ' '.join(random.sample(clean, count))
        return title

    def get_sentences(self):
        text = [sen for sen in self.sentences]
        return [s['text'] for s in self.sentences]

    def syllables(self, sentence):
        syllables = 0
        for word in sentence.split():
           syllables += round(textstat.syllable_count(word))
        return syllables

    def stanza(self):
        prose = random.sample(self.sentences, 5)
        return {'title':self.title(prose), 'prose':prose}

    def haiku(self):
        # 5/7/5 syllable count

        five = [d for d in self.sentences if d['syl'] == 5]

        if len(five) < 2:
            self._logger.warning('haiku five syllables not found.')
            return

        seven = [d for d in self.sentences if d['syl'] == 7]

        if len(seven) < 1:
            self._logger.warning('haiku seven syllables not found.')
            return

        prose = [random.choice(five), random.choice(seven), random.choice(five)]

        return {'title':self.title(prose), 'prose':prose}


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
