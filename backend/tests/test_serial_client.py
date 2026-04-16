"""Tests for serial client."""

import threading
import time
from unittest.mock import MagicMock, patch

import pytest

from ax_pp300.serial_client import BatterySimulationConfig, PP300SerialClient


@pytest.fixture
def client():
    return PP300SerialClient()


def fake_status_response():
    # A5 + status bytes + checksum + 5A
    # voltage=2V (0x07D0), current=0.5A (0x01F4), power=1W (0x0064 -> 10mW units)
    # input=12.00V (0x04B0), temp=25.0C (0x00FA), mode=CV(0x00), output=on(0x01)
    data = bytes([
        0xA5,
        0xD0, 0x07,  # voltage 2000 -> 2V
        0xF4, 0x01,  # current 500 -> 0.5A
        0x64, 0x00,  # power 100 -> 1W (100*10mW)
        0xB0, 0x04,  # input 1200 -> 12.00V
        0xFA, 0x00,  # temp 250 -> 25.0C
        0x00,        # CV
        0x01,        # output on
    ])
    checksum = sum(data[1:13]) & 0xFF
    return data + bytes([checksum, 0x5A])


@patch("ax_pp300.serial_client.serial.Serial")
def test_connect_starts_polling(mock_serial, client):
    mock_ser = MagicMock()
    mock_ser.is_open = True
    mock_serial.return_value = mock_ser

    # First read returns status, second returns ack
    status_resp = fake_status_response()
    ack = b"\x01"
    mock_ser.read.side_effect = [status_resp, ack]

    cb_called = threading.Event()
    received = {}

    def cb(status):
        received.update(status)
        cb_called.set()

    client.register_callback(cb)
    client.connect("COM3", 115200)

    # Wait for immediate query and at least one poll
    assert cb_called.wait(timeout=2)
    assert client.is_connected() is True
    assert client.get_status() is not None
    assert received["voltage_v"] == 2.0

    client.disconnect()
    assert client.is_connected() is False


@patch("ax_pp300.serial_client.serial.Serial")
def test_set_voltage(mock_serial, client):
    mock_ser = MagicMock()
    mock_ser.is_open = True
    mock_serial.return_value = mock_ser
    mock_ser.read.return_value = b"\x01"

    client.connect("COM3")
    ok = client.set_voltage(10000)
    assert ok is True

    written = mock_ser.write.call_args[0][0]
    assert written[0] == 0xA5
    assert written[1] == 0x00  # voltage identifier
    assert written[2:4] == bytes([0xE8, 0x03])  # 1000 (10V in 10mV units)

    client.disconnect()


@patch("ax_pp300.serial_client.serial.Serial")
def test_set_current(mock_serial, client):
    mock_ser = MagicMock()
    mock_ser.is_open = True
    mock_serial.return_value = mock_ser
    mock_ser.read.return_value = b"\x01"

    client.connect("COM3")
    ok = client.set_current(2000)
    assert ok is True

    written = mock_ser.write.call_args[0][0]
    assert written[1] == 0x01
    assert written[2:4] == bytes([0xC8, 0x00])  # 200 (2000mA in 10mA units)

    client.disconnect()


@patch("ax_pp300.serial_client.serial.Serial")
def test_set_output(mock_serial, client):
    mock_ser = MagicMock()
    mock_ser.is_open = True
    mock_serial.return_value = mock_ser
    mock_ser.read.return_value = b"\x01"

    client.connect("COM3")
    ok = client.set_output(True)
    assert ok is True

    written = mock_ser.write.call_args[0][0]
    assert written[1] == 0x08
    assert written[2] == 0x01

    client.disconnect()


@patch("ax_pp300.serial_client.serial.Serial")
def test_query_status(mock_serial, client):
    mock_ser = MagicMock()
    mock_ser.is_open = True
    mock_serial.return_value = mock_ser
    mock_ser.read.return_value = fake_status_response()

    client.connect("COM3")
    status = client.query_status()
    assert status is not None
    assert status["voltage_v"] == 2.0
    assert status["checksum_ok"] is True

    client.disconnect()


def test_set_voltage_out_of_range(client):
    with pytest.raises(ValueError):
        client.set_voltage(35000)


def test_set_current_out_of_range(client):
    with pytest.raises(ValueError):
        client.set_current(11000)


def test_start_battery_sim_runs_control_loop(client):
    client.set_current = MagicMock(return_value=True)
    client.set_voltage = MagicMock(return_value=True)
    client.set_output = MagicMock(return_value=True)
    client.get_status = MagicMock(return_value={"current_a": 1.25})

    client.start_battery_sim(
        BatterySimulationConfig(
            open_circuit_voltage_mv=4200,
            min_voltage_mv=3200,
            current_limit_ma=3000,
            internal_resistance_mohm=250,
            sample_interval_ms=20,
            recovery_ms=50,
            ripple_mv=20,
            transient_sag_mv=120,
            duration_ms=80,
        )
    )

    client._task_thread.join(timeout=1)

    client.set_current.assert_called_once_with(3000)
    assert client.set_output.called
    assert client.set_voltage.called
    assert client._task_overlay == {}


def test_start_battery_sim_rejects_invalid_range(client):
    with pytest.raises(ValueError):
        client.start_battery_sim(
            BatterySimulationConfig(
                open_circuit_voltage_mv=3000,
                min_voltage_mv=4000,
                current_limit_ma=3000,
                internal_resistance_mohm=100,
            )
        )


def test_augment_status_includes_task_overlay(client):
    client._set_task_overlay({"simulation_limit_voltage_v": 3.85, "simulation_type": "battery"})
    augmented = client._augment_status({"voltage_v": 3.72})
    assert augmented["voltage_v"] == 3.72
    assert augmented["simulation_limit_voltage_v"] == 3.85
    assert augmented["simulation_type"] == "battery"
