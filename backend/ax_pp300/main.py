"""FastAPI host for AX PP300."""

import asyncio
import json
from contextlib import asynccontextmanager

import serial.tools.list_ports
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .serial_client import BatterySimulationConfig, PP300SerialClient, SequenceStep

client = PP300SerialClient()
_event_loop: asyncio.AbstractEventLoop | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _event_loop
    _event_loop = asyncio.get_running_loop()
    yield
    if client.is_connected():
        client.disconnect()


app = FastAPI(
    title="AX PP300 Host",
    description="Web-based host controller for AX PP300 buck-boost CNC power supply.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ===================================================================
# Schemas
# ===================================================================
class ConnectRequest(BaseModel):
    port: str = Field(..., description="Serial port name, e.g. COM3")
    baudrate: int = 115200


class SetVoltageRequest(BaseModel):
    voltage_mv: int = Field(..., ge=0, le=30000, description="Target voltage in mV")


class SetCurrentRequest(BaseModel):
    current_ma: int = Field(..., ge=0, le=10100, description="Target current in mA")


class SetOutputRequest(BaseModel):
    on: bool


class SetOvpRequest(BaseModel):
    ovp_mv: int = Field(..., ge=0, le=30500, description="Over-voltage protection in mV")


class SetOcpRequest(BaseModel):
    ocp_ma: int = Field(..., ge=0, le=10500, description="Over-current protection in mA")


class RawCommandRequest(BaseModel):
    identifier: int = Field(..., ge=0, le=255)
    data: int = 0


class SequenceStepRequest(BaseModel):
    voltage_mv: int = Field(..., ge=0, le=30000)
    current_ma: int = Field(..., ge=0, le=10100)
    output_on: bool
    duration_ms: int = Field(..., ge=1, le=999999)


class StartPwmRequest(BaseModel):
    voltage_mv: int = Field(..., ge=0, le=30000)
    frequency: float = Field(..., gt=0, le=100)
    duty_cycle: float = Field(..., ge=0, le=100)


class StartSequenceRequest(BaseModel):
    steps: list[SequenceStepRequest]
    loop: bool = False


class PollIntervalRequest(BaseModel):
    interval_ms: int = Field(..., ge=5, le=5000, description="Polling interval in milliseconds")


class BatterySimulationRequest(BaseModel):
    open_circuit_voltage_mv: int = Field(..., ge=0, le=30000)
    min_voltage_mv: int = Field(..., ge=0, le=30000)
    current_limit_ma: int = Field(..., ge=0, le=10100)
    internal_resistance_mohm: int = Field(..., ge=0, le=5000)
    sample_interval_ms: int = Field(100, ge=5, le=5000)
    recovery_ms: int = Field(400, ge=0, le=10000)
    ripple_mv: int = Field(0, ge=0, le=2000)
    transient_sag_mv: int = Field(0, ge=0, le=5000)
    duration_ms: int = Field(0, ge=0, le=86_400_000)


# ===================================================================
# REST Routes
# ===================================================================
@app.get("/")
def root():
    return {"message": "AX PP300 Host is running"}


@app.get("/ports")
def list_ports():
    ports = [
        {"device": p.device, "description": p.description}
        for p in serial.tools.list_ports.comports()
    ]
    return {"ports": ports}


@app.post("/connect")
def connect(req: ConnectRequest):
    try:
        client.connect(req.port, req.baudrate)
        return {"status": "connected", "port": req.port, "baudrate": req.baudrate}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/disconnect")
def disconnect():
    client.disconnect()
    return {"status": "disconnected"}


@app.get("/status")
def get_status():
    status = client.get_status()
    if status is None:
        raise HTTPException(status_code=503, detail="No status available yet")
    return status


@app.get("/connection")
def get_connection():
    return client.get_connection_info()


@app.get("/connection")
def get_connection():
    return client.get_connection_info()


@app.post("/voltage")
def set_voltage(req: SetVoltageRequest):
    try:
        ok = client.set_voltage(req.voltage_mv)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    if not ok:
        raise HTTPException(status_code=500, detail="Device did not acknowledge")
    return {"ok": True, "voltage_mv": req.voltage_mv}


@app.post("/current")
def set_current(req: SetCurrentRequest):
    try:
        ok = client.set_current(req.current_ma)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    if not ok:
        raise HTTPException(status_code=500, detail="Device did not acknowledge")
    return {"ok": True, "current_ma": req.current_ma}


@app.post("/output")
def set_output(req: SetOutputRequest):
    ok = client.set_output(req.on)
    if not ok:
        raise HTTPException(status_code=500, detail="Device did not acknowledge")
    return {"ok": True, "output_on": req.on}


@app.post("/ovp")
def set_ovp(req: SetOvpRequest):
    try:
        ok = client.set_ovp(req.ovp_mv)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    if not ok:
        raise HTTPException(status_code=500, detail="Device did not acknowledge")
    return {"ok": True, "ovp_mv": req.ovp_mv}


@app.post("/ocp")
def set_ocp(req: SetOcpRequest):
    try:
        ok = client.set_ocp(req.ocp_ma)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    if not ok:
        raise HTTPException(status_code=500, detail="Device did not acknowledge")
    return {"ok": True, "ocp_ma": req.ocp_ma}


@app.post("/raw_command")
def raw_command(req: RawCommandRequest):
    """Advanced debugging endpoint to send arbitrary commands."""
    try:
        resp = client.send_command(req.identifier, req.data)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    return {"response_hex": resp.hex(), "response_len": len(resp)}


@app.post("/pwm/start")
def start_pwm(req: StartPwmRequest):
    try:
        client.start_pwm(req.voltage_mv, req.frequency, req.duty_cycle)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return {"ok": True, "type": "pwm"}


@app.post("/pwm/stop")
def stop_pwm():
    client.stop_task()
    return {"ok": True}


@app.post("/sequence/start")
def start_sequence(req: StartSequenceRequest):
    try:
        steps = [SequenceStep(**s.model_dump()) for s in req.steps]
        client.start_sequence(steps, loop=req.loop)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return {"ok": True, "type": "sequence", "steps": len(req.steps), "loop": req.loop}


@app.post("/sequence/stop")
def stop_sequence():
    client.stop_task()
    return {"ok": True}


@app.post("/battery/start")
def start_battery(req: BatterySimulationRequest):
    try:
        client.start_battery_sim(BatterySimulationConfig(**req.model_dump()))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return {"ok": True, "type": "battery"}


@app.post("/battery/stop")
def stop_battery():
    client.stop_task()
    return {"ok": True}


@app.get("/task")
def get_task():
    return {"running": client.is_task_running(), "type": client.task_type()}


@app.post("/task/stop")
def stop_task():
    client.stop_task()
    return {"ok": True}


@app.post("/poll_interval")
def set_poll_interval(req: PollIntervalRequest):
    try:
        client.set_poll_interval(req.interval_ms)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return {"ok": True, "interval_ms": req.interval_ms}


# ===================================================================
# WebSocket
# ===================================================================
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        payload = json.dumps(message)
        dead = []
        for conn in self.active_connections:
            try:
                await conn.send_text(payload)
            except Exception:
                dead.append(conn)
        for d in dead:
            self.disconnect(d)


manager = ConnectionManager()


def _on_serial_status(status: dict):
    if manager.active_connections and _event_loop is not None:
        asyncio.run_coroutine_threadsafe(manager.broadcast(status), _event_loop)


client.register_callback(_on_serial_status)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        # Send current cached status immediately upon connection
        cached = client.get_status()
        if cached:
            await websocket.send_text(json.dumps(cached))
        while True:
            # Keep connection alive and allow client to optionally send commands
            data = await websocket.receive_text()
            try:
                msg = json.loads(data)
                action = msg.get("action")
                if action == "connect":
                    client.connect(msg["port"], msg.get("baudrate", 115200))
                    await websocket.send_text(json.dumps({"type": "info", "message": "Connected"}))
                elif action == "disconnect":
                    client.disconnect()
                    await websocket.send_text(json.dumps({"type": "info", "message": "Disconnected"}))
                elif action == "set_voltage":
                    ok = client.set_voltage(msg["voltage_mv"])
                    await websocket.send_text(json.dumps({"type": "ack", "action": "set_voltage", "ok": ok}))
                elif action == "set_current":
                    ok = client.set_current(msg["current_ma"])
                    await websocket.send_text(json.dumps({"type": "ack", "action": "set_current", "ok": ok}))
                elif action == "set_output":
                    ok = client.set_output(msg["on"])
                    await websocket.send_text(json.dumps({"type": "ack", "action": "set_output", "ok": ok}))
                elif action == "pwm_start":
                    client.start_pwm(msg["voltage_mv"], msg["frequency"], msg["duty_cycle"])
                    await websocket.send_text(json.dumps({"type": "ack", "action": "pwm_start"}))
                elif action == "pwm_stop":
                    client.stop_task()
                    await websocket.send_text(json.dumps({"type": "ack", "action": "pwm_stop"}))
                elif action == "sequence_start":
                    steps = [SequenceStep(**s) for s in msg["steps"]]
                    client.start_sequence(steps, loop=msg.get("loop", False))
                    await websocket.send_text(json.dumps({"type": "ack", "action": "sequence_start"}))
                elif action == "sequence_stop":
                    client.stop_task()
                    await websocket.send_text(json.dumps({"type": "ack", "action": "sequence_stop"}))
                elif action == "battery_start":
                    client.start_battery_sim(BatterySimulationConfig(**msg["config"]))
                    await websocket.send_text(json.dumps({"type": "ack", "action": "battery_start"}))
                elif action == "battery_stop":
                    client.stop_task()
                    await websocket.send_text(json.dumps({"type": "ack", "action": "battery_stop"}))
                elif action == "task_stop":
                    client.stop_task()
                    await websocket.send_text(json.dumps({"type": "ack", "action": "task_stop"}))
                elif action == "set_poll_interval":
                    client.set_poll_interval(msg["interval_ms"])
                    await websocket.send_text(json.dumps({"type": "ack", "action": "set_poll_interval", "interval_ms": msg["interval_ms"]}))
                elif action == "ping":
                    await websocket.send_text(json.dumps({"type": "pong"}))
                else:
                    await websocket.send_text(json.dumps({"type": "error", "message": "Unknown action"}))
            except Exception as exc:
                await websocket.send_text(json.dumps({"type": "error", "message": str(exc)}))
    except WebSocketDisconnect:
        manager.disconnect(websocket)


def main():
    import uvicorn
    uvicorn.run("ax_pp300.main:app", host="0.0.0.0", port=8000, reload=False)
