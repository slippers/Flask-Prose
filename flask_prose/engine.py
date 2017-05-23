try:
    from builtins import object
except ImportError:
    pass


class ProseEngine(object):

    def __init__(self, app=None, storage=None):
        self.app = app
        self.storage = storage
        self.viewmethod_decorators()
        if self.app is not None and self.storage is not None:
            self.init_app(app, storage)

    def init_app(self, app, storage):
        self.app = app
        self.storage = storage
        self.config = self.app.config

        from .views import create_blueprint
        prose_app = create_blueprint(__name__, self)
        # extenral urls
        prefix = self.config.get("PROSE_URL_PREFIX", '/v1')

        self.app.register_blueprint(prose_app, url_prefix=prefix)

        self.app.extensions["FLASK_PROSE_ENGINE"] = self  # duplicate
        self.app.extensions["prose"] = self

    def viewmethod_decorators(self, prose=(), corpora=()):
        """
        these methods are applied in views.create_blueprint

        viewmethod decorators can be appended to the
        MethodView class's decorator.  These wrapper functions
        can facilitate custom things like security.

        they are applied to the class not instance.
        """
        self.prose_api_decorators = prose
        self.corpora_api_decorators = corpora
