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
        # Ruta global: ~/.py-android/module
        home_dir = os.path.expanduser("~")
        self.module_dir = os.path.join(home_dir, ".py-android", "module")
        self.os_type = platform.system().lower()

    def setup_env(self):
        """Prepara el entorno descargando los binarios."""
        if not os.path.exists(self.module_dir):
            os.makedirs(self.module_dir)

        jdk_url = "https://huggingface.co/datasets/Pacureai/py-adroind/resolve/main/jdk-17.0.12_windows-x64_bin.zip?download=true"
        gradle_url = "https://huggingface.co/datasets/Pacureai/py-adroind/resolve/main/gradle-8.1.1.zip?download=true"
        
        # Solo descargamos si la carpeta está vacía
        if not os.listdir(self.module_dir):
            jdk_path = os.path.join(self.module_dir, "jdk_pack.zip")
            gradle_path = os.path.join(self.module_dir, "gradle_pack.zip")
            
            # Descarga (simplificada)
            for url, path in [(jdk_url, jdk_path), (gradle_url, gradle_path)]:
                print(f"📥 Descargando: {url.split('/')[-1].split('?')[0]}...")
                r = requests.get(url, stream=True)
                with open(path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192): f.write(chunk)
                
                print("📦 Extrayendo...")
                with zipfile.ZipFile(path, 'r') as z: z.extractall(self.module_dir)
                os.remove(path)
            print("✅ Entorno preparado.")

    def find_binaries(self):
        """Busca recursivamente los ejecutables."""
        gradlew = "gradlew.bat" if self.os_type == "windows" else "gradlew"
        java_exe = "java.exe" if self.os_type == "windows" else "java"
        
        gradle_bin = None
        java_home = None

        for root, dirs, files in os.walk(self.module_dir):
            # Buscar Gradle
            if gradlew in files:
                gradle_bin = os.path.join(root, gradlew)
            # Buscar Java (buscamos la carpeta 'bin' que contiene 'java.exe')
            if "bin" in dirs and java_exe in os.listdir(os.path.join(root, "bin")):
                java_home = root
        
        # Debugging: Si falla, te diremos qué vimos
        if not gradle_bin or not java_home:
            print(f"DEBUG: Escaneando carpeta {self.module_dir}")
            print(f"DEBUG: gradle_bin encontrado: {gradle_bin}")
            print(f"DEBUG: java_home encontrado: {java_home}")
        
        return gradle_bin, java_home

    def build_apk(self, project_path):
        self.setup_env()
        
        inspector = ProjectInspector(project_path, self.base_dir)
        if inspector.inspect()[0]: sys.exit(1)

        gradle_bin, java_home = self.find_binaries()
        
        if not gradle_bin or not java_home:
            print(f"❌ Error: No se pudo localizar la estructura correcta de Gradle o Java.")
            print("Por favor, verifica que dentro de la carpeta 'module' existan las carpetas con 'bin/'.")
            sys.exit(1)

        env = os.environ.copy()
        env["JAVA_HOME"] = java_home
        
        print(f"🚀 Compilando con: {gradle_bin}")
        subprocess.run([gradle_bin, "assembleRelease"], cwd=project_path, env=env, check=True)
