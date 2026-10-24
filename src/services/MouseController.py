import subprocess
from typing import Optional
from easyhid import HIDDevice
from loguru import logger
from services.HIDController import HIDController


class MouseController(HIDController):

    def __init__(self, device_handler: Optional[HIDDevice]):
        super().__init__(device_handler)

    def connect(self) -> bool:
        """
        Opens and binds the controller to the target mouse device.
        """
        if not self.device_handler:
            logger.error("No target device provided")
            return False

        try:
            # Ensure the device handle is actually open
            self.device_handler.open()

            # Resolve device routing index on the active connection
            self.device_index = self.get_device_index()
            if self.device_index is None:
                logger.error(
                    "Failed to resolve an active device index for this mouse")
                self.disconnect()
                return False

            # Query real product name from firmware
            self.device_name = self.get_device_name()

            logger.success(
                f"Connected to {self.device_name} (Index: {self.device_index})")
            return True

        except Exception as e:
            logger.error(f"Failed to establish connection: {e}")
            self.disconnect()
            return False

    def disconnect(self) -> bool:
        """
        Closes the active connection and releases resources.
        """
        if not self.device_handler:
            return False

        try:
            self.device_handler.close()
        except Exception:
            pass

        logger.info(f"Disconnected from {self.device_name or 'mouse'}")
        self.device_index = None
        return True

    @staticmethod
    def choose_mouse() -> Optional[HIDDevice]:
        available_mices = MouseController.get_logitech_mouses()
        if not available_mices:
            print("Nenhum mouse Logitech encontrado (mova o mouse se estiver dormindo).")
            return None

        while True:
            for i, m in enumerate(available_mices):
                print(
                    f"[{i}] {m.product_string} ({m.path.decode() if isinstance(m.path, bytes) else m.path})")
            try:
                raw_in = input("Selecionar mouse -> ")
                subprocess.run("clear", shell=True)
                idx = int(raw_in)
                if 0 <= idx < len(available_mices):
                    return available_mices[idx]
                print("Escolha um número válido da lista.\n")
            except ValueError:
                print("Digite um número válido.\n")
            except Exception:
                print("Erro na seleção. Tente novamente.\n")
