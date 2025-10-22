from pathlib import Path
import json
from datetime import datetime
from funcion_verficar import verificarCronux

def crear_proyecto_cli(nombre_proyecto):
    """Versión CLI que recibe el nombre como parámetro"""
    
    # Verificar si ya existe un proyecto
    if verificarCronux():
        print("ERROR: Ya existe un proyecto Cronux-CRX en esta ubicacion")
        return False
    
    # Crear carpeta .cronux
    carpeta_cronux = Path.cwd() / ".cronux"
    carpeta_cronux.mkdir(exist_ok=True)
    
    # Crear datos del proyecto
    datos_proyecto = {
        "nombre": nombre_proyecto,
        "fecha_creacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "autor": "usuario"
    }
    
    # Guardar JSON
    archivo_proyecto = carpeta_cronux / "proyecto.json"
    with open(archivo_proyecto, "w") as f:
        json.dump(datos_proyecto, f, indent=2)
    
    print("EXITO: Proyecto inicializado")
    print(f"Nombre: {nombre_proyecto}")
    print(f"Ubicación: {Path.cwd()}")
    print("\nComandos disponibles:")
    print("  crx save -m 'mensaje'  # Guardar versión")
    print("  crx log                # Ver historial")
    print("  crx status             # Ver estado")
    
    return True