from pathlib import Path
from funcion_verficar import *
import json
from datetime import datetime
import shutil

def guardar_version_cli(mensaje):
    """Versión CLI que recibe el mensaje como parámetro"""
    # Verificar que estamos en el proyecto cronux
    if not verificarCronux():
        print("ERROR: No estas en un proyecto Cronux")
        return False

    # Determinar número de la versión
    numero_version = determinar_numero_version()

    # Crear la carpeta de versiones dentro de .cronux
    carpeta_versiones = obtener_ruta_cronux() / "versiones"
    carpeta_versiones.mkdir(exist_ok=True)

    # Crear carpeta específica para esta versión
    carpeta_version = carpeta_versiones / f"version_{numero_version}"
    carpeta_version.mkdir(exist_ok=True)

    # Copiar todos los archivos del directorio actual (excepto .cronux)
    directorio_actual = Path.cwd()
    
    archivos_copiados = 0
    for item in directorio_actual.iterdir():
        if item.name != ".cronux" and not item.name.startswith('.'):
            destino = carpeta_version / item.name
            try:
                if item.is_file():
                    shutil.copy2(item, destino)
                    archivos_copiados += 1
                elif item.is_dir():
                    shutil.copytree(item, destino)
                    archivos_copiados += 1
            except Exception as e:
                print(f"Advertencia: No se pudo copiar {item.name}: {e}")

    # Crear metadatos de la versión
    metadatos = {
        "version": numero_version,
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "mensaje": mensaje or "Sin mensaje",
        "archivos_guardados": archivos_copiados
    }

    # Guardar metadatos
    archivo_metadatos = carpeta_version / "metadatos.json"
    with open(archivo_metadatos, "w") as f:
        json.dump(metadatos, f, indent=2)

    print(f"EXITO: Version {numero_version} guardada")
    print(f"Mensaje: {metadatos['mensaje']}")
    print(f"Archivos guardados: {archivos_copiados}")
    print(f"Fecha: {metadatos['fecha']}")
    
    return True