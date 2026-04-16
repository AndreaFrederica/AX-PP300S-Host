export interface SequenceStep {
  voltage_mv: number;
  current_ma: number;
  output_on: boolean;
  duration_ms: number;
}

export interface PreviewPoint {
  timeMs: number;
  voltageV: number;
  currentA: number;
}

export type WaveformKind = 'sine' | 'breathing' | 'triangle' | 'sawtooth' | 'square' | 'staircase';
export type WaveformControlMode = 'voltage' | 'current';

export interface WaveformProgramConfig {
  controlMode: WaveformControlMode;
  kind: WaveformKind;
  lowVoltageMv: number;
  highVoltageMv: number;
  currentMa: number;
  lowCurrentMa: number;
  highCurrentMa: number;
  voltageMv: number;
  periodMs: number;
  durationMs: number;
  sampleIntervalMs: number;
  dutyCycle: number;
  staircaseSteps: number;
  outputOn: boolean;
}

export interface BatterySimulationConfig {
  openCircuitVoltageMv: number;
  minVoltageMv: number;
  currentLimitMa: number;
  internalResistanceMohm: number;
  sampleIntervalMs: number;
  recoveryMs: number;
  rippleMv: number;
  transientSagMv: number;
  previewDurationMs: number;
  previewLoadBaseMa: number;
  previewLoadSwingMa: number;
  previewLoadPeriodMs: number;
}

export interface BatteryPreset {
  key: string;
  label: string;
  category: 'healthy' | 'aged' | 'weak';
  values: Partial<BatterySimulationConfig>;
}

interface CsvRow {
  timeMs?: number;
  durationMs?: number;
  voltageMv: number;
  currentMa: number;
  outputOn: boolean;
}

export interface CsvProgramOptions {
  defaultCurrentMa: number;
  defaultLastDurationMs: number;
  defaultOutputOn: boolean;
}

export interface CsvProgramResult {
  steps: SequenceStep[];
  preview: PreviewPoint[];
  warnings: string[];
}

