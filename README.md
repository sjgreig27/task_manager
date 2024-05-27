# Task Manager

### Quick Start

To quickly spin up the app there is a docker-compose file which can be run.

Firstly, copy the environment file:

```bash
cp .env.template .env
```
The environment file provides defines variables for setting passwords and login credentials on the local database and pgAdmin instance.

```bash
docker-compose up --build -d
```
The docker-compose file spins up a PostgreSQL database and [pgAdmin](http://localhost:8080) instance for inspection of the database as well as the [FastAPI / Piccolo App](http://localhost:8000/login).

The credentials for login to pgAdmin are located in the .env file. The [FastAPI / Piccolo App](http://localhost:8000/login) uses a data migration to pre-seed the database with some example data. It should be noted that the password for the pre-defined users (smclean, lmclean and jmclean) are all the identical - namely the term "password". It should be noted that the user jmclean is the assignee of those tasks which include subtasks.

The stack can be brought back down by running:
```bash
docker-compose down -v
```
This will also remove any associated volumes if you want to start from a clean slate.

### Install Requirements
With the stack up and running in docker-compose, run the following to run the Piccolo tests from the root of the project:

As a prerequisite, follow the installation instructions for [Poetry](https://python-poetry.org/docs/#installation).

```bash
poetry install
poetry shell
piccolo tester run
```

### Running the Test Suite
Once the requirements have been installed the test suite can be run using the Piccolo runner, as follows:
```bash
piccolo tester run
```

### Useful Links
* [Login Page](http://localhost:8000/login/) - Application has basic Session Auth
* [Logout Page](http://localhost:8000/logout/) - Terminates the current session
* [Task Manager Swagger Docs](http://localhost:8000/task_manager/docs) - Details the API endpoints

### Specification
* A user must be able to create, update, list and delete tasks from a REST API
* The application must store tasks in a database
* The application must ensure each task is assigned to a user
* The user must only be able to list the tasks to which they are assigned
* The application must ensure that each task can only have one status from the following - Pending, Doing, Blocked, Done
* The application must maintain a history of the deleted tasks
* The application must support Python3.9 and 3.10
* The application code must be styled using code formatting
* The application code must include type annotations
* The application must be implemented in a lightweight framework
* The application must manage changes to the schemas via migrations in code
* The application should allow for subtasks to be associated with tasks
* The application should allow for the restoration of deleted tasks
* The application should allow for the setting of due dates for tasks
* The application should allow for setting labels for tasks

### Stack
* [FastAPI](https://fastapi.tiangolo.com/) - Lightweight framework
* [Piccolo ORM](https://piccolo-orm.readthedocs.io/en/latest/) - Migrations built into framework, similar to the Django ORM I am more familiar with
* [PostgreSQL](https://www.postgresql.org/) - Easy of setup and containerisation

### Limitations
* Test coverage less than it should be
* No logging added in
* Ideally, would have had a service layer to decouple router endpoints from the ORM logic

