from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, LargeBinary, JSON
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from .schemas import Image, Dataset

engine = create_engine("sqlite:///volume/database.db")
Base = declarative_base()
Session = sessionmaker(bind=engine)


class ImageTable(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    file_type = Column(String)
    data = Column(LargeBinary)

    def as_image(self) -> Image:
        return Image(
            id=self.id, name=self.name, file_type=self.file_type, data=self.data
        )


class DatasetTable(Base):
    __tablename__ = "datasets"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    timestamp = Column(Integer)
    items = Column(JSON)

    def as_dataset(self) -> Dataset:
        return Dataset(name=self.name, timestamp=self.timestamp, items=self.items)


class Database:
    @contextmanager
    def get_session(self):
        session = Session()
        try:
            yield session
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

    def init_db(self):
        Base.metadata.create_all(engine)

    def create_image(self, name: str, file_type: str, data: bytes) -> int:
        with self.get_session() as session:
            image = ImageTable(name=name, file_type=file_type, data=data)
            session.add(image)
            session.flush()
            return image.id

    def get_image_by_id(self, id: int) -> Image:
        with self.get_session() as session:
            return session.query(ImageTable).filter_by(id=id).first().as_image()

    def delete_image_by_id(self, id: id) -> None:
        with self.get_session() as session:
            image = session.query(ImageTable).filter_by(id=id).first()
            session.delete(image)

    def list_datasets(self) -> list[str]:
        with self.get_session() as session:
            return [dataset.name for dataset in session.query(DatasetTable).all()]

    def create_dataset(self, name: str, timestamp: int, items: dict) -> DatasetTable:
        with self.get_session() as session:
            dataset = DatasetTable(name=name, timestamp=timestamp, items=items)
            session.add(dataset)
            return dataset

    def get_dataset_by_id(self, id: int) -> Dataset:
        with self.get_session() as session:
            return session.query(DatasetTable).filter_by(id=id).first().as_dataset()

    def get_dataset_by_name(self, name: str) -> Dataset | None:
        with self.get_session() as session:
            dataset = session.query(DatasetTable).filter_by(name=name).first()
            return dataset.as_dataset() if dataset else None

    def delete_dataset_by_id(self, id: int) -> None:
        with self.get_session() as session:
            dataset = session.query(DatasetTable).filter_by(id=id).first()
            session.delete(dataset)

    def delete_dataset_by_name(self, name: str) -> None:
        with self.get_session() as session:
            dataset = session.query(DatasetTable).filter_by(name=name).first()
            session.delete(dataset)

    def update_dataset_by_id(self, id: int, dataset: Dataset) -> None:
        dataset = dataset.model_dump()
        with self.get_session() as session:
            dataset_table = session.query(DatasetTable).filter_by(id=id).first()
            dataset_table.items = dataset["items"]
            dataset_table.timestamp = dataset["timestamp"]

    def update_dataset_by_name(self, name: str, dataset: Dataset) -> None:
        dataset = dataset.model_dump()
        with self.get_session() as session:
            dataset_table = session.query(DatasetTable).filter_by(name=name).first()
            dataset_table.items = dataset["items"]
            dataset_table.timestamp = dataset["timestamp"]
