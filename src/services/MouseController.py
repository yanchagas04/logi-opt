from typing import Optional
from easyhid import HIDDevice
from loguru import logger
from services.HIDController import HIDController


class MouseController:

    def __init__(self):
        self.device_index: Optional[int] = None
        self.device_name: Optional[str] = None
        self.device_handler: Optional[HIDDevice] = None

    def connect(self, target_device: HIDDevice) -> bool:
        """
        Opens and binds the controller to the chosen mouse HID device.
        """
        if not target_device:
            logger.error("No target device provided")
            return False

        # Close existing connection if already open
        if self.device_handler:
            self.disconnect()

        try:
            target_device.open()
            self.device_handler = target_device

            # Identify target routing index on the receiver[cite: 2]
            self.device_index = HIDController.get_device_index(
                self.device_handler)
            if self.device_index is None:
                logger.error(
                    "Failed to resolve an active device index for this mouse")
                self.disconnect()
                return False

            # Query real name from firmware or fallback to USB descriptor string
            self.device_name = HIDController.get_device_name(
                self.device_handler, self.device_index)
            logger.success(
                f"Connected to {self.device_name} (Index: {self.device_index})[cite: 2]")
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
        self.device_handler = None
        self.device_index = None
        self.device_name = None
        return True
