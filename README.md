librarysite
===========

A simple library site using the Django framework.

Setup
=====

1. Create the database.
  $ sudo mysqladmin create library
2. Initialize the DB tables.
  $ python manage.py syncdb
3. Collect static files to be served.
  $ python manage.py collectstatic
4. Start the server.
  $ python manage.py runserver

The server will be running at http://localhost:8000/library/.