import subprocess

from services.MouseController import MouseController

mouse = MouseController(MouseController.choose_mouse())
if mouse.connect():
    print(f"Pronto para envio de comandos para: {mouse.device_name}")
    mouse.disconnect()
