# import jwt
# from pitch import app
from datetime import datetime, timezone
from flask_jwt_extended import decode_token

# def encode_token(payload, algorithm='HS256', expires_in=3600):
#     return jwt.encode(payload, app.config['SECRET_KEY'], algorithm=algorithm, expires_in=expires_in)

# def decode_token(token, algorithms=['HS256']):
#     return jwt.decode(token, app.config['SECRET_KEY'], algorithms=algorithms)


def is_token_expired(token):
    '''Check if token is expired'''
    decoded_token = decode_token(token)
    if not decoded_token:
        return True
    exp_timestamp = decoded_token.get('exp')
    exp_datetime = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
    return exp_datetime < datetime.now(tz=timezone.utc)
