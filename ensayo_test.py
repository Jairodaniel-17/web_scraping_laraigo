import requests
from bs4 import BeautifulSoup
import zipfile
import io
import subprocess
import os

# importar libreria para obtener la fecha de hoy
from datetime import datetime, timedelta

# URL de la página de inicio de sesión
url_login = "https://ejemplo.com/login"

# Datos de inicio de sesión
datos_login = {"usuario": "tu_usuario", "contraseña": "tu_contraseña"}

# Realizar la solicitud POST para iniciar sesión
sesion = requests.Session()
sesion.post(url_login, data=datos_login)

# Después de iniciar sesión, navegar a la página de informes
url_informes = "https://ejemplo.com/informes"
pagina_informes = sesion.get(url_informes)

# Parsear el HTML de la página de informes
soup = BeautifulSoup(pagina_informes.text, "html.parser")

# Obtener la fecha de hoy y la fecha de ayer en el formato "año-mes-dia"
fecha_hoy = datetime.now().strftime("%Y-%m-%d")
fecha_d1 = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

# Lista de fechas a considerar
fechas_a_considerar = [fecha_hoy, fecha_d1]

# Encontrar las filas de la tabla que contienen los nombres D+1 y las fechas
filas = soup.find_all("tr")
for fila in filas:
    columnas = fila.find_all("td")
    for columna in columnas:
        for fecha in fechas_a_considerar:
            if columna.text.strip().startswith("D+1 " + fecha):
                checkbox = fila.find("input", {"type": "checkbox"})
                if checkbox:
                    # Hacer clic en el checkbox
                    checkbox["checked"] = True


# Encontrar el botón de descarga y hacer clic en él
boton_descarga = soup.find("button", {"id": "boton_descarga"})
if boton_descarga:
    # Realizar la solicitud para descargar el archivo.zip
    respuesta_descarga = sesion.get(boton_descarga["action"])

    # Descomprimir el archivo.zip en el mismo directorio
    with zipfile.ZipFile(io.BytesIO(respuesta_descarga.content), "r") as zip_ref:
        zip_ref.extractall("./")

    # Ejecutar el comando java -jar laraigo.jar
    subprocess.run(["java", "-jar", "laraigo.jar"])

    # Eliminar el archivo descargado
    os.remove("archivo.zip")
