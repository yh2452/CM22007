"""Flask config file

Used to configure all the Flask settings/set up routes. 
"""

from flask import Flask
from .auth import auth as auth_bp
from .routes import main as main_bp

def create_app():
    app =  Flask(__name__)
    
    app.config['SECRET_KEY'] = 'dev'
    
    # load blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    
    return app