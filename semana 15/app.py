from flask import Flask, render_template, redirect, url_for, flash
from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user
)
from werkzeug.security import generate_password_hash, check_password_hash
from psycopg2 import IntegrityError

from forms.producto_form import ProductoForm
from forms.proveedor_form import ProveedorForm
from forms.venta_form import VentaForm
from forms.login_form import LoginForm
from forms.usuario_form import UsuarioForm

from conexion.conexion import obtener_conexion
from models import Usuario

import os


# ==================================================
# CONFIGURACION DE FLASK
# ==================================================

app = Flask(__name__)

app.config["SECRET_KEY"] = os.environ.get(
    "SECRET_KEY",
    "clave-desarrollo-semana15"
)


# ==================================================
# CONFIGURACION DE FLASK-LOGIN
# ==================================================

login_manager = LoginManager()
login_manager.init_app(app)

login_manager.login_view = "login"
login_manager.login_message = "Debes iniciar sesión para acceder a esta página."
login_manager.login_message_category = "info"


# ==================================================
# CARGAR USUARIO
# ==================================================

@login_manager.user_loader
def load_user(user_id):

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute(
        """
        SELECT id, usuario, password
        FROM usuarios
        WHERE id = %s
        """,
        (user_id,)
    )

    datos = cursor.fetchone()

    cursor.close()
    conexion.close()

    if datos:
        return Usuario(
            id=datos[0],
            usuario=datos[1],
            password=datos[2]
        )

    return None


# ==================================================
# INICIO
# ==================================================

@app.route("/")
def inicio():
    return render_template("index.html")


# ==================================================
# REGISTRO
# ==================================================

@app.route("/registro", methods=["GET", "POST"])
def registro():

    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    form = UsuarioForm()

    if form.validate_on_submit():

        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute(
            """
            SELECT id
            FROM usuarios
            WHERE usuario = %s
            """,
            (form.usuario.data,)
        )

        usuario_existente = cursor.fetchone()

        if usuario_existente:

            cursor.close()
            conexion.close()

            flash(
                "Ese nombre de usuario ya está registrado.",
                "warning"
            )

            return render_template(
                "registro.html",
                form=form
            )

        password_hash = generate_password_hash(
            form.password.data
        )

        cursor.execute(
            """
            INSERT INTO usuarios (usuario, password)
            VALUES (%s, %s)
            """,
            (
                form.usuario.data,
                password_hash
            )
        )

        conexion.commit()

        cursor.close()
        conexion.close()

        flash(
            "Usuario registrado correctamente. Ahora puedes iniciar sesión.",
            "success"
        )

        return redirect(url_for("login"))

    return render_template(
        "registro.html",
        form=form
    )


# ==================================================
# LOGIN
# ==================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    form = LoginForm()

    if form.validate_on_submit():

        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute(
            """
            SELECT id, usuario, password
            FROM usuarios
            WHERE usuario = %s
            """,
            (form.usuario.data,)
        )

        datos = cursor.fetchone()

        cursor.close()
        conexion.close()

        if datos and check_password_hash(
            datos[2],
            form.password.data
        ):

            usuario = Usuario(
                id=datos[0],
                usuario=datos[1],
                password=datos[2]
            )

            login_user(usuario)

            flash(
                "Inicio de sesión correcto.",
                "success"
            )

            return redirect(url_for("dashboard"))

        flash(
            "Usuario o contraseña incorrectos.",
            "danger"
        )

    return render_template(
        "login.html",
        form=form
    )


# ==================================================
# DASHBOARD
# ==================================================

@app.route("/dashboard")
@login_required
def dashboard():

    return render_template(
        "dashboard.html"
    )


# ==================================================
# LOGOUT
# ==================================================

@app.route("/logout")
@login_required
def logout():

    logout_user()

    flash(
        "Sesión cerrada correctamente.",
        "success"
    )

    return redirect(url_for("login"))


# ==================================================
# PROVEEDORES - LISTAR
# ==================================================

