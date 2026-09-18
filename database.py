from models import db


def init_database(app):
    """
    Connect the SQLAlchemy database to the Flask app
    and create the database tables.
    """

    db.init_app(app)

    with app.app_context():
        db.create_all()