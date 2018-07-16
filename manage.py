from app import create_app, db
from app.models.exchange import Exchange, ExchangeRate

app = create_app()


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Exchange': Exchange, 'ExchangeRate': ExchangeRate}


def recreate_db():
    db.create_all()