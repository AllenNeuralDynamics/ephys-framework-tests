import os
import json

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SECRETS_PATH = os.path.join(BASE_DIR, 'SECRETS')

with open(SECRETS_PATH, 'r') as f:
    secrets = json.load(f)

# SECURITY WARNING: Modify this secret key if using in production!
SECRET_KEY = secrets['security_key']

DEFAULT_AUTO_FIELD='django.db.models.AutoField'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': secrets['dbname'],
        'USER': secrets['user'],
        'PASSWORD': secrets['password'],
        'HOST': secrets['host'],
        'PORT': secrets['port']
    }

}


"""
To connect to an existing postgres database, first:
pip install psycopg2
then overwrite the settings above with:

DATABASES = {

"""

INSTALLED_APPS = ("db",)
