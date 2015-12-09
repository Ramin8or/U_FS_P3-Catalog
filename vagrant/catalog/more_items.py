from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item, User
import random

# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
#engine = create_engine('postgresql://catalog:catalog@localhost/catalog')
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
db_session = DBSession()

# Populate database with a few items
count = 0
for i in range(6,50007):
    # Category 1 is "All Categories", category 9 is cars+trucks
    rand_cat = 9 if i < 15000 else random.randint(2,20)
    rand_pic = random.randint(1,40)
    rand_price = random.randint(500,20000)
    item = Item(name="Item "+str(i), 
                description="Test "+str(i), 
                price=str(rand_price),
                category_id=rand_cat,  
                picture='pic_'+str(rand_pic)+".jpg",
                user_id=1)
    db_session.add(item)
    count = count + 1
db_session.commit()

print "Populated database with %d items." % (count)
