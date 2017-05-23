from flask_security import (
    SQLAlchemyUserDatastore,
    UserMixin,
    RoleMixin,
)
from sqlalchemy.ext.declarative import (
    declarative_base,
    declared_attr,
    as_declarative
)
from sqlalchemy.orm import relationship, backref
from sqlalchemy import (
    Table,
    Column,
    Integer,
    String,
    Boolean,
    ForeignKey,
    Text,
    DateTime,
    SmallInteger,
    PrimaryKeyConstraint
)


def SetupModels(db):
    # db is a flask_sqlalchemy instance

    Base = db.Model

    # Define models
    class RoleUsers(Base):
        __tablename__ = 'roles_users'
        id = Column(Integer(), primary_key=True)
        user_id = Column(Integer(), ForeignKey('users.id'))
        role_id = Column(Integer(), ForeignKey('roles.id'))


    class Role(Base, RoleMixin):
        __tablename__ = 'roles'
        id = Column(Integer(), primary_key=True)
        name = Column(String(80), unique=True)
        description = Column(String(255))


    class User(Base, UserMixin):
        __tablename__ = 'users'
        id = Column(Integer, primary_key=True)
        email = Column(String(255), unique=True)
        password = Column(String(255))
        active = Column(Boolean())
        confirmed_at = Column(DateTime())
        roles = relationship('Role',
                             secondary='roles_users',
                             backref=backref('users', lazy='dynamic'))

    return SQLAlchemyUserDatastore(db, User, Role)


def SetupUsers(user_datastore):
    user_datastore.find_or_create_role(name='prose_admin', description='prose administrator')
    if not user_datastore.get_user('test@example.com'):
        user_datastore.create_user(email='test@example.com', password='test123')
    user_datastore.add_role_to_user('test@example.com', 'prose_admin')
