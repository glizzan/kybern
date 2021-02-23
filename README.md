# Kybern

Kybern is a prototype website built using [Concord](https://github.com/glizzan/glizzan-concord), a framework for implementing user-controlled permissions and governance structures. It showcases the functionality of Concord (and also allows developers to test that they've successfully built mechanisms for extensbility into Concord). The alpha prototype is live at [Kybern.org](https://www.kybern.org/). The site is currently neither secure or reliable, so please do not store important or private information on it.

This project is maintained by the [Glizzan organization](https://www.glizzan.com/) and surrounding community. To join, please email glizzanplatform@gmail.com to ask for an invite to [our Zulip discussion space](https://glizzan.zulipchat.com/). Please note: this project uses the [Contributor Covenant](https://www.contributor-covenant.org/version/2/0/code_of_conduct/) as our Code of Conduct, and by participating you agree to abide by its terms.

Kybern has been released under a custom license, the [Concord Cooperative License](https://github.com/glizzan/kybern/blob/master/license.md). This license is more restrictive than a free software / open source software license. If you believe that your intended use might not fall under the terms of that license, please contact us to discuss alternatives

## Installation

1. Create a fork of this repository
1. Go to the directory which contains your clone of the Concord repo.  If you followed the installation instructions in the Concord repo, this directory is called 'Glizzan'.
1. Clone your fork: `git clone <your name>/kybern`
1. Change into the directory you just cloned: `cd kybern`
1. Install postgres and set up the database (see instructions below) or swap the backend in settings.py by uncommenting the sqlite3 backend and commenting the postgres backend.
1. Create Python3 virtual environment: `python3 -m venv testenv`
1. Activate the virtual environment: `source testenv/bin/activate`
1. Check pip for upgrades: `pip install --upgrade pip`
1. Install requirements: `pip install -r requirements.txt`
1. Go to glizzan-concord and run the following command to create a package to install in Kybern: `bash ./create_dist.sh`
1. Return to the kybern directory and install the newly created package: `pip install ../glizzan-concord/dist/concord-0.0.1.tar.gz`
1. Change into subdirectory: `cd kybern`
1. Run existing migrations: `python manage.py migrate`
1. Start the server: `python manage.py runserver`

You should now be able to view the site. You will need to register on the site and then log in before you can use most of the functionality.  Registration involves an email confirmation step, so before registering on the site you will need to set up a local email server.  To do this, open a separate terminal window and type:

`python -m smtpd -n -c DebuggingServer localhost:1025`

Now when you register on the site, an email will be sent to the local server, and will
be viewable in that separate tab.  Go ahead and register via the browser, using an
access code from `accounts/forms.py`.

The email sent to the local server should include an activation link. Cut and paste this activation link into your browser to active your user. You should see a response in the browser telling you that you are know able to log in - go ahead and do so.  You should
be all set!

### Working with Javascript

By default, our Javascript is saved as staticfiles and loaded using the static template utility. When making changes to the Javascript, you'll want to re-build the files with the command `npm run build`. You'll then need to collect the new files with `python manage.py collectstatic`.

This can be tedious when working intensively with the Javascript files, so there's another option: webpack_loader. To switch from staticfiles to webpack_loader, go to `settings.py` and change the variable LOAD_JS_WITH_WEBPACK to true. This will temporarily break the site as we need our Javascript files served from somewhere. Open up a new terminal window, cd into the frontend directory, and type `npm run serve` to serve the files. The site should work again, and should automatically update when you change or add Vue components, routes, etc.

### Updating Concord and re-installing in Kybern

If you update Concord and need to reinstall it in Kybern, the following command, when run from the top level of the Concord directory, should update the package, uninstall and reinstall in Kybern.  It assumes the directory structure specified in the two installation readmes in the Concord and Kybern repos.

`bash ./create_dist.sh; cd ../kybern; source venv/bin/activate; pip uninstall -y concord; pip install ../glizzan-concord/dist/concord-0.0.1.tar.gz; deactivate; cd ../glizzan-concord/`

Remember that if you make a db change in Concord, you'll need to run makemigrations in Concord, reinstall the package in kybern, and then run migrate in Kybern.


### Installing postgres and setting up the database

1. download postgres
1. to start postgres, type `sudo -u postgres -i`
1. to start psql, type `psql`
1. type `CREATE DATABASE kybern_db; CREATE USER kybern_db_superuser WITH PASSWORD 'elephant'; GRANT ALL PRIVILEGES ON DATABASE kybern_db TO kybern_db_superuser; ALTER USER kybern_db_superuser CREATEDB; ALTER ROLE kybern_db_superuser SET client_encoding TO 'utf8'; ALTER ROLE kybern_db_superuser SET default_transaction_isolation TO 'read committed'; ALTER ROLE kybern_db_superuser SET timezone TO 'UTC';`
1. to leave psql, type `\q`
1. to leave postgres, type `exit`

As long as you're just developing locally, you can keep the default password 'elephant' but make sure to change  it for anything production-like.

Note for installing postgres on Mac OSX: If you're using [Postgres.app](https://postgresapp.com/), you'll need to modify your python PATH so that the instillation file can find your pg_config file in order to install all of the requirements.

For example, add this line to your `.rc` configuration file:

`PATH=$PATH:/Applications/Postgres.app/Contents/Versions/<current_version>/bin`
