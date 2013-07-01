#!/bin/bash

mysqladmin -uroot drop library
mysqladmin -uroot create library

source ../venv/bin/activate
python manage.py syncdb
python manage.py initdata
