#!/usr/bin/env python3
"""
Script de compilación optimizado para Cronux-CRX
Genera un solo instalador con CLI embebido
"""

import os
import sys
import subprocess
import shutil
import base64
import tempfile
from pathlib import Path

def detectar_sistema():
    """Detecta el sistema operativo"""
    if sys.platform.startswith('win'):
        return 'windows'
    elif sys.platform.startswith('darwin'):
        return 'macos'
    elif sys.platform.startswith('linux'):
        return 'linux'
    else:
        return 'unknown'

def limpiar_archivos():
    """Limpia archivos de compilaciones anteriores"""
    print("🧹 Limpiando archivos anteriores...")
    
    for path in ["dist", "build", "__pycache__", "temp_gui"]:
        if Path(path).exists():
            shutil.rmtree(path)
    
    # Limpiar archivos .pyc y .spec
    for pyc_file in Path(".").rglob("*.pyc"):
        pyc_file.unlink()
    
    for spec_file in Path(".").glob("*.spec"):
        spec_file.unlink()

def compilar_cli_temporal():
    """Compila el CLI temporalmente para embeber"""
    sistema = detectar_sistema()
    print(f"🔨 Compilando CLI temporal para embeber...")
    
    # Crear directorio temporal
    temp_dir = Path("temp_cli")
    temp_dir.mkdir(exist_ok=True)
    
    # Nombre del ejecutable según el sistema
    if sistema == 'windows':
        exe_name = "crx.exe"
    else:
        exe_name = "crx"
    
    try:
        cmd = [
            "pyinstaller", 
            "--onefile", 
            "--name", "crx",
            "--distpath", str(temp_dir),
            "--workpath", str(temp_dir / "build"),
            "--specpath", str(temp_dir),
            "--clean",
            "--console" if sistema == 'windows' else "--strip",
            "cli/cronux_cli.py"
        ]
        
        # En Windows, remover --strip
        if sistema == 'windows':
            cmd = [c for c in cmd if c != "--strip"]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            exe_path = temp_dir / exe_name
            if exe_path.exists():
                size = exe_path.stat().st_size / 1024 / 1024
                print(f"✅ CLI temporal compilado: {exe_name} ({size:.1f} MB)")
                return exe_path
            else:
                print(f"❌ No se encontró {exe_name}")
                return None
        else:
            print(f"❌ Error compilando CLI: {result.stderr}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def embeber_cli_en_gui(cli_path):
    """Embebe el CLI compilado en el GUI"""
    print("📦 Embebiendo CLI en GUI...")
    
    try:
        # Leer el CLI compilado
        with open(cli_path, 'rb') as f:
            cli_data = f.read()
        
        # Codificar en base64
        cli_base64 = base64.b64encode(cli_data).decode('utf-8')
        
        # Crear directorio temporal para GUI modificado
        temp_gui_dir = Path("temp_gui")
        temp_gui_dir.mkdir(exist_ok=True)
        
        # Leer el GUI original
        with open("gui/cronux_gui.py", 'r', encoding='utf-8') as f:
            gui_content = f.read()
        
        # Reemplazar la línea EMBEDDED_CLI_DATA
        gui_content = gui_content.replace(
            "EMBEDDED_CLI_DATA = None",
            f'EMBEDDED_CLI_DATA = """{cli_base64}"""'
        )
        
        # Escribir GUI modificado
        gui_path = temp_gui_dir / "cronux_gui_embedded.py"
        with open(gui_path, 'w', encoding='utf-8') as f:
            f.write(gui_content)
        
        print(f"✅ CLI embebido en GUI ({len(cli_base64)/1024:.1f} KB)")
        return gui_path
        
    except Exception as e:
        print(f"❌ Error embebiendo CLI: {e}")
        return None

def crear_icono_windows():
    """Crea archivo .ico para Windows desde PNG"""
    try:
        from PIL import Image
        
        png_path = Path("assets/cronux_cli.png")
        ico_path = Path("assets/cronux_cli.ico")
        
        if png_path.exists():
            img = Image.open(png_path)
            img.save(ico_path, format='ICO', sizes=[(16,16), (32,32), (48,48), (64,64), (128,128), (256,256)])
            print(f"✅ Icono .ico creado: {ico_path}")
            return True
        else:
            print("⚠️  No se encontró cronux_cli.png")
            return False
    except ImportError:
        print("⚠️  PIL no disponible, no se puede crear .ico")
        return False
    except Exception as e:
        print(f"⚠️  Error creando .ico: {e}")
        return False

def compilar_instalador_final(gui_path):
    """Compila el instalador final con CLI embebido"""
    sistema = detectar_sistema()
    print(f"🖥️ Compilando instalador final para {sistema}...")
    
    # Crear icono .ico para Windows si es necesario
    if sistema == 'windows':
        crear_icono_windows()
    
    try:
        # Nombre del instalador según el sistema
        if sistema == 'windows':
            installer_name = "CronuxCRX_Installer.exe"
        elif sistema == 'linux':
            installer_name = "CronuxCRX_Installer"
        else:  # macOS
            installer_name = "CronuxCRX_Installer.app"
        
        cmd = [
            "pyinstaller", 
            "--onefile",
            "--windowed",
            "--name", "CronuxCRX_Installer",
            "--distpath", "dist",
            "--clean",
            "--add-data", "assets:assets",  # Incluir carpeta assets
            str(gui_path)
        ]
        
        # Agregar icono según el sistema
        if sistema == 'windows' and Path("assets/cronux_cli.ico").exists():
            cmd.extend(["--icon", "assets/cronux_cli.ico"])
        elif sistema == 'macos' and Path("assets/cronux_cli.png").exists():
            cmd.extend(["--icon", "assets/cronux_cli.png"])
        
        # Configuraciones específicas por sistema
        if sistema == 'windows':
            cmd.extend([
                "--uac-admin",  # Solicitar permisos de administrador
                "--version-file", "version_info.txt" if Path("version_info.txt").exists() else ""
            ])
        elif sistema == 'linux':
            cmd.extend(["--strip"])
        
        # Remover argumentos vacíos
        cmd = [c for c in cmd if c]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            installer_path = Path("dist") / installer_name
            if installer_path.exists():
                size = installer_path.stat().st_size / 1024 / 1024
                print(f"✅ Instalador compilado: {installer_name} ({size:.1f} MB)")
                return installer_path
            else:
                print(f"❌ No se encontró {installer_name}")
                return None
        else:
            print(f"❌ Error compilando instalador: {result.stderr}")
            return None
            
    except Exception as e:
        print(f"❌ Error compilando instalador: {e}")
        return None

def crear_paquete_deb(installer_path):
    """Crea paquete .deb para Linux"""
    if detectar_sistema() != 'linux':
        return None
    
    print("📦 Creando paquete .deb para Linux...")
    
    try:
        # Crear estructura de paquete .deb
        deb_dir = Path("dist/cronux-crx_1.0.0_amd64")
        deb_dir.mkdir(exist_ok=True)
        
        # DEBIAN directory
        debian_dir = deb_dir / "DEBIAN"
        debian_dir.mkdir(exist_ok=True)
        
        # Control file
        control_content = """Package: cronux-crx
Version: 1.0.0
Section: utils
Priority: optional
Architecture: amd64
Depends: python3, python3-pyqt5
Maintainer: Cronux Team <cronux@example.com>
Description: Cronux-CRX - Sistema de Control de Versiones Local
 Cronux-CRX es un sistema de control de versiones local simple y poderoso
 que te permite crear proyectos, guardar snapshots de tu trabajo,
 ver el historial y restaurar versiones anteriores.
"""
        
        with open(debian_dir / "control", 'w') as f:
            f.write(control_content)
        
        # Postinst script
        postinst_content = """#!/bin/bash
set -e

# Hacer ejecutable
chmod +x /opt/cronux-crx/CronuxCRX_Installer

# Crear enlace simbólico
ln -sf /opt/cronux-crx/CronuxCRX_Installer /usr/local/bin/cronux-installer

echo "Cronux-CRX Installer instalado correctamente"
echo "Ejecuta: cronux-installer"
"""
        
        postinst_path = debian_dir / "postinst"
        with open(postinst_path, 'w') as f:
            f.write(postinst_content)
        postinst_path.chmod(0o755)
        
        # Prerm script
        prerm_content = """#!/bin/bash
set -e

# Remover enlace simbólico
rm -f /usr/local/bin/cronux-installer

echo "Cronux-CRX Installer desinstalado"
"""
        
        prerm_path = debian_dir / "prerm"
        with open(prerm_path, 'w') as f:
            f.write(prerm_content)
        prerm_path.chmod(0o755)
        
        # Copiar el instalador
        opt_dir = deb_dir / "opt/cronux-crx"
        opt_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(installer_path, opt_dir / "CronuxCRX_Installer")
        
        # Crear .desktop file
        applications_dir = deb_dir / "usr/share/applications"
        applications_dir.mkdir(parents=True, exist_ok=True)
        
        desktop_content = """[Desktop Entry]
Name=Cronux-CRX Installer
Comment=Sistema de Control de Versiones Local
Exec=/opt/cronux-crx/CronuxCRX_Installer
Icon=cronux-crx
Terminal=false
Type=Application
Categories=Development;Utility;
"""
        
        with open(applications_dir / "cronux-crx.desktop", 'w') as f:
            f.write(desktop_content)
        
        # Crear el paquete .deb
        deb_file = Path("dist/cronux-crx_1.0.0_amd64.deb")
        result = subprocess.run([
            "dpkg-deb", "--build", str(deb_dir), str(deb_file)
        ], capture_output=True, text=True)
        
        if result.returncode == 0 and deb_file.exists():
            size = deb_file.stat().st_size / 1024 / 1024
            print(f"✅ Paquete .deb creado: {deb_file.name} ({size:.1f} MB)")
            return deb_file
        else:
            print(f"❌ Error creando .deb: {result.stderr}")
            return None
            
    except Exception as e:
        print(f"❌ Error creando paquete .deb: {e}")
        return None

def limpiar_archivos_temporales():
    """Limpia archivos temporales"""
    print("🧹 Limpiando archivos temporales...")
    
    for path in ["temp_cli", "temp_gui", "build", "__pycache__"]:
        if Path(path).exists():
            shutil.rmtree(path)
    
    for spec_file in Path(".").glob("*.spec"):
        spec_file.unlink()

def mostrar_instrucciones_optimizadas(installer_path, deb_path=None):
    """Muestra instrucciones de uso del instalador optimizado"""
    sistema = detectar_sistema()
    
    print(f"""
🎉 ¡COMPILACIÓN OPTIMIZADA COMPLETADA!

📦 Archivo generado:
   • {installer_path.name} - Instalador con CLI embebido
""")
    
    if deb_path:
        print(f"   • {deb_path.name} - Paquete .deb para distribución")
    
    print("\n🚀 INSTRUCCIONES DE USO:\n")
    
    if sistema == 'windows':
        print("""💻 WINDOWS:

🖥️ INSTALACIÓN AUTOMÁTICA:
   1. Ejecuta: CronuxCRX_Installer.exe
   2. El instalador se ejecutará como administrador automáticamente
   3. Clic en "Instalar CLI"
   4. ¡Listo! El comando 'crx' estará disponible globalmente

✨ CARACTERÍSTICAS:
   • CLI embebido (no necesita archivos externos)
   • Ejecución automática como administrador
   • Instalación en System32 para acceso global
   • Interfaz moderna adaptativa

🎯 Uso después de instalar:
   crx new mi-proyecto
   crx save -m "Primera versión"
   crx log
""")
    
    elif sistema == 'macos':
        print("""🍎 MACOS:

🖥️ INSTALACIÓN AUTOMÁTICA:
   1. Ejecuta: CronuxCRX_Installer.app
   2. El instalador solicitará permisos de administrador
   3. Clic en "Instalar CLI"
   4. ¡Listo! El comando 'crx' estará disponible globalmente

✨ CARACTERÍSTICAS:
   • CLI embebido (no necesita archivos externos)
   • Solicitud automática de permisos de administrador
   • Instalación en /usr/local/bin para acceso global
   • Interfaz nativa de macOS

🎯 Uso después de instalar:
   crx new mi-proyecto
   crx save -m "Primera versión"
   crx log
""")
    
    elif sistema == 'linux':
        print(f"""🐧 LINUX:

🖥️ OPCIÓN 1: Paquete .deb (Recomendado para Ubuntu/Debian)
   sudo dpkg -i {deb_path.name if deb_path else 'cronux-crx_1.0.0_amd64.deb'}
   cronux-installer

🖥️ OPCIÓN 2: Ejecutable directo
   ./CronuxCRX_Installer
   (Solicitará permisos de administrador automáticamente)

✨ CARACTERÍSTICAS:
   • CLI embebido (no necesita archivos externos)
   • Paquete .deb para fácil instalación/desinstalación
   • Solicitud automática de permisos de administrador
   • Instalación en /usr/local/bin para acceso global
   • Interfaz adaptativa para Linux

🎯 Uso después de instalar:
   crx new mi-proyecto
   crx save -m "Primera versión"
   crx log
""")
    
    print("""
💡 COMANDOS DISPONIBLES:
   crx new <nombre>        - Crear nuevo proyecto
   crx save -m "mensaje"   - Guardar versión
   crx log                 - Ver historial
   crx restore <version>   - Restaurar versión
   crx status              - Ver estado
   crx help                - Ver ayuda completa

🌟 ¡El instalador es completamente portable y autónomo!
   Puedes moverlo a cualquier ubicación y seguirá funcionando.
""")

def main():
    """Función principal"""
    sistema = detectar_sistema()
    
    print(f"""
🎯 CRONUX-CRX OPTIMIZED COMPILER
================================
Sistema detectado: {sistema.upper()}
Python: {sys.version.split()[0]}
Modo: Instalador único con CLI embebido
""")
    
    # Verificar que existe el CLI y GUI
    if not Path("cli/cronux_cli.py").exists():
        print("❌ No se encuentra cli/cronux_cli.py")
        return False
    
    if not Path("gui/cronux_gui.py").exists():
        print("❌ No se encuentra gui/cronux_gui.py")
        return False
    
    # Verificar PyQt5
    try:
        import PyQt5
        print("✅ PyQt5 detectado")
    except ImportError:
        print("❌ PyQt5 no disponible")
        print("💡 Instala con: pip install PyQt5")
        return False
    
    # Proceso de compilación optimizado
    limpiar_archivos()
    
    # 1. Compilar CLI temporal
    cli_path = compilar_cli_temporal()
    if not cli_path:
        return False
    
    # 2. Embeber CLI en GUI
    gui_embedded_path = embeber_cli_en_gui(cli_path)
    if not gui_embedded_path:
        return False
    
    # 3. Compilar instalador final
    installer_path = compilar_instalador_final(gui_embedded_path)
    if not installer_path:
        return False
    
    # 4. Crear paquete .deb para Linux
    deb_path = None
    if sistema == 'linux':
        deb_path = crear_paquete_deb(installer_path)
    
    # 5. Limpiar archivos temporales
    limpiar_archivos_temporales()
    
    # 6. Mostrar instrucciones
    mostrar_instrucciones_optimizadas(installer_path, deb_path)
    
    return True

if __name__ == "__main__":
    try:
        if main():
            print("\n✅ Compilación optimizada completada exitosamente")
        else:
            print("\n❌ Compilación falló")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠️  Proceso cancelado por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        sys.exit(1)