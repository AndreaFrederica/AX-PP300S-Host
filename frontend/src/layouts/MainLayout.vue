<template>
  <q-layout view="lHh Lpr lFf">
    <q-header elevated>
      <q-toolbar>
        <q-toolbar-title>
          AX PP300 上位机
        </q-toolbar-title>

        <q-select
          v-model="store.port"
          :options="portOptions"
          label="串口"
          dense
          outlined
          dark
          style="min-width: 180px"
          :disable="store.serialConnected"
          emit-value
          map-options
          class="q-mr-sm"
        >
          <template v-slot:after>
            <q-btn round dense flat icon="refresh" size="sm" @click="void store.fetchPorts()" :disable="store.serialConnected" />
          </template>
        </q-select>

        <q-btn
          :color="store.serialConnected ? 'negative' : 'primary'"
          :label="store.serialConnected ? '断开' : '连接串口'"
          dense
          unelevated
          class="q-mr-sm"
          @click="toggleSerial"
        />

        <q-btn
          color="secondary"
          label="WS"
          :disable="store.connected"
          dense
          unelevated
          class="q-mr-sm"
          @click="store.connectWs"
        />

        <q-chip
          :color="store.connected ? 'positive' : 'negative'"
          text-color="white"
          dense
          icon="wifi"
          class="q-mr-sm"
        >
          {{ store.connected ? 'WS' : 'WS断' }}
        </q-chip>

        <q-chip
          v-if="store.taskRunning"
          color="secondary"
          text-color="white"
          dense
          icon="precision_manufacturing"
          class="q-mr-sm"
        >
          {{ taskTypeLabel }}
        </q-chip>

        <q-chip
          :color="store.status?.output_on ? 'positive' : 'grey'"
          text-color="white"
          dense
        >
          {{ store.status?.output_on ? '输出开' : '输出关' }}
        </q-chip>
      </q-toolbar>
    </q-header>

    <q-page-container>
      <router-view />
    </q-page-container>
  </q-layout>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue';
import { useQuasar } from 'quasar';
import { usePowerStore } from 'src/stores/powerStore';

const $q = useQuasar();
const store = usePowerStore();

onMounted(() => {
  void store.fetchPorts();
  void store.restoreBackendState();
});

const portOptions = computed(() =>
  store.ports.map((p) => ({ label: `${p.device} — ${p.description}`, value: p.device }))
);

const taskTypeLabel = computed(() => {
  switch (store.taskType) {
    case 'pwm':
      return '任务: PWM';
    case 'sequence':
      return '任务: 程控';
    case 'battery':
      return '任务: 电池模拟';
    default:
      return '任务: 运行中';
  }
});

async function toggleSerial() {
  try {
    if (store.serialConnected) {
      await store.disconnectSerial();
      $q.notify({ type: 'positive', message: '串口已断开' });
    } else {
      await store.connectSerial();
      $q.notify({ type: 'positive', message: '串口已连接' });
      if (!store.connected) store.connectWs();
    }
  } catch (err: unknown) {
    $q.notify({ type: 'negative', message: (err as Error).message || '操作失败' });
  }
}
</script>
