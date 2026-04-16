"""AX PP300 serial protocol helpers."""

FRAME_HEAD = 0xA5
FRAME_TAIL = 0x5A


def build_command(identifier: int, data: int) -> bytes:
    """Build a 6-byte command frame.

    Args:
        identifier: The function identifier (e.g. 0x00 for voltage).
        data: 16-bit data value.

    Returns:
        6-byte command.
    """
    low = data & 0xFF
    high = (data >> 8) & 0xFF
    checksum = (identifier + low + high) & 0xFF
    return bytes([FRAME_HEAD, identifier, low, high, checksum, FRAME_TAIL])


def parse_status_response(data: bytes) -> dict:
    """Parse a 15-byte status query response.

    Args:
        data: Exactly 15 bytes.

    Returns:
        Dict with human-readable fields.
    """
    if len(data) != 15:
        raise ValueError(f"Expected 15 bytes, got {len(data)}")

    voltage = (data[2] << 8) | data[1]          # unit: 1 mV
    current = (data[4] << 8) | data[3]          # unit: 1 mA
    power = (data[6] << 8) | data[5]            # unit: 10 mW
    input_voltage = (data[8] << 8) | data[7]    # unit: 0.01 V
    temperature = (data[10] << 8) | data[9]     # unit: 0.1 °C
    mode = data[11]                             # 0x00=CV, 0x01=CC
    output_on = data[12]                        # 0x00=off, 0x01=on

    checksum_calc = sum(data[1:13]) & 0xFF
    checksum_ok = checksum_calc == data[13]

    return {
        "voltage_v": round(voltage / 1000.0, 3),
        "current_a": round(current / 1000.0, 3),
        "power_w": round((power * 10) / 1000.0, 2),
        "input_voltage_v": round(input_voltage / 100.0, 2),
        "temperature_c": round(temperature / 10.0, 1),
        "mode": "CC" if mode == 0x01 else "CV",
        "output_on": bool(output_on),
        "checksum_ok": checksum_ok,
        "raw": data.hex(),
    }
