#!/bin/bash

if ! which python ; then
    echo "Error:  Missing required program 'python', please install!"
    exit 1
fi

if ! which mysqladmin ; then
    echo "Error:  Missing required program 'mysqladmin', please install!"
    exit 1
fi

# Create the virtual environment.
if test ! -d venv ; then
    if ! which virtualenv ; then
        echo "Error:  Missing required program 'virtualenv', please install!"
        exit 1
    fi
    virtualenv venv
    source venv/bin/activate
    pip install -r requirements.txt
fi
source venv/bin/activate


# Initialize the database.
mysqladmin -uroot drop library
mysqladmin -uroot create library

python manage.py syncdb
python manage.py initdata
