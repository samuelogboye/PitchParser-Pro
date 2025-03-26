'''AuthService with business logic for the auth routes'''
from datetime import timedelta, datetime, timezone
from flask_jwt_extended import create_access_token, create_refresh_token, decode_token
from pitch import db
from pitch.utils.validation import validate_email, validate_password
from pitch.utils.logger import log_success
from pitch.models.user import User, RefreshToken

PASSWORD_VALIDATION_ERROR = 'Password must be at least 8 char, at least one letter and one number'

class AuthService:
    '''Contains the business logic for the auth routes'''

    @staticmethod
    def register_user(email, password):
        '''Registers a new user'''
        if User.query.filter_by(email=email).first():
            return {'message': 'Email already exists'}, 400

        if not validate_email(email):
            return {'message': 'Invalid email address'}, 400

        if not validate_password(password):
            return {
                'message': PASSWORD_VALIDATION_ERROR 
                }, 400

        new_user = User(email=email)
        new_user.set_password(password)

        new_user.insert()
        return {'message': 'User registered successfully'}, 201

    @staticmethod
    def authenticate_user(email, password):
        '''Authenticate a user'''
        user = User.query.filter_by(email=email).first()

        if not user or not user.check_password(password):
            return {'message': 'Invalid credentials'}, 401

        access_token = AuthService._create_access_token(user.id)
        refresh_token = AuthService._create_refresh_token(user.id)

        # Store the new refresh token in the database
        AuthService._store_refresh_token(refresh_token)

        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'message': 'User logged in successfully'
        }, 200

    @staticmethod
    def update_password(user_id, new_password):
        '''Updates a user's password'''
        if not validate_password(new_password):
            return {
                'message': PASSWORD_VALIDATION_ERROR 
                }, 400
        user = User.query.get(user_id)
        user.set_password(new_password)
        return {'message': 'Password updated successfully'}, 200

    @staticmethod
    def change_password(user_id, current_password, new_password):
        '''Changes a user's password'''
        if not validate_password(new_password):
            return {
                'message': PASSWORD_VALIDATION_ERROR 
                }, 400
        user = User.query.get(user_id)
        if not user.check_password(current_password):
            return {'message': 'Invalid current password'}, 401
        user.set_password(new_password)
        return {'message': 'Password updated successfully'}, 200

    @staticmethod
    def refresh_token(user_info):
        '''Refreshes the access token and issues a new refresh token'''
        # Invalidate the old refresh token
        old_token = RefreshToken.query.filter_by(
            token=user_info['token'],
            user_id=user_info['sub']
            ).first()
        if old_token:
            if old_token.used:
                return {'message': 'Invalid token'}, 401
            old_token.used = True
            db.session.commit()
        else:
            return {'message': 'Token not found'}, 401

        # Create new access and refresh tokens
        new_access_token = AuthService._create_access_token(user_info['sub'])
        new_refresh_token = AuthService._create_refresh_token(user_info['sub'])


        # Store the new refresh token in the database
        AuthService._store_refresh_token(new_refresh_token)

        return {
            'access_token': new_access_token,
            'refresh_token': new_refresh_token,
            'message': 'Tokens refreshed successfully'
        }, 200

    # Private Helper Methods
    @staticmethod
    def _create_access_token(user_id):
        '''Creates an access token'''
        return create_access_token(identity=user_id, expires_delta=timedelta(minutes=15))

    @staticmethod
    def _create_refresh_token(user_id):
        '''Creates a refresh token'''
        return create_refresh_token(identity=user_id, expires_delta=timedelta(minutes=60))

    @staticmethod
    def _store_refresh_token(refresh_token):
        '''Stores the new refresh token in the database'''
        # Decode the new refresh token to get the expiry date
        decoded_refresh_token = decode_token(refresh_token)
        expires_at = datetime.fromtimestamp(decoded_refresh_token['exp'], tz=timezone.utc)
        user_id = decoded_refresh_token['sub']

        # Store the new refresh token in the database
        new_token = RefreshToken(
            token=refresh_token,
            user_id=user_id,
            used=False,
            expires_at=expires_at
            )
        new_token.insert()

        # Delete all expired refresh tokens of a user
        AuthService.delete_expired_refresh_tokens(user_id)

    @staticmethod
    def delete_expired_refresh_tokens(user_id):
        '''Deletes expired refresh tokens of a user'''
        now = datetime.now(timezone.utc)
        expired_tokens = RefreshToken.query.filter(
            RefreshToken.user_id == user_id,
            RefreshToken.expires_at < now
            ).all()
        for token in expired_tokens:
            db.session.delete(token)
            log_success(
                'delete_expired_refresh_tokens()', 
                f"{token.token} belonging to {user_id} has expired and deleted successfully")
        db.session.commit()