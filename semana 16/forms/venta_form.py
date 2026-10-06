from flask_wtf import FlaskForm
from wtforms import DateField, IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired, NumberRange


class VentaForm(FlaskForm):
    fecha = DateField(
        "Fecha",
        validators=[DataRequired()]
    )

    cantidad = IntegerField(
        "Cantidad",
        validators=[
            DataRequired(),
            NumberRange(min=1)
        ]
    )

    id_producto = SelectField(
        "Producto",
        coerce=int,
        validators=[DataRequired()]
    )

    submit = SubmitField("Guardar")