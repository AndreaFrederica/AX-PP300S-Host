import { ref, onUnmounted } from 'vue';

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
}

export function useWebSocket() {
  const ws = ref<WebSocket | null>(null);
  const connected = ref(false);
  const status = ref<PowerStatus | null>(null);
  const lastError = ref<string | null>(null);

  const WS_URL = 'ws://127.0.0.1:18000/ws';

  function connect() {
    if (ws.value) return;
    lastError.value = null;
    const socket = new WebSocket(WS_URL);

    socket.onopen = () => {
      connected.value = true;
      lastError.value = null;
    };

    socket.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);
        if (msg.voltage_v !== undefined) {
          status.value = msg as PowerStatus;
        }
      } catch {
        // ignore non-json
      }
    };

    socket.onerror = () => {
      lastError.value = 'WebSocket error';
    };

    socket.onclose = () => {
      connected.value = false;
      ws.value = null;
    };

    ws.value = socket;
  }

  function disconnect() {
    ws.value?.close();
    ws.value = null;
    connected.value = false;
  }

  function send(action: string, payload?: Record<string, unknown>) {
    if (!ws.value || ws.value.readyState !== WebSocket.OPEN) {
      lastError.value = 'WebSocket not connected';
      return;
    }
    ws.value.send(JSON.stringify({ action, ...payload }));
  }

  onUnmounted(() => {
    disconnect();
  });

  return {
    ws,
    connected,
    status,
    lastError,
    connect,
    disconnect,
    send,
  };
}
