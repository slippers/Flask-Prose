from flask import (
    Blueprint,
    abort,
    current_app,
    request,
    redirect,
    url_for,
    make_response,
    render_template
)
from flask_jsontools import (
    jsonapi,
    MethodView,
    methodview,
    SqlAlchemyResponse
)
from sqlalchemy import inspect


def _get_engine(app):
    # use flask.current_app
    return app.extensions["FLASK_PROSE_ENGINE"]


class ProseAPI(MethodView):

    decorators = (jsonapi, )

    @methodview(methods=('GET',))
    def get(self, uuid=None):
        engine = _get_engine(current_app)
        prose = engine.storage.prose(uuid=uuid)
        return SqlAlchemyResponse(prose)


    @methodview(methods=('POST',))
    def post(self):
        prose_id = request.form.get('prose_id')
        reaction = request.form.get('reaction')
        engine = _get_engine(current_app)
        return SqlAlchemyResponse(engine.storage.grock(prose_id, reaction))


class CorporaAPI(MethodView):

    decorators = (jsonapi, )

    @methodview(methods=('GET',))
    def get(self, uuid=None):
        engine = _get_engine(current_app)
        return SqlAlchemyResponse(engine.storage.corpora_list(uuid))

    @methodview(methods=('DELETE',), ifset=('uuid',))
    def delete(self, uuid):
        engine = _get_engine(current_app)
        return engine.storage.corpora_delete(uuid)

    @methodview(methods=('POST',))
    def post(self):
        engine = _get_engine(current_app)
        data = request.files['file'].read()
        label = request.form.get('label')
        corpora_id = engine.storage.corpora_save(label=label, text=data.decode('utf-8'))
        return SqlAlchemyResponse(engine.storage.corpora_list(uuid=corpora_id))


def create_blueprint(import_name, engine):

    prose_app = Blueprint('prose',
                          import_name,
                          template_folder='templates')

    # append custom api decorators
    ProseAPI.decorators = ProseAPI.decorators \
            + engine.prose_api_decorators

    # create the view
    prose_view = ProseAPI.as_view('prose_api')

    # rule
    prose_app.add_url_rule("/prose",
                           view_func=prose_view)

    prose_app.add_url_rule("/prose/<uuid:uuid>",
                           view_func=prose_view)

    CorporaAPI.decorators = CorporaAPI.decorators \
            + engine.corpora_api_decorators

    corpora_view = CorporaAPI.as_view('corpora_api')

    prose_app.add_url_rule('/corpora/<uuid:uuid>',
                           view_func=corpora_view)

    prose_app.add_url_rule('/corpora',
                           view_func=corpora_view)


    return prose_app
