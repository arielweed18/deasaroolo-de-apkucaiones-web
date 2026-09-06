from flask import Flask, render_template, redirect, url_for
from forms.producto_form import ProductoForm
from forms.cliente_form import ClienteForm
from forms.proveedor_form import ProveedorForm
from forms.facturacion_form import FacturacionForm
import sqlite3
import os


app = Flask(__name__)
app.config["SECRET_KEY"] = "clave-secreta-semana12"

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "ferreteria.db")


# ==================================================
# BASE DE DATOS
# ==================================================

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
# INICIO
# ==================================================

@app.route("/")
def inicio():
    return render_template("index.html")


# ==================================================
# PRODUCTOS
# ==================================================

@app.route("/productos")
def mostrar_productos():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM productos")
    productos = cursor.fetchall()

    conn.close()

    return render_template(
        "productos.html",
        productos=productos
    )


@app.route("/productos/nuevo", methods=["GET", "POST"])
def nuevo_producto():
    form = ProductoForm()

    if form.validate_on_submit():
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO productos
            (nombre, precio, stock)
            VALUES (?, ?, ?)
            """,
            (
                form.nombre.data,
                float(form.precio.data),
                form.stock.data
            )
        )

        conn.commit()
        conn.close()

        return redirect(url_for("mostrar_productos"))

    return render_template(
        "formulario_producto.html",
        form=form
    )


# ==================================================
# CLIENTES
# ==================================================

@app.route("/clientes")
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