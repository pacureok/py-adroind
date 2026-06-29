# manager.py
import os
from builder import AndroidBuilder

def create_manifest():
    """Crea la estructura de carpetas y el manifiesto mínimo si no existen."""
    manifest_path = os.path.join("src", "main", "AndroidManifest.xml")
    if not os.path.exists(manifest_path):
        os.makedirs(os.path.join("src", "main"), exist_ok=True)
        manifest_content = """<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.example.myapp">
    <application android:label="My App" />
</manifest>"""
        with open(manifest_path, "w") as f:
            f.write(manifest_content)
        print("📄 Manifest generado.")
    else:
        print("✅ Manifest ya existente.")

def main():
    # 1. Preparar la estructura del proyecto
    create_manifest()
    
    # 2. Llamar al constructor
    builder = AndroidBuilder()
    builder.build_apk(".")

if __name__ == "__main__":
    main()
