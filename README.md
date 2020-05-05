# kybern

## Installation

1. Create a fork of this repository
1. Go to the directory which contains your clone of the Concord repo.  If you followed the installation instructions in the Concord repo, this directory is called 'Glizzan'.
1. Clone your fork: `git clone <your name>/kybern`
1. Change into the directory you just cloned: `cd kybern`
1. Create Python3 virtual environment: `python3 -m venv testenv`
1. Activate the virtual environment: `source testenv/bin/activate`
1. Check pip for upgrades: `pip install --upgrade pip`
1. Install requirements: `pip install -r requirements.txt`
1. Go to glizzan-concord and run the following command to create a package to install in Kybern: `bash ./create_dist.sh`
1. Return to the kybern directory and install the newly created package: `pip install ../glizzan-concord/dist/concord-0.0.1.tar.gz`
1. Change into subdirectory: `cd kybern`
1. Run existing migrations: `python manage.py migrate`
1. You probably need to manually specify migrations too:
   ```
   python manage.py makemigrations accounts
   python manage.py makemigrations groups
   python manage.py makemigrations actions
   python manage.py makemigrations communities
   python manage.py makemigrations conditionals
   python manage.py makemigrations permission_resources
   python manage.py makemigrations resources
   ```
1. Migrate the newly created migrations: `python manage.py migrate`
1. Start the server: `python manage.py runserver`

You should now be able to view the site. The landing page will give you a 'template not found' error - simply go to /groups/ to get a working landing page.  You will need to register on the site and then log in before you can use it.

If you update Concord and need to reinstall it in Kybern, the following command, when run from the top level of the Concord directory, should update the package, uninstall and reinstall in Kybern.  It assumes the directory structure specified in the two installation readmes in the Concord and Kybern repos.

`bash ./create_dist.sh; cd ../kybern; source venv/bin/activate; pip uninstall -y concord; pip install ../glizzan-concord/dist/concord-0.0.1.tar.gz; deactivate; cd ../glizzan-concord/`
