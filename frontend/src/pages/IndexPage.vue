<template>
  <q-page padding class="bg-grey-2">
    <div class="q-gutter-y-md" style="max-width: 1200px; margin: 0 auto;">
      <!-- Chart + Status side by side -->
      <div class="row q-col-gutter-md">
        <!-- Realtime Chart (main, larger) -->
        <div class="col-12 col-md-8">
          <q-card class="fit">
            <q-card-section class="row items-center justify-between">
              <div class="text-subtitle1">实时曲线</div>
              <q-btn color="primary" label="导出 CSV" dense unelevated @click="exportCsv" />
            </q-card-section>
            <q-card-section>
              <!-- Scope controls -->
              <div class="row q-col-gutter-sm items-center q-mb-sm">
                <div class="col-auto text-caption text-weight-bold">示波器</div>
                <div class="col-4 col-sm-2">
                  <q-input v-model.number="pollInterval" label="采样率 (ms)" outlined dense type="number" :min="5" :max="5000" step="1">
                    <template v-slot:append>
                      <q-btn color="primary" icon="send" dense flat @click="applyPollInterval" />
                    </template>
                  </q-input>
                </div>
                <div class="col-4 col-sm-2">
                  <q-input v-model.number="timeWindowSeconds" label="窗口 (s) 0=全" outlined dense type="number" :min="0" :max="300" step="1" />
                </div>
                <div class="col-4 col-sm-3">
                  <q-select v-model="curveInterpolationMode" :options="curveInterpolationOptions" label="曲线连接方式" outlined dense emit-value map-options />
                </div>
                <div class="col-auto text-caption text-grey">
                  当前约 {{ formatHzText(pollInterval) }}
                </div>
              </div>

              <!-- Voltage Y axis -->
              <div class="row q-col-gutter-sm items-center q-mb-xs">
                <div class="col-auto text-caption text-primary">电压</div>
                <div class="col-auto">
                  <q-toggle v-model="voltageYMaxAuto" label="Ymax 自动" dense />
                </div>
                <div class="col-3 col-sm-2" v-if="!voltageYMaxAuto">
                  <q-input v-model.number="voltageYMaxManual" label="Ymax (V)" outlined dense type="number" step="0.1" />
                </div>
                <div class="col-auto">
                  <q-toggle v-model="voltageYMinAuto" label="Ymin 自动" dense />
                </div>
                <div class="col-auto" v-if="!voltageYMinAuto">
                  <q-toggle v-model="voltageYMinTrackTarget" label="追踪设定" dense />
                </div>
                <div class="col-3 col-sm-2" v-if="!voltageYMinAuto && !voltageYMinTrackTarget">
                  <q-input v-model.number="voltageYMinManual" label="Ymin (V)" outlined dense type="number" step="0.1" />
                </div>
              </div>
              <!-- Current Y axis -->
              <div class="row q-col-gutter-sm items-center q-mb-xs">
                <div class="col-auto text-caption text-orange">电流</div>
                <div class="col-auto">
                  <q-toggle v-model="currentYMaxAuto" label="Ymax 自动" dense />
                </div>
                <div class="col-3 col-sm-2" v-if="!currentYMaxAuto">
                  <q-input v-model.number="currentYMaxManual" label="Ymax (A)" outlined dense type="number" step="0.1" />
                </div>
                <div class="col-auto">
                  <q-toggle v-model="currentYMinAuto" label="Ymin 自动" dense />
                </div>
                <div class="col-auto" v-if="!currentYMinAuto">
                  <q-toggle v-model="currentYMinTrackTarget" label="追踪设定" dense />
                </div>
                <div class="col-3 col-sm-2" v-if="!currentYMinAuto && !currentYMinTrackTarget">
                  <q-input v-model.number="currentYMinManual" label="Ymin (A)" outlined dense type="number" step="0.01" />
                </div>
              </div>
              <!-- Power Y axis -->
              <div class="row q-col-gutter-sm items-center q-mb-sm">
                <div class="col-auto text-caption text-positive">功率</div>
                <div class="col-auto">
                  <q-toggle v-model="powerYMaxAuto" label="Ymax 自动" dense />
                </div>
                <div class="col-3 col-sm-2" v-if="!powerYMaxAuto">
                  <q-input v-model.number="powerYMaxManual" label="Ymax (W)" outlined dense type="number" step="1" />
                </div>
                <div class="col-auto">
                  <q-toggle v-model="powerYMinAuto" label="Ymin 自动" dense />
                </div>
                <div class="col-auto" v-if="!powerYMinAuto">
                  <q-toggle v-model="powerYMinTrackTarget" label="追踪设定" dense />
                </div>
                <div class="col-3 col-sm-2" v-if="!powerYMinAuto && !powerYMinTrackTarget">
                  <q-input v-model.number="powerYMinManual" label="Ymin (W)" outlined dense type="number" step="0.1" />
                </div>
                <div class="col-3 col-sm-2" v-if="!powerYMinAuto && powerYMinTrackTarget">
                  <q-input v-model.number="targetPower" label="目标功率 (W)" outlined dense type="number" step="0.1" />
                </div>
              </div>
              <div style="position: relative; height: 400px;">
                <realtime-chart
                  :voltage-y-min-auto="voltageYMinAuto"
                  :voltage-y-min-track-target="voltageYMinTrackTarget"
                  :voltage-y-min-manual="voltageYMinManual"
                  :voltage-y-max-auto="voltageYMaxAuto"
                  :voltage-y-max-manual="voltageYMaxManual"
                  :target-voltage="targetVoltage"
                  :current-y-min-auto="currentYMinAuto"
                  :current-y-min-track-target="currentYMinTrackTarget"
                  :current-y-min-manual="currentYMinManual"
                  :current-y-max-auto="currentYMaxAuto"
                  :current-y-max-manual="currentYMaxManual"
                  :target-current="targetCurrent"
                  :power-y-min-auto="powerYMinAuto"
                  :power-y-min-track-target="powerYMinTrackTarget"
                  :power-y-min-manual="powerYMinManual"
                  :power-y-max-auto="powerYMaxAuto"
                  :power-y-max-manual="powerYMaxManual"
                  :target-power="targetPower"
                  :time-window-seconds="timeWindowSeconds"
                  :interpolation-mode="curveInterpolationMode"
                />
              </div>
            </q-card-section>
          </q-card>
        </div>

        <!-- Realtime Status (side, smaller) -->
        <div class="col-12 col-md-4">
          <q-card class="fit">
            <q-card-section>
              <div class="text-subtitle1 q-mb-sm">实时数据</div>
              <div class="row q-col-gutter-sm">
                <div class="col-6" v-for="item in statusItems" :key="item.label">
                  <q-card flat bordered class="q-pa-sm text-center">
                    <div class="text-caption text-grey">{{ item.label }}</div>
                    <div class="text-h6" :class="item.colorClass">{{ item.value }}</div>
                  </q-card>
                </div>
              </div>
            </q-card-section>
          </q-card>
        </div>
      </div>

      <!-- Controls -->
      <q-card>
        <q-card-section>
          <div class="row items-center q-mb-sm q-gutter-sm">
            <div class="text-subtitle1">控制面板</div>
            <q-space />
            <q-btn color="negative" label="关闭模拟/程控" dense unelevated @click="stopActiveProgram" />
            <q-btn-toggle v-model="voltageUnit" :options="[{label:'V',value:'V'},{label:'mV',value:'mV'}]" dense unelevated toggle-color="primary" color="white" text-color="primary" class="q-mr-sm" />
            <q-btn-toggle v-model="currentUnit" :options="[{label:'A',value:'A'},{label:'mA',value:'mA'}]" dense unelevated toggle-color="primary" color="white" text-color="primary" />
          </div>

          <!-- Basic -->
          <q-expansion-item default-opened icon="tune" label="基础控制" dense-toggle>
            <div class="row q-col-gutter-md items-end q-mt-xs">
              <div class="col-6 col-sm-3">
                <q-input v-model.number="uiTargetVoltage" :label="`目标电压 (${voltageUnit})`" outlined dense type="number" step="0.01" />
                <q-btn class="q-mt-sm full-width" color="primary" label="设置电压" :loading="loadingVoltage" @click="doAction('setVoltage')" unelevated />
              </div>
              <div class="col-6 col-sm-3">
                <q-input v-model.number="uiTargetCurrent" :label="`目标电流 (${currentUnit})`" outlined dense type="number" step="0.001" />
                <q-btn class="q-mt-sm full-width" color="primary" label="设置电流" :loading="loadingCurrent" @click="doAction('setCurrent')" unelevated />
              </div>
              <div class="col-12 col-sm-3">
                <q-btn class="full-width" :color="store.status?.output_on ? 'negative' : 'positive'" :label="store.status?.output_on ? '关闭输出' : '打开输出'" :loading="loadingOutput" @click="applyOutput" unelevated size="lg" />
              </div>
            </div>
          </q-expansion-item>

          <q-separator class="q-my-sm" />

          <!-- Protection -->
          <q-expansion-item icon="security" label="保护设置" dense-toggle>
            <div class="row q-col-gutter-md items-end q-mt-xs">
              <div class="col-6 col-sm-3">
                <q-input v-model.number="uiTargetOvp" :label="`OVP (${voltageUnit})`" outlined dense type="number" step="0.01" />
                <q-btn class="q-mt-sm full-width" color="primary" label="设置OVP" :loading="loadingOvp" @click="doAction('setOvp')" unelevated />
              </div>
              <div class="col-6 col-sm-3">
                <q-input v-model.number="uiTargetOcp" :label="`OCP (${currentUnit})`" outlined dense type="number" step="0.001" />
                <q-btn class="q-mt-sm full-width" color="primary" label="设置OCP" :loading="loadingOcp" @click="doAction('setOcp')" unelevated />
              </div>
              <div class="col-6 col-sm-3">
                <q-input v-model.number="targetOpp" label="OPP (W)" outlined dense type="number" :min="10" :max="310" />
                <q-btn class="q-mt-sm full-width" color="primary" label="设置OPP" :loading="loadingOpp" @click="doAction('setOpp')" unelevated />
              </div>
              <div class="col-6 col-sm-3">
                <q-input v-model.number="targetOtp" label="OTP (°C)" outlined dense type="number" :min="60" :max="100" />
                <q-btn class="q-mt-sm full-width" color="primary" label="设置OTP" :loading="loadingOtp" @click="doAction('setOtp')" unelevated />
              </div>
            </div>
          </q-expansion-item>

          <q-separator class="q-my-sm" />

          <!-- Timing -->
          <q-expansion-item icon="timer" label="定时设置" dense-toggle>
            <div class="row q-col-gutter-md items-end q-mt-xs">
              <div class="col-6 col-sm-3">
                <q-input v-model.number="targetDelay" label="延时输出 (s)" outlined dense type="number" :min="0" :max="9999" />
                <q-btn class="q-mt-sm full-width" color="primary" label="设置Delay" :loading="loadingDelay" @click="doAction('setDelay')" unelevated />
              </div>
              <div class="col-6 col-sm-3">
                <q-input v-model.number="targetRev" label="翻转时间 (s)" outlined dense type="number" :min="0" :max="9999" />
                <q-btn class="q-mt-sm full-width" color="primary" label="设置Rev" :loading="loadingRev" @click="doAction('setRev')" unelevated />
              </div>
            </div>
          </q-expansion-item>

          <q-separator class="q-my-sm" />

          <!-- Chinese Param List -->
          <q-expansion-item icon="list" label="中文参数列表" dense-toggle>
            <div class="row q-col-gutter-md items-end q-mt-xs">
              <div class="col-12 col-sm-3">
                <q-select v-model.number="listIndex" :options="[0,1,2,3,4]" label="参数列表" outlined dense />
              </div>
              <div class="col-12 col-sm-9 row q-gutter-sm">
                <q-btn color="primary" label="切换列表" :loading="loadingList" @click="applyListSelect" dense unelevated />
              </div>
            </div>
            <div class="row q-col-gutter-md items-end q-mt-sm">
              <div class="col-6 col-sm-3">
                <q-input v-model.number="uiListVoltage" :label="`电压 (${voltageUnit})`" outlined dense type="number" step="0.01" />
                <q-btn class="q-mt-sm full-width" color="primary" label="设电压" @click="doListAction('setListVoltage')" unelevated dense />
              </div>
              <div class="col-6 col-sm-3">
                <q-input v-model.number="uiListCurrent" :label="`电流 (${currentUnit})`" outlined dense type="number" step="0.001" />
                <q-btn class="q-mt-sm full-width" color="primary" label="设电流" @click="doListAction('setListCurrent')" unelevated dense />
              </div>
              <div class="col-6 col-sm-3">
                <q-input v-model.number="uiListOvp" :label="`OVP (${voltageUnit})`" outlined dense type="number" step="0.01" />
                <q-btn class="q-mt-sm full-width" color="primary" label="设OVP" @click="doListAction('setListOvp')" unelevated dense />
              </div>
              <div class="col-6 col-sm-3">
                <q-input v-model.number="uiListOcp" :label="`OCP (${currentUnit})`" outlined dense type="number" step="0.001" />
                <q-btn class="q-mt-sm full-width" color="primary" label="设OCP" @click="doListAction('setListOcp')" unelevated dense />
              </div>
              <div class="col-6 col-sm-3">
                <q-input v-model.number="uiListCutoffCurrent" :label="`关断电流 (${currentUnit})`" outlined dense type="number" step="0.001" />
                <q-btn class="q-mt-sm full-width" color="primary" label="设关断电流" @click="doListAction('setListCutoffCurrent')" unelevated dense />
              </div>
              <div class="col-6 col-sm-2">
                <q-input v-model.number="listCutoffTimeValue" label="时间值" outlined dense type="number" />
              </div>
              <div class="col-6 col-sm-2">
                <q-select v-model="listCutoffTimeUnit" :options="[{label:'秒',value:0},{label:'分',value:1},{label:'时',value:2}]" label="单位" outlined dense emit-value map-options />
              </div>
              <div class="col-12 col-sm-2">
                <q-btn class="full-width" color="primary" label="设关断时间" @click="applyListCutoffTime" unelevated dense />
              </div>
            </div>
          </q-expansion-item>

          <q-separator class="q-my-sm" />

          <!-- PWM -->
          <q-expansion-item icon="waves" label="PWM 输出" dense-toggle>
            <div class="row q-col-gutter-md items-end q-mt-xs">
              <div class="col-6 col-sm-3">
                <q-input v-model.number="uiPwmVoltage" :label="`PWM 电压 (${voltageUnit})`" outlined dense type="number" step="0.01" />
              </div>
              <div class="col-6 col-sm-3">
                <q-input v-model.number="pwmPeriod" label="周期 (s)" outlined dense type="number" step="0.1" />
              </div>
              <div class="col-6 col-sm-3">
                <q-input v-model.number="pwmDuty" label="占空比 (%)" outlined dense type="number" />
              </div>
              <div class="col-6 col-sm-3 row q-gutter-sm">
                <q-btn color="positive" label="开始 PWM" :loading="loadingPwm" @click="startPwm" dense unelevated />
                <q-btn color="negative" label="停止 PWM" @click="stopPwm" dense unelevated />
              </div>
            </div>
          </q-expansion-item>

          <q-separator class="q-my-sm" />

          <!-- Sequence -->
          <q-expansion-item icon="playlist_play" label="程控序列" dense-toggle>
            <div class="row q-col-gutter-md items-end q-mt-xs">
              <div class="col-6 col-sm-3">
                <q-input v-model.number="uiSeqVoltage" :label="`电压 (${voltageUnit})`" outlined dense type="number" step="0.01" />
              </div>
              <div class="col-6 col-sm-3">
                <q-input v-model.number="uiSeqCurrent" :label="`电流 (${currentUnit})`" outlined dense type="number" step="0.001" />
              </div>
              <div class="col-6 col-sm-2">
                <q-toggle v-model="seqOutput" label="输出开" dense />
              </div>
              <div class="col-6 col-sm-2">
                <q-input v-model.number="seqDuration" label="时长 (ms)" outlined dense type="number" />
              </div>
              <div class="col-12 col-sm-2">
                <q-btn color="primary" label="添加步骤" @click="addSequenceStep" dense unelevated class="full-width" />
              </div>
            </div>
            <q-list dense bordered class="q-mt-sm rounded-borders">
              <q-item v-for="(step, idx) in sequenceSteps" :key="idx">
                <q-item-section>
                  步骤{{ idx + 1 }}: {{ formatVoltage(step.voltage_mv) }} / {{ formatCurrent(step.current_ma) }} / {{ step.output_on ? '开' : '关' }} / {{ step.duration_ms }}ms
                </q-item-section>
                <q-item-section side>
                  <q-btn flat round dense icon="delete" color="negative" @click="sequenceSteps.splice(idx, 1)" />
                </q-item-section>
              </q-item>
            </q-list>
            <div class="row q-col-gutter-sm q-mt-sm items-center">
              <div class="col-auto">
                <q-toggle v-model="seqLoop" label="循环执行" dense />
              </div>
              <div class="col">
                <q-btn color="positive" label="开始程控" :loading="loadingSequence" @click="runSequence" dense unelevated class="full-width" />
              </div>
              <div class="col">
                <q-btn color="negative" label="停止程控" @click="stopSequence" dense unelevated class="full-width" />
              </div>
            </div>
          </q-expansion-item>

          <q-separator class="q-my-sm" />

          <q-expansion-item icon="auto_graph" label="函数程控 / CSV / 电池模拟" dense-toggle>
            <div class="row items-center q-gutter-sm q-mt-xs q-mb-sm">
              <q-btn-toggle
                v-model="programSource"
                :options="programSourceOptions"
                dense
                unelevated
                toggle-color="primary"
                color="white"
                text-color="primary"
              />
              <q-space />
              <div class="text-caption text-grey">{{ programSummary || '先生成预览，再下发执行' }}</div>
            </div>

            <div v-if="programSource === 'waveform'" class="row q-col-gutter-md items-end">
              <div class="col-12 col-sm-4">
                <q-btn-toggle
                  v-model="waveformControlMode"
                  :options="waveformControlModeOptions"
                  dense
                  unelevated
                  toggle-color="primary"
                  color="white"
                  text-color="primary"
                />
              </div>
              <div class="col-6 col-sm-3">
                <q-select v-model="waveformKind" :options="waveformKindOptions" label="波形类型" outlined dense emit-value map-options />
              </div>
              <div class="col-6 col-sm-3" v-if="waveformControlMode === 'voltage'">
                <q-input v-model.number="uiWaveformLowVoltage" :label="`最低电压 (${voltageUnit})`" outlined dense type="number" step="0.01" />
              </div>
              <div class="col-6 col-sm-3" v-if="waveformControlMode === 'voltage'">
                <q-input v-model.number="uiWaveformHighVoltage" :label="`最高电压 (${voltageUnit})`" outlined dense type="number" step="0.01" />
              </div>
              <div class="col-6 col-sm-3" v-if="waveformControlMode === 'voltage'">
                <q-input v-model.number="uiWaveformCurrent" :label="`限流 (${currentUnit})`" outlined dense type="number" step="0.001" />
              </div>
              <div class="col-6 col-sm-3" v-if="waveformControlMode === 'current'">
                <q-input v-model.number="uiWaveformLowCurrent" :label="`最低电流 (${currentUnit})`" outlined dense type="number" step="0.001" />
              </div>
              <div class="col-6 col-sm-3" v-if="waveformControlMode === 'current'">
                <q-input v-model.number="uiWaveformHighCurrent" :label="`最高电流 (${currentUnit})`" outlined dense type="number" step="0.001" />
              </div>
              <div class="col-6 col-sm-3" v-if="waveformControlMode === 'current'">
                <q-input v-model.number="uiWaveformVoltage" :label="`电压上限 (${voltageUnit})`" outlined dense type="number" step="0.01" />
              </div>
              <div class="col-6 col-sm-3">
                <q-input v-model.number="waveformPeriodMs" label="周期 (ms)" outlined dense type="number" step="10" />
              </div>
              <div class="col-6 col-sm-3">
                <q-input v-model.number="waveformDurationMs" label="总时长 (ms)" outlined dense type="number" step="10" />
              </div>
              <div class="col-6 col-sm-3">
                <q-input v-model.number="waveformSampleIntervalMs" label="程控计算间隔 (ms)" outlined dense type="number" :min="1" step="1" />
              </div>
              <div class="col-6 col-sm-3 text-caption text-grey">
                约 {{ formatHzText(waveformSampleIntervalMs) }}
              </div>
              <div class="col-6 col-sm-3" v-if="waveformKind === 'square'">
                <q-input v-model.number="waveformDutyCycle" label="占空比 (%)" outlined dense type="number" step="1" />
              </div>
              <div class="col-6 col-sm-3" v-if="waveformKind === 'staircase'">
                <q-input v-model.number="waveformStaircaseSteps" label="阶梯数" outlined dense type="number" step="1" />
              </div>
              <div class="col-6 col-sm-2">
                <q-toggle v-model="waveformOutputOn" label="输出打开" dense />
              </div>
              <div class="col-6 col-sm-2">
                <q-toggle v-model="waveformLoop" label="循环执行" dense />
              </div>
              <div class="col-12 col-sm-4 row q-gutter-sm">
                <q-btn color="primary" label="预览波形" @click="previewWaveformProgram" dense unelevated />
                <q-btn color="positive" label="启动波形" :loading="loadingProgram" @click="startWaveformProgram" dense unelevated />
                <q-btn color="negative" label="停止波形" @click="stopActiveProgram" dense unelevated />
              </div>
            </div>

            <div v-else-if="programSource === 'csv'" class="row q-col-gutter-md items-end">
              <div class="col-12 col-md-6">
                <q-file v-model="csvFile" accept=".csv,text/csv" label="导入 CSV 曲线" outlined dense clearable />
              </div>
              <div class="col-6 col-sm-3">
                <q-input v-model.number="uiCsvDefaultCurrent" :label="`默认限流 (${currentUnit})`" outlined dense type="number" step="0.001" />
              </div>
              <div class="col-6 col-sm-3">
                <q-input v-model.number="csvDefaultLastDurationMs" label="末尾默认时长 (ms)" outlined dense type="number" step="10" />
              </div>
              <div class="col-6 col-sm-2">
                <q-toggle v-model="csvDefaultOutputOn" label="默认输出开" dense />
              </div>
              <div class="col-6 col-sm-2">
                <q-toggle v-model="csvLoop" label="循环执行" dense />
              </div>
              <div class="col-12 col-sm-8 row q-gutter-sm">
                <q-btn color="primary" label="解析并预览" @click="previewCsvProgram" dense unelevated />
                <q-btn color="positive" label="启动 CSV 曲线" :loading="loadingProgram" @click="startCsvProgram" dense unelevated />
                <q-btn color="negative" label="停止 CSV 曲线" @click="stopActiveProgram" dense unelevated />
              </div>
              <div class="col-12 text-caption text-grey">
                支持列: voltage_mv 或 voltage_v, current_ma 或 current_a, output_on, duration_ms 或 time_ms。
              </div>
              <div class="col-12">
                <q-banner dense rounded class="bg-grey-1 text-grey-9">
                  <div class="text-caption text-weight-medium">程控电流 CSV 示例</div>
                  <div class="text-caption">time_ms,voltage_v,current_a,output_on</div>
                  <div class="text-caption">0,12.0,0.20,true</div>
                  <div class="text-caption">500,12.0,0.80,true</div>
                  <div class="text-caption">1000,12.0,1.50,true</div>
                  <div class="text-caption">这种写法表示电压上限固定 12V，按时间去扫电流。</div>
                </q-banner>
              </div>
              <div class="col-12" v-if="csvWarnings.length > 0">
                <q-banner dense rounded class="bg-orange-1 text-orange-10">
                  {{ csvWarnings.join('；') }}
                </q-banner>
              </div>
            </div>

            <div v-else class="row q-col-gutter-md items-end">
              <div class="col-12">
                <q-banner dense rounded class="bg-blue-1 text-blue-10">
                  标有“仅预览”的参数不会下发到电源，只用于下面这张仿真预览图。未标记的参数才会参与真实电池模拟控制。额外抖动默认建议填 0，只有想模拟接触不良、保护板抖动或很差的供电状态时再加。
                </q-banner>
              </div>
              <div class="col-12 text-caption text-weight-medium text-primary q-mt-xs">
                实际运行生效
              </div>
              <div class="col-12 col-sm-4">
                <q-select v-model="batteryPresetKey" :options="batteryPresetOptions" label="电池预设" outlined dense emit-value map-options>
                  <template v-slot:option="scope">
                    <q-item v-if="scope.opt.groupLabel" dense>
                      <q-item-section>
                        <q-item-label class="text-caption text-weight-bold text-grey-7">{{ scope.opt.groupLabel }}</q-item-label>
                      </q-item-section>
                    </q-item>
                    <q-item v-else v-bind="scope.itemProps" dense>
                      <q-item-section>
                        <q-item-label>{{ scope.opt.label }}</q-item-label>
                      </q-item-section>
                    </q-item>
                  </template>
                </q-select>
              </div>
              <div class="col-6 col-sm-2">
                <q-input v-model.number="uiBatteryOpenCircuitVoltage" :label="`开路电压 (${voltageUnit})`" outlined dense type="number" step="0.01" />
              </div>
              <div class="col-6 col-sm-2">
                <q-input v-model.number="uiBatteryMinVoltage" :label="`最低电压 (${voltageUnit})`" outlined dense type="number" step="0.01" />
              </div>
              <div class="col-6 col-sm-2">
                <q-input v-model.number="uiBatteryCurrentLimit" :label="`限流 (${currentUnit})`" outlined dense type="number" step="0.001" />
              </div>
              <div class="col-6 col-sm-2">
                <q-input v-model.number="batteryInternalResistanceMohm" label="内阻 (mΩ)" outlined dense type="number" step="1" />
              </div>
              <div class="col-6 col-sm-2">
                <q-input
                  v-model.number="batterySampleIntervalMs"
                  label="控制刷新间隔 (ms)"
                  :hint="`后端每隔多久按实时电流重算一次模拟上限并下发目标电压，当前约 ${formatHzText(batterySampleIntervalMs)}`"
                  outlined
                  dense
                  type="number"
                  :min="5"
                  step="1"
                />
              </div>
              <div class="col-6 col-sm-2">
                <q-input v-model.number="batteryRecoveryMs" label="恢复时间 (ms)" outlined dense type="number" step="10" />
              </div>
              <div class="col-6 col-sm-2">
                <q-input v-model.number="batteryRippleMv" label="额外抖动 (mV, 默认0)" outlined dense type="number" step="1" />
              </div>
              <div class="col-6 col-sm-2">
                <q-input v-model.number="batteryTransientSagMv" label="瞬态塌陷 (mV)" outlined dense type="number" step="1" />
              </div>
              <div class="col-6 col-sm-3">
                <q-input v-model.number="batteryRunDurationMs" label="运行时长 (ms, 0=持续)" outlined dense type="number" step="100" />
              </div>
              <div class="col-12 text-caption text-weight-medium text-deep-orange q-mt-xs">
                仅预览生效
              </div>
              <div class="col-6 col-sm-3">
                <q-input v-model.number="batteryPreviewDurationMs" label="仅预览: 时长 (ms)" outlined dense type="number" step="100" />
              </div>
              <div class="col-6 col-sm-3">
                <q-input v-model.number="uiBatteryPreviewLoadBase" :label="`仅预览: 基载 (${currentUnit})`" outlined dense type="number" step="0.001" />
              </div>
              <div class="col-6 col-sm-3">
                <q-input v-model.number="uiBatteryPreviewLoadSwing" :label="`仅预览: 脉冲负载 (${currentUnit})`" outlined dense type="number" step="0.001" />
              </div>
              <div class="col-6 col-sm-3">
                <q-input v-model.number="batteryPreviewLoadPeriodMs" label="仅预览: 负载周期 (ms)" outlined dense type="number" step="10" />
              </div>
              <div class="col-12 col-sm-6 row q-gutter-sm">
                <q-btn color="primary" label="预览电池曲线" @click="previewBatteryProgram" dense unelevated />
                <q-btn color="positive" label="启动电池模拟" :loading="loadingBattery" @click="startBatteryProgram" dense unelevated />
                <q-btn color="negative" label="停止电池模拟" @click="stopBatteryProgram" dense unelevated />
              </div>
            </div>

            <q-card flat bordered class="q-mt-md">
              <q-card-section class="row items-center justify-between q-pb-sm">
                <div class="text-subtitle2">{{ programPreviewTitle }}</div>
                <div class="text-caption text-grey">{{ programSummary || '未生成预览' }}</div>
              </q-card-section>
              <q-separator />
              <q-card-section v-if="programPreviewPoints.length > 0">
                <program-preview-chart :points="programPreviewPoints" />
              </q-card-section>
              <q-card-section v-else class="text-grey text-caption">
                这里会显示函数波形、CSV 预设曲线，或者弱电池模拟曲线的预览。
              </q-card-section>
            </q-card>
          </q-expansion-item>
        </q-card-section>
      </q-card>

      <!-- Raw Debug -->
      <q-card>
        <q-card-section>
          <div class="text-subtitle1 q-mb-sm">原始数据</div>
          <q-input
            :model-value="store.status?.raw || ''"
            label="RAW HEX"
            outlined
            dense
            readonly
            :hint="store.status ? `更新时间: ${new Date().toLocaleTimeString()}` : '等待数据...'"
          />
        </q-card-section>
      </q-card>
    </div>
  </q-page>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, computed, type Ref } from 'vue';
