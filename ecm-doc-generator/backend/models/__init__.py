from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

def init_db(db_path='database/ecm_docs.db'):
    engine = create_engine(f'sqlite:///{db_path}')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()

from .company import Company
from .document import Document
from .generation_log import GenerationLog

__all__ = ['Base', 'init_db', 'Company', 'Document', 'GenerationLog']
