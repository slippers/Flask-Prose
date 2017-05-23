from flask import Flask, render_template
from config import configure_app
from flask_sqlalchemy import SQLAlchemy
from flask_prose import FSQLAStorage, ProseEngine
from flask_security import Security
from security_models import SetupModels, SetupUsers

app = Flask(__name__, instance_relative_config=True)

configure_app(app)
db = SQLAlchemy(app)
storage = FSQLAStorage(db=db, bind_key='prose')
engine = ProseEngine(app=app, storage=storage)
user_datastore = SetupModels(db)
security = Security(app, user_datastore)


# errors
@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', title='Page Not Found'), 404

@app.errorhandler(410)
def page_not_found(e):
    return render_template('error.html', title='Page deleted'), 410

@app.errorhandler(403)
def page_not_found(e):
    return render_template('error.html', title='Forbidden'), 403

@app.errorhandler(500)
def page_not_found(e):
    return render_template('error.html', title='Server error'), 500

# execute before first request is processed
@app.before_first_request
def before_first_request():
    db.create_all()
    SetupUsers(user_datastore)
    db.session.commit()
    pass


if __name__ == '__main__':
    app.run()
    print(app.url_map)
