from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
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
print "Created catalog database."


# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

# Now populate the database with some data

# Add categories from category_list.txt file
categories = [x.rstrip() for x in open('category_list.txt')]
cats_loaded = True
DEFAULT_CAT = 'default_cat'
DEFAULT_ITEM = DEFAULT_CAT+';default item;description;0;;'
if not categories:
    print "No categories found in category_list.txt file, using default category only."
    categories = [DEFAULT_CAT]
    cats_loaded = False

for category_name in categories:
    category = Category(name=category_name)
    session.add(category)
session.commit()

# Create staff user
staff_user = User(name="Staff", email="staff@thiscatalog.com", picture='')
session.add(staff_user)
session.commit()

# Add a couple of items
item = Item(name="Antique table from 17th century", 
            description="Like new!",price="1800.00",
            picture="",category_id=1,user_id=1)
session.add(item)
item = Item(name="Ikea kitchen table", 
            description="Looks like an antique table",price="18.00",
            picture="",category_id=1,user_id=1)
session.add(item)
session.commit()

print "Added catalog categories and items."

