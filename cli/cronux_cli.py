#!/usr/bin/env python3
"""
Cronux-CRX CLI - Sistema de control de versiones local
Archivo principal que integra todos los comandos
"""

import sys
import os
from pathlib import Path

# Agregar el directorio cli al path para importar módulos
sys.path.insert(0, str(Path(__file__).parent))

# Importar funciones de los módulos
try:
    from crear_proyecto import crear_proyecto_cli
    from guardar_version import guardar_version_cli
    from ver_historial import ver_historial_cli
    from restaurar_versiones import restaurar_version_cli
    from info_proyecto import info_proyecto
    from funcion_verficar import verificarCronux
except ImportError as e:
    print(f"Error al importar módulos: {e}")
    sys.exit(1)


def mostrar_ayuda():
    """Muestra la ayuda del CLI"""
    print("""
Cronux-CRX - Control de versiones local simple

USO:
    crx <comando> [argumentos]

COMANDOS:
    new <nombre>           Crear un nuevo proyecto con control de versiones
    save [opciones]        Guardar una nueva version del proyecto
    log                    Ver el historial de versiones
    restore <version>      Restaurar una version especifica
    status                 Ver el estado actual del proyecto
    help                   Mostrar esta ayuda

OPCIONES PARA SAVE:
    -m, --message <msg>    Mensaje descriptivo de la version

EJEMPLOS:
    crx new mi-proyecto
    crx save -m "Primera version"
    crx log
    crx restore 1.0
    crx status

Para mas informacion, visita: https://github.com/cronux-crx
""")


def main():
    """Función principal del CLI"""
    if len(sys.argv) < 2:
        mostrar_ayuda()
        sys.exit(0)
    
    comando = sys.argv[1].lower()
    
    try:
        if comando in ['help', '--help', '-h']:
            mostrar_ayuda()
        
        elif comando == 'new':
            if len(sys.argv) < 3:
                print("Error: Se requiere el nombre del proyecto")
                print("Uso: crx new <nombre-proyecto>")
                sys.exit(1)
            nombre_proyecto = sys.argv[2]
            crear_proyecto_cli(nombre_proyecto)
        
        elif comando == 'save':
            # Verificar que estamos en un proyecto Cronux
            if not verificarCronux():
                print("Error: No estás en un proyecto Cronux-CRX")
                print("Usa 'crx new <nombre>' para crear un proyecto")
                sys.exit(1)
            
            # Procesar argumentos opcionales
            mensaje = None
            i = 2
            while i < len(sys.argv):
                if sys.argv[i] in ['-m', '--message']:
                    if i + 1 < len(sys.argv):
                        mensaje = sys.argv[i + 1]
                        i += 2
                    else:
                        print("Error: Se requiere un mensaje después de -m/--message")
                        sys.exit(1)
                else:
                    print(f"Error: Argumento desconocido '{sys.argv[i]}'")
                    sys.exit(1)
            
            guardar_version_cli(mensaje)
        
        elif comando == 'log':
            if not verificarCronux():
                print("Error: No estás en un proyecto Cronux-CRX")
                sys.exit(1)
            ver_historial_cli()
        
        elif comando == 'restore':
            if not verificarCronux():
                print("Error: No estás en un proyecto Cronux-CRX")
                sys.exit(1)
            
            if len(sys.argv) < 3:
                print("Error: Se requiere el número de versión")
                print("Uso: crx restore <version>")
                print("Ejemplo: crx restore 1.0")
                sys.exit(1)
            
            version = sys.argv[2]
            restaurar_version_cli(version)
        
        elif comando == 'status':
            if not verificarCronux():
                print("Error: No estás en un proyecto Cronux-CRX")
                sys.exit(1)
            info_proyecto()
        
        else:
            print(f"Error: Comando desconocido '{comando}'")
            print("Usa 'crx help' para ver los comandos disponibles")
            sys.exit(1)
    
    except KeyboardInterrupt:
        print("\nOperación cancelada por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"Error inesperado: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()