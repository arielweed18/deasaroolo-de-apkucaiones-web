import mysql.connector


def obtener_conexion():
    conexion = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Ariel12345!",
        database="ferreteria_web"
    )

    return conexion