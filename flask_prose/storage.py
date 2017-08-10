import re
try:
    from builtins import str
except ImportError:
    pass
import os.path
import logging
import json
import uuid
from flask_jsontools import DynamicJSONEncoder
from sqlalchemy.ext.serializer import loads, dumps
from sqlalchemy import (
    select,
    desc,
    func,
    and_,
    not_,
)
from sqlalchemy.orm import (
    sessionmaker,
    load_only,
    aliased,
    subqueryload,
    joinedload
)
from sqlalchemy.exc import IntegrityError
from .models import (
    Base,
    Prose,
    Grock,
    ProseType,
    Corpora,
    MarkovText,
    ProseCorpora
)
from .prosemaker import (
    ProseMakerText,
    ProseMakerSen
)


class Storage():

    def __init__(self, engine=None, bind_key=None):

        self._logger = logging.getLogger(__name__)

        self.generate_prose_callback = self.corpora_generate_prose
        self.generate_markov_callback = self.corpora_generate_markov

        if engine is None:
            raise ValueError('engine is required')

        self._engine = engine

        # __bind_key__ is a custom attribute set in the model
        # it is used by wrapper extentions like flask-sqlalchemy and flask-alchy
        # to bind the model to a engine connection
        if bind_key:
            Base.__bind_key__ = bind_key

        Session = sessionmaker(bind=engine)

        self._session = Session()

        # the models have inherited Base, we have imported base from there.
        Base.metadata.create_all(engine)

    def close(self):
        '''
        each time session.commit() is called an implict tansaction is newly created.
        this sqlalchemy behavior causes an issue with issuing DDL
        commands in newer versions of mysql.
        error 'Waiting for table metadata lock'
        '''
        self._session.close()

    def prosetype_add(self, label):
        if not label:
            raise ValueError('label requried')
        pt = self._session.query(ProseType) \
                .filter(ProseType.label == label) \
                .one_or_none()

        if pt:
            return pt.id

        try:
            pt = ProseType(label)
            self._session.add(pt)
            self._session.commit()
            return pt.id
        except:
            self._session.rollback()
            raise

    def corpora_save(self, label=None, source=None, text=None):
        rx = re.compile('[^\w\s\.\,\?\!\'\"]')
        res = rx.sub(' ', text).strip()
        if not res:
            raise ValueError('text invalid.')
        self._logger.debug('label:%s text:%s...', label, res[0:20])
        corpora = Corpora(text=res, label=label, source=source)
        try:
            self._session.add(corpora)
            self._session.commit()
            self._logger.debug('corpora.id:%s', corpora.id)
        except:
           self._session.rollback()
           raise

        if self.generate_markov_callback:
            self._logger.debug('calling generate_markov_callback:%s',
                               self.generate_markov_callback)
            self.generate_markov_callback(corpora.id)

        if self.generate_prose_callback:
            self._logger.debug('calling generate_prose_callback:%s',
                               self.generate_prose_callback)
            self.generate_prose_callback((corpora.id,))

        return corpora.id

    def corpora_list(self, uuid=None):
        corpora = self._session.query( \
                                      Corpora.id,
                                      Corpora.label,
                                      Corpora.post_date,
                                      Corpora.source,
                                      func.count(ProseCorpora.prose_id).label('prose'),
                                     ) \
                .select_from(Corpora) \
                .join(ProseCorpora, ProseCorpora.corpora_id == Corpora.id) \
                .group_by(Corpora.id)

        if uuid:
            corpora = corpora.filter(Corpora.id == uuid)

        self._logger.debug('corpora_list:%s', str(corpora))
        corpora_result  = corpora.all()
        if corpora_result:
            return json.loads(json.dumps(corpora_result, cls=DynamicJSONEncoder))
        else:
            return []

    def corpora_delete(self, uuid):
        try:
            corpora = self._session.query(Corpora) \
                    .options(load_only('id')) \
                    .filter(Corpora.id == uuid).one_or_none()

            if corpora:
                self._session.delete(corpora)
                self._session.commit()
                return True

            return False
        except:
            self._session.rollback()
            raise

    def generate_markov(self, callback):
        self.generate_markov_callback = callback
        return callback

    def corpora_generate_markov(self, corpora_id):
        """
        create markov sentences from corpora text
        """
        try:
            corpora = self._session.query(Corpora) \
                    .filter(Corpora.id == corpora_id) \
                    .one_or_none()

            if not corpora:
                raise Exception('corpora not found')

            pm = ProseMakerText(text=corpora.text)
            markovtext = [MarkovText(corpora.id, sen) for sen in pm.get_sentences()]
            self._logger.debug('markovtext count:%s',len(markovtext))
            self._session.bulk_save_objects(markovtext)
            self._session.commit()
        except:
            self._session.rollback()
            raise

    def generate_prose(self, callback):
        self.generate_prose_callback = callback
        return callback

    def corpora_generate_prose(self, corpora=set(), MAX_PROSE_COUNT = 5):
        """
        arg:corpora = set of corpora ids
        """
        MAX_SENTENCE_COUNT = 1000

        corpora_result = self._session.query(Corpora) \
                .filter(Corpora.id.in_(list(corpora))) \
                .all()

        corpora_ids = [str(x.id) for x in corpora_result]

        self._logger.debug('corpora_ids:%s',corpora_ids)

        mtext = self._session.query(MarkovText) \
                .filter(MarkovText.corpora_id.in_(corpora_ids)) \
                .order_by(func.random()) \
                .limit(MAX_SENTENCE_COUNT) \
                .all()

        self._logger.debug('mtext:%s',len(mtext))
        if not mtext:
            raise Exception('MarkovText not found for corpora:{}'.format(corpora_ids))

        # get the json of the markovtext model
        pm = ProseMakerSen([m.json() for m in mtext])

        for x in range(MAX_PROSE_COUNT):
            self.insert_prose(pm, 'stanza')

        for x in range(MAX_PROSE_COUNT):
            self.insert_prose(pm, 'haiku')

    def insert_prose(self,
                     prosemaker,
                     prose_type,
                     ):
        prosetype_id = self.prosetype_add(prose_type)

        prose_json = prosemaker.get_prose(prose_type)

        if not prose_json:
            self._logger.warning('prosemaker generator error.')
            return
        else:
            self._logger.debug('prose_json:%s', prose_json)

        try:
            prose = Prose(prosetype_id=prosetype_id,
                          title=prose_json['title'],
                          text=prose_json['prose'])

            self._session.add(prose)
            self._session.commit()
            self._logger.debug('prose %s:%s', prose_type, prose.id)

            # gather unique corpora ids here
            corpora_ids = {(x['corpora_id']) for x in prose_json['prose']}

            # create the association ProseCorpora objects
            prose_corpora = []
            prose_corpora.extend([ProseCorpora(prose.id, c_id) for c_id in corpora_ids])
            self._session.bulk_save_objects(prose_corpora)
            self._session.commit()
        except:
            self._session.rollback()
            raise

    def prose(self, uuid=None, corpora=()):
        self._logger.debug('prose uuid:%s corpora:%s', uuid, corpora)
        prose = None
        if uuid:
            prose = self._prose(uuid)
        elif corpora:
            prose = self._prose_corpora_random(corpora)
        else:
            prose = self._prose_fresh()
            if not prose:
                prose = self._prose_random()

        return self._prose_data(prose)

    def _prose(self, uuid):
        if not uuid:
            raise ValueError('uuid required.')
        prose = self._session.query(Prose.id) \
                .filter(Prose.id == uuid)

        return prose.first()

    def _prose_random(self):
        """
        return random prose
        """
        self._logger.debug('_prose_random')
        prose = self._session.query(Prose.id) \
                .order_by(func.random()) \
                .limit(1)

        return prose.first()

    def _prose_fresh(self):
        """
        left join grock with prose
        filter so only unseen prose.
        """
        self._logger.debug('_prose_fresh')
        prose = self._session.query(Prose.id) \
                .outerjoin(Grock, Grock.prose_id == Prose.id) \
                .filter(Grock.id.is_(None)) \
                .limit(1)

        return prose.first()

    def _prose_corpora_random(self, corpora):
        if not corpora:
            raise ValueError('corpora required.')

        prose = self._session.query(Prose.id) \
                .join(ProseCorpora, ProseCorpora.prose_id == Prose.id) \
                .filter(ProseCorpora.corpora_id == corpora) \
                .order_by(func.random()) \
                .limit(1) \
                .first()

        return prose

    def _prose_data(self, prose_id):
        if not prose_id:
            return {}

        prose = self._session.query(Prose) \
                .filter(Prose.id == prose_id[0]) \
                .first()

        if not prose:
            raise Exception('prose not found.')

        prosetype = self._session.query(ProseType) \
                .filter(prose.prosetype_id == ProseType.id) \
                .first()

        corpora = self._session.query(Corpora) \
                .join(ProseCorpora, ProseCorpora.corpora_id == Corpora.id) \
                .filter(ProseCorpora.prose_id == prose.id) \
                .all()

        prose_data = json.loads(json.dumps(prose, cls=DynamicJSONEncoder))
        prose_data['prosetype'] = json.loads(json.dumps(prosetype, cls=DynamicJSONEncoder))
        prose_data['corporas'] = json.loads(json.dumps(corpora, cls=DynamicJSONEncoder))

        self._grock(prose.id, reaction='saw')

        return prose_data

    def _grock(self, prose_id, reaction='saw'):
        self._logger.debug('prose_id:%s reaction:%s', prose_id, reaction)
        reactions = ['omg', 'meh', 'saw']
        if reaction not in reactions:
            raise ValueError("Expected one of: %s" % reactions)

        try:
            self._session.add(Grock(prose_id, reaction))
            self._session.commit()
        except:
            self._session.rollback()
            raise

    def grock(self, prose_id, reaction='saw'):
        """
        """
        prose = self._prose(prose_id)
        if not prose:
            raise Exception('prose not found.')

        self._grock(prose.id, reaction)

    def ratings(self, rate_type='omg', prose_id=None, limit=10):
        """
        arg: rate_type = omg | meh
        controls if the query looks for meh or omg results

        arg: prose_id: just returns result for this prose id

        arg: limit: always applied defaulting to 10

        select prose_id, saw,omg,meh
        from (
        select prose_id,
        count(*) as saw,
        omg - meh as total,
        (
        select count(*)
        from grock omg
        where  omg.reaction = 'omg'
        and omg.prose_id = grock.prose_id
        ) as omg,
        (
        select count(*)
        from grock meh where  meh.reaction = 'meh'
        and meh.prose_id = grock.prose_id
        ) as meh
        from grock
        where reaction = 'saw'
        group by(prose_id)
        )
        where omg - meh > 0
        order by (omg - meh) desc, saw desc;
        """
        omg = aliased(Grock)
        meh = aliased(Grock)
        saw = aliased(Grock)
        prose = aliased(Prose)

        _query = select([saw.prose_id,
                         func.count().label('saw'),

                         select([prose.title]) \
                         .select_from(prose) \
                         .where(saw.prose_id == prose.id) \
                         .as_scalar() \
                         .label('title'),

                         select([func.count()]) \
                         .select_from(meh) \
                         .where(meh.reaction == 'meh') \
                         .where(meh.prose_id == saw.prose_id) \
                         .as_scalar() \
                         .label('meh'),

                         select([func.count()]) \
                         .select_from(omg) \
                         .where(omg.reaction == 'omg') \
                         .where(omg.prose_id == saw.prose_id) \
                         .as_scalar() \
                         .label('omg'),
                        ]) \
                .select_from(saw) \
                .where(saw.reaction == 'saw') \
                .group_by(saw.prose_id)

        # if asking for a single prose constrain in subquery
        if prose_id:
            _query = _query.where(saw.prose_id == prose_id)

        # postgres requires subquery AS to be valid
        _query = _query.alias('xray')

        query = select([_query, (_query.c.omg - _query.c.meh).label('total')])

        # if asking for a single prose always return no constraint
        if not prose_id and rate_type == 'omg':
            query = query.where((_query.c.omg - _query.c.meh) > 0) \
                    .order_by((_query.c.omg - _query.c.meh).desc())

        if not prose_id and rate_type == 'meh':
            query = query.where((_query.c.omg - _query.c.meh) < 0) \
                    .order_by((_query.c.omg - _query.c.meh))

        query = query.limit(limit) \
                .alias('gamma')

        self._logger.debug('query:%s %s', prose_id, str(query))
        try:
            rating_result = self._session.query(query).all()
            if rating_result:
                return json.loads(json.dumps(rating_result, cls=DynamicJSONEncoder))
            else:
                return []
        except:
            self._session.rollback()
            raise

    def ratings_all(self):
        omg = self.ratings(rate_type='omg')
        meh = self.ratings(rate_type='meh')
        omg.extend(meh)
        return omg
