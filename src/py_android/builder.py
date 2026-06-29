import os
import subprocess
import platform
import sys
import zipfile
import requests
from tqdm import tqdm
from .intre import ProjectInspector

class AndroidBuilder:
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        # Corregido: apunto directamente a la ruta donde vi que se descargan tus cosas
        self.module_dir = r"C:\Users\cano5\AppData\Local\Programs\Python\Python312\Lib\module"
        self.os_type = platform.system().lower()

    def _find_file(self, filename):
        """Busca el ejecutable en cualquier subcarpeta de module/."""
        for root, dirs, files in os.walk(self.module_dir):
            if filename in files:
                return os.path.join(root, filename)
        return None

    def build_apk(self, project_path):
        # 1. Localizar Gradle
        gradle_name = "gradlew.bat" if self.os_type == "windows" else "gradlew"
        gradle_bin = self._find_file(gradle_name)
        
        # 2. Localizar JAVA_HOME (busca la carpeta que contenga 'bin/java.exe')
        java_home = None
        for root, dirs, files in os.walk(self.module_dir):
            if "bin" in dirs and os.path.exists(os.path.join(root, "bin", "java.exe")):
                java_home = root
                break
        
        if not gradle_bin or not java_home:
            print(f"❌ Error: No se encontró Gradle o Java en {self.module_dir}")
            return

        # 3. Preparar entorno
        env = os.environ.copy()
        env["JAVA_HOME"] = java_home
        
        print(f"🚀 Ejecutando: {gradle_bin}")
        print(f"☕ JAVA_HOME: {java_home}")
        
        try:
            subprocess.run([gradle_bin, "assembleRelease"], cwd=project_path, env=env, check=True)
            print("✅ ¡APK generado exitosamente!")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error en Gradle: {e}")