export const batteryPresets: BatteryPreset[] = [
  {
    key: 'phone-healthy',
    label: '手机电池 健康状态',
    category: 'healthy',
    values: {
      openCircuitVoltageMv: 4050,
      minVoltageMv: 3300,
      currentLimitMa: 3500,
      internalResistanceMohm: 70,
      recoveryMs: 120,
      rippleMv: 0,
      transientSagMv: 25,
      previewLoadBaseMa: 250,
      previewLoadSwingMa: 1200,
      previewLoadPeriodMs: 1800,
    },
  },
  {
    key: 'phone-low',
    label: '手机电池 亏电发软',
    category: 'weak',
    values: {
      openCircuitVoltageMv: 3650,
      minVoltageMv: 3000,
      currentLimitMa: 2500,
      internalResistanceMohm: 260,
      recoveryMs: 650,
      rippleMv: 0,
      transientSagMv: 180,
      previewLoadBaseMa: 300,
      previewLoadSwingMa: 1400,
      previewLoadPeriodMs: 1800,
    },
  },
  {
    key: 'phone-cold',
    label: '手机电池 低温瞬降',
    category: 'weak',
    values: {
      openCircuitVoltageMv: 3780,
      minVoltageMv: 2950,
      currentLimitMa: 2800,
      internalResistanceMohm: 340,
      recoveryMs: 900,
      rippleMv: 0,
      transientSagMv: 260,
      previewLoadBaseMa: 250,
      previewLoadSwingMa: 1700,
      previewLoadPeriodMs: 1400,
    },
  },
  {
    key: 'fresh-18650',
    label: '18650 新电芯',
    category: 'healthy',
    values: {
      openCircuitVoltageMv: 4180,
      minVoltageMv: 3100,
      currentLimitMa: 5000,
      internalResistanceMohm: 45,
      recoveryMs: 100,
      rippleMv: 0,
      transientSagMv: 15,
      previewLoadBaseMa: 350,
      previewLoadSwingMa: 2200,
      previewLoadPeriodMs: 2000,
    },
  },
  {
    key: 'aging-18650',
    label: '18650 老化高内阻',
    category: 'aged',
    values: {
      openCircuitVoltageMv: 4050,
      minVoltageMv: 3000,
      currentLimitMa: 4000,
      internalResistanceMohm: 180,
      recoveryMs: 450,
      rippleMv: 0,
      transientSagMv: 120,
      previewLoadBaseMa: 500,
      previewLoadSwingMa: 2000,
      previewLoadPeriodMs: 2200,
    },
  },
  {
    key: 'lipo-2s-racer',
    label: '2S 锂电 高动态负载',
    category: 'healthy',
    values: {
      openCircuitVoltageMv: 7900,
      minVoltageMv: 6200,
      currentLimitMa: 6500,
      internalResistanceMohm: 140,
      recoveryMs: 280,
      rippleMv: 0,
      transientSagMv: 320,
      previewLoadBaseMa: 700,
      previewLoadSwingMa: 3200,
      previewLoadPeriodMs: 900,
    },
  },
  {
    key: 'powerbank-good',
    label: '移动电源 正常状态',
    category: 'healthy',
    values: {
      openCircuitVoltageMv: 5150,
      minVoltageMv: 4700,
      currentLimitMa: 3500,
      internalResistanceMohm: 55,
      recoveryMs: 120,
      rippleMv: 0,
      transientSagMv: 20,
      previewLoadBaseMa: 300,
      previewLoadSwingMa: 1600,
      previewLoadPeriodMs: 1600,
    },
  },
  {
    key: 'powerbank-aged',
    label: '移动电源 老化掉压',
    category: 'aged',
    values: {
      openCircuitVoltageMv: 5200,
      minVoltageMv: 4300,
      currentLimitMa: 3200,
      internalResistanceMohm: 220,
      recoveryMs: 520,
      rippleMv: 0,
      transientSagMv: 140,
      previewLoadBaseMa: 400,
      previewLoadSwingMa: 1800,
      previewLoadPeriodMs: 1600,
    },
  },
  {
    key: 'good-12v',
    label: '12V 电池 健康状态',
    category: 'healthy',
    values: {
      openCircuitVoltageMv: 12600,
      minVoltageMv: 11200,
      currentLimitMa: 7000,
      internalResistanceMohm: 90,
      recoveryMs: 180,
      rippleMv: 0,
      transientSagMv: 30,
      previewLoadBaseMa: 500,
      previewLoadSwingMa: 2500,
      previewLoadPeriodMs: 2500,
    },
  },
  {
    key: 'weak-12v',
    label: '12V 电池 带载掉压',
    category: 'weak',
    values: {
      openCircuitVoltageMv: 12200,
      minVoltageMv: 9800,
      currentLimitMa: 5000,
      internalResistanceMohm: 350,
      recoveryMs: 900,
      rippleMv: 0,
      transientSagMv: 260,
      previewLoadBaseMa: 600,
      previewLoadSwingMa: 2800,
      previewLoadPeriodMs: 2500,
    },
  },
  {
    key: 'lead-acid-cold',
    label: '铅酸电池 冷启动无力',
    category: 'weak',
    values: {
      openCircuitVoltageMv: 12400,
      minVoltageMv: 8800,
      currentLimitMa: 7000,
      internalResistanceMohm: 420,
      recoveryMs: 1300,
      rippleMv: 0,
      transientSagMv: 520,
      previewLoadBaseMa: 500,
      previewLoadSwingMa: 4200,
      previewLoadPeriodMs: 2100,
    },
  },
  {
    key: 'drycell-aa',
    label: 'AA 碱性电池 后段乏力',
    category: 'aged',
    values: {
      openCircuitVoltageMv: 1450,
      minVoltageMv: 850,
      currentLimitMa: 900,
      internalResistanceMohm: 480,
      recoveryMs: 700,
      rippleMv: 0,
      transientSagMv: 160,
      previewLoadBaseMa: 60,
      previewLoadSwingMa: 420,
      previewLoadPeriodMs: 1300,
    },
  },
];

function clamp(value: number, min: number, max: number) {
  return Math.min(max, Math.max(min, value));
}

function roundTo10(value: number) {
  return Math.round(value / 10) * 10;
}

