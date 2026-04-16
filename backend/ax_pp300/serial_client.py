"""Serial client for AX PP300 with background polling and task control."""

import math
import threading
import time
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional

import serial

from .protocol import FRAME_HEAD, FRAME_TAIL, build_command, parse_status_response


@dataclass
class SequenceStep:
    voltage_mv: int
    current_ma: int
    output_on: bool
    duration_ms: int


@dataclass
class BatterySimulationConfig:
    open_circuit_voltage_mv: int
    min_voltage_mv: int
    current_limit_ma: int
    internal_resistance_mohm: int
    sample_interval_ms: int = 100
    recovery_ms: int = 400
    ripple_mv: int = 0
    transient_sag_mv: int = 0
    duration_ms: int = 0


class PP300SerialClient:
    """Thread-safe serial client for AX PP300."""

    def __init__(self):
        self._ser: Optional[serial.Serial] = None
        self._port: Optional[str] = None
        self._baudrate: Optional[int] = None
        self._lock = threading.Lock()
        self._latest_status: Optional[Dict[str, Any]] = None
        self._task_overlay: Dict[str, Any] = {}
        self._poll_thread: Optional[threading.Thread] = None
        self._running = False
        self._callbacks: List[Callable[[Dict[str, Any]], None]] = []
        self._callback_lock = threading.Lock()
        self._task_overlay_lock = threading.Lock()
        # Task control
        self._task_thread: Optional[threading.Thread] = None
        self._task_stop = threading.Event()
        self._task_type: Optional[str] = None  # 'pwm', 'sequence', 'battery'
        self._poll_interval = 0.05  # seconds
        self._connected_port: Optional[str] = None
        self._connected_baudrate: Optional[int] = None

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------
    def connect(self, port: str, baudrate: int = 115200) -> None:
        """Open the serial port and start the background polling thread."""
        if self._ser is not None and self._ser.is_open:
            self.disconnect()
        self._ser = serial.Serial(port, baudrate, timeout=1)
        self._port = port
        self._baudrate = baudrate
        self._connected_port = port
        self._connected_baudrate = baudrate
        self._running = True
        self._poll_thread = threading.Thread(target=self._poll_loop, daemon=True)
        self._poll_thread.start()
        # Immediate query once connected
        try:
            status = self.query_status()
            if status:
                status = self._augment_status(status)
                self._latest_status = status
                self._notify(status)
        except Exception:
            pass

    def set_poll_interval(self, interval_ms: int) -> None:
        """Set the background polling interval in milliseconds."""
        if interval_ms < 5:
            interval_ms = 5
        self._poll_interval = interval_ms / 1000.0

    def disconnect(self) -> None:
        """Stop polling and close the serial port."""
        self.stop_task()
        self._running = False
        if self._poll_thread:
            self._poll_thread.join(timeout=2)
        if self._ser and self._ser.is_open:
            self._ser.close()
        self._ser = None
        self._latest_status = None
        self._clear_task_overlay()
        self._connected_port = None
        self._connected_baudrate = None

    def is_connected(self) -> bool:
        return self._ser is not None and self._ser.is_open

    def get_connection_info(self) -> Dict[str, Any]:
        return {
            "connected": self.is_connected(),
            "port": self._port,
            "baudrate": self._baudrate,
        }

    # ------------------------------------------------------------------
    # Callbacks
    # ------------------------------------------------------------------
    def register_callback(self, cb: Callable[[Dict[str, Any]], None]) -> None:
        with self._callback_lock:
            self._callbacks.append(cb)

    def unregister_callback(self, cb: Callable[[Dict[str, Any]], None]) -> None:
        with self._callback_lock:
            if cb in self._callbacks:
                self._callbacks.remove(cb)

    def _notify(self, status: Dict[str, Any]) -> None:
        with self._callback_lock:
            cbs = list(self._callbacks)
        for cb in cbs:
            try:
                cb(status)
            except Exception:
                pass

    # ------------------------------------------------------------------
    # Background polling
    # ------------------------------------------------------------------
    def _poll_loop(self) -> None:
        while self._running:
            try:
                status = self.query_status()
                if status:
                    status = self._augment_status(status)
                    self._latest_status = status
                    self._notify(status)
            except Exception:
                pass
            time.sleep(self._poll_interval)

    def _set_task_overlay(self, overlay: Dict[str, Any]) -> None:
        with self._task_overlay_lock:
            self._task_overlay = dict(overlay)

    def _clear_task_overlay(self) -> None:
        with self._task_overlay_lock:
            self._task_overlay = {}

    def _augment_status(self, status: Dict[str, Any]) -> Dict[str, Any]:
        with self._task_overlay_lock:
            if not self._task_overlay:
                return status
            return {**status, **self._task_overlay}

    # ------------------------------------------------------------------
    # Low-level I/O
    # ------------------------------------------------------------------
    def send_command(
        self,
        identifier: int,
        data: int = 0,
        response_len: int = 1,
        timeout: float = 1.0,
    ) -> bytes:
        """Send a command and read the response."""
        with self._lock:
            if not self._ser or not self._ser.is_open:
                raise ConnectionError("Serial port not open")
            self._ser.reset_input_buffer()
            self._ser.write(build_command(identifier, data))
            self._ser.timeout = timeout
            return self._ser.read(response_len)

    # ------------------------------------------------------------------
    # High-level helpers
    # ------------------------------------------------------------------
    def set_voltage(self, voltage_mv: int) -> bool:
        """Set target voltage in millivolts (0–30000)."""
        data = voltage_mv // 10
        if not (0 <= data <= 3000):
            raise ValueError("Voltage out of range (0–30000 mV)")
        resp = self.send_command(0x00, data)
        return resp == b"\x01"

    def set_current(self, current_ma: int) -> bool:
        """Set target current in milliamps (0–10100)."""
        data = current_ma // 10
        if not (0 <= data <= 1010):
            raise ValueError("Current out of range (0–10100 mA)")
        resp = self.send_command(0x01, data)
        return resp == b"\x01"

    def set_output(self, on: bool) -> bool:
        """Turn output ON or OFF."""
        resp = self.send_command(0x08, 1 if on else 0)
        return resp == b"\x01"

    def set_ovp(self, ovp_mv: int) -> bool:
        """Set over-voltage protection in millivolts (0–30500)."""
        data = ovp_mv // 10
        if not (0 <= data <= 3050):
            raise ValueError("OVP out of range (0–30500 mV)")
        resp = self.send_command(0x02, data)
        return resp == b"\x01"

    def set_ocp(self, ocp_ma: int) -> bool:
        """Set over-current protection in milliamps (0–10500)."""
        data = ocp_ma // 10
        if not (0 <= data <= 1050):
            raise ValueError("OCP out of range (0–10500 mA)")
        resp = self.send_command(0x03, data)
        return resp == b"\x01"

    def query_status(self) -> Optional[Dict[str, Any]]:
        """Query real-time status from the device."""
        resp = self.send_command(0xFF, 0, response_len=15)
        if (
            len(resp) == 15
            and resp[0] == FRAME_HEAD
            and resp[14] == FRAME_TAIL
        ):
            return parse_status_response(resp)
        return None

    def get_status(self) -> Optional[Dict[str, Any]]:
        """Return the latest cached status (or None if not polled yet)."""
        return self._latest_status

    def get_connection_info(self) -> Dict[str, Any]:
        """Return current serial connection state."""
        return {
            "connected": self.is_connected(),
            "port": self._connected_port,
            "baudrate": self._connected_baudrate,
        }

    # ------------------------------------------------------------------
    # Task control (PWM & Sequence)
    # ------------------------------------------------------------------
    def is_task_running(self) -> bool:
        return self._task_thread is not None and self._task_thread.is_alive()

    def task_type(self) -> Optional[str]:
        return self._task_type if self.is_task_running() else None

    def stop_task(self) -> None:
        if self.is_task_running():
            self._task_stop.set()
            self._task_thread.join(timeout=2)
        self._task_stop.clear()
        self._task_type = None
        self._task_thread = None
        self._clear_task_overlay()

    def start_pwm(self, voltage_mv: int, frequency: float, duty_cycle: float) -> None:
        """Start PWM output.

        Args:
            voltage_mv: Target voltage when ON.
            frequency: Hz, e.g. 1.0 means 1 second per period. Min 0.001 Hz (1000s period).
            duty_cycle: 0.0 ~ 100.0.
        """
        if self.is_task_running():
            self.stop_task()
        if not (0.001 <= frequency <= 100):
            raise ValueError("Frequency must be 0.001 <= f <= 100 Hz")
        if not (0 <= duty_cycle <= 100):
            raise ValueError("Duty cycle must be 0~100")
        self._task_stop.clear()
        self._task_type = "pwm"
        self._task_thread = threading.Thread(
            target=self._pwm_loop,
            args=(voltage_mv, frequency, duty_cycle),
            daemon=True,
        )
        self._task_thread.start()

    def _pwm_loop(self, voltage_mv: int, frequency: float, duty_cycle: float) -> None:
        period = 1.0 / frequency
        on_time = period * (duty_cycle / 100.0)
        off_time = period - on_time
        # Pre-set voltage
        try:
            self.set_voltage(voltage_mv)
        except Exception:
            pass
        while not self._task_stop.is_set():
            try:
                if on_time > 0:
                    self.set_output(True)
                    self._task_stop.wait(timeout=on_time)
                if off_time > 0 and not self._task_stop.is_set():
                    self.set_output(False)
                    self._task_stop.wait(timeout=off_time)
            except Exception:
                pass
        # Ensure output off when stopped
        try:
            self.set_output(False)
        except Exception:
            pass

    def start_sequence(self, steps: List[SequenceStep], loop: bool = False) -> None:
        """Start a programmed sequence.

        Args:
            steps: List of sequence steps.
            loop: If True, repeat the sequence indefinitely until stopped.
        """
        if not steps:
            raise ValueError("Sequence is empty")
        if self.is_task_running():
            self.stop_task()
        self._task_stop.clear()
        self._task_type = "sequence"
        self._task_thread = threading.Thread(
            target=self._sequence_loop,
            args=(steps, loop),
            daemon=True,
        )
        self._task_thread.start()

    def _sequence_loop(self, steps: List[SequenceStep], loop: bool) -> None:
        while True:
            for step in steps:
                if self._task_stop.is_set():
                    break
                try:
                    self.set_voltage(step.voltage_mv)
                    self.set_current(step.current_ma)
                    self.set_output(step.output_on)
                except Exception:
                    pass
                if self._task_stop.wait(timeout=step.duration_ms / 1000.0):
                    break
            if not loop or self._task_stop.is_set():
                break
        # Optional: turn off at end
        # try:
        #     self.set_output(False)
        # except Exception:
        #     pass

    def start_battery_sim(self, config: BatterySimulationConfig) -> None:
        """Start a weak battery simulation driven by measured load current."""
        if not (0 <= config.open_circuit_voltage_mv <= 30000):
            raise ValueError("Open-circuit voltage out of range (0–30000 mV)")
        if not (0 <= config.min_voltage_mv <= config.open_circuit_voltage_mv):
            raise ValueError("Minimum voltage must be between 0 and open-circuit voltage")
        if not (0 <= config.current_limit_ma <= 10100):
            raise ValueError("Current limit out of range (0–10100 mA)")
        if not (0 <= config.internal_resistance_mohm <= 5000):
            raise ValueError("Internal resistance out of range (0–5000 mOhm)")
        if not (5 <= config.sample_interval_ms <= 5000):
            raise ValueError("Sample interval out of range (5–5000 ms)")
        if not (0 <= config.recovery_ms <= 10000):
            raise ValueError("Recovery time out of range (0–10000 ms)")
        if not (0 <= config.ripple_mv <= 2000):
            raise ValueError("Ripple out of range (0–2000 mV)")
        if not (0 <= config.transient_sag_mv <= 5000):
            raise ValueError("Transient sag out of range (0–5000 mV)")
        if not (0 <= config.duration_ms <= 86_400_000):
            raise ValueError("Duration out of range (0–86400000 ms)")

        if self.is_task_running():
            self.stop_task()
        self._task_stop.clear()
        self._task_type = "battery"
        self._set_task_overlay(
            {
                "simulation_active": True,
                "simulation_type": "battery",
                "simulation_limit_voltage_v": round(config.open_circuit_voltage_mv / 1000.0, 3),
            }
        )
        self._task_thread = threading.Thread(
            target=self._battery_loop,
            args=(config,),
            daemon=True,
        )
        self._task_thread.start()

    def _battery_loop(self, config: BatterySimulationConfig) -> None:
        started_at = time.monotonic()
        last_tick = started_at
        modeled_voltage_mv = float(config.open_circuit_voltage_mv)
        last_command_mv: Optional[int] = None

        try:
            self.set_current(config.current_limit_ma)
            self.set_output(True)
        except Exception:
            pass

        while not self._task_stop.is_set():
            now = time.monotonic()
            elapsed_ms = int((now - started_at) * 1000)
            if config.duration_ms > 0 and elapsed_ms >= config.duration_ms:
                break

            latest_status = self.get_status() or {}
            try:
                load_current_ma = max(0, int(round(float(latest_status.get("current_a", 0)) * 1000)))
            except (TypeError, ValueError):
                load_current_ma = 0

            load_ratio = 0.0
            if config.current_limit_ma > 0:
                load_ratio = min(load_current_ma / config.current_limit_ma, 1.0)

            resistive_droop_mv = (load_current_ma * config.internal_resistance_mohm) / 1000.0
            transient_droop_mv = config.transient_sag_mv * load_ratio
            target_voltage_mv = max(
                config.min_voltage_mv,
                config.open_circuit_voltage_mv - resistive_droop_mv - transient_droop_mv,
            )

            dt_ms = max((now - last_tick) * 1000.0, 1.0)
            last_tick = now
            if config.recovery_ms <= 0:
                alpha = 1.0
            else:
                alpha = min(1.0, dt_ms / config.recovery_ms)
            modeled_voltage_mv += (target_voltage_mv - modeled_voltage_mv) * alpha

            if config.ripple_mv > 0:
                ripple_period_ms = max(config.sample_interval_ms * 8, 200)
                modeled_voltage_mv += config.ripple_mv * math.sin((2 * math.pi * elapsed_ms) / ripple_period_ms)

            command_mv = int(round(modeled_voltage_mv / 10.0) * 10)
            command_mv = max(config.min_voltage_mv, min(config.open_circuit_voltage_mv, command_mv))

            self._set_task_overlay(
                {
                    "simulation_active": True,
                    "simulation_type": "battery",
                    "simulation_limit_voltage_v": round(target_voltage_mv / 1000.0, 3),
                    "simulation_command_voltage_v": round(command_mv / 1000.0, 3),
                    "simulation_load_current_a": round(load_current_ma / 1000.0, 3),
                }
            )

            try:
                if command_mv != last_command_mv:
                    self.set_voltage(command_mv)
                    last_command_mv = command_mv
            except Exception:
                pass

            if self._task_stop.wait(timeout=config.sample_interval_ms / 1000.0):
                break

        try:
            self.set_output(False)
        except Exception:
            pass
        self._clear_task_overlay()
