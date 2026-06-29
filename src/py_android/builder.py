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

    def _find_file(self, filename):
        """Busca el ejecutable en cualquier subcarpeta de module/."""
        for root, dirs, files in os.walk(self.module_dir):
            if filename in files:
                return os.path.join(root, filename)
        return None

    def _download_file(self, url, dest_path):
        """Descarga binarios de forma estable."""
        print(f"📥 Descargando: {url.split('/')[-1].split('?')[0]}...")
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            total_size = int(r.headers.get('content-length', 0))
            with open(dest_path, 'wb') as f, tqdm(total=total_size, unit='B', unit_scale=True) as pbar:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
                    pbar.update(len(chunk))

    def setup_env(self):
        """Prepara el entorno buscando automáticamente los ejecutables."""
        if not os.path.exists(self.module_dir):
            os.makedirs(self.module_dir)

        # URLs de Hugging Face
        jdk_url = "https://huggingface.co/datasets/Pacureai/py-adroind/resolve/main/jdk-17.0.12_windows-x64_bin.zip?download=true"
        gradle_url = "https://huggingface.co/datasets/Pacureai/py-adroind/resolve/main/gradle-8.1.1.zip?download=true"
        
        jdk_path = os.path.join(self.module_dir, "jdk_pack.zip")
        gradle_path = os.path.join(self.module_dir, "gradle_pack.zip")

        # Descarga y extracción si no existe el JDK
        if not os.path.exists(os.path.join(self.module_dir, "jdk-17.0.12")):
            self._download_file(jdk_url, jdk_path)
            self._download_file(gradle_url, gradle_path)
            
            print("📦 Extrayendo archivos...")
            for p in [jdk_path, gradle_path]:
                with zipfile.ZipFile(p, 'r') as z: z.extractall(self.module_dir)
                os.remove(p)
            print("✅ Entorno preparado.")

    def build_apk(self, project_path):
        self.setup_env() # AQUÍ ESTÁ EL MÉTODO QUE FALTABA
        
        # Validar proyecto
        inspector = ProjectInspector(project_path, self.base_dir)
        if inspector.inspect()[0]: sys.exit(1)

        gradlew = "gradlew.bat" if self.os_type == "windows" else "gradlew"
        gradle_bin = self._find_file(gradlew)
        
        # Localización dinámica de JAVA_HOME
        java_home = None
        for root, dirs, files in os.walk(self.module_dir):
            if "bin" in dirs and os.path.exists(os.path.join(root, "bin", "java.exe")):
                java_home = root
                break
        
        if not gradle_bin or not java_home:
            print(f"❌ Error: No se encontró Gradle o Java en {self.module_dir}")
            sys.exit(1)

        env = os.environ.copy()
        env["JAVA_HOME"] = java_home
        
        print(f"🚀 Ejecutando: {gradle_bin}")
        subprocess.run([gradle_bin, "assembleRelease"], cwd=project_path, env=env, check=True)