import { useQuasar } from 'quasar';
import { usePowerStore } from 'src/stores/powerStore';
import ProgramPreviewChart from 'src/components/ProgramPreviewChart.vue';
import RealtimeChart from 'src/components/RealtimeChart.vue';
import {
  batteryPresets,
  buildBatteryPreview,
  buildWaveformProgram,
  parseCsvProgram,
  type BatterySimulationConfig,
  type PreviewPoint,
  type WaveformControlMode,
  type WaveformKind,
} from 'src/utils/programs';

const $q = useQuasar();
const store = usePowerStore();

const loadingVoltage = ref(false);
const loadingCurrent = ref(false);
const loadingOutput = ref(false);
const loadingOvp = ref(false);
const loadingOcp = ref(false);
const loadingOpp = ref(false);
const loadingOtp = ref(false);
const loadingDelay = ref(false);
const loadingRev = ref(false);
const loadingList = ref(false);
const loadingPwm = ref(false);
const loadingSequence = ref(false);

// Internal values are always mV / mA
const targetVoltage = ref(5000);
const targetCurrent = ref(1000);
const targetOvp = ref(30500);
const targetOcp = ref(10500);
const targetOpp = ref(310);
const targetOtp = ref(100);
const targetDelay = ref(0);
const targetRev = ref(0);

