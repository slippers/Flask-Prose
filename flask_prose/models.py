import datetime
import uuid
from sqlalchemy.ext.declarative import (
    declarative_base,
    declared_attr
)
from sqlalchemy import (
    Table,
    Column,
    Integer,
    String,
    ForeignKey,
    Text,
    DateTime,
    SmallInteger,
    PrimaryKeyConstraint
)
from sqlalchemy.orm import (
    relationship,
    deferred,
    backref
)
from sqlalchemy_utils import UUIDType, JSONType
from flask_jsontools import JsonSerializableBase


class BaseModel(object):

    __bind_key__ = 'DEFAULT'
    #id = Column(UUIDType(binary=False), default=uuid.uuid4, primary_key=True)

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()


Base = declarative_base(cls=(BaseModel, JsonSerializableBase))


class Corpora(Base):
    id = Column(UUIDType(binary=False), default=uuid.uuid4, primary_key=True)
    # exclude text from json output,  too big.
    _json_exclude = ['text']
    # a short description of the content
    label = Column(String(256), default="")
    # source of the content, url file...
    source = Column(String(256), default="")
    text = deferred(Column(Text))
    post_date = Column(DateTime)

    def __init__(self, label, source, text):
        self.post_date = datetime.datetime.utcnow()
        self.label = label
        self.text = text
        self.source = source


class MarkovText(Base):
    id = Column(UUIDType(binary=False), default=uuid.uuid4, primary_key=True)
    corpora_id = Column(
        UUIDType(binary=False),
        ForeignKey('corpora.id', ondelete='CASCADE')
    )
    text = Column(String(500))
    created_date = Column(DateTime)

    def __init__(self, corpora_id, text):
        self.corpora_id = corpora_id
        self.text = text
        self.created_date = datetime.datetime.utcnow()

    def json(self):
        return {
            'id':str(self.id),
            'corpora_id':str(self.corpora_id),
            'text':self.text
        }


class ProseType(Base):
    id = Column(UUIDType(binary=False), default=uuid.uuid4, primary_key=True)
    label = Column(String(256))

    def __init__(self, label):
        self.label = label


class ProseCorpora(Base):
    prose_id = Column(UUIDType(binary=False),
                      ForeignKey('prose.id'),
                      primary_key=True)
    corpora_id = Column(UUIDType(binary=False),
                        ForeignKey('corpora.id', ondelete='CASCADE'),
                        primary_key=True)
    corpora = relationship('Corpora', lazy='joined')

    def __init__(self, prose_id, corpora_id):
        self.prose_id = prose_id
        self.corpora_id = corpora_id


class Prose(Base):
    _json_exclude = ['prosetype_id']
    id = Column(UUIDType(binary=False), default=uuid.uuid4, primary_key=True)
    prosetype_id = Column(
        UUIDType(binary=False),
        ForeignKey('prosetype.id', ondelete='CASCADE')
    )
    title = Column(String(256))
    text = Column(JSONType)
    created_date = Column(DateTime)

    def __init__(self, prosetype_id, title, text):
        self.prosetype_id = prosetype_id
        self.title = title
        self.text = text
        self.created_date = datetime.datetime.utcnow()


class Grock(Base):
    id = Column(UUIDType(binary=False), default=uuid.uuid4, primary_key=True)
    prose_id = Column(
        UUIDType(binary=False),
        ForeignKey('prose.id', ondelete='CASCADE')
    )
    reaction = Column(String(10))
    created_date = Column(DateTime)

    def __init__(self, prose_id, reaction):
        self.prose_id = prose_id
        self.reaction = reaction
        self.created_date = datetime.datetime.utcnow()
