<template>
  <section class="monitor" aria-labelledby="monitor-title">
    <header class="page-header">
      <h1 id="monitor-title" class="page-title">
        <span aria-hidden="true">📡</span> 环境监测
      </h1>
      <div class="header-actions">
        <button class="btn btn-primary" @click="toggleCapture"
          :aria-label="isCapturing ? '停止摄像头采集' : '开启摄像头采集'">
          <span aria-hidden="true">{{ isCapturing ? '⏹' : '📷' }}</span>
          {{ isCapturing ? '停止采集' : '开启摄像头' }}
        </button>
        <button class="btn btn-ghost" @click="toggleMode"
          :aria-label="`切换至${autoMode ? '手动' : '自动'}识别模式`">
          <span aria-hidden="true">🔄</span>
          {{ autoMode ? '自动模式' : '手动模式' }}
        </button>
      </div>
    </header>

    <div class="monitor-layout">
      <!-- 摄像头画面 -->
      <div class="camera-panel card" aria-label="摄像头实时画面">
        <div class="camera-wrap">
          <video ref="videoEl" class="camera-feed" autoplay muted playsinline
            aria-label="摄像头实时画面"></video>
          <canvas ref="canvasEl" class="camera-canvas" aria-hidden="true"></canvas>

          <!-- 未开启状态 -->
          <div v-if="!isCapturing" class="camera-placeholder" role="img"
            aria-label="摄像头未开启">
            <span class="placeholder-icon" aria-hidden="true">📷</span>
            <p>点击「开启摄像头」开始采集</p>
            <p class="placeholder-hint">系统将调用设备摄像头进行环境识别</p>
          </div>

          <!-- 识别中蒙层 -->
          <div v-if="isDetecting" class="detecting-overlay" aria-hidden="true">
            <span class="detecting-dot"></span>
            <span class="detecting-dot"></span>
            <span class="detecting-dot"></span>
          </div>
        </div>

        <div class="camera-info" role="status" aria-live="polite">
          <span class="info-item">
            <span class="status-dot" :class="isCapturing ? 'active' : 'inactive'"></span>
            {{ isCapturing ? '采集中' : '未开启' }}
          </span>
          <span class="info-item">帧率 <strong>{{ systemStore.fps }} FPS</strong></span>
          <span class="info-item">识别到 <strong>{{ systemStore.lastDetections.length }}</strong> 个目标</span>
          <button class="btn btn-ghost btn-sm" @click="captureSnapshot"
            :disabled="!isCapturing"
            aria-label="截图并发送至后端识别">
            <span aria-hidden="true">🔍</span> 手动识别
          </button>
        </div>
      </div>

      <!-- 识别结果面板 -->
      <aside class="result-panel" aria-labelledby="result-title">
        <h2 id="result-title" class="panel-title">识别结果</h2>

        <div v-if="!systemStore.lastDetections.length" class="empty-state"
          role="status" aria-label="暂无识别结果">
          <span aria-hidden="true">🎯</span>
          <p>暂无识别结果</p>
        </div>

        <ul v-else class="result-list" role="list" aria-label="识别到的环境目标列表">
          <li v-for="d in systemStore.lastDetections" :key="d.id"
            class="result-item"
            :class="`risk-${d.risk}`"
            :aria-label="`检测到${d.label}，距离${d.distance}，风险等级${riskText(d.risk)}`">
            <div class="ri-top">
              <span class="ri-label">{{ d.label }}</span>
              <span class="risk-badge" :class="d.risk">{{ riskText(d.risk) }}</span>
            </div>
            <div class="ri-bottom">
              <span class="ri-meta">距离：{{ d.distance }}</span>
              <span class="ri-meta">置信度：{{ (d.confidence * 100).toFixed(1) }}%</span>
              <span class="ri-meta">{{ d.direction }}</span>
            </div>
            <div class="ri-bar">
              <div class="ri-bar-fill" :style="{ width: (d.confidence * 100) + '%' }"
                :class="d.risk"></div>
            </div>
          </li>
        </ul>

        <!-- 风险汇总 -->
        <div class="risk-summary card" role="region" aria-label="风险汇总">
          <h3 class="summary-title">风险汇总</h3>
          <div class="summary-row">
            <span>当前最高风险</span>
            <span :style="{ color: riskColor(systemStore.riskLevel) }"
              :aria-label="`当前最高风险：${riskText(systemStore.riskLevel)}`">
              {{ riskText(systemStore.riskLevel) }}
            </span>
          </div>
          <div class="summary-row">
            <span>高风险目标数</span>
            <span style="color: var(--accent-red)">
              {{ systemStore.lastDetections.filter(d => d.risk === 'high').length }}
            </span>
          </div>
        </div>
      </aside>
    </div>

    <!-- 日志条 -->
    <section class="log-panel card" aria-labelledby="log-title">
      <h2 id="log-title" class="panel-title">识别日志</h2>
      <ul class="log-list" role="log" aria-live="polite" aria-label="实时识别日志">
        <li v-for="log in logList" :key="log.id" class="log-item">
          <span class="log-time">{{ log.time }}</span>
          <span class="log-msg">{{ log.msg }}</span>
          <span class="risk-badge" :class="log.level">{{ log.level }}</span>
        </li>
        <li v-if="!logList.length" class="log-empty">暂无日志</li>
      </ul>
    </section>
  </section>