const listIndex = ref(0);
const listVoltage = ref(5000);
const listCurrent = ref(1000);
const listOvp = ref(30500);
const listOcp = ref(10500);
const listCutoffCurrent = ref(1000);
const listCutoffTimeValue = ref(0);
const listCutoffTimeUnit = ref<0 | 1 | 2>(0);

// PWM (period in seconds, sent as frequency = 1/period)
const pwmVoltage = ref(5000);
const pwmPeriod = ref(1);
const pwmDuty = ref(50);

// Sequence
const seqVoltage = ref(5000);
const seqCurrent = ref(1000);
const seqOutput = ref(true);
const seqDuration = ref(1000);
const seqLoop = ref(false);
const sequenceSteps = ref<{ voltage_mv: number; current_ma: number; output_on: boolean; duration_ms: number }[]>([]);

// Display units
const voltageUnit = ref<'mV' | 'V'>('V');
const currentUnit = ref<'mA' | 'A'>('A');

const voltageYMinAuto = ref(false);
const voltageYMinTrackTarget = ref(false);
const voltageYMinManual = ref(0);
const voltageYMaxAuto = ref(true);
const voltageYMaxManual = ref(35);

const currentYMinAuto = ref(false);
const currentYMinTrackTarget = ref(false);
const currentYMinManual = ref(0);
const currentYMaxAuto = ref(true);
const currentYMaxManual = ref(5);

