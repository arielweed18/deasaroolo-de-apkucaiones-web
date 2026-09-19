from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, DecimalField, SubmitField
from wtforms.validators import DataRequired, NumberRange


class FacturacionForm(FlaskForm):
    cliente = StringField(
        "Cliente",
        validators=[DataRequired()]
    )

    producto = StringField(
        "Producto",
        validators=[DataRequired()]
    )

    cantidad = IntegerField(
        "Cantidad",
        validators=[DataRequired(), NumberRange(min=1)]
    )

    total = DecimalField(
        "Total",
        validators=[DataRequired(), NumberRange(min=0)]
    )

    submit = SubmitField("Registrar factura")