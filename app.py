import requests
from bs4 import BeautifulSoup
import zipfile
import io
import subprocess
import os
from datetime import datetime, timedelta
from typing import List, Optional, Union


def iniciar_sesion(url_login: str, datos_login: dict) -> requests.Session:
    """Inicia sesión en el sitio web, bearer token."""
    sesion = requests.Session()
    sesion.post(url_login, data=datos_login)
    return sesion


def obtener_informes(sesion: requests.Session, url_informes: str) -> requests.Response:
    """Obtiene la página de informes después de iniciar sesión."""
    return sesion.get(url_informes)


def marcar_checkbox(fechas_a_considerar: List[str], soup: BeautifulSoup) -> None:
    """Marca las casillas de verificación según las fechas dadas."""
    for fecha in fechas_a_considerar:
        elementos_filtrados = soup.find_all(
            lambda tag: tag.name == "td" and tag.text.strip().startswith(f"D+1 {fecha}")
        )
        for elemento in elementos_filtrados:
            checkbox = elemento.find_previous_sibling("td").find(
                "input", {"type": "checkbox"}
            )
            if checkbox:
                checkbox["checked"] = True


def descargar_y_ejecutar_archivo(
    sesion: requests.Session, boton_descarga: Optional[dict]
) -> None:
    """Descarga, descomprime y ejecuta el archivo, y luego elimina el archivo descargado."""
    if boton_descarga:
        respuesta_descarga = sesion.get(boton_descarga["action"])
        with zipfile.ZipFile(io.BytesIO(respuesta_descarga.content), "r") as zip_ref:
            zip_ref.extractall("./")
        subprocess.run(["java", "-jar", "laraigo.jar"])
        os.remove("archivo.zip")


def time_wrapper(func: callable) -> callable:
    def wrapper(*args, **kwargs) -> Union[None, any]:
        start = datetime.now()
        result = func(*args, **kwargs)
        end = datetime.now()
        print(f"Tiempo de ejecución: {end - start}")
        return result

    return wrapper


@time_wrapper
def main() -> None:
    # URL de la página de inicio de sesión
    url_login = "https://ejemplo.com/login"

    # Datos de inicio de sesión
    datos_login = {"usuario": "tu_usuario", "contraseña": "tu_contraseña"}

    # Realizar la solicitud POST para iniciar sesión
    sesion = iniciar_sesion(url_login, datos_login)

    # Después de iniciar sesión, navegar a la página de informes
    url_informes = "https://ejemplo.com/informes"
    pagina_informes = obtener_informes(sesion, url_informes)

    # Parsear el HTML de la página de informes
    soup = BeautifulSoup(pagina_informes.text, "html.parser")

    # Obtener la fecha de hoy y la fecha de ayer en el formato "año-mes-dia"
    fecha_hoy = datetime.now().strftime("%Y-%m-%d")
    fecha_d1 = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

    # Lista de fechas a considerar
    fechas_a_considerar = [fecha_hoy, fecha_d1]

    # Marcar las casillas de verificación
    marcar_checkbox(fechas_a_considerar, soup)

    # Encontrar el botón de descarga y hacer clic en él
    boton_descarga = soup.find("button", {"id": "boton_descarga"})
    descargar_y_ejecutar_archivo(sesion, boton_descarga)


if __name__ == "__main__":
    main()
