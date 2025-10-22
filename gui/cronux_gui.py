#!/usr/bin/env python3
"""
Cronux-CRX GUI - Instalador optimizado con CLI embebido
Diseño adaptativo para Windows, macOS y Linux
"""

import sys
import os
import threading
import subprocess
import shutil
import tempfile
import base64
import platform
from pathlib import Path

# Verificar si PyQt5 está disponible
try:
    from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                                QWidget, QLabel, QPushButton, QProgressBar, QMessageBox,
                                QFrame, QSpacerItem, QSizePolicy, QGraphicsDropShadowEffect)
    from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QSize, QPropertyAnimation, QEasingCurve
    from PyQt5.QtGui import QFont, QPalette, QColor, QPixmap, QIcon, QPainter, QBrush, QLinearGradient
    PYQT5_AVAILABLE = True
except ImportError:
    PYQT5_AVAILABLE = False
    print("⚠️  PyQt5 no está instalado. Instala con: pip install PyQt5")

# CLI embebido como base64 (se generará automáticamente durante la compilación)
EMBEDDED_CLI_DATA = None


class InstallWorker(QThread):
    """Worker thread para instalación/desinstalación"""
    finished = pyqtSignal(bool, str)
    
    def __init__(self, action, cli_path=None):
        super().__init__()
        self.action = action  # 'install' o 'uninstall'
        self.cli_path = cli_path
    
    def run(self):
        try:
            if self.action == 'install':
                if not self.cli_path or not Path(self.cli_path).exists():
                    self.finished.emit(False, "No se encontró el ejecutable CLI")
                    return
                
                # Método de instalación según el sistema
                if sys.platform.startswith('win'):
                    self.install_windows()
                elif sys.platform.startswith('darwin'):
                    self.install_macos()
                elif sys.platform.startswith('linux'):
                    self.install_linux()
                else:
                    self.finished.emit(False, "Sistema operativo no soportado")
                    
            else:  # uninstall
                if sys.platform.startswith('win'):
                    self.uninstall_windows()
                elif sys.platform.startswith('darwin'):
                    self.uninstall_macos()
                elif sys.platform.startswith('linux'):
                    self.uninstall_linux()
                else:
                    self.finished.emit(False, "Sistema operativo no soportado")
        
        except Exception as e:
            self.finished.emit(False, f"Error inesperado: {str(e)}")
    
    def install_windows(self):
        """Instalación en Windows"""
        try:
            # Copiar a System32 o crear en PATH
            system32_path = Path("C:/Windows/System32/crx.exe")
            
            # Intentar copiar a System32
            try:
                shutil.copy2(self.cli_path, system32_path)
                self.finished.emit(True, "¡Instalación completada exitosamente!")
            except PermissionError:
                # Si no hay permisos, sugerir instalación manual
                self.finished.emit(False, 
                    f"Necesitas permisos de administrador.\n"
                    f"Copia manualmente {self.cli_path} a C:\\Windows\\System32\\")
        except Exception as e:
            self.finished.emit(False, f"Error en instalación Windows: {e}")
    
    def install_macos(self):
        """Instalación en macOS"""
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='_crx') as temp_file:
                temp_path = temp_file.name
            
            # Copiar al temporal
            shutil.copy2(self.cli_path, temp_path)
            subprocess.run(["chmod", "+x", temp_path], check=True)
            
            # Comando para mover a /usr/local/bin
            cmd = f"sudo /bin/rm -f /usr/local/bin/crx && sudo /bin/mv '{temp_path}' /usr/local/bin/crx && sudo /bin/chmod 755 /usr/local/bin/crx"
            applescript = f'do shell script "{cmd}" with administrator privileges'
            result = subprocess.run(["osascript", "-e", applescript], capture_output=True, text=True)
            
            if result.returncode == 0:
                crx_path = Path("/usr/local/bin/crx")
                if crx_path.exists():
                    self.finished.emit(True, "¡Instalación completada exitosamente!")
                else:
                    self.finished.emit(False, "Error: El archivo no se instaló correctamente")
            else:
                self.finished.emit(False, f"Error durante la instalación: {result.stderr}")
                
        except Exception as e:
            self.finished.emit(False, f"Error en instalación macOS: {e}")
    
    def install_linux(self):
        """Instalación en Linux"""
        try:
            # Intentar copiar a /usr/local/bin
            target_path = Path("/usr/local/bin/crx")
            
            try:
                shutil.copy2(self.cli_path, target_path)
                target_path.chmod(0o755)
                self.finished.emit(True, "¡Instalación completada exitosamente!")
            except PermissionError:
                self.finished.emit(False, 
                    f"Necesitas permisos de administrador.\n"
                    f"Ejecuta: sudo cp {self.cli_path} /usr/local/bin/crx")
        except Exception as e:
            self.finished.emit(False, f"Error en instalación Linux: {e}")
    
    def uninstall_windows(self):
        """Desinstalación en Windows"""
        try:
            system32_path = Path("C:/Windows/System32/crx.exe")
            if system32_path.exists():
                system32_path.unlink()
                self.finished.emit(True, "¡Desinstalación completada exitosamente!")
            else:
                self.finished.emit(False, "CLI no encontrado en el sistema")
        except Exception as e:
            self.finished.emit(False, f"Error en desinstalación: {e}")
    
    def uninstall_macos(self):
        """Desinstalación en macOS"""
        try:
            cmd = "sudo /bin/rm -f /usr/local/bin/crx"
            applescript = f'do shell script "{cmd}" with administrator privileges'
            result = subprocess.run(["osascript", "-e", applescript], capture_output=True, text=True)
            
            if result.returncode == 0:
                if not Path("/usr/local/bin/crx").exists():
                    self.finished.emit(True, "¡Desinstalación completada exitosamente!")
                else:
                    self.finished.emit(False, "Error: No se pudo eliminar completamente")
            else:
                self.finished.emit(False, f"Error durante la desinstalación: {result.stderr}")
        except Exception as e:
            self.finished.emit(False, f"Error en desinstalación: {e}")
    
    def uninstall_linux(self):
        """Desinstalación en Linux"""
        try:
            target_path = Path("/usr/local/bin/crx")
            if target_path.exists():
                target_path.unlink()
                self.finished.emit(True, "¡Desinstalación completada exitosamente!")
            else:
                self.finished.emit(False, "CLI no encontrado en el sistema")
        except Exception as e:
            self.finished.emit(False, f"Error en desinstalación: {e}")


class CronuxGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.is_installed = self.check_if_installed()
        self.worker = None
        self.init_ui()
    
    def init_ui(self):
        """Inicializa la interfaz de usuario con diseño adaptativo"""
        self.setWindowTitle("Cronux-CRX Installer")
        
        # Tamaño adaptativo según el sistema (optimizado para mostrar todo el contenido)
        if platform.system() == "Darwin":  # macOS
            self.setFixedSize(600, 700)
        elif platform.system() == "Windows":
            self.setFixedSize(600, 700)
        else:  # Linux
            self.setFixedSize(620, 720)
        
        # Estilo moderno y adaptativo
        self.setStyleSheet(self.get_adaptive_stylesheet())
        
        # Configurar ventana sin bordes nativos para mejor control
        self.setWindowFlags(Qt.Window | Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint)
        
        # Agregar sombra a la ventana
        self.add_window_shadow()
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(40, 40, 40, 40)
        
        # Spacer superior
        main_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        # Icono grande (cargar icono real)
        icon_label = QLabel()
        icon_label.setAlignment(Qt.AlignCenter)
        
        # Intentar cargar el icono real
        try:
            icon_path = self.get_icon_path()
            if icon_path and icon_path.exists():
                pixmap = QPixmap(str(icon_path))
                scaled_pixmap = pixmap.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                icon_label.setPixmap(scaled_pixmap)
            else:
                # Fallback al emoji
                icon_label.setText("🖥️")
                icon_font = QFont()
                icon_font.setPointSize(48)
                icon_label.setFont(icon_font)
        except Exception:
            # Fallback al emoji
            icon_label.setText("🖥️")
            icon_font = QFont()
            icon_font.setPointSize(48)
            icon_label.setFont(icon_font)
        
        main_layout.addWidget(icon_label)
        
        # Título de estado
        self.status_label = QLabel()
        self.status_label.setAlignment(Qt.AlignCenter)
        status_font = QFont()
        status_font.setPointSize(20)
        status_font.setBold(True)
        self.status_label.setFont(status_font)
        main_layout.addWidget(self.status_label)
        
        # Versión
        version_label = QLabel("v0.1.0 Beta")
        version_label.setAlignment(Qt.AlignCenter)
        version_font = QFont()
        version_font.setPointSize(12)
        version_label.setFont(version_font)
        version_label.setStyleSheet("color: #9ca3af; margin-bottom: 20px;")
        main_layout.addWidget(version_label)
        
        # Spacer
        main_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Fixed))
        
        # Descripción
        desc_label = QLabel(
            "Cronux-CRX es un sistema de control de versiones local simple\n"
            "que te permite crear proyectos, guardar snapshots de tu trabajo,\n"
            "ver el historial y restaurar versiones anteriores.\n"
            "Compatible con cualquier tipo de archivo y proyecto."
        )
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setWordWrap(True)
        desc_font = QFont()
        desc_font.setPointSize(13)
        desc_label.setFont(desc_font)
        desc_label.setStyleSheet("color: #9ca3af; line-height: 1.4;")
        main_layout.addWidget(desc_label)
        
        # Spacer
        main_layout.addItem(QSpacerItem(20, 25, QSizePolicy.Minimum, QSizePolicy.Fixed))
        
        # Botón de desinstalación
        self.uninstall_button = QPushButton("Desinstalar CLI")
        self.uninstall_button.setObjectName("uninstallButton")
        self.uninstall_button.setFixedSize(160, 35)
        self.uninstall_button.clicked.connect(self.confirm_uninstall)
        main_layout.addWidget(self.uninstall_button, alignment=Qt.AlignCenter)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setRange(0, 0)  # Indeterminado
        main_layout.addWidget(self.progress_bar)
        
        # Botón principal
        self.main_button = QPushButton()
        self.main_button.setObjectName("primaryButton")
        self.main_button.setFixedSize(300, 48)
        self.main_button.clicked.connect(self.on_main_button_click)
        main_layout.addWidget(self.main_button, alignment=Qt.AlignCenter)
        
        # Botón cerrar
        close_button = QPushButton("Cerrar")
        close_button.setObjectName("closeButton")
        close_button.setFixedSize(280, 40)
        close_button.clicked.connect(self.close)
        main_layout.addWidget(close_button, alignment=Qt.AlignCenter)
        
        # Spacer inferior
        main_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        # Actualizar estado inicial
        self.update_ui_state()
        
        # Centrar ventana
        self.center_window()
    
    def get_adaptive_stylesheet(self):
        """Retorna estilos adaptativos según el sistema operativo"""
        base_style = """
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #0f172a, stop:1 #1e293b);
                border-radius: 12px;
            }
            QLabel {
                color: #f1f5f9;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            }
            QPushButton {
                background-color: #334155;
                color: #f1f5f9;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                font-weight: 600;
                font-size: 14px;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            }
            QPushButton:hover {
                background-color: #475569;
                transform: translateY(-1px);
            }
            QPushButton:pressed {
                background-color: #1e293b;
                transform: translateY(0px);
            }
            QPushButton#primaryButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3b82f6, stop:1 #1d4ed8);
                font-size: 16px;
                font-weight: 700;
                padding: 16px 32px;
                border-radius: 12px;
                min-height: 20px;
            }
            QPushButton#primaryButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #60a5fa, stop:1 #2563eb);
            }
            QPushButton:disabled {
                background-color: #64748b;
                color: #94a3b8;
            }
            QPushButton#closeButton {
                background-color: #64748b;
                font-weight: 500;
            }
            QPushButton#closeButton:hover {
                background-color: #475569;
            }
            QPushButton#uninstallButton {
                background-color: rgba(248, 113, 113, 0.1);
                color: #f87171;
                border: 1px solid rgba(248, 113, 113, 0.3);
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 13px;
                font-weight: 600;
            }
            QPushButton#uninstallButton:hover {
                background-color: rgba(239, 68, 68, 0.2);
                color: #ef4444;
                border: 1px solid rgba(239, 68, 68, 0.5);
            }
            QProgressBar {
                border: 2px solid #475569;
                border-radius: 8px;
                text-align: center;
                height: 24px;
                background-color: #1e293b;
                color: #f1f5f9;
                font-weight: 600;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #10b981, stop:1 #059669);
                border-radius: 6px;
            }
        """
        
        # Ajustes específicos por sistema
        if platform.system() == "Darwin":  # macOS
            base_style += """
                QPushButton {
                    font-size: 13px;
                }
                QPushButton#primaryButton {
                    font-size: 15px;
                }
            """
        elif platform.system() == "Windows":
            base_style += """
                QPushButton {
                    font-size: 14px;
                }
                QPushButton#primaryButton {
                    font-size: 16px;
                }
            """
        else:  # Linux
            base_style += """
                QPushButton {
                    font-size: 14px;
                }
                QPushButton#primaryButton {
                    font-size: 16px;
                }
            """
        
        return base_style
    
    def add_window_shadow(self):
        """Agrega sombra moderna a la ventana"""
        try:
            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(20)
            shadow.setXOffset(0)
            shadow.setYOffset(4)
            shadow.setColor(QColor(0, 0, 0, 80))
            self.setGraphicsEffect(shadow)
        except Exception:
            pass  # Si falla, continuar sin sombra
    
    def center_window(self):
        """Centra la ventana en la pantalla"""
        screen = QApplication.desktop().screenGeometry()
        size = self.geometry()
        self.move(
            (screen.width() - size.width()) // 2,
            (screen.height() - size.height()) // 2
        )
    
    def check_if_installed(self):
        """Verifica si Cronux-CRX CLI está instalado"""
        if sys.platform.startswith('win'):
            return Path("C:/Windows/System32/crx.exe").exists()
        else:
            return Path("/usr/local/bin/crx").exists()
    
    def get_cli_executable_path(self):
        """Obtiene la ruta del ejecutable CLI (embebido o externo)"""
        # Primero intentar extraer el CLI embebido
        if EMBEDDED_CLI_DATA:
            return self.extract_embedded_cli()
        
        # Fallback: buscar en el directorio actual o dist
        for path in [Path("dist/crx"), Path("dist/crx.exe"), Path("crx"), Path("crx.exe")]:
            if path.exists():
                return path
        return None
    
    def extract_embedded_cli(self):
        """Extrae el CLI embebido a un archivo temporal"""
        if not EMBEDDED_CLI_DATA:
            return None
        
        try:
            # Crear archivo temporal
            temp_dir = Path(tempfile.gettempdir()) / "cronux_installer"
            temp_dir.mkdir(exist_ok=True)
            
            if platform.system() == "Windows":
                cli_path = temp_dir / "crx.exe"
            else:
                cli_path = temp_dir / "crx"
            
            # Decodificar y escribir el CLI
            cli_data = base64.b64decode(EMBEDDED_CLI_DATA)
            with open(cli_path, 'wb') as f:
                f.write(cli_data)
            
            # Hacer ejecutable en Unix
            if platform.system() != "Windows":
                cli_path.chmod(0o755)
            
            return cli_path
            
        except Exception as e:
            print(f"Error extrayendo CLI embebido: {e}")
            return None
    
    def get_icon_path(self):
        """Obtiene la ruta del icono principal"""
        if getattr(sys, 'frozen', False):
            return Path(sys._MEIPASS) / "assets" / "cronux_cli.png"
        else:
            base = Path(__file__).parent.parent
            return base / "assets" / "cronux_cli.png"
    
    def get_utility_icon_path(self, icon_name):
        """Obtiene la ruta de un icono de utilidades"""
        if getattr(sys, 'frozen', False):
            return Path(sys._MEIPASS) / "assets" / icon_name
        else:
            base = Path(__file__).parent.parent
            return base / "assets" / icon_name
    
    def update_ui_state(self):
        """Actualiza el estado mostrado"""
        if self.is_installed:
            self.status_label.setText("Cronux-CRX CLI está instalado")
            self.status_label.setStyleSheet("color: #10b981;")
            self.set_button_with_icon(self.main_button, "Probar CLI", "terminal.png", 24)
            self.uninstall_button.setVisible(True)
            self.set_button_with_icon(self.uninstall_button, "Desinstalar CLI", "uninstall.png", 16)
        else:
            self.status_label.setText("Cronux-CRX CLI no está instalado")
            self.status_label.setStyleSheet("color: #ef4444;")
            self.set_button_with_icon(self.main_button, "Instalar CLI", "install.png", 24)
            self.uninstall_button.setVisible(False)
    
    def set_button_with_icon(self, button, text, icon_name, icon_size=24):
        """Configura un botón con icono y texto"""
        try:
            icon_path = self.get_utility_icon_path(icon_name)
            if icon_path and icon_path.exists():
                pixmap = QPixmap(str(icon_path))
                if not pixmap.isNull():
                    scaled_pixmap = pixmap.scaled(icon_size * 2, icon_size * 2, 
                                                Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    icon = QIcon(scaled_pixmap)
                    button.setIcon(icon)
                    button.setIconSize(QSize(icon_size, icon_size))
                    button.setText(f"   {text}")
                    return
        except Exception as e:
            print(f"Error cargando icono {icon_name}: {e}")
        
        # Fallback: solo texto
        button.setText(text)
    
    def on_main_button_click(self):
        """Maneja el clic del botón principal"""
        if self.worker and self.worker.isRunning():
            return
        
        if self.is_installed:
            self.test_cli()
        else:
            self.confirm_install()
    
    def confirm_install(self):
        """Confirma la instalación"""
        msg = QMessageBox(self)
        msg.setWindowTitle("Instalar CLI")
        msg.setText("¿Deseas instalar Cronux-CRX CLI?")
        msg.setInformativeText("Puede requerir permisos de administrador.")
        msg.setIcon(QMessageBox.Question)
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.Yes)
        
        if msg.exec_() == QMessageBox.Yes:
            self.install_cli()
    
    def confirm_uninstall(self):
        """Confirma la desinstalación"""
        msg = QMessageBox(self)
        msg.setWindowTitle("Desinstalar CLI")
        msg.setText("¿Deseas eliminar Cronux-CRX CLI del sistema?")
        msg.setInformativeText("Esta acción eliminará el comando 'crx' globalmente.")
        msg.setIcon(QMessageBox.Warning)
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.No)
        
        if msg.exec_() == QMessageBox.Yes:
            self.uninstall_cli()
    
    def install_cli(self):
        """Instala el CLI"""
        cli_path = self.get_cli_executable_path()
        if not cli_path:
            QMessageBox.critical(self, "Error", "No se encontró el ejecutable CLI")
            return
        
        self.start_operation("Instalando...", 'install', cli_path)
    
    def uninstall_cli(self):
        """Desinstala el CLI"""
        self.start_operation("Desinstalando...", 'uninstall')
    
    def start_operation(self, message, action, cli_path=None):
        """Inicia una operación de instalación/desinstalación"""
        self.main_button.setText(message)
        self.main_button.setEnabled(False)
        self.uninstall_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        
        self.worker = InstallWorker(action, cli_path)
        self.worker.finished.connect(self.on_operation_finished)
        self.worker.start()
    
    def on_operation_finished(self, success, message):
        """Maneja el fin de una operación"""
        self.progress_bar.setVisible(False)
        self.main_button.setEnabled(True)
        self.uninstall_button.setEnabled(True)
        
        if success:
            # Actualizar estado
            self.is_installed = self.check_if_installed()
            self.update_ui_state()
            self.show_success_message(message)
        else:
            self.show_error_message(message)
    
    def show_success_message(self, message):
        """Muestra mensaje de éxito personalizado"""
        msg = QMessageBox(self)
        msg.setWindowTitle("¡Éxito!")
        
        # Usar icono de éxito real
        success_icon_set = False
        try:
            success_icon_path = self.get_utility_icon_path("succes.png")
            if success_icon_path and success_icon_path.exists():
                pixmap = QPixmap(str(success_icon_path))
                if not pixmap.isNull():
                    scaled_pixmap = pixmap.scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    msg.setWindowIcon(QIcon(scaled_pixmap))
                    msg.setText(f"✓ {message}")
                    success_icon_set = True
        except Exception as e:
            print(f"Error cargando icono de éxito: {e}")
        
        if not success_icon_set:
            msg.setText("✓ " + message)
        
        msg.setIcon(QMessageBox.Information)
        msg.setStandardButtons(QMessageBox.Ok)
        
        # Personalizar botón
        ok_button = msg.button(QMessageBox.Ok)
        ok_button.setText("Perfecto")
        
        # Estilo moderno
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #1f2937;
                color: #e8eaed;
                font-size: 14px;
            }
            QMessageBox QPushButton {
                background-color: #10b981;
                color: white;
                border: none;
                padding: 8px 20px;
                border-radius: 6px;
                font-weight: bold;
                min-width: 100px;
            }
            QMessageBox QPushButton:hover {
                background-color: #059669;
            }
        """)
        
        msg.exec_()
    
    def show_error_message(self, message):
        """Muestra mensaje de error personalizado"""
        msg = QMessageBox(self)
        msg.setWindowTitle("Error")
        
        # Usar icono de error real
        error_icon_set = False
        try:
            error_icon_path = self.get_utility_icon_path("error.png")
            if error_icon_path and error_icon_path.exists():
                pixmap = QPixmap(str(error_icon_path))
                if not pixmap.isNull():
                    scaled_pixmap = pixmap.scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    msg.setWindowIcon(QIcon(scaled_pixmap))
                    msg.setText(f"✗ {message}")
                    error_icon_set = True
        except Exception as e:
            print(f"Error cargando icono de error: {e}")
        
        if not error_icon_set:
            msg.setText("✗ " + message)
        
        msg.setIcon(QMessageBox.Critical)
        msg.setStandardButtons(QMessageBox.Ok)
        
        # Personalizar botón
        ok_button = msg.button(QMessageBox.Ok)
        ok_button.setText("Entendido")
        
        # Estilo moderno
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #1f2937;
                color: #e8eaed;
                font-size: 14px;
            }
            QMessageBox QPushButton {
                background-color: #dc2626;
                color: white;
                border: none;
                padding: 8px 20px;
                border-radius: 6px;
                font-weight: bold;
                min-width: 100px;
            }
            QMessageBox QPushButton:hover {
                background-color: #b91c1c;
            }
        """)
        
        msg.exec_()
    
    def test_cli(self):
        """Abre una terminal para probar el CLI"""
        try:
            if sys.platform.startswith('win'):
                # Windows
                subprocess.run(["cmd", "/c", "start", "cmd", "/k", "crx --help"])
            elif sys.platform.startswith('darwin'):
                # macOS
                applescript = '''
                tell application "Terminal"
                    activate
                    do script "echo 'Probando Cronux-CRX CLI:' && crx --help"
                end tell
                '''
                subprocess.run(["osascript", "-e", applescript])
            else:
                # Linux
                subprocess.run(["gnome-terminal", "--", "bash", "-c", "crx --help; read"])
            
            self.show_success_message("Terminal abierta para probar el CLI")
            
        except Exception as e:
            self.show_error_message(f"No se pudo abrir la terminal: {e}")


