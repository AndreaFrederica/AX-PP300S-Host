"""Tests for FastAPI main app."""

import json
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from ax_pp300.main import app, client as real_client


@pytest.fixture
def mock_client():
    m = MagicMock()
    m.is_connected.return_value = False
    m.get_status.return_value = None
    return m


@pytest.fixture(autouse=True)
def patch_client(mock_client):
    with patch("ax_pp300.main.client", mock_client):
        yield


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def test_root(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert resp.json()["message"] == "AX PP300 Host is running"


@patch("ax_pp300.main.serial.tools.list_ports.comports")
def test_list_ports(mock_comports, client):
    mock_comports.return_value = [
        MagicMock(device="COM3", description="USB-SERIAL CH340"),
        MagicMock(device="COM4", description="Bluetooth"),
    ]
    resp = client.get("/ports")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["ports"]) == 2
    assert data["ports"][0]["device"] == "COM3"


def test_connect(client, mock_client):
    resp = client.post("/connect", json={"port": "COM3", "baudrate": 115200})
    assert resp.status_code == 200
    assert resp.json()["status"] == "connected"
    mock_client.connect.assert_called_once_with("COM3", 115200)


def test_connect_error(client, mock_client):
    mock_client.connect.side_effect = RuntimeError("Port busy")
    resp = client.post("/connect", json={"port": "COM3", "baudrate": 115200})
    assert resp.status_code == 400
    assert "Port busy" in resp.json()["detail"]


def test_disconnect(client, mock_client):
    resp = client.post("/disconnect")
    assert resp.status_code == 200
    mock_client.disconnect.assert_called_once()


def test_status_cached(client, mock_client):
    mock_client.get_status.return_value = {
        "voltage_v": 5.0,
        "current_a": 0.0,
        "power_w": 0.0,
        "input_voltage_v": 20.0,
        "temperature_c": 30.0,
        "mode": "CV",
        "output_on": True,
        "checksum_ok": True,
        "raw": "a5...",
    }
    resp = client.get("/status")
    assert resp.status_code == 200
    assert resp.json()["voltage_v"] == 5.0


def test_connection_state(client, mock_client):
    mock_client.get_connection_info.return_value = {
        "connected": True,
        "port": "COM7",
        "baudrate": 115200,
    }
    resp = client.get("/connection")
    assert resp.status_code == 200
    assert resp.json()["connected"] is True
    assert resp.json()["port"] == "COM7"


def test_status_unavailable(client, mock_client):
    mock_client.get_status.return_value = None
    resp = client.get("/status")
    assert resp.status_code == 503


def test_set_voltage(client, mock_client):
    mock_client.set_voltage.return_value = True
    resp = client.post("/voltage", json={"voltage_mv": 12000})
    assert resp.status_code == 200
    assert resp.json()["ok"] is True
    mock_client.set_voltage.assert_called_once_with(12000)


def test_set_voltage_ack_fail(client, mock_client):
    mock_client.set_voltage.return_value = False
    resp = client.post("/voltage", json={"voltage_mv": 12000})
    assert resp.status_code == 500


def test_set_current(client, mock_client):
    mock_client.set_current.return_value = True
    resp = client.post("/current", json={"current_ma": 2000})
    assert resp.status_code == 200
    mock_client.set_current.assert_called_once_with(2000)


def test_set_output(client, mock_client):
    mock_client.set_output.return_value = True
    resp = client.post("/output", json={"on": True})
    assert resp.status_code == 200
    mock_client.set_output.assert_called_once_with(True)


def test_set_ovp(client, mock_client):
    mock_client.set_ovp.return_value = True
    resp = client.post("/ovp", json={"ovp_mv": 30500})
    assert resp.status_code == 200
    mock_client.set_ovp.assert_called_once_with(30500)


def test_set_ocp(client, mock_client):
    mock_client.set_ocp.return_value = True
    resp = client.post("/ocp", json={"ocp_ma": 10500})
    assert resp.status_code == 200
    mock_client.set_ocp.assert_called_once_with(10500)


def test_raw_command(client, mock_client):
    mock_client.send_command.return_value = b"\x01"
    resp = client.post("/raw_command", json={"identifier": 6, "data": 10})
    assert resp.status_code == 200
    assert resp.json()["response_hex"] == "01"
    mock_client.send_command.assert_called_once_with(6, 10)


def test_start_battery_simulation(client, mock_client):
    resp = client.post(
        "/battery/start",
        json={
            "open_circuit_voltage_mv": 4200,
            "min_voltage_mv": 3000,
            "current_limit_ma": 3000,
            "internal_resistance_mohm": 220,
            "sample_interval_ms": 100,
            "recovery_ms": 500,
            "ripple_mv": 30,
            "transient_sag_mv": 100,
            "duration_ms": 0,
        },
    )
    assert resp.status_code == 200
    assert resp.json()["type"] == "battery"
    assert mock_client.start_battery_sim.called


def test_stop_battery_simulation(client, mock_client):
    resp = client.post("/battery/stop")
    assert resp.status_code == 200
    mock_client.stop_task.assert_called_once()


def test_stop_any_task(client, mock_client):
    resp = client.post("/task/stop")
    assert resp.status_code == 200
    mock_client.stop_task.assert_called_once()


def test_websocket(client, mock_client):
    mock_client.get_status.return_value = {
        "voltage_v": 5.0,
        "current_a": 0.0,
        "power_w": 0.0,
        "input_voltage_v": 20.0,
        "temperature_c": 30.0,
        "mode": "CV",
        "output_on": True,
        "checksum_ok": True,
        "raw": "a5...",
    }
    mock_client.set_voltage.return_value = True
    mock_client.set_output.return_value = True

    with client.websocket_connect("/ws") as ws:
        # First message should be cached status
        msg = json.loads(ws.receive_text())
        assert msg["voltage_v"] == 5.0

        # Send set_voltage via websocket
        ws.send_text(json.dumps({"action": "set_voltage", "voltage_mv": 5000}))
        msg = json.loads(ws.receive_text())
        assert msg["type"] == "ack"
        assert msg["action"] == "set_voltage"
        assert msg["ok"] is True
        mock_client.set_voltage.assert_called_with(5000)

        # Send set_output via websocket
        ws.send_text(json.dumps({"action": "set_output", "on": False}))
        msg = json.loads(ws.receive_text())
        assert msg["type"] == "ack"
        mock_client.set_output.assert_called_with(False)

        # Send ping
        ws.send_text(json.dumps({"action": "ping"}))
        msg = json.loads(ws.receive_text())
        assert msg["type"] == "pong"

        # Send unknown action
        ws.send_text(json.dumps({"action": "foobar"}))
        msg = json.loads(ws.receive_text())
        assert msg["type"] == "error"
