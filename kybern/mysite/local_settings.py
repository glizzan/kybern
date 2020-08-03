DEBUG = True
SECRET_KEY = '_1ds_$#sknsg7rvr4jqv@re7os*$g-!%5+!jjkkqwqdw61d+=d'


#########################
### Database settings ###
#########################


# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#     }
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'kybern_db',
        'USER': 'kybern_db_superuser',
        'PASSWORD': 'elephant',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}


######################
### Email Settings ###
######################

EMAIL_HOST = "localhost"
EMAIL_PORT = 1025
