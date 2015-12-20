from flask import Flask, render_template, request, redirect
from flask import jsonify, url_for, flash, make_response
from flask import session as login_session

from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker

from database_setup import Base, Category, Item, User

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError

from PIL import Image
from resizeimage import resizeimage

from werkzeug import secure_filename

import random, string, httplib2, json, requests, os, datetime

import logging

# Constants
ALL_CATEGORIES = "All Categories" # Used to show all categories
ALL_CATEGORIES_ID = 1   # Category id for 'All Categories'
DEFAULT_CAT = "general" # This category name is used if none is specified
SHOW_LIMIT = 12         # Limit for number of recent tems shown in catalog
APPLICATION_NAME = "Catalog Application"
UPLOAD_FOLDER = "static/"
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
CLIENT_SECRET_FILE = "client_secrets.json" 
APACHE_ROOT = "/var/www/catalog/catalog/"

if __name__ != '__main__':
    # When running under Apache use absolute paths
    UPLOAD_FOLDER = APACHE_ROOT + UPLOAD_FOLDER
    CLIENT_SECRET_FILE = APACHE_ROOT + CLIENT_SECRET_FILE 

CLIENT_ID = json.loads(
    open(CLIENT_SECRET_FILE, 'r').read())['web']['client_id']

logger = logging.getLogger('app')
log_handler = logging.FileHandler(UPLOAD_FOLDER+"application.log")
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
log_handler.setFormatter(formatter)
logger.addHandler(log_handler)
logger.setLevel(logging.DEBUG)

# Start Flask 
app = Flask(__name__)
# Set upload folder and max content size for image uploads
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024 # Limit each upload to 32 MB

# Connect to the appropriate database and create database session
engine = None
if __name__ == '__main__':
    engine = create_engine('sqlite:///catalog.db')
else:
    engine = create_engine('postgresql://catalog:catalog@localhost/catalog')

Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
db_session = DBSession()

@app.route('/login')
def showLogin():
    ''' Create anti-forgery state token '''

    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)

@app.route('/gconnect', methods=['POST'])
def gconnect():
    ''' Implemenation of Google connect '''

    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data
    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets(CLIENT_SECRET_FILE, scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match the app's."
        response.headers['Content-Type'] = 'application/json'
        return response
    # Is current user already connected?
    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Store the access token in the session for later use.
    login_session['credentials'] = credentials.access_token
    login_session['gplus_id'] = gplus_id
    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    data = answer.json()
    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    login_session['provider'] = 'google'
    # see if user exists, if it doesn't make a new one
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id
    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    return output

# User Helper Functions
def createUser(login_session):
    ''' Add a new user to the database '''

    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    db_session.add(newUser)
    db_session.commit()
    user = db_session.query(User).filter_by(email=login_session['email']).one()
    return user.id

def getUserInfo(user_id):
    ''' Get user from db given an id '''
    user = db_session.query(User).filter_by(id=user_id).one()
    return user

def getUserID(email):
    ''' Get user from db given an email '''
    try:
        user = db_session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

@app.route('/gdisconnect')
def gdisconnect():
    ''' 
    Implementation of Google disconnect:
    Revokes a current user's token and reset their login_session
    '''

    # Only disconnect a connected user.
    credentials = login_session.get('credentials')
    if credentials is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % credentials
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] != '200':
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response

@app.route('/disconnect')
def disconnect():
    ''' Disconnect from provider (currently only Google is a provider) '''

    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['credentials']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('showCatalog'))
    else:
        flash("You were not logged in")
        return redirect(url_for('showCatalog'))

@app.route('/')
@app.route('/catalog')
def showCatalog():
    ''' Display the catalog '''

    categories = db_session.query(Category).order_by(asc(Category.name))
    all_cat = categories.filter_by(name=ALL_CATEGORIES).one()
    items = db_session.query(
            Item).order_by(desc(Item.id)).limit(SHOW_LIMIT).all()
    return render_template('catalog.html', 
                            categories=categories, 
                            category=all_cat, items=items)

@app.route('/catalog/<category_name>/')
def showCategory(category_name):
    ''' Show items for selected category '''

    categories = db_session.query(Category).order_by(asc(Category.name))
    category = categories.filter_by(name=category_name).one()
    if category.id == ALL_CATEGORIES_ID:
        items = db_session.query(Item).all()
    else:
        items = db_session.query(Item).filter_by(category_id=category.id).all()
    count = len(items)
    return render_template('category.html', 
                            categories=categories, 
                            category=category, items=items, 
                            count=count)

@app.route('/catalog/<category_name>/<item_name>')
def showItem(item_name, category_name):
    ''' Show item given a name '''

    try:
        item = db_session.query(Item).filter_by(name=item_name).one()
    except:
        flash("Item by the name of %s does not exist!" % (item_name))
        return redirect(url_for('showCategory', category_name=category_name))        
    return render_template('item.html', item=item, category_name=category_name)