</template>

<script setup>
import { ref, onUnmounted } from 'vue'
import { useSystemStore } from '../stores/system.js'
import axios from 'axios'

const systemStore = useSystemStore()
const videoEl = ref(null)
const canvasEl = ref(null)
const isCapturing = ref(false)
const isDetecting = ref(false)
const autoMode = ref(true)
const logList = ref([])
let stream = null
let detectInterval = null

async function toggleCapture() {
  if (isCapturing.value) {
    stopCapture()
  } else {
    await startCapture()
  }
}

async function startCapture() {
  try {
    stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' }, audio: false })
    videoEl.value.srcObject = stream
    isCapturing.value = true
    addLog('摄像头已开启', 'low')
    systemStore.speak('摄像头已开启，开始环境采集')
    if (autoMode.value) startAutoDetect()
  } catch (e) {
    console.error('[Camera]', e.name, e.message)
    const msg = {
      NotAllowedError: '摄像头权限被拒绝，请点击地址栏锁形图标→摄像头→允许，然后刷新页面',
      NotFoundError: '未检测到摄像头设备，请确认摄像头已连接',
      NotReadableError: '摄像头被其他程序占用，请关闭其他使用摄像头的应用',
      OverconstrainedError: '摄像头不支持当前配置，尝试切换后置摄像头',
      SecurityError: '当前页面不允许访问摄像头（需在 localhost 或 HTTPS 下运行）',
    }[e.name] || `摄像头错误：${e.name} - ${e.message}`
    systemStore.showAlert(msg, 'medium')
  }
}

function stopCapture() {
  stopAutoDetect()
  stream?.getTracks().forEach(t => t.stop())
  stream = null
  isCapturing.value = false
  addLog('摄像头已关闭', 'low')
  systemStore.speak('摄像头已关闭')
}

function toggleMode() {
  autoMode.value = !autoMode.value
  if (isCapturing.value) {
    autoMode.value ? startAutoDetect() : stopAutoDetect()
  }
}

function startAutoDetect() {
  detectInterval = setInterval(captureSnapshot, 200)  // ~5 FPS 推理
}

function stopAutoDetect() {
  clearInterval(detectInterval)
  detectInterval = null
}

async function captureSnapshot() {
  if (!videoEl.value || !canvasEl.value || isDetecting.value) return
  const video = videoEl.value
  const canvas = canvasEl.value
  canvas.width = video.videoWidth
  canvas.height = video.videoHeight
  canvas.getContext('2d').drawImage(video, 0, 0)
  const blob = await new Promise(resolve => canvas.toBlob(resolve, 'image/jpeg', 0.8))
  if (!blob) return

  isDetecting.value = true
  try {
    const form = new FormData()
    form.append('file', blob, 'frame.jpg')
    const res = await axios.post('/api/detect', form, { timeout: 3000 })
    const { detections, fps } = res.data
    systemStore.updateDetections(detections, fps)
    if (detections.length) {
      addLog(`检测到 ${detections.length} 个目标`, detections.find(d => d.risk === 'high') ? 'high' : 'low')
    }
  } catch (_) {
    // 后端未启动时静默失败
  } finally {
    isDetecting.value = false
  }
}

function addLog(msg, level = 'low') {
  const now = new Date()
  const time = `${now.getHours().toString().padStart(2,'0')}:${now.getMinutes().toString().padStart(2,'0')}:${now.getSeconds().toString().padStart(2,'0')}`
  logList.value.unshift({ id: Date.now(), time, msg, level })
  if (logList.value.length > 50) logList.value.pop()
}

function riskText(r) {
  return { high: '高风险', medium: '中风险', low: '低风险', none: '安全' }[r] || '未知'
}
function riskColor(r) {
  return { high: 'var(--accent-red)', medium: 'var(--accent-amber)', low: 'var(--accent-green)', none: 'var(--text-muted)' }[r] || 'var(--text-muted)'
}

onUnmounted(() => stopCapture())
</script>

