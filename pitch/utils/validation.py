
'''Validate inputs'''
import re

def validate_email(email):
    ''' Validate Email address'''
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email) is not None

def validate_password(password):
    ''' Validate Password'''
    # Example: Minimum 8 characters, at least one letter and one number
    password_regex = r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$'
    return re.match(password_regex, password) is not None
