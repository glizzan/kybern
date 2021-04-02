release: python ~/kybern/manage.py migrate
web: gunicorn kybern.mysite.wsgi --log-file -
worker: python ~/kybern/manage.py qcluster