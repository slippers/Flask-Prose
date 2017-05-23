from .storage import Storage


class FSQLAStorage(Storage):
    """flask_sqlalchemy wrapper class for SQLAStorage
    """
    def __init__(self, db=None, bind_key=None):
        """
        :param db is flask_sqlalchemy SQLAlchemy object
        :param bind_key: (Optional) Reference the database to bind for multiple
        database scenario with binds.
        """
        if db is None:
            raise ValueError("db cannot be None.")

        engine = db.get_engine(db.get_app(), bind=bind_key)

        Storage.__init__(self, engine=engine, bind_key=bind_key)

        db.metadata.reflect(engine)
