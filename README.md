**Udacity Full-Stack Nanodegree Project 3: Catalog App** *(U_FS_P3-Catalog)*

# Introduction
This is the third project for Udacity Full-Stack Nanodegree. For more information about the project assignment please refer to [this document.](https://docs.google.com/document/d/1jFjlq_f-hJoAZP8dYuo5H3xY62kGyziQmiv9EPIA7tM/pub?embedded=true)

This implementation of the Catalog Application presents a list of items for sale listed by category. All users can view the catalog. Users authenticated with their Google account can post new items, including a picture of the item. Users who posted their own items can also edit and delete them. Catalog information is also presented via JSON and ATOM end-points. 

The model and controller portion of this project was inspired by "Full Stack Foundations" and "Authentication & Authorization: OAuth" Udacity courses taught by Lorenzo Brown. The views of the application were implemented using components from Bootstrap.

# Setup and pre-requisites
Here's what you should do to run the project:

1. Install Vagrant and VirtualBox
2. Clone the U_FS_P3-Catalog repository
3. Go to the vagrant directory under U_FS_P3-Catalog
4. Launch the Vagrant VM (vagrant up)
5. Connect to the VM (vagrant ssh)
6. Go to the shared project location (cd /vagrant/catalog)
7. Create the catalog database (python database_setup.py)
8. Populate the database with sample data (python populate_db.py)
9. Run the Catalog web server (python project.py)
10. Access and test the Catalog App by visiting http://localhost:8000 locally

# Project design
This application relies on Flask to create a web server for a catalog application. Declarative SqlAlchemy in Flask is used which is similar to Django. The database model is represented in database_setup.py. This is were the tables for Category, Item, and User are defined in an Object Relation Mapping using SqlAlchemy in Flask. Populate_db.py is used to populate the database with sample items and categories. The controller is represented in the project.py file. The routing mechanism is used heavily to control the flow of the application.
The view of the application is represented by the html files under the template sub-directory. The UI is designed to work on any size device by using the Bootstrap CSS components. Additional CSS customization is done using CSS files located in the static sub-directory. 
The NavBar Bootstrap component is used to show the application brand and actions. 
