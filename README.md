# Venezia Stone

It was necessary to implement a large-scale online store for the sale of stones, slabs, etc.
The project was created in a team of 3 people (2 - back on Django REST, including me, 1 - front on React) (2020-2021).

## Getting Started
Python version: 3.7.9

Clone project:
```
git clone https://github.com/pymaster13/venezia_stone.git && cd venezia_stone
```

Create and activate virtual environment:
```
python3 -m venv venv && source venv/bin/activate
```

Install libraries:
```
python3 -m pip install -r requirements.txt
```

Run local Django server:
```
python3 manage.py runserver
```

## Functional

- Users can register and confirm registration, authenticate, reset password, change user data and select products.
- Showing of products from different categories.
- Work with API 1C-system.

### Features

Main libraries that are used : 
* Django 3,
* djangorestframework,
* djoser (for working with users)
* twilio (for sending sms),
* celery and redis (for asynchronous sending sms),
* PIL (for working with images).