const powerYMinAuto = ref(false);
const powerYMinTrackTarget = ref(false);
const powerYMinManual = ref(0);
const powerYMaxAuto = ref(true);
const powerYMaxManual = ref(50);
const targetPower = ref(10);

const pollInterval = ref(50);
const timeWindowSeconds = ref(0);
const curveInterpolationMode = ref<'linear' | 'smooth' | 'step-start' | 'step-end' | 'step-middle'>('smooth');

type ProgramSource = 'waveform' | 'csv' | 'battery';

const programSource = ref<ProgramSource>('waveform');
const loadingProgram = ref(false);
const loadingBattery = ref(false);
const programPreviewPoints = ref<PreviewPoint[]>([]);
const programPreviewTitle = ref('预览尚未生成');
const programSummary = ref('');

const waveformControlMode = ref<WaveformControlMode>('voltage');
const waveformKind = ref<WaveformKind>('sine');
const waveformLowVoltage = ref(3000);
const waveformHighVoltage = ref(12000);
const waveformCurrent = ref(1000);
const waveformLowCurrent = ref(500);
const waveformHighCurrent = ref(3000);
const waveformVoltage = ref(12000);
const waveformPeriodMs = ref(2500);
const waveformDurationMs = ref(15000);
const waveformSampleIntervalMs = ref(100);
const waveformDutyCycle = ref(50);
const waveformStaircaseSteps = ref(8);
const waveformOutputOn = ref(true);
const waveformLoop = ref(false);

const csvFile = ref<File | null>(null);
const csvDefaultCurrent = ref(1000);
const csvDefaultLastDurationMs = ref(200);
const csvDefaultOutputOn = ref(true);
const csvLoop = ref(false);
const csvWarnings = ref<string[]>([]);
const parsedCsvSteps = ref<{ voltage_mv: number; current_ma: number; output_on: boolean; duration_ms: number }[] | null>(null);

const batteryPresetKey = ref(batteryPresets[0]?.key ?? '');
const batteryOpenCircuitVoltage = ref(3650);
const batteryMinVoltage = ref(3000);
const batteryCurrentLimit = ref(2500);
const batteryInternalResistanceMohm = ref(260);
const batterySampleIntervalMs = ref(100);
const batteryRecoveryMs = ref(650);
const batteryRippleMv = ref(25);
const batteryTransientSagMv = ref(180);
const batteryPreviewDurationMs = ref(15000);
const batteryPreviewLoadBase = ref(300);
const batteryPreviewLoadSwing = ref(1400);
const batteryPreviewLoadPeriodMs = ref(1800);
const batteryRunDurationMs = ref(0);

// Unit helpers
function makeVoltageRef(internal: Ref<number>) {
  return computed({
    get: () => (voltageUnit.value === 'V' ? internal.value / 1000 : internal.value),
    set: (v: number) => {
      internal.value = voltageUnit.value === 'V' ? Math.round(v * 1000) : Math.round(v);
    },
  });
}
function makeCurrentRef(internal: Ref<number>) {
  return computed({
    get: () => (currentUnit.value === 'A' ? internal.value / 1000 : internal.value),
    set: (v: number) => {
      internal.value = currentUnit.value === 'A' ? Math.round(v * 1000) : Math.round(v);
    },
  });
}

const uiTargetVoltage = makeVoltageRef(targetVoltage);
const uiTargetOvp = makeVoltageRef(targetOvp);
const uiListVoltage = makeVoltageRef(listVoltage);
const uiListOvp = makeVoltageRef(listOvp);
const uiPwmVoltage = makeVoltageRef(pwmVoltage);
const uiSeqVoltage = makeVoltageRef(seqVoltage);
const uiWaveformLowVoltage = makeVoltageRef(waveformLowVoltage);
const uiWaveformHighVoltage = makeVoltageRef(waveformHighVoltage);
const uiWaveformVoltage = makeVoltageRef(waveformVoltage);
const uiBatteryOpenCircuitVoltage = makeVoltageRef(batteryOpenCircuitVoltage);
const uiBatteryMinVoltage = makeVoltageRef(batteryMinVoltage);

const uiTargetCurrent = makeCurrentRef(targetCurrent);
const uiTargetOcp = makeCurrentRef(targetOcp);
const uiListCurrent = makeCurrentRef(listCurrent);
const uiListOcp = makeCurrentRef(listOcp);
const uiListCutoffCurrent = makeCurrentRef(listCutoffCurrent);
const uiSeqCurrent = makeCurrentRef(seqCurrent);
const uiWaveformCurrent = makeCurrentRef(waveformCurrent);
const uiWaveformLowCurrent = makeCurrentRef(waveformLowCurrent);
const uiWaveformHighCurrent = makeCurrentRef(waveformHighCurrent);
const uiCsvDefaultCurrent = makeCurrentRef(csvDefaultCurrent);
const uiBatteryCurrentLimit = makeCurrentRef(batteryCurrentLimit);
const uiBatteryPreviewLoadBase = makeCurrentRef(batteryPreviewLoadBase);
const uiBatteryPreviewLoadSwing = makeCurrentRef(batteryPreviewLoadSwing);

function formatVoltage(mv: number) {
  return voltageUnit.value === 'V' ? `${(mv / 1000).toFixed(2)}V` : `${mv}mV`;
}
function formatCurrent(ma: number) {
  return currentUnit.value === 'A' ? `${(ma / 1000).toFixed(3)}A` : `${ma}mA`;
}

function formatHzText(intervalMs: number) {
  if (!Number.isFinite(intervalMs) || intervalMs <= 0) {
    return '-- Hz';
  }
  const hz = 1000 / intervalMs;
  return hz >= 100 ? `${hz.toFixed(0)} Hz` : `${hz.toFixed(1)} Hz`;
}

function getLoadResistanceText(voltage?: number, current?: number) {
  if (voltage === undefined || current === undefined || current <= 0.000001) {
    return '--';
  }
  const resistance = voltage / current;
  if (!Number.isFinite(resistance)) {
    return '--';
  }
  if (resistance >= 1000) {
    return `${(resistance / 1000).toFixed(2)} kΩ`;
  }
  return `${resistance.toFixed(2)} Ω`;
}

