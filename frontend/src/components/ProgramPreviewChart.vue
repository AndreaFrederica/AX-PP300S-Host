<template>
  <div style="position: relative; height: 260px;">
    <Line :data="chartData" :options="chartOptions" />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { Line } from 'vue-chartjs';
import {
  CategoryScale,
  Chart as ChartJS,
  Legend,
  LineElement,
  LinearScale,
  PointElement,
  Title,
  Tooltip,
  type ChartData,
  type ChartOptions,
} from 'chart.js';
import type { PreviewPoint } from 'src/utils/programs';

ChartJS.register(CategoryScale, Legend, LineElement, LinearScale, PointElement, Title, Tooltip);

interface Props {
  points: PreviewPoint[];
}

const props = defineProps<Props>();

const chartData = computed<ChartData<'line'>>(() => ({
  labels: props.points.map((point) => (point.timeMs / 1000).toFixed(2)),
  datasets: [
    {
      label: '预览电压 (V)',
      data: props.points.map((point) => point.voltageV),
      borderColor: '#00695c',
      backgroundColor: '#00695c',
      tension: 0.2,
      pointRadius: 0,
      yAxisID: 'y',
    },
    {
      label: '预览电流 (A)',
      data: props.points.map((point) => point.currentA),
      borderColor: '#ef6c00',
      backgroundColor: '#ef6c00',
      tension: 0.15,
      pointRadius: 0,
      yAxisID: 'y1',
    },
  ],
}));

const chartOptions = computed<ChartOptions<'line'>>(() => ({
  responsive: true,
  maintainAspectRatio: false,
  animation: false,
  interaction: {
    mode: 'index',
    intersect: false,
  },
  plugins: {
    legend: {
      position: 'bottom',
      labels: {
        usePointStyle: true,
      },
    },
  },
  scales: {
    x: {
      title: {
        display: true,
        text: '时间 (s)',
      },
      ticks: {
        maxTicksLimit: 10,
      },
    },
    y: {
      type: 'linear',
      position: 'left',
      title: {
        display: true,
        text: '电压 (V)',
      },
    },
    y1: {
      type: 'linear',
      position: 'right',
      grid: {
        drawOnChartArea: false,
      },
      title: {
        display: true,
        text: '电流 (A)',
      },
    },
  },
}));
</script>