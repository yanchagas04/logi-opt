import easyhid
from services.MouseController import MouseController
from services.HIDController import HIDController
from loguru import logger

device_enumeration = easyhid.Enumeration()
devices = device_enumeration.find(manufacturer="Logitech", vid=0x046D)

print(type(devices[0]))

# for device in devices:
#     print(device)

mouse_controller = MouseController()
mouse_controller.connect()
try:
    type_name = HIDController.get_device_type(device=mouse_controller.device)
    logger.log(f"Type of {mouse_controller.device_name}: {type_name}")
except easyhid.HIDException:
    logger.error("No device connected")
except Exception as e:
    logger.error(f"Something went wrong: {e}")
mouse_controller.disconnect()
