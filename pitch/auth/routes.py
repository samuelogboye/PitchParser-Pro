'''Contains the route and its business logic call to authservice'''
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from pitch.utils.logger import log_route
from pitch.services.auth_service import AuthService

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
@log_route
def register():
    """
    Endpoint to register a user
    ---
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            email:
              type: string
            password:
              type: string
          required:
            - email
            - password
    tags:
      - auth
    responses:
      201:
        description: User registered successfully
        examples:
          application/json:
            message: User registered successfully
      400:
        description: Missing required fields or validation errors
        examples:
          application/json:
            message: Email already exists
    """
    data = request.get_json()

    if not data or not data.get('email') or not data.get('password'):
        return {'message': 'Missing required fields: Email and Password'}, 400

    email = data['email']
    password = data['password']

    response, status = AuthService.register_user(email, password)
    return response, status

@auth_bp.route('/login', methods=['POST'])
@log_route
def login():
    """
    Endpoint to login a user
    ---
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            email:
              type: string
            password:
              type: string
          required:
            - email
            - password
    tags:
      - auth
    responses:
      200:
        description: User logged in successfully
        examples:
          application/json:
            access_token: string
            refresh_token: string
            message: User logged in successfully
      400:
        description: Missing required fields
        examples:
          application/json:
            message: Missing required fields
      401:
        description: Invalid credentials
        examples:
          application/json:
            message: Invalid credentials
    """
    data = request.get_json()

    if not data or not data.get('email') or not data.get('password'):
        return {'message': 'Missing required fields'}, 400

    email = data['email']
    password = data['password']

    response, status = AuthService.authenticate_user(email, password)
    return response, status

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
@log_route
def refresh():
    """
    Endpoint to refresh access token
    ---
    security:
      - Bearer: []
    tags:
      - auth
    responses:
      200:
        description: Tokens refreshed successfully
        examples:
          application/json:
            access_token: string
            refresh_token: string
            message: Tokens refreshed successfully
      401:
        description: Invalid token
        examples:
          application/json:
            message: Invalid token
    """
    current_user = get_jwt_identity()
    jti = get_jwt()['jti']
    # Extract the token from the header
    refresh_token = request.headers.get('Authorization').split()[1]
    user_info = {'sub': current_user, 'jti': jti, 'token': refresh_token}
    response, status = AuthService.refresh_token(user_info)
    return response, status