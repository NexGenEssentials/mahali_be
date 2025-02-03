## Mahali Backend 



### Prerequisites

Ensure you have the following installed before proceeding:

1. Python (>=3.8)

2. pip (latest version recommended)

3. Virtual environment tool (venv or virtualenv)

4. PostgreSQL

### Installation Guide

Step 1: Clone the Repository

$ git clone https://github.com/NexGenEssentials/mahali_be.git
$ cd mahali_be

Step 2: Create and Activate Virtual Environment

On macOS/Linux:

$ python3 -m venv venv
$ source venv/bin/activate

On Windows:

$ python -m venv venv
$ venv\Scripts\activate

Step 3: Install Dependencies

$ pip install -r requirements.txt

Step 4: Configure Environment Variables

Create a .env file in the project root and add necessary environment variables:

DJANGO_SECRET_KEY=your_secret_key
DATABASE_URL=your_database_connection_string
DEBUG=True  # Set to False in production

Step 5: Apply Database Migrations
Make sure to creat the database named "mahali" and update your db user credentials before running this command
$ python manage.py migrate

Step 6: Create a Superuser (Optional for Admin Access)

$ python manage.py createsuperuser

Follow the prompts to set up an admin account.

Step 7: Run the Development Server

$ python manage.py runserver

The application should now be accessible at http://127.0.0.1:8000/.