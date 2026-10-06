from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Email, Length


class ProveedorForm(FlaskForm):
    nombre = StringField(
        "Nombre",
        validators=[
            DataRequired(),
            Length(min=2, max=100)
        ]
    )

    telefono = StringField(
        "Teléfono",
        validators=[
            DataRequired(),
            Length(max=20)
        ]
    )

    correo = StringField(
        "Correo",
        validators=[
            DataRequired(),
            Email()
        ]
    )

    submit = SubmitField("Guardar")