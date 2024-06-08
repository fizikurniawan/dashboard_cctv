# Django REST Framework App

This is a Django app built with Django REST Framework.

Please see https://ardzix.notion.site/Django-Rest-Framework-5ac1d218c3ff470ba1133bc70601c24e for detailed installation guide.

## Installation:
1. Clone the repository:
   `git clone https://github.com/fizikurniawan/dashboard_cctv_be.git`

2. Create and activate a virtual environment:
   - `python -m venv venv`
   - `source venv/bin/activate`

3. Install the required packages:
   `pip install -r requirements.txt`

4. Apply database migrations:
   `python manage.py migrate`

## Running the App:
To run the Django app, execute the following command:
`python manage.py runserver`

The app will be accessible at http://localhost:8000/.

## API Endpoints:
- Login: /api/auth/login/ (POST)
  - Request Body: username and password
  - Response: Authentication token

## API Documentation:
API documentation is available using Swagger and ReDoc:
- Swagger UI: /swagger/
- ReDoc: /redoc/
