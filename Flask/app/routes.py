from flask import Blueprint, jsonify, render_template, redirect, url_for, flash, request
from flask_login import current_user, login_user, logout_user, login_required
from sqlalchemy import text
from .forms import LoginForm, RegisterForm, ReservaForm, CancelaReservaForm
from .models import User, Reserves
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
        
        user = User(username=form.username.data, email=form.email.data, plate=form.plate.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Account created successfully.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)

@main_bp.route('/apireserves', methods=['GET'])
def api_reserves():
    #Consula directa a la bbdd de les reserves actuals
    query = text("SELECT id_parking, id_usuari, data, id FROM reserves")
    result = db.session.execute(query)
    
    data = [{'id_parking': row[0], 'id_usuari': row[1], 'data': row[2], 'id':row[3]} for row in result]
    
    return jsonify(data)

#Obtindre ocupacions actuals del parking
@main_bp.route("/apiocupacions", methods=['GET'])
def api_ocupacions():
    query = text("SELECT placa FROM ocupacions")
    result = db.session.execute(query)

    data = [{'placa': row[0]} for row in result]

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

    usuari_id = current_user.id

    form.id_usuari.data = current_user.id

    if form.validate_on_submit():
        data_reserva = form.dataReserva.data
        placa = form.placa.data
        id_usuari = form.id_usuari.data

        nova_reserva = Reserves(id_parking=placa, id_usuari=id_usuari, data=data_reserva)
        db.session.add(nova_reserva)
        db.session.commit()
        return redirect(url_for('main.reservas'))

    return render_template('reservas.html', form=form, usuari_id=usuari_id)

#Porta a la pagina de perfil
@main_bp.route('/perfil')
@login_required
def perfil():

    username = current_user.username
    name = current_user.email
    plate = current_user.plate

    return render_template('perfil.html', username = username, name=name, plate=plate)

#Porta a la pagina de cancelacio de reserva
@main_bp.route("/cancelarReserva", methods=['GET', 'POST', 'DELETE'])
@login_required
def cancelarReserva():
    form = CancelaReservaForm()

    form.idReserva.data = request.args.get('id')
    form.id_usuari.data = request.args.get('user') 

    flash(str(form.id_usuari.data) + " " + str(current_user.id))

    # Validación del formulari
    if form.validate_on_submit():
        cancelareserva = form.idReserva.data
        reserva = Reserves.query.filter_by(id=cancelareserva).first()

        if reserva and reserva.id_usuari == current_user.id:
            db.session.delete(reserva)
            db.session.commit()
            flash("Reserva eliminada correctament.")
        else:
            flash("No s'ha trobat la reserva")

        return redirect(url_for('main.reservas'))

    return render_template('cancelarReserva.html', usuari_id=current_user.id, form=form)