function normalizeWaveformValue(
  kind: WaveformKind,
  phase: number,
  dutyCycle: number,
  staircaseSteps: number,
) {
  switch (kind) {
    case 'sine':
      return 0.5 - 0.5 * Math.cos(2 * Math.PI * phase);
    case 'breathing': {
      const eased = 0.5 - 0.5 * Math.cos(2 * Math.PI * phase);
      return Math.pow(eased, 1.8);
    }
    case 'triangle':
      return phase < 0.5 ? phase * 2 : (1 - phase) * 2;
    case 'sawtooth':
      return phase;
    case 'square':
      return phase < clamp(dutyCycle / 100, 0, 1) ? 1 : 0;
    case 'staircase': {
      const steps = Math.max(2, Math.floor(staircaseSteps));
      return Math.floor(phase * steps) / (steps - 1);
    }
  }
}

function compactSteps(steps: SequenceStep[]) {
  if (steps.length === 0) return steps;
  const compacted: SequenceStep[] = [structuredClone(steps[0])];

  for (let index = 1; index < steps.length; index += 1) {
    const current = steps[index];
    const previous = compacted[compacted.length - 1];
    if (
      previous.voltage_mv === current.voltage_mv &&
      previous.current_ma === current.current_ma &&
      previous.output_on === current.output_on
    ) {
      previous.duration_ms += current.duration_ms;
      continue;
    }
    compacted.push(structuredClone(current));
  }

  return compacted;
}

export function buildWaveformProgram(config: WaveformProgramConfig) {
  if (config.periodMs <= 0) {
    throw new Error('周期必须大于 0');
  }
  if (config.durationMs <= 0) {
    throw new Error('总时长必须大于 0');
  }
  if (config.sampleIntervalMs <= 0) {
    throw new Error('采样间隔必须大于 0');
  }
  if (config.controlMode === 'voltage') {
    if (config.highVoltageMv < config.lowVoltageMv) {
      throw new Error('最高电压必须大于或等于最低电压');
    }
    if (config.currentMa < 0 || config.currentMa > 10100) {
      throw new Error('限流必须在 0~10100mA');
    }
  } else {
    if (config.highCurrentMa < config.lowCurrentMa) {
      throw new Error('最高电流必须大于或等于最低电流');
    }
    if (config.voltageMv < 0 || config.voltageMv > 30000) {
      throw new Error('电压上限必须在 0~30000mV');
    }
  }

  const preview: PreviewPoint[] = [];
  const steps: SequenceStep[] = [];
  let elapsedMs = 0;

  while (elapsedMs < config.durationMs) {
    const phase = ((elapsedMs % config.periodMs) + config.periodMs) % config.periodMs / config.periodMs;
    const normalized = normalizeWaveformValue(
      config.kind,
      phase,
      config.dutyCycle,
      config.staircaseSteps,
    );
    const voltageMv = config.controlMode === 'voltage'
      ? roundTo10(
        clamp(
          config.lowVoltageMv + (config.highVoltageMv - config.lowVoltageMv) * normalized,
          config.lowVoltageMv,
          config.highVoltageMv,
        ),
      )
      : roundTo10(clamp(config.voltageMv, 0, 30000));
    const currentMa = config.controlMode === 'current'
      ? roundTo10(
        clamp(
          config.lowCurrentMa + (config.highCurrentMa - config.lowCurrentMa) * normalized,
          config.lowCurrentMa,
          config.highCurrentMa,
        ),
      )
      : roundTo10(clamp(config.currentMa, 0, 10100));
    const durationMs = Math.min(config.sampleIntervalMs, config.durationMs - elapsedMs);

    preview.push({
      timeMs: elapsedMs,
      voltageV: voltageMv / 1000,
      currentA: currentMa / 1000,
    });
    steps.push({
      voltage_mv: voltageMv,
      current_ma: currentMa,
      output_on: config.outputOn,
      duration_ms: durationMs,
    });

    elapsedMs += durationMs;
  }

  return {
    preview,
    steps: compactSteps(steps),
  };
}

