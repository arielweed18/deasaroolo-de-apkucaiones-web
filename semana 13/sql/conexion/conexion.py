import mysql.connector
import os


def obtener_conexion():
    conexion = mysql.connector.connect(
        host="localhost",
        user="root",
        password=os.environ.get("MYSQL_PASSWORD"),
        database="ferreteria_web"
    )

    return conexion