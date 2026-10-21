import json
import os
import struct
import time

DEV_PATH = "/dev/hidraw3"
DEVICE_INDEX = 0x01
FEATURE_PROFILES = 0x0F  # 0x8100 Onboard Profiles
FEATURE_DPI = 0x0B       # 0x2202 Extended Adjustable DPI

BUTTON_NAMES = [
    "Left Click",
    "Right Click",
    "Middle Click",
    "Lateral Front Left (BTN_EXTRA)",
    "Lateral Rear Left (BTN_SIDE)",
    "Lateral Front Right (BTN_TASK)",
    "Lateral Rear Right (BTN_BACK)",
    "Bottom DPI Cycle (BTN_FORWARD)",
    "Auxiliary / Macro 1",
    "Auxiliary / Macro 2",
]


def send_hidpp(fd, feature_idx, func_idx, params=b"", read_len=20):
    cmd = bytearray(20)
    cmd[0] = 0x11
    cmd[1] = DEVICE_INDEX
    cmd[2] = feature_idx
    cmd[3] = (func_idx << 4) & 0xF0

    for i, b in enumerate(params):
        cmd[4 + i] = b

    os.write(fd, bytes(cmd))
    time.sleep(0.03)
    return os.read(fd, read_len)


def read_profile_memory(fd, profile_idx=0, address=0):
    # Função 2 da Feature 0x8100: Leitura de bloco de memória por offset
    params = struct.pack(">BH", profile_idx, address)
    resp = send_hidpp(fd, FEATURE_PROFILES, 0x02, params)
    # Bytes 0-3 são cabeçalho HID++; bytes 4-19 contêm os 16 bytes úteis de payload
    return resp[4:20]


def main():
    if not os.path.exists(DEV_PATH):
        print(f"Erro: Dispositivo {DEV_PATH} não encontrado.")
        return

    fd = os.open(DEV_PATH, os.O_RDWR)
    print(f"[*] Conectado a {DEV_PATH} (Mouse PRO 2 - Índice {DEVICE_INDEX})")

    # 1. Informações de Capacidade (Função 0x00)
    dir_info = send_hidpp(fd, FEATURE_PROFILES, 0x00)
    max_profiles = dir_info[5] & 0x07
    active_profile = dir_info[6]
    dpi_slots_count = dir_info[7]
    active_dpi_slot = dir_info[8]
    total_buttons = dir_info[13]

    print(f"[*] Perfis Suportados : {max_profiles} (Ativo: Perfil {active_profile})")
    print(f"[*] Níveis de DPI     : {dpi_slots_count} (Ativo: Slot {active_dpi_slot})")
    print(f"[*] Botões Físicos    : {total_buttons}")

    # 2. Leitura contínua dos primeiros 128 bytes do Perfil Ativo (setor de configuração)
    print("\n[*] Lendo bloco de configuração da flash do Perfil Ativo...")
    profile_bytes = bytearray()
    for offset in range(0, 128, 14):  # Janelas sequenciais de payload
        chunk = read_profile_memory(fd, profile_idx=0, address=offset)
        profile_bytes.extend(chunk)

    print("\n--- HEX DUMP DO PERFIL (PRIMEIROS 64 BYTES) ---")
    for row in range(0, 64, 16):
        hex_str = " ".join(f"{b:02X}" for b in profile_bytes[row:row + 16])
        ascii_str = "".join(chr(b) if 32 <= b < 127 else "." for b in profile_bytes[row:row + 16])
        print(f"0x{row:04X}:  {hex_str:<48}  |{ascii_str}|")

    # 3. Extração dos Steps de DPI
    # Na arquitetura HERO/HID++ 2.0, os slots de DPI ficam nos primeiros bytes do perfil
    dpi_values = []
    print("\n--- NÍVEIS DE DPI CONFIGURADOS ---")
    for i in range(dpi_slots_count):
        # Cada step ocupa 2 bytes big-endian
        dpi_val = struct.unpack(">H", profile_bytes[i * 2:(i * 2) + 2])[0]
        is_active = (i + 1) == active_dpi_slot
        status = " (ATIVO)" if is_active else ""
        dpi_values.append({"slot": i + 1, "dpi": dpi_val, "active": is_active})
        print(f"  Slot {i + 1}: {dpi_val} DPI{status}")

    # 4. Extração do Mapeamento de Botões
    # A tabela de botões inicia imediatamente após a tabela de DPI e flags do sensor (offset ~0x10)
    button_offset = 0x10
    buttons_map = []
    print("\n--- MAPEAMENTO DOS BOTÕES FÍSICOS ---")
    for btn_idx in range(min(total_buttons, len(BUTTON_NAMES))):
        base = button_offset + (btn_idx * 2)
        mode = profile_bytes[base]
        code = profile_bytes[base + 1]

        desc = BUTTON_NAMES[btn_idx] if btn_idx < len(BUTTON_NAMES) else f"Button {btn_idx + 1}"
        buttons_map.append({
            "button_index": btn_idx,
            "name": desc,
            "raw_hex": f"0x{mode:02X} 0x{code:02X}",
            "type_byte": hex(mode),
            "code_byte": hex(code)
        })
        print(f"  [{btn_idx}] {desc:<32} -> Tipo: 0x{mode:02X} | Código HID: 0x{code:02X}")

    # 5. Exportar JSON consolidado do perfil para o seu app
    export_data = {
        "device": "PRO 2 LIGHTSPEED",
        "active_profile": active_profile,
        "dpi_modes": dpi_values,
        "buttons": buttons_map,
        "raw_dump_hex": profile_bytes[:64].hex()
    }

    if not os.path.exists("mappings"):
        os.makedirs("mappings")

    with open("mappings/profile_mapping.json", "w", encoding="utf-8") as f:
        json.dump(export_data, f, indent=2, ensure_ascii=False)

    print("\n[+] Mapeamento salvo com sucesso em 'mappings/profile_mapping.json'")
    os.close(fd)


if __name__ == "__main__":
    main()