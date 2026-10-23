import subprocess

from services.HIDController import HIDController
from services.MouseController import MouseController

# 1. Encontra exclusivamente dispositivos que respondem como mouse
available_mice = HIDController.get_logitech_devices()

if not available_mice:
    print("Nenhum mouse Logitech encontrado (mova o mouse se estiver dormindo).")
    exit(1)

# 2. Escolha do mouse (aqui pegamos o primeiro da lista como exemplo)
while True:
    for i, mouse in enumerate(available_mice):
        print(f"[{i}] {mouse.product_string} ({mouse.path})")
    try:
        idx = int(input("Selecionar mouse -> "))
    except IndexError:
        subprocess.run("clear")
        print(f"Escolha um número da lista.\n")
    except ValueError:
        subprocess.run("clear")
        print(f"Digite um número.\n")
    except Exception as e:
        subprocess.run("clear")
        print(f"Erro. Digite novamente")
    finally:
        selected_mouse = available_mice[idx]
        break


# 3. Conecta passando o mouse selecionado
controller = MouseController()
if controller.connect(target_device=selected_mouse):
    print(f"Pronto para envio de comandos para: {controller.device_name}")
    controller.disconnect()
