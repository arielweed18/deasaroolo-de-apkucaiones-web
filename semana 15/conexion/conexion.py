import os
import psycopg2
from dotenv import load_dotenv
from pathlib import Path

# Buscar el archivo .env que está en la carpeta "semana 15"
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"

# Cargar las variables del archivo .env
load_dotenv(dotenv_path=ENV_PATH, override=True)


def obtener_conexion():
    return psycopg2.connect(
        host="localhost",
        port="5432",
        database="ferreteria_web",
        user="postgres",
        password=os.getenv("POSTGRES_PASSWORD")
    )