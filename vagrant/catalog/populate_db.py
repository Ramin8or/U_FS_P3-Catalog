from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item, User
import random

# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
db_session = DBSession()

# Add categories from category_list.txt file
categories = [x.rstrip() for x in open('category_list.txt')]
for category_name in categories:
    category = Category(name=category_name)
    db_session.add(category)
    db_session.commit()

# Create staff user 
staff_user = User(name="Staff", email="ramin@outlook.com", picture="") 
db_session.add(staff_user)
db_session.commit()

# Populate database with a few items
for i in range(0,50):
    rand_id = random.randint(2,20)
    rand_price = random.randint(1,500)
    item = Item(name=str(i)+" Item for sale!", 
                description="Cras justo odio, dapibus ac facilisis in, egestas eget quam.", 
                price=str(rand_price)+'.00',
                category_id=rand_id, 
                picture="", user_id=1)
    db_session.add(item)
    db_session.commit()

print "Added catalog categories and items."
