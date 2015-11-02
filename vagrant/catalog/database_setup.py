from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

STRING_SIZE = 256

Base = declarative_base()

class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(STRING_SIZE), nullable=False)
    email = Column(String(STRING_SIZE), nullable=False)
    picture = Column(String(STRING_SIZE))

class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String(STRING_SIZE), nullable=False)

    # TODO: why is this and the one below necessary? Why not user?
    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'id': self.id,
        }

class Item(Base):
    __tablename__ = 'item'

    name = Column(String(STRING_SIZE), nullable=False)
    id = Column(Integer, primary_key=True)
    description = Column(String(STRING_SIZE))
    price = Column(String(16))
    picture = Column(String(STRING_SIZE))
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'description': self.description,
            'id': self.id,
            'price': self.price,
        }

engine = create_engine('sqlite:///catalog.db')
Base.metadata.create_all(engine)
