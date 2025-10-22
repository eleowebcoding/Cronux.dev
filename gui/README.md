# GUI - Cronux-CRX

**Interfaz Gráfica para el Instalador de Cronux-CRX**

Cronux-CRX (Cronux Control de Revisiones eXtendido) incluye una interfaz gráfica moderna para facilitar la instalación del CLI.

## 📁 Contenido

- `cronux_gui.py` - Interfaz gráfica principal del instalador

## 🚀 Uso

### Ejecutar la interfaz gráfica:
```bash
python gui/cronux_gui.py
```

### Requisitos:
```bash
pip install PyQt5
```

## 🎨 Características

- **Diseño moderno** con tema oscuro
- **Multiplataforma** (Windows, macOS, Linux)
- **Instalación automática** del CLI
- **Detección del sistema** operativo
- **Interfaz intuitiva** con botones grandes
- **Feedback visual** con progress bar

## 🖥️ Capturas de Pantalla

La interfaz incluye:
- Logo/icono principal
- Estado de instalación
- Botón principal de instalación/prueba
- Botón de desinstalación
- Información del proyecto
- Botones de acción claros

## 🔧 Compilación

Para crear un ejecutable de la GUI:

```bash
# Instalar dependencias
pip install PyQt5 pyinstaller

# Compilar GUI
pyinstaller --onefile --windowed --name CronuxCRX_Installer gui/cronux_gui.py
```

## 🎯 Funcionalidades

### Instalación
- Detecta el sistema operativo automáticamente
- Instala el CLI en la ubicación correcta
- Maneja permisos de administrador
- Verifica la instalación

### Desinstalación
- Elimina el CLI del sistema
- Limpieza completa
- Confirmación de usuario

### Prueba
- Abre terminal con comandos de prueba
- Específico para cada sistema operativo
- Feedback inmediato

## 📱 Compatibilidad

- ✅ **Windows** - Instala en System32
- ✅ **macOS** - Instala en /usr/local/bin
- ✅ **Linux** - Instala en /usr/local/bin