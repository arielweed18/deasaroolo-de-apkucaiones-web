from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Length


class ProductoForm(FlaskForm):
    nombre = StringField(
        "Nombre del producto",
        validators=[
            DataRequired(),
            Length(min=2, max=100)
        ]
    )

    precio = DecimalField(
        "Precio",
        validators=[
            DataRequired(),
            NumberRange(min=0.01)
        ],
        places=2
    )

    stock = IntegerField(
        "Stock",
        validators=[
            DataRequired(),
            NumberRange(min=0)
        ]
    )

    id_proveedor = SelectField(
        "Proveedor",
        coerce=int,
        validators=[DataRequired()]
    )

    submit = SubmitField("Guardar")