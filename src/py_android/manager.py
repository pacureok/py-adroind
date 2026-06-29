import os
from builder import AndroidBuilder

def fix_project_structure():
    """Genera los archivos y carpetas necesarios para que Gradle no se queje."""
    project_path = os.getcwd()
    
    # 1. Crear local.properties
    sdk_path = os.path.join(os.path.expanduser("~"), "AppData", "Local", "Android", "Sdk")
    with open("local.properties", "w") as f:
        f.write(f"sdk.dir={sdk_path.replace(os.sep, '/')}")

    # 2. Crear build.gradle
    with open("build.gradle", "w") as f:
        f.write("""plugins { id 'com.android.application' version '8.1.0' }
android {
    namespace 'com.example.myapp'
    compileSdk 33
    defaultConfig { applicationId "com.example.myapp"; minSdk 21; targetSdk 33 }
}""")

    # 3. Crear settings.gradle
    with open("settings.gradle", "w") as f:
        f.write("rootProject.name = 'MyAndroidApp'")

    # 4. Crear AndroidManifest.xml (ESTO EVITA TU ERROR ACTUAL)
    manifest_dir = os.path.join("src", "main")
    os.makedirs(manifest_dir, exist_ok=True)
    with open(os.path.join(manifest_dir, "AndroidManifest.xml"), "w") as f:
        f.write("""<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android" package="com.example.myapp" />""")
    
    print("✅ Estructura de proyecto validada y corregida.")

if __name__ == "__main__":
    fix_project_structure()
    builder = AndroidBuilder()
    builder.build_apk(".")
