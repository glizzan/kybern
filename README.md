# kybern

## Installation

1. Make directory for project `mkdir kybern`
1. Change into directory: `cd kybern`
1. Create Python3 virtual environment: `python3 -m venv testenv`
1. Fork the repo on GitHub
3. Clone your fork: `git clone <your name>/kybern`
4. `cd kybern`
5. Go to glizzan-concord. Run `create_dist.sh`. This will create the package
   so you can install concord as a dependency of kybern.
6. `pip install --upgrade pip`
7. `pip install -r requirements.txt`
8. `cd kybern`
9. `python manage.py migrate`
10. `python manage.py makemigrations accounts`
11. `python manage.py makemigrations groups`
12. `python manage.py migrate`
13. `python manage.py makemigrations actions`
14. `python manage.py makemigrations communities`
15. `python manage.py makemigrations conditionals`
16. `python manage.py makemigrations permission_resources`
17. `python manage.py makemigrations resources`
18. `python manage.py migrate`
19. `python manage.py runserver`
`python manage.py makemigrations groups`
