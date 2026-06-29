class AndroidBridge:
    def __init__(self):
        try:
            # Le decimos a Pylance que ignore esta línea porque 'java' solo existe en el APK
            from java import jclass # type: ignore
            
            self.Context = jclass("android.content.Context")
            self.Intent = jclass("android.content.Intent")
            self.MediaStore = jclass("android.provider.MediaStore")
            self.in_android = True
        except ImportError:
            self.in_android = False
            print("Entorno local detectado: Las funciones nativas de Android están desactivadas.")

    def request_camera(self, activity_context):
        if not self.in_android:
            print("Simulando cámara en PC...")
            return {"status": "success", "message": "Cámara simulada"}

        intent = self.Intent(self.MediaStore.ACTION_IMAGE_CAPTURE)
        if intent.resolveActivity(activity_context.getPackageManager()) is not None:
            activity_context.startActivityForResult(intent, 100)
            return {"status": "success", "message": "Cámara abierta"}
        return {"status": "error", "message": "Cámara no disponible"}