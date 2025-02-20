import datetime
from flask import Blueprint, jsonify, render_template, redirect, url_for, flash, request
from flask_login import current_user, login_user, logout_user, login_required
from sqlalchemy import text
from .forms import LoginForm, RegisterForm, ReservaForm, CancelaReservaForm, PerfilForm
from .models import User, Reserves, Ocupacions, ParkingLog
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

        result = Reserves.query.filter_by(id_parking=placa, data=data_reserva).first()
        if result == None:
            nova_reserva = Reserves(id_parking=placa, id_usuari=id_usuari, data=data_reserva)
            db.session.add(nova_reserva)
            db.session.commit()
            return redirect(url_for('main.reservas'))
        else:
            flash("Error al conseguir reservar, la plaça ja esta ocupada")

    return render_template('reservas.html', form=form, usuari_id=usuari_id)

#Porta a la pagina de perfil
@main_bp.route('/perfil', methods=['GET', 'POST'])
@login_required
def perfil():
    form = PerfilForm()

    id_usuario = current_user.id
    username = current_user.username
    name = current_user.email
    plate = current_user.plate

    if not form.is_submitted():
        form.plate.data = plate

    if form.validate_on_submit():
        plate = form.plate.data

        usuario = User.query.get(id_usuario)
        if usuario:
            usuario.plate = plate
            db.session.commit()

        return redirect(url_for('main.perfil'))

    return render_template(
        'perfil.html',
        username=username,
        name=name,
        plate=plate,
        form=form
    )

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


#API per a el sensor de porta, si retorna negative es que no hi ha reserva o matricula registrada, si torna positive es que hi existeix una reserva
@main_bp.route("/api/checkMatricula", methods=['POST'])
def checkMatricula():
    data = request.get_json()
    matricula = data.get('matricula')
    accio = data.get('accio')

    print(str(accio)+str(matricula))

    fecha_actual = datetime.date.today()

    if not matricula:
        return jsonify({"check": "negative",
                        "message": "Error al llegir matricula"}), 200

    query = text("SELECT id FROM user WHERE plate = :matricula")
    result = db.session.execute(query, {'matricula': matricula})

    if result.rowcount == 0:
        return jsonify({"check": "negative",
                        "message": "Matricula o Usuari no trobat"}), 200

    user_id = result.fetchone().id

    query2 = text("SELECT id_parking FROM reserves WHERE id_usuari = :id_usuari AND data = :fecha")
    result2 = db.session.execute(query2, {'id_usuari': user_id, 'fecha': fecha_actual})

    if result2.rowcount == 0:
        return jsonify({"check": "negative",
                        "message":"Ninguna reserva trobada, Si us plau reservi abans d'entrar"})

    now = datetime.datetime.now()

    hora = now.hour
    minuto = now.minute

    hora_actual = str(now.day)+":"+str(now.month)+":"+str(now.year)+"T"+str(hora)+":"+str(minuto)

    nou_registre = ParkingLog(plate=matricula, accio=accio+","+str(hora_actual))
    db.session.add(nou_registre)
    db.session.commit()

    return jsonify({"check": "positive",
                    "message":"Reserva Trobada, Obrin Porta..."})


#API per ocupar plaçes, aquesta comanda sera operada per els sensors de cada plaça
@main_bp.route("/api/ocupar", methods=['POST'])
def ocupar():
    data = request.get_json()
    accio = data.get('accio')
    placa = data.get('placa')

    #Afegir una ocupacio a la BBDD
    if (accio == "ocupar"):
        intentarocupar = Ocupacions.query.filter_by(placa=placa).first()
        if intentarocupar == None:
            nova_ocupacio = Ocupacions(placa=placa)
            db.session.add(nova_ocupacio)
            db.session.commit()
            return jsonify({"message": "Ocupat",
                            "placa": placa}), 200
        else:
            return jsonify({"message": "Error: Aquesta plaça ja esta ocupada"}), 400
    
    #Eliminar una ocupacio de la BBDD
    elif (accio == "lliurar"):
        eliminar_ocupacio = Ocupacions.query.filter_by(placa=placa).first()
        try:
            db.session.delete(eliminar_ocupacio)
            db.session.commit()
            return jsonify({"message": "Lliurat",
                            "placa": placa}), 200
        except:
            return jsonify({"message": "Error: Aquesta ocupacio no existeix"}), 400
    
    else:
        return jsonify({"message": "Error"}), 418



#Tuto
# @main_bp.route('/api/entrada', methods=['POST'])
# def entrada():
#     data = request.get_json(force=True)

    

#     return data