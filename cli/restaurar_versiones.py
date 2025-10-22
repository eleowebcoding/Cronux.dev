from pathlib import Path
from funcion_verficar import * 
import json
import shutil

def restaurar_version_cli(version_elegida):
    """Versión CLI que recibe la versión como parámetro"""
    if not verificarCronux():
        print("ERROR: No estas en un proyecto Cronux")
        return False
    
    # Limpiar la 'v' si viene incluida
    if version_elegida.startswith('v'):
        version_elegida = version_elegida[1:]
    
    # Verificar que la versión existe
    carpeta_version = obtener_ruta_cronux() / "versiones" / f"version_{version_elegida}"
    
    if not carpeta_version.exists():
        print(f"ERROR: La version '{version_elegida}' no existe")
        print("Usa 'cronux log' para ver las versiones disponibles")
        return False
    
    # Leer metadatos si existen
    metadatos_file = carpeta_version / "metadatos.json"
    if metadatos_file.exists():
        try:
            with open(metadatos_file, "r") as f:
                metadatos = json.load(f)
            print(f"Restaurando version {version_elegida}:")
            print(f"Fecha: {metadatos['fecha']}")
            print(f"Mensaje: {metadatos['mensaje']}")
        except Exception as e:
            print(f"Advertencia: Error leyendo metadatos: {e}")
    
    # Confirmar restauración
    respuesta = input(f"¿Confirmas restaurar la version {version_elegida}? (s/N): ")
    if respuesta.lower() not in ['s', 'si', 'sí', 'y', 'yes']:
        print("Operación cancelada")
        return False
    
    # Limpiar directorio actual (excepto .cronux)
    directorio_actual = Path.cwd()
    archivos_eliminados = 0
    
    for item in directorio_actual.iterdir():
        if item.name != ".cronux" and not item.name.startswith('.'):
            try:
                if item.is_file():
                    item.unlink()
                    archivos_eliminados += 1
                elif item.is_dir():
                    shutil.rmtree(item)
                    archivos_eliminados += 1
            except Exception as e:
                print(f"Advertencia: No se pudo eliminar {item.name}: {e}")
    
    # Restaurar archivos de la versión
    archivos_restaurados = 0
    for item in carpeta_version.iterdir():
        if item.name != "metadatos.json":
            destino = directorio_actual / item.name
            try:
                if item.is_file():
                    shutil.copy2(item, destino)
                    archivos_restaurados += 1
                elif item.is_dir():
                    shutil.copytree(item, destino)
                    archivos_restaurados += 1
            except Exception as e:
                print(f"Error restaurando {item.name}: {e}")
    
    print(f"EXITO: Version {version_elegida} restaurada")
    print(f"Archivos eliminados: {archivos_eliminados}")
    print(f"Archivos restaurados: {archivos_restaurados}")
    
    return True