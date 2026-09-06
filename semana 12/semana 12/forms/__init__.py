from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, IntegerField, SubmitField
from wtforms.validators import DataRequired, NumberRange


class ProductoForm(FlaskForm):
    nombre = StringField(
        "Nombre del producto",
        validators=[DataRequired()]
    )

    precio = DecimalField(
        "Precio",
        validators=[DataRequired(), NumberRange(min=0)]
    )

    stock = IntegerField(
        "Stock",
        validators=[DataRequired(), NumberRange(min=0)]
    )

    submit = SubmitField("Guardar producto")