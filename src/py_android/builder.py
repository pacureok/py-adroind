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
        home_dir = os.path.expanduser("~")
        self.module_dir = os.path.join(home_dir, ".py-android", "module")
        self.os_type = platform.system().lower()

    def setup_env(self):
        if not os.path.exists(self.module_dir):
            os.makedirs(self.module_dir)
        
        # Si la carpeta parece vacía o no tiene binarios, descargamos
        if not any(fname.endswith('.zip') for fname in os.listdir(self.module_dir)) and \
           not any(os.path.isdir(os.path.join(self.module_dir, d)) for d in os.listdir(self.module_dir) if 'jdk' in d or 'gradle' in d):
            
            jdk_url = "https://huggingface.co/datasets/Pacureai/py-adroind/resolve/main/jdk-17.0.12_windows-x64_bin.zip?download=true"
            gradle_url = "https://huggingface.co/datasets/Pacureai/py-adroind/resolve/main/gradle-8.1.1.zip?download=true"
            
            for url, name in [(jdk_url, "jdk.zip"), (gradle_url, "gradle.zip")]:
                path = os.path.join(self.module_dir, name)
                print(f"📥 Descargando: {name}...")
                r = requests.get(url, stream=True)
                with open(path, 'wb') as f: f.write(r.content)
                with zipfile.ZipFile(path, 'r') as z: z.extractall(self.module_dir)
                os.remove(path)
            print("✅ Entorno descargado.")

    def find_binaries(self):
        gradlew = "gradlew.bat" if self.os_type == "windows" else "gradlew"
        java_exe = "java.exe" if self.os_type == "windows" else "java"
        
        gradle_bin = None
        java_home = None

        # Escaneo profundo
        for root, dirs, files in os.walk(self.module_dir):
            if gradlew in files:
                gradle_bin = os.path.join(root, gradlew)
            if "bin" in dirs and (java_exe in os.listdir(os.path.join(root, "bin"))):
                java_home = root
        
        # SI FALLA: Imprime lo que hay en la carpeta para debuggear
        if not gradle_bin:
            print("\n❌ ERROR CRÍTICO: No se encontró 'gradlew.bat'.")
            print(f"Buscando en: {self.module_dir}")
            print("Estructura de archivos encontrada:")
            for root, dirs, files in os.walk(self.module_dir):
                level = root.replace(self.module_dir, '').count(os.sep)
                indent = ' ' * 4 * level
                print(f"{indent}{os.path.basename(root)}/")
                for f in files:
                    print(f"{indent}    {f}")
        
        return gradle_bin, java_home

    def build_apk(self, project_path):
        self.setup_env()
        inspector = ProjectInspector(project_path, self.base_dir)
        if inspector.inspect()[0]: sys.exit(1)

        gradle_bin, java_home = self.find_binaries()
        
        if not gradle_bin or not java_home:
            sys.exit(1)

        env = os.environ.copy()
        env["JAVA_HOME"] = java_home
        
        print(f"🚀 Compilando con Gradle: {gradle_bin}")
        subprocess.run([gradle_bin, "assembleRelease"], cwd=project_path, env=env, check=True)
