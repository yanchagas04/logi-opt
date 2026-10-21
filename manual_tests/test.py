import easyhid

device_enumeration = easyhid.Enumeration()
devices = device_enumeration.find(manufacturer="Logitech", vid=0x046D)

for device in devices:
    print(device.description())