const statusItems = computed(() => [
  { label: '输出电压', value: `${fmt(store.status?.voltage_v)} V`, colorClass: 'text-primary' },
  { label: '输出电流', value: `${fmt(store.status?.current_a)} A`, colorClass: 'text-orange' },
  { label: '输出功率', value: `${fmt(store.status?.power_w)} W`, colorClass: 'text-positive' },
  { label: '负载电阻', value: getLoadResistanceText(store.status?.voltage_v, store.status?.current_a), colorClass: '' },
  { label: '输入电压', value: `${fmt(store.status?.input_voltage_v)} V`, colorClass: '' },
  { label: '温度', value: `${fmt(store.status?.temperature_c)} ℃`, colorClass: '' },
  { label: '模式', value: store.status?.mode ?? '--', colorClass: '' },
  { label: '输出状态', value: store.status?.output_on ? '开启' : '关闭', colorClass: store.status?.output_on ? 'text-positive' : 'text-grey' },
  { label: '校验', value: store.status?.checksum_ok === false ? '失败' : '正常', colorClass: store.status?.checksum_ok === false ? 'text-negative' : 'text-positive' },
]);

const programSourceOptions = [
  { label: '函数波形', value: 'waveform' },
  { label: 'CSV 曲线', value: 'csv' },
  { label: '弱电池', value: 'battery' },
];

const waveformKindOptions = [
  { label: '正弦 Sin', value: 'sine' },
  { label: '呼吸灯', value: 'breathing' },
  { label: '三角波', value: 'triangle' },
  { label: '锯齿波', value: 'sawtooth' },
  { label: '方波', value: 'square' },
  { label: '阶梯波', value: 'staircase' },
];

const waveformControlModeOptions = [
  { label: '程控电压', value: 'voltage' },
  { label: '程控电流', value: 'current' },
];

const curveInterpolationOptions = [
  { label: '直线', value: 'linear' },
  { label: '平滑', value: 'smooth' },
  { label: '阶梯-前沿', value: 'step-start' },
  { label: '阶梯-后沿', value: 'step-end' },
  { label: '阶梯-居中', value: 'step-middle' },
];

const batteryPresetOptions = computed(() =>
  [
    { groupLabel: '健康状态', label: '健康状态', value: '__group_healthy', disable: true },
    ...batteryPresets
      .filter((preset) => preset.category === 'healthy')
      .map((preset) => ({ label: preset.label, value: preset.key })),
    { groupLabel: '老化状态', label: '老化状态', value: '__group_aged', disable: true },
    ...batteryPresets
      .filter((preset) => preset.category === 'aged')
      .map((preset) => ({ label: preset.label, value: preset.key })),
    { groupLabel: '极差 / 特殊状态', label: '极差 / 特殊状态', value: '__group_weak', disable: true },
    ...batteryPresets
      .filter((preset) => preset.category === 'weak')
      .map((preset) => ({ label: preset.label, value: preset.key })),
  ],
);

const LS_KEYS = {
  voltage: 'ax_pp300_targetVoltage',
  current: 'ax_pp300_targetCurrent',
  ovp: 'ax_pp300_targetOvp',
  ocp: 'ax_pp300_targetOcp',
  opp: 'ax_pp300_targetOpp',
  otp: 'ax_pp300_targetOtp',
  delay: 'ax_pp300_targetDelay',
  rev: 'ax_pp300_targetRev',
  listIndex: 'ax_pp300_listIndex',
  listVoltage: 'ax_pp300_listVoltage',
  listCurrent: 'ax_pp300_listCurrent',
  listOvp: 'ax_pp300_listOvp',
  listOcp: 'ax_pp300_listOcp',
  listCutoffCurrent: 'ax_pp300_listCutoffCurrent',
  listCutoffTimeValue: 'ax_pp300_listCutoffTimeValue',
  listCutoffTimeUnit: 'ax_pp300_listCutoffTimeUnit',
  voltageYMinAuto: 'ax_pp300_voltageYMinAuto',
  voltageYMinTrackTarget: 'ax_pp300_voltageYMinTrackTarget',
  voltageYMinManual: 'ax_pp300_voltageYMinManual',
  voltageYMaxAuto: 'ax_pp300_voltageYMaxAuto',
  voltageYMaxManual: 'ax_pp300_voltageYMaxManual',
  currentYMinAuto: 'ax_pp300_currentYMinAuto',
  currentYMinTrackTarget: 'ax_pp300_currentYMinTrackTarget',
  currentYMinManual: 'ax_pp300_currentYMinManual',
  currentYMaxAuto: 'ax_pp300_currentYMaxAuto',
  currentYMaxManual: 'ax_pp300_currentYMaxManual',
  powerYMinAuto: 'ax_pp300_powerYMinAuto',
  powerYMinTrackTarget: 'ax_pp300_powerYMinTrackTarget',
  powerYMinManual: 'ax_pp300_powerYMinManual',
  powerYMaxAuto: 'ax_pp300_powerYMaxAuto',
  powerYMaxManual: 'ax_pp300_powerYMaxManual',
  targetPower: 'ax_pp300_targetPower',
  pollInterval: 'ax_pp300_pollInterval',
  timeWindowSeconds: 'ax_pp300_timeWindowSeconds',
  curveInterpolationMode: 'ax_pp300_curveInterpolationMode',
  voltageUnit: 'ax_pp300_voltageUnit',
  currentUnit: 'ax_pp300_currentUnit',
  waveformControlMode: 'ax_pp300_waveformControlMode',
  waveformKind: 'ax_pp300_waveformKind',
  waveformLowVoltage: 'ax_pp300_waveformLowVoltage',
  waveformHighVoltage: 'ax_pp300_waveformHighVoltage',
  waveformCurrent: 'ax_pp300_waveformCurrent',
  waveformLowCurrent: 'ax_pp300_waveformLowCurrent',
  waveformHighCurrent: 'ax_pp300_waveformHighCurrent',
  waveformVoltage: 'ax_pp300_waveformVoltage',
  waveformPeriodMs: 'ax_pp300_waveformPeriodMs',
  waveformDurationMs: 'ax_pp300_waveformDurationMs',
  waveformSampleIntervalMs: 'ax_pp300_waveformSampleIntervalMs',
  waveformDutyCycle: 'ax_pp300_waveformDutyCycle',
  waveformStaircaseSteps: 'ax_pp300_waveformStaircaseSteps',
  waveformOutputOn: 'ax_pp300_waveformOutputOn',
  waveformLoop: 'ax_pp300_waveformLoop',
  batteryPresetKey: 'ax_pp300_batteryPresetKey',
  batteryOpenCircuitVoltage: 'ax_pp300_batteryOpenCircuitVoltage',
  batteryMinVoltage: 'ax_pp300_batteryMinVoltage',
  batteryCurrentLimit: 'ax_pp300_batteryCurrentLimit',
  batteryInternalResistanceMohm: 'ax_pp300_batteryInternalResistanceMohm',
  batterySampleIntervalMs: 'ax_pp300_batterySampleIntervalMs',
  batteryRecoveryMs: 'ax_pp300_batteryRecoveryMs',
  batteryRippleMv: 'ax_pp300_batteryRippleMv',
  batteryTransientSagMv: 'ax_pp300_batteryTransientSagMv',
  batteryPreviewDurationMs: 'ax_pp300_batteryPreviewDurationMs',
  batteryPreviewLoadBase: 'ax_pp300_batteryPreviewLoadBase',
  batteryPreviewLoadSwing: 'ax_pp300_batteryPreviewLoadSwing',
  batteryPreviewLoadPeriodMs: 'ax_pp300_batteryPreviewLoadPeriodMs',
  batteryRunDurationMs: 'ax_pp300_batteryRunDurationMs',
} as const;

function loadInt(key: string, fallback: number) {
  const v = localStorage.getItem(key);
  return v ? parseInt(v, 10) : fallback;
}

function loadBool(key: string, fallback: boolean) {
  const v = localStorage.getItem(key);
  return v ? v === 'true' : fallback;
}

function loadFloat(key: string, fallback: number) {
  const v = localStorage.getItem(key);
  return v ? parseFloat(v) : fallback;
}