def is_admin():
    """Verifica si se está ejecutando como administrador"""
    try:
        if platform.system() == "Windows":
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin()
        else:
            return os.geteuid() == 0
    except Exception:
        return False

def run_as_admin():
    """Ejecuta el programa como administrador"""
    try:
        if platform.system() == "Windows":
            import ctypes
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, " ".join(sys.argv), None, 1
            )
        elif platform.system() == "Darwin":  # macOS
            applescript = f'''
            do shell script "'{sys.executable}' {' '.join(sys.argv)}" with administrator privileges
            '''
            subprocess.run(["osascript", "-e", applescript])
        else:  # Linux
            # Intentar con pkexec, gksu o kdesu
            for cmd in ["pkexec", "gksu", "kdesu"]:
                if shutil.which(cmd):
                    subprocess.run([cmd, sys.executable] + sys.argv)
                    return
            # Fallback: sudo en terminal
            subprocess.run(["sudo", sys.executable] + sys.argv)
    except Exception as e:
        print(f"Error ejecutando como administrador: {e}")

def main():
    """Función principal"""
    if not PYQT5_AVAILABLE:
        print("❌ PyQt5 no está disponible")
        print("💡 Instala con: pip install PyQt5")
        return 1
    
    # Verificar si se necesitan permisos de administrador
    if not is_admin() and "--no-admin" not in sys.argv:
        print("🔐 Solicitando permisos de administrador...")
        run_as_admin()
        return 0
    
    app = QApplication(sys.argv)
    app.setApplicationName("Cronux-CRX Installer")
    app.setApplicationVersion("1.0.0")
    app.setStyle('Fusion')
    
    # Configurar paleta oscura moderna
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(15, 23, 42))
    palette.setColor(QPalette.WindowText, QColor(241, 245, 249))
    palette.setColor(QPalette.Base, QColor(30, 41, 59))
    palette.setColor(QPalette.AlternateBase, QColor(51, 65, 85))
    palette.setColor(QPalette.ToolTipBase, QColor(0, 0, 0))
    palette.setColor(QPalette.ToolTipText, QColor(255, 255, 255))
    palette.setColor(QPalette.Text, QColor(241, 245, 249))
    palette.setColor(QPalette.Button, QColor(51, 65, 85))
    palette.setColor(QPalette.ButtonText, QColor(241, 245, 249))
    palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
    palette.setColor(QPalette.Link, QColor(59, 130, 246))
    palette.setColor(QPalette.Highlight, QColor(59, 130, 246))
    palette.setColor(QPalette.HighlightedText, QColor(0, 0, 0))
    app.setPalette(palette)
    
    installer = CronuxGUI()
    installer.show()
    
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())