function guessDelimiter(line: string) {
  const candidates = [',', ';', '\t'];
  let selected = ',';
  let bestCount = -1;
  for (const candidate of candidates) {
    const count = line.split(candidate).length;
    if (count > bestCount) {
      bestCount = count;
      selected = candidate;
    }
  }
  return selected;
}

function parseBooleanValue(raw: string | undefined, fallback: boolean) {
  if (raw === undefined || raw.trim() === '') return fallback;
  const normalized = raw.trim().toLowerCase();
  if (['1', 'true', 'on', 'yes', 'y'].includes(normalized)) return true;
  if (['0', 'false', 'off', 'no', 'n'].includes(normalized)) return false;
  return fallback;
}

function parseNumberValue(raw: string | undefined) {
  if (raw === undefined) return undefined;
  const trimmed = raw.trim();
  if (!trimmed) return undefined;
  const value = Number(trimmed);
  return Number.isFinite(value) ? value : undefined;
}

function getVoltageMv(raw: string | undefined, header: string | undefined) {
  const value = parseNumberValue(raw);
  if (value === undefined) return undefined;
  if (header === 'voltage_mv') return Math.round(value);
  if (header === 'voltage_v') return Math.round(value * 1000);
  return value > 60 ? Math.round(value) : Math.round(value * 1000);
}

function getCurrentMa(raw: string | undefined, header: string | undefined, fallback: number) {
  const value = parseNumberValue(raw);
  if (value === undefined) return fallback;
  if (header === 'current_ma') return Math.round(value);
  if (header === 'current_a') return Math.round(value * 1000);
  return value > 50 ? Math.round(value) : Math.round(value * 1000);
}

export function parseCsvProgram(text: string, options: CsvProgramOptions): CsvProgramResult {
  const sourceLines = text
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter((line) => line && !line.startsWith('#'));

  if (sourceLines.length < 2) {
    throw new Error('CSV 至少需要表头和一行数据');
  }

  const delimiter = guessDelimiter(sourceLines[0]);
  const headers = sourceLines[0].split(delimiter).map((header) => header.trim().toLowerCase());
  const headerMap = new Map(headers.map((header, index) => [header, index]));
  const warnings: string[] = [];

  const voltageHeader = headers.find((header) => ['voltage_mv', 'voltage_v', 'voltage'].includes(header));
  if (!voltageHeader) {
    throw new Error('CSV 缺少 voltage_mv 或 voltage_v 列');
  }

  const currentHeader = headers.find((header) => ['current_ma', 'current_a', 'current'].includes(header));
  const outputHeader = headers.find((header) => ['output_on', 'output'].includes(header));
  const durationHeader = headers.find((header) => ['duration_ms', 'duration_s'].includes(header));
  const timeHeader = headers.find((header) => ['time_ms', 'time_s'].includes(header));

  if (!durationHeader && !timeHeader) {
    throw new Error('CSV 需要 duration_ms/duration_s 或 time_ms/time_s 列');
  }

  const rows: CsvRow[] = sourceLines.slice(1).map((line, lineIndex) => {
    const cells = line.split(delimiter).map((cell) => cell.trim());
    const voltageMv = getVoltageMv(cells[headerMap.get(voltageHeader) ?? -1], voltageHeader);
    if (voltageMv === undefined) {
      throw new Error(`第 ${lineIndex + 2} 行电压无效`);
    }

    let durationMs: number | undefined;
    if (durationHeader) {
      const rawDuration = parseNumberValue(cells[headerMap.get(durationHeader) ?? -1]);
      if (rawDuration === undefined) {
        throw new Error(`第 ${lineIndex + 2} 行时长无效`);
      }
      durationMs = durationHeader === 'duration_s' ? Math.round(rawDuration * 1000) : Math.round(rawDuration);
    }

    let timeMs: number | undefined;
    if (timeHeader) {
      const rawTime = parseNumberValue(cells[headerMap.get(timeHeader) ?? -1]);
      if (rawTime === undefined) {
        throw new Error(`第 ${lineIndex + 2} 行时间无效`);
      }
      timeMs = timeHeader === 'time_s' ? Math.round(rawTime * 1000) : Math.round(rawTime);
    }

    return {
      timeMs,
      durationMs,
      voltageMv: roundTo10(clamp(voltageMv, 0, 30000)),
      currentMa: clamp(
        getCurrentMa(cells[headerMap.get(currentHeader ?? '') ?? -1], currentHeader, options.defaultCurrentMa),
        0,
        10100,
      ),
      outputOn: parseBooleanValue(cells[headerMap.get(outputHeader ?? '') ?? -1], options.defaultOutputOn),
    };
  });

  if (timeHeader) {
    for (let index = 1; index < rows.length; index += 1) {
      if ((rows[index].timeMs ?? 0) < (rows[index - 1].timeMs ?? 0)) {
        throw new Error('time 列必须单调递增');
      }
    }
  }

  const preview: PreviewPoint[] = [];
  const steps: SequenceStep[] = [];

  for (let index = 0; index < rows.length; index += 1) {
    const row = rows[index];
    let durationMs = row.durationMs;

    if (durationMs === undefined) {
      const currentTime = row.timeMs ?? 0;
      const nextTime = rows[index + 1]?.timeMs;
      if (nextTime !== undefined) {
        durationMs = nextTime - currentTime;
      } else if (index > 0 && rows[index - 1].timeMs !== undefined) {
        durationMs = currentTime - (rows[index - 1].timeMs ?? 0);
      } else {
        durationMs = options.defaultLastDurationMs;
      }
    }

    if (durationMs <= 0) {
      warnings.push(`第 ${index + 2} 行时长非正值，已按 ${options.defaultLastDurationMs}ms 处理`);
      durationMs = options.defaultLastDurationMs;
    }

    const previewTimeMs = row.timeMs ?? steps.reduce((sum, step) => sum + step.duration_ms, 0);
    preview.push({
      timeMs: previewTimeMs,
      voltageV: row.voltageMv / 1000,
      currentA: row.currentMa / 1000,
    });

    steps.push({
      voltage_mv: row.voltageMv,
      current_ma: row.currentMa,
      output_on: row.outputOn,
      duration_ms: durationMs,
    });
  }

  return {
    preview,
    steps: compactSteps(steps),
    warnings,
  };
}

