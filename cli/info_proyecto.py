import json
from pathlib import Path
from funcion_verficar import verificarCronux, obtener_ruta_proyecto_json, obtener_ruta_cronux

def info_proyecto():
    """Muestra información del proyecto Cronux"""
    # 1. Verificar si existe proyecto Cronux
    if not verificarCronux():
        print("No estamos en un proyecto Cronux")
        print("Usa 'cronux new <nombre>' para crear uno")
        return
    
    # 2. Leer el JSON
    archivo_proyecto = obtener_ruta_proyecto_json()

    if archivo_proyecto.exists():
        with open(archivo_proyecto, "r") as f:
            datos = json.load(f)

        # 3. Mostrar información del proyecto
        print("INFORMACIÓN DEL PROYECTO CRONUX")
        print("=" * 40)
        print(f"Nombre: {datos.get('nombre', 'Sin nombre')}")
        print(f"Fecha de creación: {datos.get('fecha_creacion', 'Desconocida')}")
        print(f"Autor: {datos.get('autor', 'Desconocido')}")
        print(f"Ubicación: {Path.cwd()}")
        
        # 4. Información de versiones
        carpeta_versiones = obtener_ruta_cronux() / "versiones"
        if carpeta_versiones.exists():
            versiones = list(carpeta_versiones.glob("version_*"))
            print(f"Versiones guardadas: {len(versiones)}")
            
            if versiones:
                # Mostrar última versión
                versiones_ordenadas = []
                for version_dir in versiones:
                    try:
                        numero = version_dir.name.replace("version_", "")
                        if "." in numero:
                            mayor, menor = numero.split(".")
                            versiones_ordenadas.append((int(mayor), int(menor), numero))
                        else:
                            versiones_ordenadas.append((int(numero), 0, numero))
                    except ValueError:
                        continue
                
                if versiones_ordenadas:
                    versiones_ordenadas.sort()
                    ultima_version = versiones_ordenadas[-1][2]
                    print(f"Última versión: {ultima_version}")
        else:
            print("Versiones guardadas: 0")
        
        print("\nComandos disponibles:")
        print("  cronux save -m 'mensaje'  # Guardar nueva versión")
        print("  cronux log                # Ver historial")
        print("  cronux restore <version>  # Restaurar versión")
        
    else:
        print("ERROR: No se pudo leer la información del proyecto")
        print("El archivo proyecto.json no existe o está corrupto")