function loadSettings() {
  targetVoltage.value = loadInt(LS_KEYS.voltage, 5000);
  targetCurrent.value = loadInt(LS_KEYS.current, 1000);
  targetOvp.value = loadInt(LS_KEYS.ovp, 30500);
  targetOcp.value = loadInt(LS_KEYS.ocp, 10500);
  targetOpp.value = loadInt(LS_KEYS.opp, 310);
  targetOtp.value = loadInt(LS_KEYS.otp, 100);
  targetDelay.value = loadInt(LS_KEYS.delay, 0);
  targetRev.value = loadInt(LS_KEYS.rev, 0);
  listIndex.value = loadInt(LS_KEYS.listIndex, 0);
  listVoltage.value = loadInt(LS_KEYS.listVoltage, 5000);
  listCurrent.value = loadInt(LS_KEYS.listCurrent, 1000);
  listOvp.value = loadInt(LS_KEYS.listOvp, 30500);
  listOcp.value = loadInt(LS_KEYS.ocp, 10500);
  listCutoffCurrent.value = loadInt(LS_KEYS.listCutoffCurrent, 1000);
  listCutoffTimeValue.value = loadInt(LS_KEYS.listCutoffTimeValue, 0);
  listCutoffTimeUnit.value = loadInt(LS_KEYS.listCutoffTimeUnit, 0) as 0 | 1 | 2;
  voltageYMinAuto.value = loadBool(LS_KEYS.voltageYMinAuto, false);
  voltageYMinTrackTarget.value = loadBool(LS_KEYS.voltageYMinTrackTarget, false);
  voltageYMinManual.value = loadFloat(LS_KEYS.voltageYMinManual, 0);
  voltageYMaxAuto.value = loadBool(LS_KEYS.voltageYMaxAuto, true);
  voltageYMaxManual.value = loadFloat(LS_KEYS.voltageYMaxManual, 35);

  currentYMinAuto.value = loadBool(LS_KEYS.currentYMinAuto, false);
  currentYMinTrackTarget.value = loadBool(LS_KEYS.currentYMinTrackTarget, false);
  currentYMinManual.value = loadFloat(LS_KEYS.currentYMinManual, 0);
  currentYMaxAuto.value = loadBool(LS_KEYS.currentYMaxAuto, true);
  currentYMaxManual.value = loadFloat(LS_KEYS.currentYMaxManual, 5);

  powerYMinAuto.value = loadBool(LS_KEYS.powerYMinAuto, false);
  powerYMinTrackTarget.value = loadBool(LS_KEYS.powerYMinTrackTarget, false);
  powerYMinManual.value = loadFloat(LS_KEYS.powerYMinManual, 0);
  powerYMaxAuto.value = loadBool(LS_KEYS.powerYMaxAuto, true);
  powerYMaxManual.value = loadFloat(LS_KEYS.powerYMaxManual, 50);
  targetPower.value = loadFloat(LS_KEYS.targetPower, 10);
  pollInterval.value = loadInt(LS_KEYS.pollInterval, 50);
  timeWindowSeconds.value = loadInt(LS_KEYS.timeWindowSeconds, 0);
  curveInterpolationMode.value = (localStorage.getItem(LS_KEYS.curveInterpolationMode) as typeof curveInterpolationMode.value) || 'smooth';

  waveformControlMode.value = (localStorage.getItem(LS_KEYS.waveformControlMode) as typeof waveformControlMode.value) || 'voltage';
  waveformKind.value = (localStorage.getItem(LS_KEYS.waveformKind) as typeof waveformKind.value) || 'sine';
  waveformLowVoltage.value = loadInt(LS_KEYS.waveformLowVoltage, 3000);
  waveformHighVoltage.value = loadInt(LS_KEYS.waveformHighVoltage, 12000);
  waveformCurrent.value = loadInt(LS_KEYS.waveformCurrent, 1000);
  waveformLowCurrent.value = loadInt(LS_KEYS.waveformLowCurrent, 500);
  waveformHighCurrent.value = loadInt(LS_KEYS.waveformHighCurrent, 3000);
  waveformVoltage.value = loadInt(LS_KEYS.waveformVoltage, 12000);
  waveformPeriodMs.value = loadInt(LS_KEYS.waveformPeriodMs, 2500);
  waveformDurationMs.value = loadInt(LS_KEYS.waveformDurationMs, 15000);
  waveformSampleIntervalMs.value = loadInt(LS_KEYS.waveformSampleIntervalMs, 100);
  waveformDutyCycle.value = loadInt(LS_KEYS.waveformDutyCycle, 50);
  waveformStaircaseSteps.value = loadInt(LS_KEYS.waveformStaircaseSteps, 8);
  waveformOutputOn.value = loadBool(LS_KEYS.waveformOutputOn, true);
  waveformLoop.value = loadBool(LS_KEYS.waveformLoop, false);

  batteryPresetKey.value = localStorage.getItem(LS_KEYS.batteryPresetKey) || batteryPresetKey.value;
  batteryOpenCircuitVoltage.value = loadInt(LS_KEYS.batteryOpenCircuitVoltage, 3650);
  batteryMinVoltage.value = loadInt(LS_KEYS.batteryMinVoltage, 3000);
  batteryCurrentLimit.value = loadInt(LS_KEYS.batteryCurrentLimit, 2500);
  batteryInternalResistanceMohm.value = loadInt(LS_KEYS.batteryInternalResistanceMohm, 260);
  batterySampleIntervalMs.value = loadInt(LS_KEYS.batterySampleIntervalMs, 100);
  batteryRecoveryMs.value = loadInt(LS_KEYS.batteryRecoveryMs, 650);
  batteryRippleMv.value = loadInt(LS_KEYS.batteryRippleMv, 0);
  batteryTransientSagMv.value = loadInt(LS_KEYS.batteryTransientSagMv, 180);
  batteryPreviewDurationMs.value = loadInt(LS_KEYS.batteryPreviewDurationMs, 15000);
  batteryPreviewLoadBase.value = loadInt(LS_KEYS.batteryPreviewLoadBase, 300);
  batteryPreviewLoadSwing.value = loadInt(LS_KEYS.batteryPreviewLoadSwing, 1400);
  batteryPreviewLoadPeriodMs.value = loadInt(LS_KEYS.batteryPreviewLoadPeriodMs, 1800);
  batteryRunDurationMs.value = loadInt(LS_KEYS.batteryRunDurationMs, 0);

  if (!localStorage.getItem(LS_KEYS.batteryOpenCircuitVoltage)) {
    applyBatteryPreset(batteryPresetKey.value);
  }

  voltageUnit.value = (localStorage.getItem(LS_KEYS.voltageUnit) as 'V' | 'mV') || 'V';
  currentUnit.value = (localStorage.getItem(LS_KEYS.currentUnit) as 'A' | 'mA') || 'A';
}

watch(targetVoltage, (v) => localStorage.setItem(LS_KEYS.voltage, String(v)));
watch(targetCurrent, (v) => localStorage.setItem(LS_KEYS.current, String(v)));
watch(targetOvp, (v) => localStorage.setItem(LS_KEYS.ovp, String(v)));
watch(targetOcp, (v) => localStorage.setItem(LS_KEYS.ocp, String(v)));
watch(targetOpp, (v) => localStorage.setItem(LS_KEYS.opp, String(v)));
watch(targetOtp, (v) => localStorage.setItem(LS_KEYS.otp, String(v)));
watch(targetDelay, (v) => localStorage.setItem(LS_KEYS.delay, String(v)));
watch(targetRev, (v) => localStorage.setItem(LS_KEYS.rev, String(v)));
watch(listIndex, (v) => localStorage.setItem(LS_KEYS.listIndex, String(v)));
watch(listVoltage, (v) => localStorage.setItem(LS_KEYS.listVoltage, String(v)));
watch(listCurrent, (v) => localStorage.setItem(LS_KEYS.listCurrent, String(v)));
watch(listOvp, (v) => localStorage.setItem(LS_KEYS.listOvp, String(v)));
watch(listOcp, (v) => localStorage.setItem(LS_KEYS.listOcp, String(v)));
watch(listCutoffCurrent, (v) => localStorage.setItem(LS_KEYS.listCutoffCurrent, String(v)));
watch(listCutoffTimeValue, (v) => localStorage.setItem(LS_KEYS.listCutoffTimeValue, String(v)));
watch(listCutoffTimeUnit, (v) => localStorage.setItem(LS_KEYS.listCutoffTimeUnit, String(v)));
watch(voltageYMinAuto, (v) => localStorage.setItem(LS_KEYS.voltageYMinAuto, String(v)));
watch(voltageYMinTrackTarget, (v) => localStorage.setItem(LS_KEYS.voltageYMinTrackTarget, String(v)));
watch(voltageYMinManual, (v) => localStorage.setItem(LS_KEYS.voltageYMinManual, String(v)));
watch(voltageYMaxAuto, (v) => localStorage.setItem(LS_KEYS.voltageYMaxAuto, String(v)));
watch(voltageYMaxManual, (v) => localStorage.setItem(LS_KEYS.voltageYMaxManual, String(v)));

watch(currentYMinAuto, (v) => localStorage.setItem(LS_KEYS.currentYMinAuto, String(v)));
watch(currentYMinTrackTarget, (v) => localStorage.setItem(LS_KEYS.currentYMinTrackTarget, String(v)));
watch(currentYMinManual, (v) => localStorage.setItem(LS_KEYS.currentYMinManual, String(v)));
watch(currentYMaxAuto, (v) => localStorage.setItem(LS_KEYS.currentYMaxAuto, String(v)));
watch(currentYMaxManual, (v) => localStorage.setItem(LS_KEYS.currentYMaxManual, String(v)));

watch(powerYMinAuto, (v) => localStorage.setItem(LS_KEYS.powerYMinAuto, String(v)));
watch(powerYMinTrackTarget, (v) => localStorage.setItem(LS_KEYS.powerYMinTrackTarget, String(v)));
watch(powerYMinManual, (v) => localStorage.setItem(LS_KEYS.powerYMinManual, String(v)));
watch(powerYMaxAuto, (v) => localStorage.setItem(LS_KEYS.powerYMaxAuto, String(v)));
watch(powerYMaxManual, (v) => localStorage.setItem(LS_KEYS.powerYMaxManual, String(v)));
watch(targetPower, (v) => localStorage.setItem(LS_KEYS.targetPower, String(v)));
watch(pollInterval, (v) => localStorage.setItem(LS_KEYS.pollInterval, String(v)));
watch(timeWindowSeconds, (v) => localStorage.setItem(LS_KEYS.timeWindowSeconds, String(v)));
watch(curveInterpolationMode, (v) => localStorage.setItem(LS_KEYS.curveInterpolationMode, v));

