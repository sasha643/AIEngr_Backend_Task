# AIEngr Backend Setup Guide

## Prerequisites

Ensure you have the following installed:
- Python (>=3.10)
- pip (Python package manager)
- virtualenv

```bash
# Clone the repository
git clone https://github.com/sasha643/AIEngr_Backend_Task.git
cd AIEngr_Backend
```

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py makemigrations authentication
python manage.py migrate

# Run the Django development server
python manage.py runserver 0.0.0.0:8000