@app.route("/proveedores")
@login_required
def mostrar_proveedores():

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute(
        """
        SELECT id_proveedor,
               nombre,
               telefono,
               correo
        FROM proveedores
        ORDER BY id_proveedor
        """
    )

    proveedores = cursor.fetchall()

    cursor.close()
    conexion.close()

    return render_template(
        "proveedores.html",
        proveedores=proveedores
    )


# ==================================================
# PROVEEDORES - CREAR
# ==================================================

@app.route(
    "/proveedores/nuevo",
    methods=["GET", "POST"]
)
@login_required
def nuevo_proveedor():

    form = ProveedorForm()

    if form.validate_on_submit():

        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute(
            """
            INSERT INTO proveedores
            (nombre, telefono, correo)
            VALUES (%s, %s, %s)
            """,
            (
                form.nombre.data,
                form.telefono.data,
                form.correo.data
            )
        )

        conexion.commit()

        cursor.close()
        conexion.close()

        flash(
            "Proveedor agregado correctamente.",
            "success"
        )

        return redirect(
            url_for("mostrar_proveedores")
        )

    return render_template(
        "formulario_proveedor.html",
        form=form,
        editando=False
    )


# ==================================================
# PROVEEDORES - EDITAR
# ==================================================

@app.route(
    "/proveedores/editar/<int:id_proveedor>",
    methods=["GET", "POST"]
)
@login_required
def editar_proveedor(id_proveedor):

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute(
        """
        SELECT id_proveedor,
               nombre,
               telefono,
               correo
        FROM proveedores
        WHERE id_proveedor = %s
        """,
        (id_proveedor,)
    )

    proveedor = cursor.fetchone()

    if proveedor is None:

        cursor.close()
        conexion.close()

        flash(
            "Proveedor no encontrado.",
            "danger"
        )

        return redirect(
            url_for("mostrar_proveedores")
        )

    form = ProveedorForm()

    if form.validate_on_submit():

        cursor.execute(
            """
            UPDATE proveedores
            SET nombre = %s,
                telefono = %s,
                correo = %s
            WHERE id_proveedor = %s
            """,
            (
                form.nombre.data,
                form.telefono.data,
                form.correo.data,
                id_proveedor
            )
        )

        conexion.commit()

        cursor.close()
        conexion.close()

        flash(
            "Proveedor actualizado correctamente.",
            "success"
        )

        return redirect(
            url_for("mostrar_proveedores")
        )

    if not form.is_submitted():

        form.nombre.data = proveedor[1]
        form.telefono.data = proveedor[2]
        form.correo.data = proveedor[3]

    cursor.close()
    conexion.close()

    return render_template(
        "formulario_proveedor.html",
        form=form,
        editando=True
    )


# ==================================================
# PROVEEDORES - ELIMINAR
# ==================================================

@app.route(
    "/proveedores/eliminar/<int:id_proveedor>",
    methods=["POST"]
)
@login_required
def eliminar_proveedor(id_proveedor):

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    try:

        cursor.execute(
            """
            DELETE FROM proveedores
            WHERE id_proveedor = %s
            """,
            (id_proveedor,)
        )

        conexion.commit()

        flash(
            "Proveedor eliminado correctamente.",
            "success"
        )

    except IntegrityError:

        conexion.rollback()

        flash(
            "No puedes eliminar este proveedor porque tiene productos relacionados.",
            "danger"
        )

    finally:

        cursor.close()
        conexion.close()

    return redirect(
        url_for("mostrar_proveedores")
    )


# ==================================================
# PRODUCTOS - LISTAR CON JOIN
# ==================================================

@app.route("/productos")
@login_required
def mostrar_productos():

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute(
        """
        SELECT
            p.id_producto,
            p.nombre,
            p.precio,
            p.stock,
            pr.nombre
        FROM productos p
        INNER JOIN proveedores pr
            ON p.id_proveedor = pr.id_proveedor
        ORDER BY p.id_producto
        """
    )

    productos = cursor.fetchall()

    cursor.close()
    conexion.close()

    return render_template(
        "productos.html",
        productos=productos
    )


