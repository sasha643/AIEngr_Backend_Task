# AIEngr Backend Setup Guide

## Prerequisites

Ensure you have the following installed:
- Python (>=3.10)
- pip (Python package manager)
- virtualenv

## Clone the repository  

```bash
git clone https://github.com/sasha643/AIEngr_Backend_Task.git
cd AIEngr_Backend
```

## Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

## Install dependencies

```bash
pip install -r requirements.txt
```

## Run migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

## Environment Variables

Create a .env file in the project root with the following values:

- DJANGO_SECRET
- EMAIL_HOST
- EMAIL_PORT
- EMAIL_USER
- EMAIL_PASSWORD
- SECRET_KEY (To encode & decode the auth_token)

## Run the Django development server

```bash
python manage.py runserver
```
