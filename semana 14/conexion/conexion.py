import mysql.connector
import os
from dotenv import load_dotenv


# Cargar las variables del archivo .env
# override=True hace que use el valor del .env
# aunque PowerShell tenga otro valor guardado.
load_dotenv(override=True)


def obtener_conexion():
    conexion = mysql.connector.connect(
        host="localhost",
        user="root",
        password=os.getenv("MYSQL_PASSWORD"),
        database="ferreteria_web"
    )

    return conexion