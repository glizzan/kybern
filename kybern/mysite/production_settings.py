# https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/


DEBUG = False
SECRET_KEY = os.environ['SECRET_KEY']


#########################
### Database settings ###
#########################


import dj_database_url
DATABASES = {}
db_from_env = dj_database_url.config(conn_max_age=500)
DATABASES['default'].update(db_from_env)
