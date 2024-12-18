import requests
from flask import Flask, redirect, request, make_response, render_template, session, flash
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash

from app import create_app

app = create_app()

items=["Huawei", "Xiaomi", "Samsung", "Sony"]

app = Flask(__name__)
bootstrap = Bootstrap(app)

app.config["SECRET_KEY"]="ç"

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:secret@localhost:3306/parking'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), unique=True, nullable=False)
    created = db.Column(db.DateTime, default = db.func.current_timestamp())

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Submit')

@app.route('/index')
def index():

    user_ip_information = request.remote_addr
    response = make_response(redirect('/show_information'))
    session['user_ip'] = user_ip_information
    return response

@app.route('/show_information', methods=['GET', 'POST'])
def show_information():
    user_ip = session.get("user_ip")

    username = session.get("username")

    login_form = LoginForm()

    context = {
        'ip' : user_ip,
        'items' : items,
        'login_form': login_form
    }

    if login_form.validate_on_submit():
        username = login_form.username.data
        session['username'] = username
        return make_response("information.html", **context)

    return render_template('information.html', **context)

if __name__ == "__main__":
    with app.app_context():
        users = User.query.all()
    for user in users:
        user.password = generate_password_hash("1234", method="pbkdf2:sha256")
        db.session.add(user)

    db.session.commit()
    print(f"S'han actualitzat {len(users)} usuaris amb contrasenyes valides.")

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



if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(host="0.0.0.0", port=81, debug=True)