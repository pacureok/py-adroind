import os
import subprocess
import platform
import sys
import tarfile
import zipfile
import requests
from tqdm import tqdm
from .intre import ProjectInspector

class AndroidBuilder:
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.module_dir = os.path.abspath(os.path.join(self.base_dir, "..", "..", "module"))
        self.os_type = platform.system().lower()
        self.arch = platform.machine().lower()

        # URLs directas a Hugging Face
        self.files = {
            "jdk-windows": "https://huggingface.co/datasets/Pacureai/py-adroind/resolve/main/jdk-17.0.12_windows-x64_bin.zip?download=true",
            "jdk-linux-x64": "https://huggingface.co/datasets/Pacureai/py-adroind/resolve/main/jdk-17.0.12_linux-x64_bin.tar.gz?download=true",
            "jdk-linux-arm": "https://huggingface.co/datasets/Pacureai/py-adroind/resolve/main/jdk-17.0.12_linux-aarch64_bin.tar.gz?download=true",
            "gradle": "https://huggingface.co/datasets/Pacureai/py-adroind/resolve/main/gradle-8.1.1.zip?download=true"
        }

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

        jdk_url = self.files["jdk-windows"] if self.os_type == "windows" else \
                  (self.files["jdk-linux-arm"] if "aarch64" in self.arch else self.files["jdk-linux-x64"])

        # Rutas temporales
        jdk_path = os.path.join(self.module_dir, "jdk_pack")
        gradle_path = os.path.join(self.module_dir, "gradle_pack")

        if not os.path.exists(os.path.join(self.module_dir, "jdk-17")):
            self._download_file(jdk_url, jdk_path)
            self._download_file(self.files["gradle"], gradle_path)
            
            print("📦 Extrayendo archivos...")
            for p in [jdk_path, gradle_path]:
                if zipfile.is_zipfile(p):
                    with zipfile.ZipFile(p, 'r') as z: z.extractall(self.module_dir)
                else:
                    with tarfile.open(p, "r:gz") as t: t.extractall(self.module_dir)
                os.remove(p)
            print("✅ Entorno preparado.")

    def _find_file(self, filename):
        """Busca recursivamente un archivo dentro de module/."""
        for root, dirs, files in os.walk(self.module_dir):
            if filename in files:
                return os.path.join(root, filename)
        return None

    def build_apk(self, project_path):
        self.setup_env()
        
        # Validar proyecto
        inspector = ProjectInspector(project_path, self.base_dir)
        if inspector.inspect()[0]: sys.exit(1)

        # Localización dinámica del ejecutable
        gradlew = "gradlew.bat" if self.os_type == "windows" else "gradlew"
        gradle_bin = self._find_file(gradlew)
        
        # Localización dinámica de JAVA_HOME
        java_home = None
        for root, dirs, files in os.walk(self.module_dir):
            if "bin" in dirs and "java.exe" in os.listdir(os.path.join(root, "bin")) or "java" in os.listdir(os.path.join(root, "bin")):
                java_home = root
                break
        
        if not gradle_bin or not java_home:
            print(f"❌ Error: No se pudo encontrar Gradle o JDK en {self.module_dir}")
            sys.exit(1)

        env = os.environ.copy()
        env["JAVA_HOME"] = java_home
        
        print(f"🚀 Iniciando compilación con: {gradle_bin}")
        subprocess.run([gradle_bin, "assembleRelease"], cwd=project_path, env=env, check=True)
