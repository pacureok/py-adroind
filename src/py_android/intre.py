import os
import ast
import sys

# Lista de librerías conocidas que son exclusivas de Windows o PC
FORBIDDEN_IMPORTS = {
    'win32api', 'win32con', 'win32gui', 'win32com', 'pywintypes',
    'pyautogui', 'keyboard', 'mouse', 'winsound', 'ctypes.wintypes',
    'winreg', 'msvcrt'
}

# Archivos binarios que Android no entiende
FORBIDDEN_EXTENSIONS = {'.exe', '.dll', '.bat', '.cmd'}

class ProjectInspector:
    def __init__(self, project_path, compiler_base_dir):
        self.project_path = os.path.abspath(project_path)
        # Guardamos la ruta de tu librería para ignorarla y no auto-analizarnos
        self.compiler_base_dir = os.path.abspath(compiler_base_dir)

    def inspect(self):
        """Escanea el proyecto y devuelve una lista de errores."""
        errors = []
        warnings = []

        print(f"🕵️ Inspeccionando código en: {self.project_path}...")

        for root, dirs, files in os.walk(self.project_path):
            # 1. Ignorar la propia librería, módulos de compilación y entornos virtuales
            abs_root = os.path.abspath(root)
            if self.compiler_base_dir in abs_root or 'module' in abs_root:
                continue
            if '.venv' in root or 'venv' in root or '__pycache__' in root or '.git' in root:
                continue

            for file in files:
                ext = os.path.splitext(file)[1].lower()
                filepath = os.path.join(root, file)

                # 2. Buscar archivos binarios de Windows
                if ext in FORBIDDEN_EXTENSIONS:
                    errors.append(f"❌ Archivo incompatible de Windows detectado: {file}")

                # 3. Analizar código fuente de Python
                if ext == '.py':
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            tree = ast.parse(f.read(), filename=filepath)
                        
                        # Recorremos el árbol de sintaxis del archivo
                        for node in ast.walk(tree):
                            if isinstance(node, ast.Import):
                                for alias in node.names:
                                    base_module = alias.name.split('.')[0]
                                    if base_module in FORBIDDEN_IMPORTS:
                                        errors.append(f"❌ Importación prohibida de PC ('{alias.name}') en: {file}")
                            
                            elif isinstance(node, ast.ImportFrom):
                                if node.module:
                                    base_module = node.module.split('.')[0]
                                    if base_module in FORBIDDEN_IMPORTS:
                                        errors.append(f"❌ Importación prohibida de PC ('{node.module}') en: {file}")
                    
                    except SyntaxError:
                        warnings.append(f"⚠️ Error de sintaxis al leer {file}, se omitió el análisis.")
                    except Exception as e:
                        warnings.append(f"⚠️ No se pudo leer {file}: {e}")

        return errors, warnings