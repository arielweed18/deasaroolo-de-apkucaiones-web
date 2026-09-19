from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, SubmitField
from wtforms.validators import DataRequired, Email


class ProveedorForm(FlaskForm):
    nombre = StringField(
        "Nombre del proveedor",
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

    empresa = StringField(
        "Empresa",
        validators=[DataRequired()]
    )

    submit = SubmitField("Guardar proveedor")