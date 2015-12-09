from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy import UniqueConstraint

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
    # Category name is unique since it's used for routing
    name = Column(String(STRING_SIZE), nullable=False, unique=True)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'name': self.name,
        }

class Item(Base):
    __tablename__ = 'item'

    id = Column(Integer, primary_key=True)
    # Item name is unique since it's used for routing
    name = Column(String(STRING_SIZE), nullable=False, unique=True)
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
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'picture': self.picture,
            'category_id': self.category_id,
        }

engine = create_engine('sqlite:///catalog.db')
#engine = create_engine('postgresql://catalog:catalog@localhost/catalog')
Base.metadata.create_all(engine)