<style scoped>
.monitor { display: flex; flex-direction: column; gap: 28px; }
.page-header {
  display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 14px;
}
.page-title {
  font-size: 1.8rem; font-weight: 900;
  color: var(--text-primary); display: flex; align-items: center; gap: 10px;
}
.header-actions { display: flex; gap: 12px; flex-wrap: wrap; }

.monitor-layout {
  display: grid;
  grid-template-columns: 1fr 340px;
  gap: 24px;
  align-items: start;
}
@media (max-width: 900px) { .monitor-layout { grid-template-columns: 1fr; } }

/* Camera */
.camera-panel { padding: 0; overflow: hidden; }
.camera-wrap {
  position: relative;
  background: #000;
  aspect-ratio: 16/9;
  display: flex; align-items: center; justify-content: center;
}
.camera-feed {
  width: 100%; height: 100%;
  object-fit: cover; display: block;
}
.camera-canvas {
  position: absolute; inset: 0;
  width: 100%; height: 100%;
  pointer-events: none; opacity: 0;
}
.camera-placeholder {
  position: absolute; inset: 0;
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  gap: 12px; color: var(--text-muted);
}
.placeholder-icon { font-size: 4rem; opacity: 0.4; }
.placeholder-hint { font-size: 0.85rem; }
.detecting-overlay {
  position: absolute; top: 12px; right: 12px;
  display: flex; gap: 5px;
}
.detecting-dot {
  width: 8px; height: 8px; border-radius: 50%;
  background: var(--accent-amber);
  animation: blink 1s ease-in-out infinite;
}
.detecting-dot:nth-child(2) { animation-delay: 0.2s; }
.detecting-dot:nth-child(3) { animation-delay: 0.4s; }
@keyframes blink {
  0%, 100% { opacity: 0.2; } 50% { opacity: 1; }
}
.camera-info {
  display: flex; align-items: center; gap: 20px; flex-wrap: wrap;
  padding: 14px 20px;
  background: var(--bg-card);
  border-top: 1px solid var(--border-subtle);
  font-size: 0.9rem; color: var(--text-secondary);
}
.info-item { display: flex; align-items: center; gap: 6px; }
.btn-sm { padding: 8px 16px; font-size: 0.85rem; min-height: 36px; min-width: 80px; margin-left: auto; }

/* Result panel */
.result-panel { display: flex; flex-direction: column; gap: 16px; }
.panel-title {
  font-size: 1rem; font-weight: 700;
  color: var(--text-secondary); text-transform: uppercase;
  letter-spacing: 0.08em; margin-bottom: 4px;
}
.empty-state {
  text-align: center; padding: 40px 20px;
  color: var(--text-muted); font-size: 1rem;
  display: flex; flex-direction: column; align-items: center; gap: 10px;
}
.empty-state span { font-size: 2.5rem; opacity: 0.4; }
.result-list { list-style: none; display: flex; flex-direction: column; gap: 10px; }
.result-item {
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-sm);
  padding: 14px 16px;
  transition: border-color var(--transition);
}
.result-item.risk-high { border-left: 3px solid var(--accent-red); }
.result-item.risk-medium { border-left: 3px solid var(--accent-amber); }
.result-item.risk-low { border-left: 3px solid var(--accent-green); }
.ri-top { display: flex; align-items: center; justify-content: space-between; margin-bottom: 6px; }
.ri-label { font-weight: 700; font-size: 1rem; }
.ri-bottom { display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 8px; }
.ri-meta { font-size: 0.8rem; color: var(--text-muted); }
.ri-bar { height: 4px; background: var(--border-subtle); border-radius: 2px; overflow: hidden; }
.ri-bar-fill { height: 100%; border-radius: 2px; transition: width 0.4s ease; }
.ri-bar-fill.high { background: var(--accent-red); }
.ri-bar-fill.medium { background: var(--accent-amber); }
.ri-bar-fill.low { background: var(--accent-green); }

.risk-summary { padding: 16px; margin-top: 4px; }
.summary-title { font-size: 0.85rem; color: var(--text-muted); margin-bottom: 12px; text-transform: uppercase; letter-spacing: 0.06em; }
.summary-row { display: flex; justify-content: space-between; font-size: 0.95rem; padding: 6px 0; border-bottom: 1px solid var(--border-subtle); }
.summary-row:last-child { border-bottom: none; }

/* Log */
.log-panel { max-height: 220px; overflow: hidden; }
.log-list { overflow-y: auto; max-height: 160px; display: flex; flex-direction: column; gap: 6px; list-style: none; }
.log-item { display: flex; align-items: center; gap: 12px; font-size: 0.85rem; }
.log-time { color: var(--text-muted); font-family: monospace; flex-shrink: 0; }
.log-msg { flex: 1; color: var(--text-secondary); }
.log-empty { color: var(--text-muted); font-size: 0.85rem; }
</style>
