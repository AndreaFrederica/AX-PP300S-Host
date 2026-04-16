"""Tests for protocol helpers."""

import pytest

from ax_pp300.protocol import FRAME_HEAD, FRAME_TAIL, build_command, parse_status_response


def test_build_command_voltage():
    # Example 2 from protocol doc: 10V -> data=1000 -> 0x03E8
    cmd = build_command(0x00, 1000)
    assert cmd == bytes([0xA5, 0x00, 0xE8, 0x03, 0xEB, 0x5A])


def test_build_command_output_on():
    # Example 3: output on -> identifier 0x08, data 1
    cmd = build_command(0x08, 1)
    assert cmd == bytes([0xA5, 0x08, 0x01, 0x00, 0x09, 0x5A])


def test_build_command_cutoff_time():
    # Example 4: list0 cutoff time 5 minutes -> identifier 0x0F, data=0x0105 -> low=5 high=1
    data = (1 << 8) | 5
    cmd = build_command(0x0F, data)
    assert cmd == bytes([0xA5, 0x0F, 0x05, 0x01, 0x15, 0x5A])


def test_parse_status_response():
    # Example 1 from protocol doc
    resp = bytes([0xA5, 0x88, 0x13, 0x00, 0x00, 0x00, 0x00, 0xB4, 0x07, 0x25, 0x01, 0x00, 0x01, 0x7D, 0x5A])
    status = parse_status_response(resp)
    assert status["voltage_v"] == 5.0
    assert status["current_a"] == 0.0
    assert status["power_w"] == 0.0
    assert status["input_voltage_v"] == 19.72
    assert status["temperature_c"] == 29.3
    assert status["mode"] == "CV"
    assert status["output_on"] is True
    assert status["checksum_ok"] is True
    assert status["raw"] == resp.hex()


def test_parse_status_response_bad_checksum():
    resp = bytes([0xA5, 0x88, 0x13, 0x00, 0x00, 0x00, 0x00, 0xB4, 0x07, 0x25, 0x01, 0x00, 0x01, 0x00, 0x5A])
    status = parse_status_response(resp)
    assert status["checksum_ok"] is False


def test_parse_status_response_wrong_length():
    with pytest.raises(ValueError):
        parse_status_response(bytes([0xA5, 0x00, 0x5A]))
