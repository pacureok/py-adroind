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

        # URLs directas de Hugging Face (con ?download=true)
        self.files = {
            "jdk-windows": "https://huggingface.co/datasets/Pacureai/py-adroind/resolve/main/jdk-17.0.12_windows-x64_bin.zip?download=true",
            "jdk-linux-x64": "https://huggingface.co/datasets/Pacureai/py-adroind/resolve/main/jdk-17.0.12_linux-x64_bin.tar.gz?download=true",
            "jdk-linux-arm": "https://huggingface.co/datasets/Pacureai/py-adroind/resolve/main/jdk-17.0.12_linux-aarch64_bin.tar.gz?download=true",
            "gradle": "https://huggingface.co/datasets/Pacureai/py-adroind/resolve/main/gradle-8.1.1.zip?download=true"
        }

    def _download_file(self, url, dest_path):
        """Descarga binarios de forma segura."""
        print(f"📥 Descargando: {url.split('/')[-1].split('?')[0]}...")
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            total_size = int(r.headers.get('content-length', 0))
            with open(dest_path, 'wb') as f, tqdm(total=total_size, unit='B', unit_scale=True) as pbar:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
                    pbar.update(len(chunk))

    def setup_env(self):
        if not os.path.exists(self.module_dir):
            os.makedirs(self.module_dir)

        # Seleccionar JDK
        if self.os_type == "windows":
            jdk_url = self.files["jdk-windows"]
        else:
            jdk_url = self.files["jdk-linux-arm"] if "aarch64" in self.arch else self.files["jdk-linux-x64"]

        jdk_path = os.path.join(self.module_dir, "jdk_pack")
        gradle_path = os.path.join(self.module_dir, "gradle_pack")

        # Descarga y extracción
        if not os.path.exists(os.path.join(self.module_dir, "jdk-17")):
            self._download_file(jdk_url, jdk_path)
            self._download_file(self.files["gradle"], gradle_path)
            
            print("📦 Extrayendo archivos...")
            self._extract_all(jdk_path, self.module_dir)
            self._extract_all(gradle_path, self.module_dir)
            os.remove(jdk_path)
            os.remove(gradle_path)
            print("✅ Entorno preparado.")

    def _extract_all(self, file_path, target):
        """Extrae según el formato detectado."""
        if zipfile.is_zipfile(file_path):
            with zipfile.ZipFile(file_path, 'r') as z: z.extractall(target)
        else:
            with tarfile.open(file_path, "r:gz") as t: t.extractall(target)

    def build_apk(self, project_path):
        self.setup_env()
        
        # Validar proyecto
        inspector = ProjectInspector(project_path, self.base_dir)
        if inspector.inspect()[0]: sys.exit(1)

        # Configurar Gradle
        # NOTA: Asegúrate de que el nombre de la carpeta sea 'gradle-8.1.1'
        gradle_bin = os.path.join(self.module_dir, "gradle-8.1.1", "bin", 
                                  "gradlew.bat" if self.os_type == "windows" else "gradlew")
        
        env = os.environ.copy()
        env["JAVA_HOME"] = os.path.join(self.module_dir, "jdk-17")
        
        print("🚀 Iniciando compilación...")
        subprocess.run([gradle_bin, "assembleRelease"], cwd=project_path, env=env, check=True)