watch(waveformControlMode, (v) => localStorage.setItem(LS_KEYS.waveformControlMode, v));
watch(waveformKind, (v) => localStorage.setItem(LS_KEYS.waveformKind, v));
watch(waveformLowVoltage, (v) => localStorage.setItem(LS_KEYS.waveformLowVoltage, String(v)));
watch(waveformHighVoltage, (v) => localStorage.setItem(LS_KEYS.waveformHighVoltage, String(v)));
watch(waveformCurrent, (v) => localStorage.setItem(LS_KEYS.waveformCurrent, String(v)));
watch(waveformLowCurrent, (v) => localStorage.setItem(LS_KEYS.waveformLowCurrent, String(v)));
watch(waveformHighCurrent, (v) => localStorage.setItem(LS_KEYS.waveformHighCurrent, String(v)));
watch(waveformVoltage, (v) => localStorage.setItem(LS_KEYS.waveformVoltage, String(v)));
watch(waveformPeriodMs, (v) => localStorage.setItem(LS_KEYS.waveformPeriodMs, String(v)));
watch(waveformDurationMs, (v) => localStorage.setItem(LS_KEYS.waveformDurationMs, String(v)));
watch(waveformSampleIntervalMs, (v) => localStorage.setItem(LS_KEYS.waveformSampleIntervalMs, String(v)));
watch(waveformDutyCycle, (v) => localStorage.setItem(LS_KEYS.waveformDutyCycle, String(v)));
watch(waveformStaircaseSteps, (v) => localStorage.setItem(LS_KEYS.waveformStaircaseSteps, String(v)));
watch(waveformOutputOn, (v) => localStorage.setItem(LS_KEYS.waveformOutputOn, String(v)));
watch(waveformLoop, (v) => localStorage.setItem(LS_KEYS.waveformLoop, String(v)));

watch(batteryPresetKey, (v) => localStorage.setItem(LS_KEYS.batteryPresetKey, v));
watch(batteryOpenCircuitVoltage, (v) => localStorage.setItem(LS_KEYS.batteryOpenCircuitVoltage, String(v)));
watch(batteryMinVoltage, (v) => localStorage.setItem(LS_KEYS.batteryMinVoltage, String(v)));
watch(batteryCurrentLimit, (v) => localStorage.setItem(LS_KEYS.batteryCurrentLimit, String(v)));
watch(batteryInternalResistanceMohm, (v) => localStorage.setItem(LS_KEYS.batteryInternalResistanceMohm, String(v)));
watch(batterySampleIntervalMs, (v) => localStorage.setItem(LS_KEYS.batterySampleIntervalMs, String(v)));
watch(batteryRecoveryMs, (v) => localStorage.setItem(LS_KEYS.batteryRecoveryMs, String(v)));
watch(batteryRippleMv, (v) => localStorage.setItem(LS_KEYS.batteryRippleMv, String(v)));
watch(batteryTransientSagMv, (v) => localStorage.setItem(LS_KEYS.batteryTransientSagMv, String(v)));
watch(batteryPreviewDurationMs, (v) => localStorage.setItem(LS_KEYS.batteryPreviewDurationMs, String(v)));
watch(batteryPreviewLoadBase, (v) => localStorage.setItem(LS_KEYS.batteryPreviewLoadBase, String(v)));
watch(batteryPreviewLoadSwing, (v) => localStorage.setItem(LS_KEYS.batteryPreviewLoadSwing, String(v)));
watch(batteryPreviewLoadPeriodMs, (v) => localStorage.setItem(LS_KEYS.batteryPreviewLoadPeriodMs, String(v)));
watch(batteryRunDurationMs, (v) => localStorage.setItem(LS_KEYS.batteryRunDurationMs, String(v)));

watch(voltageUnit, (v) => localStorage.setItem(LS_KEYS.voltageUnit, v));
watch(currentUnit, (v) => localStorage.setItem(LS_KEYS.currentUnit, v));

onMounted(() => {
  loadSettings();
});

watch(batteryPresetKey, (key) => {
  applyBatteryPreset(key);
});

function fmt(n?: number) {
  return n !== undefined && n !== null ? n.toFixed(3) : '--.---';
}

function exportCsv() {
  const csv = store.exportCsv();
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `ax_pp300_${new Date().toISOString().replace(/[:.]/g, '-')}.csv`;
  a.click();
  URL.revokeObjectURL(url);
  $q.notify({ type: 'positive', message: 'CSV 已导出' });
}

type StoreAction = 'setVoltage' | 'setCurrent' | 'setOvp' | 'setOcp' | 'setOpp' | 'setOtp' | 'setDelay' | 'setRev';
type ListAction = 'setListVoltage' | 'setListCurrent' | 'setListOvp' | 'setListOcp' | 'setListCutoffCurrent';

const actionMap: Record<StoreAction, { valueRef: Ref<number>; unit: string; loader: Ref<boolean> }> = {
  setVoltage: { valueRef: targetVoltage, unit: 'mV', loader: loadingVoltage },
  setCurrent: { valueRef: targetCurrent, unit: 'mA', loader: loadingCurrent },
  setOvp: { valueRef: targetOvp, unit: 'mV', loader: loadingOvp },
  setOcp: { valueRef: targetOcp, unit: 'mA', loader: loadingOcp },
  setOpp: { valueRef: targetOpp, unit: 'W', loader: loadingOpp },
  setOtp: { valueRef: targetOtp, unit: '°C', loader: loadingOtp },
  setDelay: { valueRef: targetDelay, unit: 's', loader: loadingDelay },
  setRev: { valueRef: targetRev, unit: 's', loader: loadingRev },
};

const listActionMap: Record<ListAction, { valueRef: Ref<number>; unit: string }> = {
  setListVoltage: { valueRef: listVoltage, unit: 'mV' },
  setListCurrent: { valueRef: listCurrent, unit: 'mA' },
  setListOvp: { valueRef: listOvp, unit: 'mV' },
  setListOcp: { valueRef: listOcp, unit: 'mA' },
  setListCutoffCurrent: { valueRef: listCutoffCurrent, unit: 'mA' },
};

async function doAction(action: StoreAction) {
  const cfg = actionMap[action];
  cfg.loader.value = true;
  try {
    await (store[action] as (v: number) => Promise<void>)(cfg.valueRef.value);
    $q.notify({ type: 'positive', message: `已设为 ${cfg.valueRef.value} ${cfg.unit}` });
  } catch (err: unknown) {
    $q.notify({ type: 'negative', message: (err as Error).message || '设置失败' });
  } finally {
    cfg.loader.value = false;
  }
}

async function applyOutput() {
  loadingOutput.value = true;
  try {
    const on = !store.status?.output_on;
    await store.setOutput(on);
    $q.notify({ type: 'positive', message: on ? '输出已打开' : '输出已关闭' });
  } catch (err: unknown) {
    $q.notify({ type: 'negative', message: (err as Error).message || '操作失败' });
  } finally {
    loadingOutput.value = false;
  }
}

async function applyListSelect() {
  loadingList.value = true;
  try {
    await store.setParamList(listIndex.value);
    $q.notify({ type: 'positive', message: `已切换到参数列表 ${listIndex.value}` });
  } catch (err: unknown) {
    $q.notify({ type: 'negative', message: (err as Error).message || '切换失败' });
  } finally {
    loadingList.value = false;
  }
}

async function doListAction(action: ListAction) {
  const cfg = listActionMap[action];
  try {
    await (store[action] as (idx: number, v: number) => Promise<void>)(listIndex.value, cfg.valueRef.value);
    $q.notify({ type: 'positive', message: `列表${listIndex.value} 已设为 ${cfg.valueRef.value} ${cfg.unit}` });
  } catch (err: unknown) {
    $q.notify({ type: 'negative', message: (err as Error).message || '设置失败' });
  }
}

async function applyListCutoffTime() {
  try {
    await store.setListCutoffTime(listIndex.value, listCutoffTimeValue.value, listCutoffTimeUnit.value);
    const unitText = ['秒', '分', '时'][listCutoffTimeUnit.value];
    $q.notify({ type: 'positive', message: `列表${listIndex.value} 关断时间已设为 ${listCutoffTimeValue.value} ${unitText}` });
  } catch (err: unknown) {
    $q.notify({ type: 'negative', message: (err as Error).message || '设置失败' });
  }
}

async function applyPollInterval() {
  let ms = pollInterval.value;
  if (ms < 5) ms = 5;
  if (ms > 5000) ms = 5000;
  pollInterval.value = ms;
  try {
    await store.setPollInterval(ms);
    $q.notify({ type: 'positive', message: `采样率已设为 ${ms}ms (${formatHzText(ms)})` });
  } catch (err: unknown) {
    $q.notify({ type: 'negative', message: (err as Error).message || '设置失败' });
  }
}

async function startPwm() {
  if (pwmPeriod.value <= 0) {
    $q.notify({ type: 'negative', message: '周期必须大于 0' });
    return;
  }
  loadingPwm.value = true;
  try {
    const frequency = 1 / pwmPeriod.value;
    await store.startPwm(pwmVoltage.value, frequency, pwmDuty.value);
    $q.notify({ type: 'positive', message: `PWM 已启动: 周期 ${pwmPeriod.value}s, ${pwmDuty.value}%` });
  } catch (err: unknown) {
    $q.notify({ type: 'negative', message: (err as Error).message || '启动失败' });
  } finally {
    loadingPwm.value = false;
  }
}

async function stopPwm() {
  try {
    await store.stopPwm();
    $q.notify({ type: 'positive', message: 'PWM 已停止' });
  } catch (err: unknown) {
    $q.notify({ type: 'negative', message: (err as Error).message || '停止失败' });
  }
}

function addSequenceStep() {
  sequenceSteps.value.push({
    voltage_mv: seqVoltage.value,
    current_ma: seqCurrent.value,
    output_on: seqOutput.value,
    duration_ms: seqDuration.value,
  });
}

