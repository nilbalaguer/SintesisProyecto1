from flask import Flask, render_template, request, session, redirect, url_for, flash, make_response
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired
from werkzeug.security import check_password_hash
from datetime import datetime


app = Flask(__name__)
app.secret_key = 'a_random_secret_key'

# Formulari
class LoginForm(FlaskForm):
    username = StringField('Nom d’usuari', validators=[DataRequired()])
    password = PasswordField('Contrasenya', validators=[DataRequired()])
    submit = SubmitField('Inicia sessió')

#TEST!! BORRAR LUEGO
def get_user_by_username(username):
    fake_db = {
        "test_user": {
            "password": "pbkdf2:sha256:260000$example_hash",
            
        }
    }
    return fake_db.get(username)

@app.route('/', methods=['GET', 'POST'])
def index():
    #Cookies
    if 'session_id' not in session:
        session['session_id'] = str(datetime.now())  
        flash("S'ha reiniciat la sessió. Torna-ho a intentar.", 'warning')
        return redirect(url_for('index'))

    
    user_ip = request.remote_addr
    username = session.get('username')

   
    form = LoginForm()

    if form.validate_on_submit():
        input_username = form.username.data
        input_password = form.password.data

        # Comprovación de existencia
        user = get_user_by_username(input_username)
        if user:
            # Comprovación de que el usuario no esté vacío
            if 'password' in user and user['password']:
                if check_password_hash(user['password'], input_password):
                    session['username'] = input_username  #Igual que en PHP guarda la sesión
                    flash('Has iniciat sessió correctament!', 'success')
                else:
                    flash('Contrasenya incorrecta. Torna-ho a provar.', 'error')
            else:
                flash('No s’ha configurat cap contrasenya per aquest usuari.', 'error')
        else:
            flash('Usuari no trobat.', 'error')

   
    context = {
        'ip_address': user_ip,
        'username': username,
        'form': form
    }
    return render_template('information.html', **context)

if __name__ == "__main__":
    app.run(debug=True)