# ==================================================
# PRODUCTOS - CREAR
# ==================================================

@app.route(
    "/productos/nuevo",
    methods=["GET", "POST"]
)
@login_required
def nuevo_producto():

    form = ProductoForm()

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute(
        """
        SELECT id_proveedor, nombre
        FROM proveedores
        ORDER BY nombre
        """
    )

    proveedores = cursor.fetchall()

    cursor.close()
    conexion.close()

    form.id_proveedor.choices = [
        (proveedor[0], proveedor[1])
        for proveedor in proveedores
    ]

    if form.validate_on_submit():

        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute(
            """
            INSERT INTO productos
            (nombre, precio, stock, id_proveedor)
            VALUES (%s, %s, %s, %s)
            """,
            (
                form.nombre.data,
                form.precio.data,
                form.stock.data,
                form.id_proveedor.data
            )
        )

        conexion.commit()

        cursor.close()
        conexion.close()

        flash(
            "Producto agregado correctamente.",
            "success"
        )

        return redirect(
            url_for("mostrar_productos")
        )

    return render_template(
        "formulario_producto.html",
        form=form,
        editando=False
    )


# ==================================================
# PRODUCTOS - EDITAR
# ==================================================

@app.route(
    "/productos/editar/<int:id_producto>",
    methods=["GET", "POST"]
)
@login_required
def editar_producto(id_producto):

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute(
        """
        SELECT id_producto,
               nombre,
               precio,
               stock,
               id_proveedor
        FROM productos
        WHERE id_producto = %s
        """,
        (id_producto,)
    )

    producto = cursor.fetchone()

    if producto is None:

        cursor.close()
        conexion.close()

        flash(
            "Producto no encontrado.",
            "danger"
        )

        return redirect(
            url_for("mostrar_productos")
        )

    cursor.execute(
        """
        SELECT id_proveedor, nombre
        FROM proveedores
        ORDER BY nombre
        """
    )

    proveedores = cursor.fetchall()

    cursor.close()
    conexion.close()

    form = ProductoForm()

    form.id_proveedor.choices = [
        (proveedor[0], proveedor[1])
        for proveedor in proveedores
    ]

    if form.validate_on_submit():

        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute(
            """
            UPDATE productos
            SET nombre = %s,
                precio = %s,
                stock = %s,
                id_proveedor = %s
            WHERE id_producto = %s
            """,
            (
                form.nombre.data,
                form.precio.data,
                form.stock.data,
                form.id_proveedor.data,
                id_producto
            )
        )

        conexion.commit()

        cursor.close()
        conexion.close()

        flash(
            "Producto actualizado correctamente.",
            "success"
        )

        return redirect(
            url_for("mostrar_productos")
        )

    if not form.is_submitted():

        form.nombre.data = producto[1]
        form.precio.data = producto[2]
        form.stock.data = producto[3]
        form.id_proveedor.data = producto[4]

    return render_template(
        "formulario_producto.html",
        form=form,
        editando=True
    )


# ==================================================
# PRODUCTOS - ELIMINAR
# ==================================================

@app.route(
    "/productos/eliminar/<int:id_producto>",
    methods=["POST"]
)
@login_required
def eliminar_producto(id_producto):

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    try:

        cursor.execute(
            """
            DELETE FROM productos
            WHERE id_producto = %s
            """,
            (id_producto,)
        )

        conexion.commit()

        flash(
            "Producto eliminado correctamente.",
            "success"
        )

    except IntegrityError:

        conexion.rollback()

        flash(
            "No puedes eliminar este producto porque tiene ventas relacionadas.",
            "danger"
        )

    finally:

        cursor.close()
        conexion.close()

    return redirect(
        url_for("mostrar_productos")
    )


# ==================================================
# VENTAS - LISTAR CON JOIN
# ==================================================

