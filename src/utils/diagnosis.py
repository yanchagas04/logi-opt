import os
import time

DEV = "/dev/hidraw3"  # Receptor USB
DEVICE_INDEX = 0x01   # Mouse PRO 2
FEATURE_INDEX = 0x0F  # Índice da Feature 0x8100 (ONBOARD PROFILES)

def send_hidpp(fd, func, params=b""):
    cmd = bytearray(20)
    cmd[0] = 0x11
    cmd[1] = DEVICE_INDEX
    cmd[2] = FEATURE_INDEX
    cmd[3] = (func << 4) & 0xF0
    for i, b in enumerate(params):
        cmd[4 + i] = b
    
    os.write(fd, bytes(cmd))
    time.sleep(0.05)
    res = os.read(fd, 20)
    return res

fd = os.open(DEV, os.O_RDWR)

print("--- Consultando Feature 0x8100 ---")

# Função 0: getProfileDirectory / getCapabilities
res_func0 = send_hidpp(fd, 0)
print("Func 0x00 (Capabilities/Dir):", [hex(b) for b in res_func0])

# Função 1: getMode
res_func1 = send_hidpp(fd, 1)
print("Func 0x10 (Current Mode):    ", [hex(b) for b in res_func1])

# Função 2: getActiveProfile
res_func2 = send_hidpp(fd, 2)
print("Func 0x20 (Active Profile):  ", [hex(b) for b in res_func2])

os.close(fd)