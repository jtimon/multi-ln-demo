
# From https://flask.palletsprojects.com/en/1.1.x/patterns/sqlalchemy/
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# TODO Move to env variables
POSTGRES_URL="db:5432"
POSTGRES_USER="postgres"
POSTGRES_PW="password"
POSTGRES_DB="gateway_db"

DB_URL = 'postgresql+psycopg2://{user}:{pw}@{url}/{db}'.format(user=POSTGRES_USER,pw=POSTGRES_PW,url=POSTGRES_URL,db=POSTGRES_DB)
engine = create_engine(DB_URL, convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()

def init_db():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata. Otherwise
    # you will have to import them first before calling init_db()
    import py_ln_gateway.models
    Base.metadata.create_all(bind=engine)
