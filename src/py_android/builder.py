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
        """Descarga e instala el entorno si no está presente."""
        if not os.path.exists(self.module_dir):
            os.makedirs(self.module_dir)
        
        # Verificar si la carpeta está vacía
        if not os.listdir(self.module_dir):
            jdk_url = "https://huggingface.co/datasets/Pacureai/py-adroind/resolve/main/jdk-17.0.12_windows-x64_bin.zip?download=true"
            gradle_url = "https://huggingface.co/datasets/Pacureai/py-adroind/resolve/main/gradle-8.1.1.zip?download=true"
            
            for url, name in [(jdk_url, "jdk.zip"), (gradle_url, "gradle.zip")]:
                path = os.path.join(self.module_dir, name)
                print(f"📥 Descargando: {name}...")
                r = requests.get(url, stream=True)
                with open(path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                with zipfile.ZipFile(path, 'r') as z:
                    z.extractall(self.module_dir)
                os.remove(path)
            print("✅ Entorno descargado correctamente.")

    def find_binaries(self):
        """Busca gradlew.bat/gradle.bat y JAVA_HOME en la carpeta de módulos."""
        is_win = self.os_type == "windows"
        
        # Lista de candidatos: prioridad para gradlew, fallback a gradle
        gradle_candidates = ["gradlew.bat", "gradle.bat"] if is_win else ["gradlew", "gradle"]
        java_exe = "java.exe" if is_win else "java"
        
        gradle_bin = None
        java_home = None

        # Escaneo profundo
        for root, dirs, files in os.walk(self.module_dir):
            # Buscar el ejecutable de Gradle
            for candidate in gradle_candidates:
                if candidate in files:
                    gradle_bin = os.path.join(root, candidate)
            
            # Buscar el JAVA_HOME (carpeta que contenga /bin/java.exe)
            if "bin" in dirs and java_exe in os.listdir(os.path.join(root, "bin")):
                java_home = root
        
        if not gradle_bin:
            print(f"❌ Error: No se encontró un ejecutable de Gradle válido en {self.module_dir}")
        if not java_home:
            print("❌ Error: No se pudo localizar la carpeta JDK.")
            
        return gradle_bin, java_home

    def build_apk(self, project_path):
        self.setup_env()
        
        # Inspección del proyecto
        inspector = ProjectInspector(project_path, self.base_dir)
        if inspector.inspect()[0]: 
            sys.exit(1)

        # Localizar binarios
        gradle_bin, java_home = self.find_binaries()
        
        if not gradle_bin or not java_home:
            sys.exit(1)

        # Preparar variables de entorno
        env = os.environ.copy()
        env["JAVA_HOME"] = java_home
        
        print(f"🚀 Iniciando construcción con Gradle: {gradle_bin}")
        try:
            # Ejecución del comando de compilación
            subprocess.run([gradle_bin, "assembleRelease"], cwd=project_path, env=env, check=True)
            print("✅ ¡Compilación finalizada con éxito!")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error durante la compilación: {e}")
            sys.exit(1)
