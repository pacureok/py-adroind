import os
import subprocess
import platform
import stat
import sys
import tarfile
import zipfile
import gdown
from jinja2 import Environment, FileSystemLoader
from .intre import ProjectInspector

class AndroidBuilder:
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.module_dir = os.path.abspath(os.path.join(self.base_dir, "..", "..", "module"))
        self.templates_dir = os.path.join(self.base_dir, "templates")
        self.os_type = platform.system().lower()
        self.arch = platform.machine().lower()

        # IDs de tus archivos en Google Drive
        self.drive_ids = {
            "linux-x64": "17RDQI-2s2LJ2vmcAGvLGZV75DpKpkek5",
            "linux-arm": "1EUGTBjOED2hoJbiqIcyqJ0zEBZqlW4da",
            "windows": "1S_pUlTJgMkgKIarLyqG-Vyze0KQHVF5W",
            "gradle": "18Xo8geowVpO4ZVVtY_ZFHGqcAboXiFKB"
        }

    def setup_env(self):
        """Descarga y prepara el JDK y Gradle automáticamente."""
        if not os.path.exists(self.module_dir):
            os.makedirs(self.module_dir)

        # 1. Determinar qué descargar
        if self.os_type == "windows":
            jdk_id = self.drive_ids["windows"]
        else:
            jdk_id = self.drive_ids["linux-arm"] if "aarch64" in self.arch else self.drive_ids["linux-x64"]

        jdk_path = os.path.join(self.module_dir, "jdk_pack.zip" if self.os_type == "windows" else "jdk_pack.tar.gz")
        gradle_path = os.path.join(self.module_dir, "gradle_pack.zip")

        # 2. Descargar si no existe la carpeta JDK
        if not os.path.exists(os.path.join(self.module_dir, "jdk-17")):
            print("📥 Descargando JDK y Gradle desde Drive...")
            gdown.download(id=jdk_id, output=jdk_path, quiet=False)
            gdown.download(id=self.drive_ids["gradle"], output=gradle_path, quiet=False)

            # 3. Extraer
            self._extract(jdk_path, self.module_dir)
            self._extract(gradle_path, self.module_dir)
            
            # Limpiar comprimidos
            os.remove(jdk_path)
            os.remove(gradle_path)
            print("✅ Entorno configurado.")

    def _extract(self, file_path, extract_to):
        if file_path.endswith('.zip'):
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(extract_to)
        else:
            with tarfile.open(file_path, "r:gz") as tar:
                tar.extractall(extract_to)

    def build_apk(self, project_path):
        self.setup_env() # Asegura tener todo antes de construir
        
        # Validar código (intre.py)
        inspector = ProjectInspector(project_path, self.base_dir)
        errors, _ = inspector.inspect()
        if errors:
            print("🚨 Error: Código incompatible detectado.")
            sys.exit(1)

        # Configurar Gradle
        gradlew = "gradlew.bat" if self.os_type == "windows" else "./gradlew"
        # Asegúrate de ajustar la ruta si el nombre de la carpeta cambia al descomprimir
        gradle_path = os.path.join(self.module_dir, "gradle-8.1", "bin", gradlew)
        
        env = os.environ.copy()
        env["JAVA_HOME"] = os.path.join(self.module_dir, "jdk-17")
        
        print("🚀 Compilando...")
        subprocess.run([gradle_path, "assembleRelease"], cwd=project_path, env=env, check=True)