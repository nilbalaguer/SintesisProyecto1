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
    dataReserva = StringField('Data de Reserva', validators=[DataRequired(), Disabled()])
    placa = IntegerField('Plaça', validators=[DataRequired(), Disabled()])
    email = HiddenField('Email')
    submit = SubmitField('Nova Reserva')