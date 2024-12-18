import requests
from flask import Flask, redirect, request, make_response, render_template, session, flash
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
import os

from app import create_app

app = create_app()
# Cambia el nombre del blueprint en la inicialización
bootstrap = Bootstrap(app)
bootstrap.init_app(app, name="custom_bootstrap")

# Usar una sola instancia de Flask

# Configuración de Flask y Bootstrap
#bootstrap = Bootstrap(app)

# Usar una clave secreta segura
app.config["SECRET_KEY"] = os.urandom(24)

# Configuración de SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:secret@localhost:3306/parking'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Lista de items (esto puede ser movido a un archivo separado si es necesario)
items = ["Huawei", "Xiaomi", "Samsung", "Sony"]

# Modelo de base de datos User
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), unique=True, nullable=False)
    created = db.Column(db.DateTime, default=db.func.current_timestamp())

# Formulario de Login
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Submit')

# Ruta para la página principal
@app.route('/index')
def index():
    user_ip_information = request.remote_addr
    response = make_response(redirect('/show_information'))
    session['user_ip'] = user_ip_information
    return response

# Ruta para mostrar la información del usuario
@app.route('/show_information', methods=['GET', 'POST'])
def show_information():
    user_ip = session.get("user_ip")
    username = session.get("username")
    login_form = LoginForm()

    context = {
        'ip': user_ip,
        'items': items,
        'login_form': login_form
    }

    # Verificar si el formulario se envió correctamente
    if login_form.validate_on_submit():
        username = login_form.username.data
        session['username'] = username
        return render_template("information.html", **context)

    return render_template('information.html', **context)

# Ruta para obtener la ubicación geográfica basada en la IP
@app.route('/')
def hello_world():
    user_ip_information = request.remote_addr
    response = requests.get(f"http://www.geoplugin.net/json.gp?ip={user_ip_information}")

    if response.status_code == 200:
        geo = response.json()
        region = geo.get("geoplugin_regionName", "Desconeguda")
        return f"Se on vius: {region}"
    else:
        return "No es pot obtenir la informació de localització."

# Bloque de código para actualizar contraseñas de usuarios (esto debería ser un script separado)
@app.cli.command('update_passwords')
def update_passwords():
    with app.app_context():
        users = User.query.all()
        for user in users:
            user.password = generate_password_hash("1234", method="pbkdf2:sha256")
            db.session.add(user)
        db.session.commit()
        print(f"S'han actualitzat {len(users)} usuaris amb contrasenyes valides.")

# Configurar y crear la base de datos si no existe
if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(host="0.0.0.0", port=81, debug=True)