@app.route("/ventas")
@login_required
def mostrar_ventas():

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute(
        """
        SELECT
            v.id_venta,
            v.fecha,
            v.cantidad,
            p.nombre,
            p.precio,
            (v.cantidad * p.precio) AS total,
            pr.nombre
        FROM ventas v
        INNER JOIN productos p
            ON v.id_producto = p.id_producto
        INNER JOIN proveedores pr
            ON p.id_proveedor = pr.id_proveedor
        ORDER BY v.id_venta
        """
    )

    ventas = cursor.fetchall()

    cursor.close()
    conexion.close()

    return render_template(
        "ventas.html",
        ventas=ventas
    )


# ==================================================
# VENTAS - CREAR
# ==================================================

@app.route(
    "/ventas/nueva",
    methods=["GET", "POST"]
)
@login_required
def nueva_venta():

    form = VentaForm()

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute(
        """
        SELECT id_producto, nombre
        FROM productos
        ORDER BY nombre
        """
    )

    productos = cursor.fetchall()

    cursor.close()
    conexion.close()

    form.id_producto.choices = [
        (producto[0], producto[1])
        for producto in productos
    ]

    if form.validate_on_submit():

        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute(
            """
            INSERT INTO ventas
            (fecha, cantidad, id_producto)
            VALUES (%s, %s, %s)
            """,
            (
                form.fecha.data,
                form.cantidad.data,
                form.id_producto.data
            )
        )

        conexion.commit()

        cursor.close()
        conexion.close()

        flash(
            "Venta registrada correctamente.",
            "success"
        )

        return redirect(
            url_for("mostrar_ventas")
        )

    return render_template(
        "formulario_venta.html",
        form=form,
        editando=False
    )


# ==================================================
# VENTAS - EDITAR
# ==================================================

@app.route(
    "/ventas/editar/<int:id_venta>",
    methods=["GET", "POST"]
)
@login_required
def editar_venta(id_venta):

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute(
        """
        SELECT id_venta,
               fecha,
               cantidad,
               id_producto
        FROM ventas
        WHERE id_venta = %s
        """,
        (id_venta,)
    )

    venta = cursor.fetchone()

    if venta is None:

        cursor.close()
        conexion.close()

        flash(
            "Venta no encontrada.",
            "danger"
        )

        return redirect(
            url_for("mostrar_ventas")
        )

    cursor.execute(
        """
        SELECT id_producto, nombre
        FROM productos
        ORDER BY nombre
        """
    )

    productos = cursor.fetchall()

    cursor.close()
    conexion.close()

    form = VentaForm()

    form.id_producto.choices = [
        (producto[0], producto[1])
        for producto in productos
    ]

    if form.validate_on_submit():

        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute(
            """
            UPDATE ventas
            SET fecha = %s,
                cantidad = %s,
                id_producto = %s
            WHERE id_venta = %s
            """,
            (
                form.fecha.data,
                form.cantidad.data,
                form.id_producto.data,
                id_venta
            )
        )

        conexion.commit()

        cursor.close()
        conexion.close()

        flash(
            "Venta actualizada correctamente.",
            "success"
        )

        return redirect(
            url_for("mostrar_ventas")
        )

    if not form.is_submitted():

        form.fecha.data = venta[1]
        form.cantidad.data = venta[2]
        form.id_producto.data = venta[3]

    return render_template(
        "formulario_venta.html",
        form=form,
        editando=True
    )


# ==================================================
# VENTAS - ELIMINAR
# ==================================================

@app.route(
    "/ventas/eliminar/<int:id_venta>",
    methods=["POST"]
)
@login_required
def eliminar_venta(id_venta):

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute(
        """
        DELETE FROM ventas
        WHERE id_venta = %s
        """,
        (id_venta,)
    )

    conexion.commit()

    cursor.close()
    conexion.close()

    flash(
        "Venta eliminada correctamente.",
        "success"
    )

    return redirect(
        url_for("mostrar_ventas")
    )


# ==================================================
# EJECUTAR APLICACION
# ==================================================

if __name__ == "__main__":
    app.run(debug=True)