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

        # URLs directas de descarga (usando la técnica de export=download)
        self.files = {
            "jdk-windows": "https://drive.google.com/uc?export=download&id=1S_pUlTJgMkgKIarLyqG-Vyze0KQHVF5W",
            "jdk-linux-x64": "https://drive.google.com/uc?export=download&id=17RDQI-2s2LJ2vmcAGvLGZV75DpKpkek5",
            "jdk-linux-arm": "https://drive.google.com/uc?export=download&id=1EUGTBjOED2hoJbiqIcyqJ0zEBZqlW4da",
            "gradle": "https://drive.google.com/uc?export=download&id=18Xo8geowVpO4ZVVtY_ZFHGqcAboXiFKB"
        }

    def _download_file(self, url, dest_path):
        """Descarga archivos con barra de progreso."""
        print(f"📥 Descargando: {url.split('/')[-1]}...")
        response = requests.get(url, stream=True)
        total_size = int(response.headers.get('content-length', 0))
        
        with open(dest_path, 'wb') as f, tqdm(total=total_size, unit='B', unit_scale=True) as pbar:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
                    pbar.update(len(chunk))

    def setup_env(self):
        if not os.path.exists(self.module_dir):
            os.makedirs(self.module_dir)

        # Determinar qué JDK bajar
        if self.os_type == "windows":
            jdk_url = self.files["jdk-windows"]
        else:
            jdk_url = self.files["jdk-linux-arm"] if "aarch64" in self.arch else self.files["jdk-linux-x64"]

        jdk_zip = os.path.join(self.module_dir, "jdk.zip")
        gradle_zip = os.path.join(self.module_dir, "gradle.zip")

        if not os.path.exists(os.path.join(self.module_dir, "jdk-17")):
            self._download_file(jdk_url, jdk_zip)
            self._download_file(self.files["gradle"], gradle_zip)
            
            print("📦 Extrayendo archivos...")
            for f_path in [jdk_zip, gradle_zip]:
                if f_path.endswith('.zip'):
                    with zipfile.ZipFile(f_path, 'r') as z: z.extractall(self.module_dir)
                else:
                    with tarfile.open(f_path, "r:gz") as t: t.extractall(self.module_dir)
                os.remove(f_path)
            print("✅ Entorno listo.")

    def build_apk(self, project_path):
        self.setup_env()
        
        # Validar
        inspector = ProjectInspector(project_path, self.base_dir)
        if inspector.inspect()[0]: # Si hay errores
            sys.exit(1)

        # Compilar
        gradlew = "gradlew.bat" if self.os_type == "windows" else "./gradlew"
        # Ajusta "gradle-8.1" al nombre real de la carpeta descomprimida
        gradle_bin = os.path.join(self.module_dir, "gradle-8.1", "bin", gradlew)
        
        env = os.environ.copy()
        env["JAVA_HOME"] = os.path.join(self.module_dir, "jdk-17")
        
        print("🚀 Compilando...")
        subprocess.run([gradle_bin, "assembleRelease"], cwd=project_path, env=env, check=True)
