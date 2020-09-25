# https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/
import os
import dj_database_url


DEBUG = os.environ.get("DEBUG_MODE", False)

SECRET_KEY = os.environ['SECRET_KEY']


#########################
### Database settings ###
#########################


DATABASES = {}
db_from_env = dj_database_url.config(conn_max_age=500)
DATABASES['default'] = db_from_env


############################
### Staticfiles settings ###
############################

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# STATICFILE_DIRS are where we collect static files *from*, can list multiple (for instance, if we're keeping
# static files in individual apps)
STATICFILES_DIRS = (
)

# STATIC_ROOT are where we collect staticfiles *to*
STATIC_ROOT = os.path.join(BASE_DIR, 'mysite', 'static')


######################
### Email Settings ###
######################

EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'apikey'
EMAIL_HOST_PASSWORD = os.environ.get('SENDGRID_API_KEY')
