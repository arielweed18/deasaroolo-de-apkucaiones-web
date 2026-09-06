from flask import Flask, render_template, redirect, url_for
from forms.producto_form import ProductoForm
import sqlite3
import os

app = Flask(__name__)
app.config["SECRET_KEY"] = "clave-secreta-semana12"

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "ferreteria.db")


def crear_base_datos():
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

    conn.commit()
    conn.close()


@app.route("/")
def inicio():
    return render_template("index.html")


@app.route("/productos")
def mostrar_productos():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM productos")
    productos = cursor.fetchall()

    conn.close()

    return render_template("productos.html", productos=productos)


@app.route("/productos/nuevo", methods=["GET", "POST"])
def nuevo_producto():
    form = ProductoForm()

    if form.validate_on_submit():
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO productos (nombre, precio, stock) VALUES (?, ?, ?)",
            (
                form.nombre.data,
                float(form.precio.data),
                form.stock.data
            )
        )

        conn.commit()
        conn.close()

        return redirect(url_for("mostrar_productos"))

    return render_template("formulario_producto.html", form=form)


if __name__ == "__main__":
    os.makedirs(os.path.join(BASE_DIR, "data"), exist_ok=True)
    crear_base_datos()
    app.run(debug=True)