import { defineStore } from 'pinia';
import { ref, watch } from 'vue';

export interface PowerStatus {
  voltage_v: number;
  current_a: number;
  power_w: number;
  input_voltage_v: number;
  temperature_c: number;
  mode: 'CV' | 'CC';
  output_on: boolean;
  checksum_ok: boolean;
  raw: string;
  simulation_active?: boolean;
  simulation_type?: string;
  simulation_limit_voltage_v?: number;
  simulation_command_voltage_v?: number;
  simulation_load_current_a?: number;
}

export interface HistoryPoint {
  time: string;
  timestamp: number;
  voltage: number;
  current: number;
  power: number;
  simulationLimitVoltage?: number | null;
  simulationCommandVoltage?: number | null;
}

export const usePowerStore = defineStore('power', () => {
  const connected = ref(false);
  const status = ref<PowerStatus | null>(null);
  const serialConnected = ref(false);
  const taskRunning = ref(false);
  const taskType = ref<string | null>(null);
  const port = ref(localStorage.getItem('ax_pp300_serial_port') || 'COM3');
  const baudrate = ref(Number(localStorage.getItem('ax_pp300_serial_baudrate') || '115200'));
  const history = ref<HistoryPoint[]>([]);
  const maxHistory = 2000;
  const ports = ref<{ device: string; description: string }[]>([]);

  // WebSocket
  const ws = ref<WebSocket | null>(null);

  const apiBase = 'http://127.0.0.1:18000';
  const WS_URL = 'ws://127.0.0.1:18000/ws';

  async function fetchPorts() {
    try {
      const res = await fetch(`${apiBase}/ports`);
      if (res.ok) {
        const data = await res.json();
        ports.value = data.ports || [];
      }
    } catch {
      ports.value = [];
    }
  }

  function pushHistory(s: PowerStatus) {
    const now = new Date();
    const time = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}:${now.getSeconds().toString().padStart(2, '0')}.${now.getMilliseconds().toString().padStart(3, '0')}`;
    history.value.push({
      time,
      timestamp: now.getTime(),
      voltage: s.voltage_v,
      current: s.current_a,
      power: s.power_w,
      simulationLimitVoltage: s.simulation_active && s.simulation_type === 'battery'
        ? (s.simulation_limit_voltage_v ?? null)
        : null,
      simulationCommandVoltage: s.simulation_active && s.simulation_type === 'battery'
        ? (s.simulation_command_voltage_v ?? null)
        : null,
    });
    if (history.value.length > maxHistory) {
      history.value.shift();
    }
  }

  function exportCsv(): string {
    const lines = ['time,voltage,current,power'];
    for (const h of history.value) {
      lines.push(`${h.time},${h.voltage},${h.current},${h.power}`);
    }
    return lines.join('\n');
  }

  async function postJson(path: string, body: Record<string, unknown>) {
    const res = await fetch(`${apiBase}${path}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    if (!res.ok) throw new Error(await res.text());
  }

  async function getJson<T>(path: string): Promise<T> {
    const res = await fetch(`${apiBase}${path}`);
    if (!res.ok) throw new Error(await res.text());
    return res.json() as Promise<T>;
  }

  async function connectSerial() {
    await postJson('/connect', { port: port.value, baudrate: baudrate.value });
    serialConnected.value = true;
  }

  async function disconnectSerial() {
    await fetch(`${apiBase}/disconnect`, { method: 'POST' });
    serialConnected.value = false;
    taskRunning.value = false;
    taskType.value = null;
  }

  async function restoreBackendState() {
    try {
      const connection = await getJson<{ connected: boolean; port: string | null; baudrate: number | null }>('/connection');
      serialConnected.value = connection.connected;
      if (connection.port) {
        port.value = connection.port;
      }
      if (connection.baudrate) {
        baudrate.value = connection.baudrate;
      }

      if (connection.connected) {
        try {
          const task = await getJson<{ running: boolean; type: string | null }>('/task');
          taskRunning.value = task.running;
          taskType.value = task.type;
        } catch {
          taskRunning.value = false;
          taskType.value = null;
        }
        try {
          const currentStatus = await getJson<PowerStatus>('/status');
          status.value = currentStatus;
          if (history.value.length === 0) {
            pushHistory(currentStatus);
          }
        } catch {
          // ignore status restore failures when backend has no cached frame yet
        }
        if (!connected.value) {
          connectWs();
        }
      }
    } catch {
      serialConnected.value = false;
      taskRunning.value = false;
      taskType.value = null;
    }
  }

  async function setVoltage(voltage_mv: number) {
    await postJson('/voltage', { voltage_mv });
  }

  async function setCurrent(current_ma: number) {
    await postJson('/current', { current_ma });
  }

  async function setOutput(on: boolean) {
    await postJson('/output', { on });
  }

  async function setOvp(ovp_mv: number) {
    await postJson('/ovp', { ovp_mv });
  }

  async function setOcp(ocp_ma: number) {
    await postJson('/ocp', { ocp_ma });
  }

  async function setOpp(opp_w: number) {
    const data = Math.round((opp_w - 10) / 10);
    if (data < 0 || data > 30) throw new Error('OPP out of range (10~310 W)');
    await postJson('/raw_command', { identifier: 0x06, data });
  }

  async function setOtp(otp_c: number) {
    const data = Math.round(otp_c / 10);
    if (data < 6 || data > 10) throw new Error('OTP out of range (60~100 °C)');
    await postJson('/raw_command', { identifier: 0x07, data });
  }

  async function setDelay(delay_s: number) {
    if (delay_s < 0 || delay_s > 9999) throw new Error('DELAY out of range (0~9999 s)');
    await postJson('/raw_command', { identifier: 0x04, data: delay_s });
  }

  async function setRev(rev_s: number) {
    if (rev_s < 0 || rev_s > 9999) throw new Error('REV out of range (0~9999 s)');
    await postJson('/raw_command', { identifier: 0x05, data: rev_s });
  }

  async function setParamList(index: number) {
    if (index < 0 || index > 4) throw new Error('Param list index 0~4');
    await postJson('/raw_command', { identifier: 0x09, data: index });
  }

  async function setListVoltage(listIndex: number, voltage_mv: number) {
    const data = Math.round(voltage_mv / 10);
    if (data < 0 || data > 3000) throw new Error('Voltage out of range');
    await postJson('/raw_command', { identifier: 0x0A + listIndex * 0x10, data });
  }
  async function setListCurrent(listIndex: number, current_ma: number) {
    const data = Math.round(current_ma / 10);
    if (data < 0 || data > 1010) throw new Error('Current out of range');
    await postJson('/raw_command', { identifier: 0x0B + listIndex * 0x10, data });
  }
  async function setListOvp(listIndex: number, ovp_mv: number) {
    const data = Math.round(ovp_mv / 10);
    if (data < 0 || data > 3050) throw new Error('OVP out of range');
    await postJson('/raw_command', { identifier: 0x0C + listIndex * 0x10, data });
  }
  async function setListOcp(listIndex: number, ocp_ma: number) {
    const data = Math.round(ocp_ma / 10);
    if (data < 0 || data > 1050) throw new Error('OCP out of range');
    await postJson('/raw_command', { identifier: 0x0D + listIndex * 0x10, data });
  }
  async function setListCutoffCurrent(listIndex: number, current_ma: number) {
    const data = Math.round(current_ma / 10);
    if (data < 0 || data > 1000) throw new Error('Cutoff current out of range');
    await postJson('/raw_command', { identifier: 0x0E + listIndex * 0x10, data });
  }
  async function setListCutoffTime(listIndex: number, value: number, unit: 0 | 1 | 2) {
    if (value < 0 || value > 99) throw new Error('Cutoff time value 0~99');
    if (unit === 1 && value > 60) throw new Error('Minutes max 60');
    if (unit === 2 && value > 60) throw new Error('Hours max 60');
    const data = (unit << 8) | value;
    await postJson('/raw_command', { identifier: 0x0F + listIndex * 0x10, data });
  }

  // PWM
  async function startPwm(voltage_mv: number, frequency: number, duty_cycle: number) {
    await postJson('/pwm/start', { voltage_mv, frequency, duty_cycle });
    taskRunning.value = true;
    taskType.value = 'pwm';
  }

  async function stopPwm() {
    await fetch(`${apiBase}/pwm/stop`, { method: 'POST' });
    taskRunning.value = false;
    taskType.value = null;
  }

  // Sequence
  async function startSequence(steps: { voltage_mv: number; current_ma: number; output_on: boolean; duration_ms: number }[], loop = false) {
    await postJson('/sequence/start', { steps, loop });
    taskRunning.value = true;
    taskType.value = 'sequence';
  }

  async function stopSequence() {
    await fetch(`${apiBase}/sequence/stop`, { method: 'POST' });
    taskRunning.value = false;
    taskType.value = null;
  }

  async function startBatterySimulation(config: {
    open_circuit_voltage_mv: number;
    min_voltage_mv: number;
    current_limit_ma: number;
    internal_resistance_mohm: number;
    sample_interval_ms: number;
    recovery_ms: number;
    ripple_mv: number;
    transient_sag_mv: number;
    duration_ms: number;
  }) {
    await postJson('/battery/start', config);
    taskRunning.value = true;
    taskType.value = 'battery';
  }

  async function stopBatterySimulation() {
    await fetch(`${apiBase}/battery/stop`, { method: 'POST' });
    taskRunning.value = false;
    taskType.value = null;
  }

  async function stopTask() {
    await fetch(`${apiBase}/task/stop`, { method: 'POST' });
    taskRunning.value = false;
    taskType.value = null;
  }

  async function setPollInterval(interval_ms: number) {
    await postJson('/poll_interval', { interval_ms });
  }

  // WebSocket
  function connectWs() {
    if (ws.value) return;
    const socket = new WebSocket(WS_URL);
    socket.onopen = () => {
      connected.value = true;
    };
    socket.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data) as PowerStatus;
        if (msg.voltage_v !== undefined) {
          status.value = msg;
          pushHistory(msg);
        }
      } catch {
        // ignore
      }
    };
    socket.onclose = () => {
      connected.value = false;
      ws.value = null;
    };
    ws.value = socket;
  }

  function disconnectWs() {
    ws.value?.close();
    ws.value = null;
    connected.value = false;
  }

  watch(port, (value) => localStorage.setItem('ax_pp300_serial_port', value));
  watch(baudrate, (value) => localStorage.setItem('ax_pp300_serial_baudrate', String(value)));

  return {
    connected,
    status,
    serialConnected,
    taskRunning,
    taskType,
    port,
    baudrate,
    history,
    ports,
    fetchPorts,
    restoreBackendState,
    pushHistory,
    exportCsv,
    connectSerial,
    disconnectSerial,
    setVoltage,
    setCurrent,
    setOutput,
    setOvp,
    setOcp,
    setOpp,
    setOtp,
    setDelay,
    setRev,
    setParamList,
    setListVoltage,
    setListCurrent,
    setListOvp,
    setListOcp,
    setListCutoffCurrent,
    setListCutoffTime,
    startPwm,
    stopPwm,
    startSequence,
    stopSequence,
    startBatterySimulation,
    stopBatterySimulation,
    stopTask,
    setPollInterval,
    connectWs,
    disconnectWs,
  };
});
