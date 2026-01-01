# Pet Social Media

Here is my social media project for pets! I have created this full stack application to allow pet owners to create profiles for their pets, share updates, and connect with other pet owners. The core idea is that social media nowadays can seem angry and predatory with its specific targeting of emotions and personal data, so I wanted to create a more wholesome and lighthearted experience centered around our beloved animal companions where we can all spend some time laughing and enjoying their silly antics.

## Overview

The design of this project follows the general flask web app structure, with clear separation of concerns between models, views, controllers, and templates. The application is built to be modular and extensible. Intentional use of abstraction layers allows for easy swapping of components like databases or front-end frameworks.

## Tech stack

- Backend: Python (Flask)
- Database: SQLite for local development Google Cloud SQL for later in pipeline
- ORM: SQLAlchemy
- Frontend: HTML/CSS/JavaScript (framework-agnostic)
- Dependencies: listed in `requirements.txt`

## Key capabilities

- Account creation, authentication, and profile management
- Create, edit, and display posts (text, images, simple media) (wip)
- Feed aggregation and basic discovery (algo wip)
- Commenting and lightweight reactions
- Configurable privacy controls and moderations tools (wip)

These represent the foundational capabilities. Additional features and improvements will be added iteratively.

## Getting started (developer)

Prerequisites: Python 3.8+, pip, and a virtual environment tool. Optional: Node.js if running a separate frontend.

1. Clone the repository:

```powershell
git clone <repo-url>
cd Pet_Social_Media
```


2. Create and activate a virtual environment, then install Python dependencies:

```powershell
python -m venv .venv 
.venv\Scripts\Activate.ps1 
pip install -r requirements.txt
```

3. Configure environment variables:

- In `.env` file in project root

```

# Flask variables
# ---------------
FLASK_APP = 'wsgi.py'                                     # this is our entry point so when we run flask run in the terminal wsgi.py is called
FLASK_ENV = 'development'                                 # means its in debugging mode (useful for developing our app)
SECRET_KEY = 'thisisourverysecretkeythatnoonewilleverknow'           # Used to encrypt session data. signing cookies or csrf tokens
TESTING = False                                           # True or False. false means normal mode, true means run test cases

# WTForm variables
# ----------------
WTF_CSRF_SECRET_KEY='theothersecret'  # Needed by Flask WTForms to combat cross-site request forgery (csrf attacks).

# Database/ORM Variables
# ---------------
#SQLALCHEMY_DATABASE_URI='sqlite:///pets.db'            #Uncomment for sqlite dev DB
SQLALCHEMY_DATABASE_URI='[Other database URI]'
SQLALCHEMY_ECHO=False

# Repository selection variable
# ----------------
#REPOSITORY='memory'
REPOSITORY='database'

```

Create a `.env` or set variables in your shell before running.

## Running locally 

Start the application using the project's entry point. Adjust commands to your chosen framework or runner.

```powershell
# example for Flask-based entrypoint
$env:FLASK_APP = "wsgi.py"
flask run
```

Or run the WSGI entry directly with Python if configured:

```powershell
python wsgi.py
```

## Testing

Run the test suite (pytest is used in this repository):

```powershell
pip install -r requirements.txt ; pytest -q
```

## Configuration & Data

- Database: On first run, the app will create a local SQLite database file `pets.db` populating it with data from CSVs in `pets/adapters/data/`.
- Mode: Site can be run in Memory Repo mode or Database Repo mode place in `.env` the following `REPOSITORY='database'` and change to `memory` for desired implementation.
- Testing: As of now tests are only configured to run in Memory Repo mode.

