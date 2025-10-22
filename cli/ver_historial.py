from pathlib import Path
import json
from funcion_verficar import *

def ver_historial_cli():
    """Versión CLI para mostrar historial"""
    if not verificarCronux():
        print("ERROR: No estas en un proyecto Cronux")
        return False
    
    carpeta_versiones = obtener_ruta_cronux() / "versiones"

    if not carpeta_versiones.exists():
        print("INFO: No hay versiones guardadas")
        return False
    
    versiones = list(carpeta_versiones.glob("version_*"))
    
    if not versiones:
        print("INFO: No hay versiones guardadas")
        return False

    print("HISTORIAL DE VERSIONES:")
    print("=" * 50)
    
    # Ordenar versiones
    versiones_ordenadas = []
    for version_dir in versiones:
        try:
            numero = version_dir.name.replace("version_", "")
            if "." in numero:
                mayor, menor = numero.split(".")
                versiones_ordenadas.append((int(mayor), int(menor), version_dir))
            else:
                versiones_ordenadas.append((int(numero), 0, version_dir))
        except ValueError:
            continue
    
    versiones_ordenadas.sort(reverse=True)
    
    for mayor, menor, version_dir in versiones_ordenadas:
        metadatos_file = version_dir / "metadatos.json"
        
        if metadatos_file.exists():
            try:
                with open(metadatos_file, "r") as f:
                    metadatos = json.load(f)
                
                print(f"Versión: {metadatos['version']}")
                print(f"Fecha: {metadatos['fecha']}")
                print(f"Mensaje: {metadatos['mensaje']}")
                print(f"Archivos: {metadatos.get('archivos_guardados', 'N/A')}")
                print("-" * 30)
                
            except Exception as e:
                print(f"Error leyendo metadatos de {version_dir.name}: {e}")
        else:
            print(f"Versión: {version_dir.name.replace('version_', '')}")
            print("Metadatos no disponibles")
            print("-" * 30)
    
    return True