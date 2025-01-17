from flask import Blueprint, jsonify, render_template, redirect, url_for, flash, request
from flask_login import current_user, login_user, logout_user, login_required
from sqlalchemy import text
from .forms import LoginForm, RegisterForm, ReservaForm
from .models import User, Reserva
from . import db

auth_bp = Blueprint('auth', __name__)

main_bp = Blueprint('main', __name__)

#Porta a la pagina d'inici / Mapa del Parking
@main_bp.route('/')
@login_required
def index():
    return render_template('index.html')

#Porta a la pagina de login i realitza aquesta accio
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash('Logged in successfully.', 'success')
            return redirect(url_for('main.index'))
        flash('Invalid email or password.', 'danger')
    return render_template('auth/login.html', form=form)

#Porta a la pagina de registre i registra el usuari al enviar el formulari
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            flash('Email address already exists.', 'danger')
            return redirect(url_for('auth.register'))
        
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Account created successfully.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)


#Mini API para JavaScript del parking
@main_bp.route('/apiparking', methods=['GET'])
def api_reservas():
    #Consulta directa a la bbdd
    query = text("SELECT id, id_usuari, estat FROM parking")
    result = db.session.execute(query)
    
    data = [{'id': row[0], 'id_usuari': row[1], 'estat': row[2]} for row in result]
    
    return jsonify(data)

@main_bp.route('/apireserves', methods=['GET'])
def api_reserves():
    #Consula directa a la bbdd de les reserves actuals
    query = text("SELECT id_parking, id_usuari, data FROM reserves")
    result = db.session.execute(query)
    
    data = [{'id_parking': row[0], 'id_usuari': row[1], 'data': row[2]} for row in result]
    
    return jsonify(data)

#Realitza el Logout de l'usuari
@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))

#Porta a la pagina de reserves
@main_bp.route('/reservas', methods=['GET', 'POST'])
@login_required
def reservas():
    form = ReservaForm()

    if current_user.is_authenticated:
        form.id_usuari.data = current_user.id

    if form.validate_on_submit():
        data_reserva = form.dataReserva.data
        placa = form.placa.data
        id_usuari = form.id_usuari.data

        nova_reserva = Reserva(id_parking=placa, id_usuari=id_usuari, data=data_reserva)
        db.session.add(nova_reserva)
        db.session.commit()
        return redirect(url_for('main.index'))

    return render_template('reservas.html', form=form)

#Porta a la pagina de perfil
@main_bp.route('/perfil')
@login_required
def perfil():
    return render_template('perfil.html')