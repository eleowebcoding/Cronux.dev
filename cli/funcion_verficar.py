from pathlib import Path
import json

def verificarCronux():
    """Verifica si estamos en un proyecto Cronux"""
    carpeta_cronux = Path.cwd() / ".cronux"
    archivo_proyecto = carpeta_cronux / "proyecto.json"
    return carpeta_cronux.exists() and archivo_proyecto.exists()

def obtener_ruta_cronux():
    """Obtiene la ruta de la carpeta .cronux"""
    return Path.cwd() / ".cronux"

def obtener_ruta_proyecto_json():
    """Obtiene la ruta del archivo proyecto.json"""
    return obtener_ruta_cronux() / "proyecto.json"

def determinar_numero_version():
    """Determina el siguiente número de versión"""
    carpeta_versiones = obtener_ruta_cronux() / "versiones"
    
    if not carpeta_versiones.exists():
        return "1.0"
    
    versiones = list(carpeta_versiones.glob("version_*"))
    
    if not versiones:
        return "1.0"
    
    # Extraer números de versión
    numeros = []
    for version_dir in versiones:
        try:
            numero = version_dir.name.replace("version_", "")
            if "." in numero:
                mayor, menor = numero.split(".")
                numeros.append((int(mayor), int(menor)))
            else:
                numeros.append((int(numero), 0))
        except ValueError:
            continue
    
    if not numeros:
        return "1.0"
    
    # Encontrar la versión más alta
    numeros.sort()
    ultimo_mayor, ultimo_menor = numeros[-1]
    
    # Incrementar versión menor
    return f"{ultimo_mayor}.{ultimo_menor + 1}"