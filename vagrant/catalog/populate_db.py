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
for i in range(1,6):
    # Category 1 is "All Categories", category 9 is cars+trucks
    rand_price = random.randint(400,10000)
    item = Item(name=str(i)+" Priced to sell!", 
                description="Cras justo odio, dapibus ac facilisis in, egestas eget quam.", 
                price=str(i)+','+str(i * 115)+'.00',
                category_id=9,  
                picture='car_'+str(i)+".jpg",
                user_id=1)
    db_session.add(item)
db_session.commit()

print "Populated database with category, user and items."
