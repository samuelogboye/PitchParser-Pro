import os
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask import Flask, request
from flask_redis import FlaskRedis
from celery import Celery
from flask_migrate import Migrate
# from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from pitch.config import DevelopmentConfig, TestingConfig, Config, ProductionConfig
from flasgger import Swagger
from pitch.utils.logger import log_warning
from flask_caching import Cache
import yaml

db = SQLAlchemy()
migrate = Migrate()
# bcrypt = Bcrypt()
jwt = JWTManager()

swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'apispec_1',
            "route": '/apispec_1.json',
            "rule_filter": lambda rule: True,  # all in
            "model_filter": lambda tag: True,  # all in
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/apidocs/",
}

swagger_template = {
    "info": {
        "title": "PitchParser Pro API Documentation",
        "description": "This is a custom API documentation for a \
            simple PitchParser Pro with Flask.",
        "version": "1.0.0",
        "termsOfService": "/terms",
        "contact": {
            "email": "ogboyesam@gmail.com"
        },
        "license": {
            "name": "MIT",
            "url": "https://opensource.org/licenses/MIT"
        }
    },
    "host": "", # Initially empty
    "basePath": "/",  # Base path for the APIs
    "schemes": [
        "http",
        "https"
    ],
    "securityDefinitions": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "Enter your bearer token in the format **Bearer &lt;token>**"
        }
    },
    "security": [
        {
            "Bearer": []
        }
    ],
    "operationId": "get_my_data",
    "produces": [
        "application/json"
    ],
    "consumes": [
        "application/json"
    ],
    "tags": [
        {
            "name": "pitch",
            "description": "PitchParser Pro related endpoints"
        }
    ]
}

# Create an instance of Swagger
swagger = Swagger()

#Create an instance of the cach
cache = Cache()

def create_app():
    """
    Create a new instance of the app with the given configuration.

    :param config_class: configuration class
    :return: app
    """
    # Initialize Flask-

    app = Flask(__name__)

    # Load Configuration
    config_map = {
        'development': DevelopmentConfig,
        'testing': TestingConfig,
        'production': ProductionConfig
    }

    env = os.getenv('FLASK_ENV', 'development')
    app.config.from_object(config_map.get(env, Config))

    # from pitch.celery.celery import make_celery
    # celery = make_celery(app)
    # app.celery = celery

    if app.config["SQLALCHEMY_DATABASE_URI"]:
        print("using db")

    # # Load Swagger content from the file
    # with open("swagger_config.yaml", "r") as file:
    #     swagger_config = yaml.load(file, Loader=yaml.FullLoader)
    # # Initialize Flasgger with the loaded Swagger configuration
    # Swagger(app, template=swagger_config)

    #initialize the caching system
    cache.init_app(app)

    # Redis (Caching)
    # redis_client = FlaskRedis(app)

    
    # Initialize SQLAlchemy
    db.init_app(app)
    migrate.init_app(app, db)
    # bcrypt.init_app(app)
    jwt.init_app(app)

    # Initialize CORS
    allowed_origins = os.getenv('ALLOWED_ORIGINS')
    if allowed_origins is None:
        log_warning(
            "createapp()", 
            "ALLOWED_ORIGINS environment variable not set. Allowing all origins."
        )
        allowed_origins = '*'
    else:
        allowed_origins = allowed_origins.split(',')
    CORS(app, origins=allowed_origins, supports_credentials=True)

    # imports blueprints
    from pitch.auth.routes import auth_bp
    from pitch.parsers.routes import parser_bp
    from pitch.errors.handlers import error

    # register blueprint
    app.register_blueprint(error)
    app.register_blueprint(auth_bp, url_prefix="/api/v1/auth")
    app.register_blueprint(parser_bp, url_prefix="/api/v1/parser")
   
     # Update Swagger host dynamically
    with app.test_request_context():
        from pitch.utils.logger import log_debug # pylint: disable=import-outside-toplevel

        swagger_template["host"] = os.getenv('SWAGGER_HOST', request.host)
        Swagger(app, config=swagger_config, template=swagger_template)
        log_debug(
            "createapp.update_swagger_host()", f"Swagger host updated- {swagger_template['host']}")
        
    # Import models before creating tables
    from pitch.models.user import User, RefreshToken
    from pitch.models.pitch_deck import PitchDeck
    from pitch.models.pitch_deck_slide import PitchDeckSlide

    # create db tables from models if not exists
    with app.app_context():
        try:
            db.create_all()
        except Exception as e: # pylint: disable=broad-exception-caught
            from pitch.utils.logger import log_error # pylint: disable=import-outside-toplevel
            log_error("create_app()", f"An error occurred: {e}")

    return app #, celery