@app.route('/catalog/<item_name>/edit', methods=['GET', 'POST'])
def editItem(item_name):
    ''' Edit an item '''

    if 'username' not in login_session:
        return redirect('/login')
    try:
        item = db_session.query(Item).filter_by(name=item_name).one()
    except:
        flash("Item by the name of %s does not exist!" % (item_name))
        return redirect(url_for('/'))

    if login_session['user_id'] != item.user_id:
        return "<script>function myFunction() {alert('You are not authorized to edit this item.');}</script><body onload='myFunction()''>"

    if request.method == 'POST':
        # Note since Name is used for routing, it cannot be changed
        if request.form['description']:
            item.description = request.form['description']
        if request.form['price']:
            item.price = request.form['price']
        db_session.add(item)
        db_session.commit()
        # If picture, save with unique name to static folder and update item.
        if request.files['picture']:
            item.picture = savePicture(request.files['picture'], 
                                       item.id)
            db_session.commit()

        flash('Item Successfully Edited')
        return redirect(url_for('showItem', 
                                item_name=item_name, 
                                category_name=item.category.name))
    else:
        return render_template('editItem.html', item=item)


def savePicture(file, id):
    '''
    Resize and save an uploaded picture for an item into static folder and
    return the filename of the picture.
    '''

    extension = file.filename.rsplit('.', 1)[1]
    if extension.lower() not in ALLOWED_EXTENSIONS:
        flash("Unable to save uploaded picture.")
        return ""

    # Make filename unique and secure
    filename = str(id)+"_"+secure_filename(file.filename)
    uploaded_file = os.path.join(app.config['UPLOAD_FOLDER'],"u_"+filename)
    # First save the original uploaded picture in upload_folder
    file.save(uploaded_file)
    try:
        # Try to resize the picture
        fd_img = open(uploaded_file, 'r')
        img = Image.open(fd_img)
        img = resizeimage.resize_contain(img, [400, 300])
        img.save(os.path.join(app.config['UPLOAD_FOLDER'],filename), img.format)
        fd_img.close()
        os.remove(uploaded_file)
    except:
        # Could not resize, just use the uploaded file instead
        os.rename(uploaded_file, os.path.join(app.config['UPLOAD_FOLDER'], filename))
    return filename

@app.route('/catalog/newItem/test', methods=['GET', 'POST'])
def newItemTest():
    ''' Test Adding a new item '''
    if request.method == 'POST':
        return "Picture" if request.files['picture'] else "No pictures"
    else:
        return render_template('newItemTest.html')

 
@app.route('/catalog/newItem/', methods=['GET', 'POST'])
def newItem():
    ''' Add a new item '''
    logger.debug("newItem called with method: " + request.method)
    if request.method == 'POST':
        logger.debug("POST: " + request.form['name'])
        if request.files['picture']:
            logger.debug("POST: has picture")

    if 'username' not in login_session:
        logger.debug("newItem redirect to login")
        return redirect('/login')

    if request.method == 'POST':
        item_name = ""
        item_desc = ""
        item_cat = DEFAULT_CAT
        item_price = ""

        logger.debug("POST: " + request.form['name'])

        if request.form['name']:
            item_name = request.form['name']
        
        if request.form['category']:
            item_cat = request.form['category']
            if item_cat == ALL_CATEGORIES:
                item_cat = DEFAULT_CAT

        if request.form['description']:
            item_desc = request.form['description']

        if request.form['price']:
            item_price = request.form['price']

        try:
            logger.debug("POST: querying categories")
            categories = db_session.query(Category).order_by(asc(Category.name))

            category = db_session.query(Category).filter_by(name=item_cat).one()
            newItem = Item(name=item_name, 
                           description=item_desc, 
                           price=item_price,
                           category_id=category.id, 
                           picture="", 
                           user_id=login_session['user_id'])
            db_session.add(newItem)
            db_session.commit()
            logger.debug("POST: about to savePicture")

            # If picture, save with unique name to static folder and update item.
            if request.files['picture']:
                newItem.picture = savePicture(request.files['picture'], 
                                              newItem.id)
                db_session.commit()

            flash('Successfully Created: %s' % (newItem.name))
            return redirect(url_for('showItem', 
                                    item_name=newItem.name, 
                                    category_name=newItem.category.name))
        except:
            logger.debug("POST: exception")
            flash('Invalid input, could not create new item. Please specify a unique name, and use a category.')
            db_session.rollback()
            return render_template('newItem.html', categories=categories)

    else:
        logger.debug("GET: querying categories")
        categories = db_session.query(Category).order_by(asc(Category.name))
        logger.debug("GET: returning")
        return render_template('newItem.html', categories=categories)

@app.route('/catalog/<item_name>/delete', methods=['GET', 'POST'])
def deleteItem(item_name):
    ''' Delete an item using POST '''

    if 'username' not in login_session:
        return redirect('/login')

    try:
        item = db_session.query(Item).filter_by(name=item_name).one()
    except:
        flash("Item by the name of %s does not exist!" % (item_name))
        return redirect(url_for('/'))
    if item.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized to delete this item.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        category_name = item.category.name
        db_session.delete(item)
        db_session.commit()
        flash('%s Successfully Deleted' % item.name)
        return redirect(url_for('showCategory', category_name=category_name))
    else:
        return render_template('deleteItem.html', item=item)


app.secret_key = 'super_secret_key'
app.debug = True
# Main application running locally
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
