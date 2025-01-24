from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, LargeBinary, JSON
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine("sqlite:///database.db")
Base = declarative_base(engine)
Session = sessionmaker(bind=engine)

class ImageTable(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    data = Column(LargeBinary)

class DatasetTable(Base):
    __tablename__ = "datasets"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    timestamp = Column(Integer)
    items = Column(JSON)

@contextmanager
def get_session():
    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()

def init_db():
    Base.metadata.create_all(engine)

def create_image(name: str, data: bytes) -> ImageTable:
    with get_session() as session:
        image = ImageTable(name=name, data=data)
        session.add(image)
        return image
def get_image_by_id(id: int) -> ImageTable:
    with get_session() as session:
        return session.query(ImageTable).filter_by(id=id).first()

def delete_image(image: ImageTable) -> None:
    with get_session() as session:
        session.delete(image)

def create_dataset(name: str, timestamp: int, items: dict) -> DatasetTable:
    with get_session() as session:
        dataset = DatasetTable(name=name, timestamp=timestamp, items=items)
        session.add(dataset)
        return dataset

def get_dataset_by_id(id: int) -> DatasetTable:
    with get_session() as session:
        return session.query(DatasetTable).filter_by(id=id).first()

def get_dataset_by_name(name: str) -> DatasetTable:
    with get_session() as session:
        return session.query(DatasetTable).filter_by(name=name).first()

def update_dataset(dataset: DatasetTable, items: dict) -> None:
    with get_session() as session:
        dataset.items = items
        session.add(dataset)

def delete_dataset(dataset: DatasetTable) -> None:
    with get_session() as session:
        session.delete(dataset)