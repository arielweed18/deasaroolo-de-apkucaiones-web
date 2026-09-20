from flask import Flask, render_template, redirect, url_for, flash
from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user
)
from werkzeug.security import generate_password_hash, check_password_hash

from forms.producto_form import ProductoForm
from forms.cliente_form import ClienteForm
from forms.proveedor_form import ProveedorForm
from forms.facturacion_form import FacturacionForm
from forms.login_form import LoginForm
from forms.usuario_form import UsuarioForm

from conexion.conexion import obtener_conexion
from models import Usuario

import sqlite3
import os


# ==================================================
# CONFIGURACION DE FLASK
# ==================================================

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get(
    "FLASK_SECRET_KEY",
    "clave-desarrollo-semana14"
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
# BASE DE DATOS SQLITE
# Se mantiene para los módulos existentes
# ==================================================

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "ferreteria.db")


def crear_base_datos():
    os.makedirs(os.path.join(BASE_DIR, "data"), exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            precio REAL NOT NULL,
            stock INTEGER NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            correo TEXT NOT NULL,
            telefono TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS proveedores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            correo TEXT NOT NULL,
            telefono TEXT NOT NULL,
            empresa TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS facturacion (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente TEXT NOT NULL,
            producto TEXT NOT NULL,
            cantidad INTEGER NOT NULL,
            total REAL NOT NULL
        )
    """)

    conn.commit()
    conn.close()


# ==================================================
# CARGAR USUARIO PARA FLASK-LOGIN
# ==================================================

@login_manager.user_loader
def load_user(user_id):
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute(
        "SELECT id, usuario, password FROM usuarios WHERE id = %s",
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
# REGISTRO DE USUARIOS
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
            "SELECT id FROM usuarios WHERE usuario = %s",
            (form.usuario.data,)
        )

        usuario_existente = cursor.fetchone()

        if usuario_existente:
            cursor.close()
            conexion.close()

            flash("Ese nombre de usuario ya está registrado.")
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

        flash("Usuario registrado correctamente. Ahora puedes iniciar sesión.")

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

            flash("Inicio de sesión correcto.")

            return redirect(url_for("dashboard"))

        flash("Usuario o contraseña incorrectos.")

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
    return render_template("dashboard.html")


# ==================================================
# LOGOUT
# ==================================================

@app.route("/logout")
@login_required
def logout():
    logout_user()

    flash("Sesión cerrada correctamente.")

    return redirect(url_for("login"))


# ==================================================
# PRODUCTOS - MYSQL
# ==================================================

@app.route("/productos")
@login_required
def mostrar_productos():
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("SELECT * FROM productos")
    productos = cursor.fetchall()

    cursor.close()
    conexion.close()

    return render_template(
        "productos.html",
        productos=productos
    )


@app.route("/productos/nuevo", methods=["GET", "POST"])
@login_required
def nuevo_producto():
    form = ProductoForm()

    if form.validate_on_submit():
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute(
            """
            INSERT INTO productos (nombre, precio, stock)
            VALUES (%s, %s, %s)
            """,
            (
                form.nombre.data,
                float(form.precio.data),
                form.stock.data
            )
        )

        conexion.commit()
        cursor.close()
        conexion.close()

        return redirect(url_for("mostrar_productos"))

    return render_template(
        "formulario_producto.html",
        form=form
    )


@app.route(
    "/productos/editar/<int:id_producto>",
    methods=["GET", "POST"]
)
@login_required
def editar_producto(id_producto):
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute(
        "SELECT * FROM productos WHERE id_producto = %s",
        (id_producto,)
    )

    producto = cursor.fetchone()

    if producto is None:
        cursor.close()
        conexion.close()

        return "Producto no encontrado", 404

    form = ProductoForm()

    if form.validate_on_submit():
        cursor.execute(
            """
            UPDATE productos
            SET nombre = %s,
                precio = %s,
                stock = %s
            WHERE id_producto = %s
            """,
            (
                form.nombre.data,
                float(form.precio.data),
                form.stock.data,
                id_producto
            )
        )

        conexion.commit()
        cursor.close()
        conexion.close()

        return redirect(url_for("mostrar_productos"))

    if not form.is_submitted():
        form.nombre.data = producto[1]
        form.precio.data = producto[2]
        form.stock.data = producto[3]

    cursor.close()
    conexion.close()

    return render_template(
        "formulario_producto.html",
        form=form,
        editando=True
    )


@app.route(
    "/productos/eliminar/<int:id_producto>",
    methods=["POST"]
)
@login_required
def eliminar_producto(id_producto):
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute(
        "DELETE FROM productos WHERE id_producto = %s",
        (id_producto,)
    )

    conexion.commit()
    cursor.close()
    conexion.close()

    return redirect(url_for("mostrar_productos"))


# ==================================================
# CLIENTES
# ==================================================

@app.route("/clientes")
@login_required
def mostrar_clientes():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM clientes")
    clientes = cursor.fetchall()

    conn.close()

    return render_template(
        "clientes.html",
        clientes=clientes
    )


@app.route("/clientes/nuevo", methods=["GET", "POST"])
@login_required
def nuevo_cliente():
    form = ClienteForm()

    if form.validate_on_submit():
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO clientes
            (nombre, correo, telefono)
            VALUES (?, ?, ?)
            """,
            (
                form.nombre.data,
                form.correo.data,
                form.telefono.data
            )
        )

        conn.commit()
        conn.close()

        return redirect(url_for("mostrar_clientes"))

    return render_template(
        "formulario_cliente.html",
        form=form
    )


# ==================================================
# PROVEEDORES
# ==================================================

@app.route("/proveedores")
@login_required
def mostrar_proveedores():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM proveedores")
    proveedores = cursor.fetchall()

    conn.close()

    return render_template(
        "proveedores.html",
        proveedores=proveedores
    )


@app.route("/proveedores/nuevo", methods=["GET", "POST"])
@login_required
def nuevo_proveedor():
    form = ProveedorForm()

    if form.validate_on_submit():
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO proveedores
            (nombre, correo, telefono, empresa)
            VALUES (?, ?, ?, ?)
            """,
            (
                form.nombre.data,
                form.correo.data,
                form.telefono.data,
                form.empresa.data
            )
        )

        conn.commit()
        conn.close()

        return redirect(url_for("mostrar_proveedores"))

    return render_template(
        "formulario_proveedor.html",
        form=form
    )


# ==================================================
# FACTURACION
# ==================================================

@app.route("/facturacion")
@login_required
def mostrar_facturacion():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM facturacion")
    facturas = cursor.fetchall()

    conn.close()

    return render_template(
        "facturacion.html",
        facturas=facturas
    )


@app.route("/facturacion/nueva", methods=["GET", "POST"])
@login_required
def nueva_factura():
    form = FacturacionForm()

    if form.validate_on_submit():
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO facturacion
            (cliente, producto, cantidad, total)
            VALUES (?, ?, ?, ?)
            """,
            (
                form.cliente.data,
                form.producto.data,
                form.cantidad.data,
                float(form.total.data)
            )
        )

        conn.commit()
        conn.close()

        return redirect(url_for("mostrar_facturacion"))

    return render_template(
        "formulario_facturacion.html",
        form=form
    )


# ==================================================
# EJECUTAR APLICACION
# ==================================================

if __name__ == "__main__":
    crear_base_datos()
    app.run(debug=True)