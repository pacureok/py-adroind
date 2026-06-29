# 📱 Py-Android: Compilador Definitivo de Python a APK

Py-Android es una herramienta de línea de comandos (CLI) que permite empaquetar aplicaciones escritas en **Python (3.12)** y **HTML/JS/CSS** directamente en un archivo **APK nativo de Android**. 

Todo esto se logra **sin necesidad de instalar Android Studio** y sin que el usuario tenga que configurar complejas variables de entorno. Ideal para GitHub Codespaces, Linux y Windows.

---

## ✨ Características Principales

* 📦 **Herramientas Autocontenidas:** Incluye su propia distribución portátil de Java (JDK 17) y Gradle (8.1.1). Solo necesitas tener Python instalado.
* 🌉 **Puente Nativo (Bridge):** Comunica tu código Python con funciones nativas del teléfono (como la cámara) y una interfaz web (WebView).
* 🛡️ **Inspector de Código Inteligente:** Analiza tu código antes de compilar. Si detecta librerías exclusivas de Windows (como `pyautogui`, `win32api`) o archivos `.exe`, bloquea la compilación para evitarte dolores de cabeza.
* ⚙️ **Autoconfiguración:** Genera automáticamente los archivos `build.gradle` necesarios para inyectar Chaquopy y compilar tu proyecto.
* 🌐 **Soporte para C-Extensions:** A través de Chaquopy, descarga versiones precompiladas para arquitectura ARM de librerías complejas automáticamente.

---

## 🚀 Instalación

La forma más rápida de usar la herramienta es instalarla directamente desde el repositorio (recomendado usar un entorno virtual o GitHub Codespaces):

```bash
pip install git+[https://github.com/pacureok/py-adroind](https://github.com/pacureok/py-adroind)