export function buildBatteryPreview(config: BatterySimulationConfig) {
  if (config.openCircuitVoltageMv < config.minVoltageMv) {
    throw new Error('开路电压必须大于或等于最低电压');
  }
  if (config.previewDurationMs <= 0) {
    throw new Error('预览时长必须大于 0');
  }
  if (config.sampleIntervalMs <= 0) {
    throw new Error('采样间隔必须大于 0');
  }

  const preview: PreviewPoint[] = [];
  let voltageMv = config.openCircuitVoltageMv;
  let elapsedMs = 0;

  while (elapsedMs <= config.previewDurationMs) {
    const phase = ((elapsedMs % config.previewLoadPeriodMs) + config.previewLoadPeriodMs) % config.previewLoadPeriodMs / config.previewLoadPeriodMs;
    const loadMa = clamp(
      config.previewLoadBaseMa + (phase < 0.5 ? config.previewLoadSwingMa : 0),
      0,
      config.currentLimitMa,
    );
    const loadRatio = config.currentLimitMa > 0 ? loadMa / config.currentLimitMa : 0;
    const targetMv = clamp(
      config.openCircuitVoltageMv - (loadMa * config.internalResistanceMohm) / 1000 - config.transientSagMv * loadRatio,
      config.minVoltageMv,
      config.openCircuitVoltageMv,
    );
    const alpha = config.recoveryMs <= 0 ? 1 : Math.min(1, config.sampleIntervalMs / config.recoveryMs);
    voltageMv += (targetMv - voltageMv) * alpha;

    const ripple = config.rippleMv > 0
      ? config.rippleMv * Math.sin((2 * Math.PI * elapsedMs) / Math.max(config.previewLoadPeriodMs, 200))
      : 0;

    preview.push({
      timeMs: elapsedMs,
      voltageV: clamp(voltageMv + ripple, config.minVoltageMv, config.openCircuitVoltageMv) / 1000,
      currentA: loadMa / 1000,
    });

    elapsedMs += config.sampleIntervalMs;
  }

  return preview;
}