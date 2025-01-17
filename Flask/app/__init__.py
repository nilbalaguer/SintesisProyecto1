from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Inicializar extensiones
db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    # Inicializar extensiones con la app
    db.init_app(app)
    login_manager.init_app(app)

    login_manager.login_view = 'auth.login'

    # Registrar blueprints después de inicializar extensiones
    from .routes import main_bp
    from .routes import auth_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')

    return app

# Importar `User` después de que `db` esté definido
from .models import User

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


