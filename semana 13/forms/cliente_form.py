from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, SubmitField
from wtforms.validators import DataRequired, Email


class ClienteForm(FlaskForm):
    nombre = StringField(
        "Nombre del cliente",
        validators=[DataRequired()]
    )

    correo = EmailField(
        "Correo electrónico",
        validators=[DataRequired(), Email()]
    )

    telefono = StringField(
        "Teléfono",
        validators=[DataRequired()]
    )

    submit = SubmitField("Guardar cliente")