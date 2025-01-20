from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, HiddenField, IntegerField
from wtforms.validators import DataRequired, Email, Length, Disabled

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField('Contrasenya', validators=[DataRequired(), Length(min=4)])
    submit = SubmitField('Entrar')

class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=32)])
    username = StringField('Nom d\'usuari', validators=[DataRequired(), Length(max=32)])
    password = PasswordField('Contrasenya', validators=[DataRequired(), Length(min=4)])
    submit = SubmitField('Registrar-se')

class ReservaForm(FlaskForm):
    dataReserva = StringField('Data de Reserva')
    placa = IntegerField('Plaça')
    id_usuari = HiddenField('id_usuari')
    submit = SubmitField('Nova Reserva')

class CancelaReservaForm(FlaskForm):
    idReserva = HiddenField('id', validators=[DataRequired()])
    id_usuari = HiddenField('id_usuari', validators=[DataRequired()])
    submit = SubmitField('Cancelar Reserva')