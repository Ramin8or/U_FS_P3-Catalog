from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item, User

# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
db_session = DBSession()

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
    db_session.add(category)
db_session.commit()

# Create staff user
staff_user = User(name="Staff", email="staff@thiscatalog.com", picture='')
db_session.add(staff_user)
db_session.commit()

# Add a couple of items
item = Item(name="Antique table from 17th century", 
            description="Like new!",price="1800.00",
            picture="",category_id=1,user_id=1)
db_session.add(item)
item = Item(name="Ikea kitchen table", 
            description="Looks like an antique table",price="18.00",
            picture="",category_id=1,user_id=1)
db_session.add(item)
db_session.commit()

print "Added catalog categories and items."