async function runSequence() {
  if (sequenceSteps.value.length === 0) {
    $q.notify({ type: 'warning', message: '请先添加步骤' });
    return;
  }
  loadingSequence.value = true;
  try {
    await store.startSequence([...sequenceSteps.value], seqLoop.value);
    const loopText = seqLoop.value ? ' (循环)' : '';
    $q.notify({ type: 'positive', message: `程控序列已启动，共 ${sequenceSteps.value.length} 步${loopText}` });
  } catch (err: unknown) {
    $q.notify({ type: 'negative', message: (err as Error).message || '启动失败' });
  } finally {
    loadingSequence.value = false;
  }
}

async function stopSequence() {
  try {
    await store.stopSequence();
    $q.notify({ type: 'positive', message: '程控序列已停止' });
  } catch (err: unknown) {
    $q.notify({ type: 'negative', message: (err as Error).message || '停止失败' });
  }
}

async function stopActiveProgram() {
  try {
    await store.stopTask();
    $q.notify({ type: 'positive', message: '模拟/程控任务已停止' });
  } catch (err: unknown) {
    $q.notify({ type: 'negative', message: (err as Error).message || '停止失败' });
  }
}

function setProgramPreview(title: string, points: PreviewPoint[], summary: string) {
  programPreviewTitle.value = title;
  programPreviewPoints.value = points;
  programSummary.value = summary;
}

function applyBatteryPreset(key: string) {
  const preset = batteryPresets.find((item) => item.key === key);
  if (!preset) return;
  batteryOpenCircuitVoltage.value = preset.values.openCircuitVoltageMv ?? batteryOpenCircuitVoltage.value;
  batteryMinVoltage.value = preset.values.minVoltageMv ?? batteryMinVoltage.value;
  batteryCurrentLimit.value = preset.values.currentLimitMa ?? batteryCurrentLimit.value;
  batteryInternalResistanceMohm.value = preset.values.internalResistanceMohm ?? batteryInternalResistanceMohm.value;
  batteryRecoveryMs.value = preset.values.recoveryMs ?? batteryRecoveryMs.value;
  batteryRippleMv.value = preset.values.rippleMv ?? batteryRippleMv.value;
  batteryTransientSagMv.value = preset.values.transientSagMv ?? batteryTransientSagMv.value;
  batteryPreviewLoadBase.value = preset.values.previewLoadBaseMa ?? batteryPreviewLoadBase.value;
  batteryPreviewLoadSwing.value = preset.values.previewLoadSwingMa ?? batteryPreviewLoadSwing.value;
  batteryPreviewLoadPeriodMs.value = preset.values.previewLoadPeriodMs ?? batteryPreviewLoadPeriodMs.value;
}

function previewWaveformProgram() {
  try {
    const result = buildWaveformProgram({
      controlMode: waveformControlMode.value,
      kind: waveformKind.value,
      lowVoltageMv: waveformLowVoltage.value,
      highVoltageMv: waveformHighVoltage.value,
      currentMa: waveformCurrent.value,
      lowCurrentMa: waveformLowCurrent.value,
      highCurrentMa: waveformHighCurrent.value,
      voltageMv: waveformVoltage.value,
      periodMs: waveformPeriodMs.value,
      durationMs: waveformDurationMs.value,
      sampleIntervalMs: waveformSampleIntervalMs.value,
      dutyCycle: waveformDutyCycle.value,
      staircaseSteps: waveformStaircaseSteps.value,
      outputOn: waveformOutputOn.value,
    });
    setProgramPreview(
      '函数波形预览',
      result.preview,
      `${waveformControlMode.value === 'voltage' ? '程控电压' : '程控电流'} / ${waveformKindOptions.find((item) => item.value === waveformKind.value)?.label ?? waveformKind.value}，共 ${result.steps.length} 步`,
    );
  } catch (err: unknown) {
    $q.notify({ type: 'negative', message: (err as Error).message || '预览失败' });
  }
}

async function startWaveformProgram() {
  loadingProgram.value = true;
  try {
    const result = buildWaveformProgram({
      controlMode: waveformControlMode.value,
      kind: waveformKind.value,
      lowVoltageMv: waveformLowVoltage.value,
      highVoltageMv: waveformHighVoltage.value,
      currentMa: waveformCurrent.value,
      lowCurrentMa: waveformLowCurrent.value,
      highCurrentMa: waveformHighCurrent.value,
      voltageMv: waveformVoltage.value,
      periodMs: waveformPeriodMs.value,
      durationMs: waveformDurationMs.value,
      sampleIntervalMs: waveformSampleIntervalMs.value,
      dutyCycle: waveformDutyCycle.value,
      staircaseSteps: waveformStaircaseSteps.value,
      outputOn: waveformOutputOn.value,
    });
    if (result.steps.length > 5000) {
      throw new Error('生成步数过多，请增大采样间隔或缩短总时长');
    }
    setProgramPreview(
      '函数波形预览',
      result.preview,
      `${waveformControlMode.value === 'voltage' ? '程控电压' : '程控电流'}，将下发 ${result.steps.length} 步${waveformLoop.value ? '，循环执行' : ''}`,
    );
    await store.startSequence(result.steps, waveformLoop.value);
    $q.notify({ type: 'positive', message: `函数波形已启动，共 ${result.steps.length} 步` });
  } catch (err: unknown) {
    $q.notify({ type: 'negative', message: (err as Error).message || '启动失败' });
  } finally {
    loadingProgram.value = false;
  }
}

async function parseCsvSelection(showSuccessNotify = false) {
  if (!csvFile.value) {
    throw new Error('请先选择 CSV 文件');
  }
  const text = await csvFile.value.text();
  const result = parseCsvProgram(text, {
    defaultCurrentMa: csvDefaultCurrent.value,
    defaultLastDurationMs: csvDefaultLastDurationMs.value,
    defaultOutputOn: csvDefaultOutputOn.value,
  });
  parsedCsvSteps.value = result.steps;
  csvWarnings.value = result.warnings;
  setProgramPreview('CSV 曲线预览', result.preview, `CSV 已解析，共 ${result.steps.length} 步`);
  if (showSuccessNotify) {
    $q.notify({ type: 'positive', message: `CSV 已解析，共 ${result.steps.length} 步` });
  }
  return result.steps;
}

async function previewCsvProgram() {
  try {
    await parseCsvSelection(true);
  } catch (err: unknown) {
    $q.notify({ type: 'negative', message: (err as Error).message || 'CSV 解析失败' });
  }
}

async function startCsvProgram() {
  loadingProgram.value = true;
  try {
    const steps = parsedCsvSteps.value ?? (await parseCsvSelection(false));
    await store.startSequence(steps, csvLoop.value);
    $q.notify({ type: 'positive', message: `CSV 曲线已启动，共 ${steps.length} 步` });
  } catch (err: unknown) {
    $q.notify({ type: 'negative', message: (err as Error).message || 'CSV 曲线启动失败' });
  } finally {
    loadingProgram.value = false;
  }
}

function getBatteryConfig(): BatterySimulationConfig {
  return {
    openCircuitVoltageMv: batteryOpenCircuitVoltage.value,
    minVoltageMv: batteryMinVoltage.value,
    currentLimitMa: batteryCurrentLimit.value,
    internalResistanceMohm: batteryInternalResistanceMohm.value,
    sampleIntervalMs: batterySampleIntervalMs.value,
    recoveryMs: batteryRecoveryMs.value,
    rippleMv: batteryRippleMv.value,
    transientSagMv: batteryTransientSagMv.value,
    previewDurationMs: batteryPreviewDurationMs.value,
    previewLoadBaseMa: batteryPreviewLoadBase.value,
    previewLoadSwingMa: batteryPreviewLoadSwing.value,
    previewLoadPeriodMs: batteryPreviewLoadPeriodMs.value,
  };
}

function previewBatteryProgram() {
  try {
    const points = buildBatteryPreview(getBatteryConfig());
    setProgramPreview('弱电池模拟预览', points, `${batteryPresetOptions.value.find((item) => item.value === batteryPresetKey.value)?.label ?? '自定义'}，共 ${points.length} 点`);
  } catch (err: unknown) {
    $q.notify({ type: 'negative', message: (err as Error).message || '预览失败' });
  }
}

async function startBatteryProgram() {
  loadingBattery.value = true;
  try {
    const config = getBatteryConfig();
    const points = buildBatteryPreview(config);
    setProgramPreview('弱电池模拟预览', points, `实时按负载调压${batteryRunDurationMs.value > 0 ? `，运行 ${batteryRunDurationMs.value}ms` : '，持续运行'}`);
    await store.startBatterySimulation({
      open_circuit_voltage_mv: config.openCircuitVoltageMv,
      min_voltage_mv: config.minVoltageMv,
      current_limit_ma: config.currentLimitMa,
      internal_resistance_mohm: config.internalResistanceMohm,
      sample_interval_ms: config.sampleIntervalMs,
      recovery_ms: config.recoveryMs,
      ripple_mv: config.rippleMv,
      transient_sag_mv: config.transientSagMv,
      duration_ms: batteryRunDurationMs.value,
    });
    $q.notify({ type: 'positive', message: '弱电池模拟已启动' });
  } catch (err: unknown) {
    $q.notify({ type: 'negative', message: (err as Error).message || '启动失败' });
  } finally {
    loadingBattery.value = false;
  }
}

async function stopBatteryProgram() {
  try {
    await store.stopBatterySimulation();
    $q.notify({ type: 'positive', message: '弱电池模拟已停止' });
  } catch (err: unknown) {
    $q.notify({ type: 'negative', message: (err as Error).message || '停止失败' });
  }
}
</script>
