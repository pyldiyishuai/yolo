<template>
  <section class="home" aria-labelledby="home-title">
    <!-- Hero -->
    <div class="hero fade-in-up">
      <div class="hero-bg" aria-hidden="true">
        <div class="hero-ring ring1"></div>
        <div class="hero-ring ring2"></div>
        <div class="hero-ring ring3"></div>
      </div>
      <div class="hero-content">
        <h1 id="home-title" class="hero-title">
          <span class="title-main">视助系统</span>
          <span class="title-sub">基于改进 YOLO 的视障环境感知平台</span>
        </h1>
        <p class="hero-desc">
          实时识别盲道、障碍物、行人与车辆，语音播报风险预警，守护每一步安全出行。
        </p>

        <!-- 核心操作按钮 -->
        <div class="hero-actions" role="group" aria-label="核心操作">
          <button
            v-if="!systemStore.isRunning"
            class="btn btn-primary btn-lg"
            @click="handleStart()"
            :disabled="systemStore.isLoading"
            aria-label="启动视觉感知系统"
          >
            <span aria-hidden="true">{{ systemStore.isLoading ? '⏳' : '▶' }}</span>
            {{ systemStore.isLoading ? '启动中...' : '启动系统' }}
          </button>
          <button
            v-else
            class="btn btn-ghost btn-lg"
            @click="systemStore.stopSystem()"
            aria-label="关闭视觉感知系统"
          >
            <span aria-hidden="true">⏹</span> 关闭系统
          </button>

          <router-link to="/monitor" class="btn btn-ghost btn-lg" aria-label="进入环境监测页面">
            <span aria-hidden="true">📷</span> 进入监测
          </router-link>

          <router-link to="/emergency" class="btn btn-danger btn-lg" aria-label="应急求助">
            <span aria-hidden="true">🆘</span> 应急求助
          </router-link>
        </div>

        <!-- 语音控制提示 -->
        <p class="voice-hint" aria-label="语音控制说明">
          <span aria-hidden="true">🎤</span>
          说 <strong>「小视 启动」</strong> 或 <strong>「小视 求助」</strong> 等指令控制系统
        </p>
      </div>
    </div>

    <!-- 状态面板 -->
    <div class="status-grid fade-in-up" role="region" aria-label="系统状态">
      <article class="card status-card" v-for="item in statusCards" :key="item.label">
        <div class="sc-icon" aria-hidden="true">{{ item.icon }}</div>
        <div class="sc-body">
          <div class="sc-value" :style="{ color: item.color }">{{ item.value }}</div>
          <div class="sc-label">{{ item.label }}</div>
        </div>
      </article>
    </div>

    <!-- 最新识别结果 -->
    <section v-if="systemStore.lastDetections.length" class="detections fade-in-up"
      aria-labelledby="detect-title">
      <h2 id="detect-title" class="section-title">最新识别结果</h2>
      <ul class="detection-list" role="list">
        <li v-for="d in systemStore.lastDetections" :key="d.id"
          class="detection-item"
          :aria-label="`${d.label}，风险等级${d.risk}，距离${d.distance}`"
        >
          <span class="d-label">{{ d.label }}</span>
          <span class="d-dist">{{ d.distance }}</span>
          <span class="risk-badge" :class="d.risk">{{ riskText(d.risk) }}</span>
        </li>
      </ul>
    </section>

    <!-- 功能入口卡片 -->
    <nav class="feature-grid fade-in-up" aria-label="功能导航">
      <router-link v-for="f in features" :key="f.path"
        :to="f.path" class="feature-card card"
        :aria-label="f.label + '：' + f.desc"
      >
        <div class="fc-icon" aria-hidden="true">{{ f.icon }}</div>
        <div class="fc-body">
          <h3 class="fc-title">{{ f.label }}</h3>
          <p class="fc-desc">{{ f.desc }}</p>
        </div>
        <span class="fc-arrow" aria-hidden="true">›</span>
      </router-link>
    </nav>
  </section>
</template>

<script setup>
import { computed } from 'vue'
import { useSystemStore } from '../stores/system.js'
import { useVoiceStore } from '../stores/voice.js'

const systemStore = useSystemStore()
const voiceStore = useVoiceStore()

//启动系统时同步请求麦克风权限并开启语音监听
async function handleStart() {
  await systemStore.startSystem()
  // 请求权限并启动语音监听（startListening内部会自动请求麦克风权限）
  await voiceStore.startListening()
}

const statusCards = computed(() => [
  {
    icon: '🔄',
    label: '系统状态',
    value: systemStore.isRunning ? '运行中' : '已停止',
    color: systemStore.isRunning ? 'var(--accent-green)' : 'var(--text-muted)'
  },
  {
    icon: '📊',
    label: '推理帧率',
    value: systemStore.isRunning ? `${systemStore.fps} FPS` : '—',
    color: 'var(--accent-cyan)'
  },
  {
    icon: '🎯',
    label: '识别目标数',
    value: systemStore.lastDetections.length || '—',
    color: 'var(--accent-amber)'
  },
  {
    icon: '⚠️',
    label: '当前风险',
    value: riskLabel(systemStore.riskLevel),
    color: riskColor(systemStore.riskLevel)
  }
])

const features = [
  { path: '/monitor', icon: '📡', label: '环境监测', desc: '实时摄像头画面与目标识别' },
  { path: '/settings', icon: '⚙️', label: '系统设置', desc: '语音、联系人、路线配置' },
  { path: '/emergency', icon: '🆘', label: '应急求助', desc: '一键触发紧急联系人通知' },
]

function riskText(r) {
  return { high: '高风险', medium: '中风险', low: '低风险' }[r] || '未知'
}
function riskLabel(r) {
  return { high: '高风险', medium: '中等', low: '安全', none: '无目标' }[r] || '—'
}
function riskColor(r) {
  return { high: 'var(--accent-red)', medium: 'var(--accent-amber)', low: 'var(--accent-green)', none: 'var(--text-muted)' }[r] || 'var(--text-muted)'
}
</script>

<style scoped>
.home { display: flex; flex-direction: column; gap: 40px; }

/* Hero */
.hero {
  position: relative;
  border-radius: var(--radius-lg);
  overflow: hidden;
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  padding: 60px 48px;
  min-height: 360px;
  display: flex;
  align-items: center;
}
.hero-bg {
  position: absolute; inset: 0;
  pointer-events: none;
}
.hero-ring {
  position: absolute;
  border-radius: 50%;
  border: 1px solid rgba(245, 166, 35, 0.08);
  top: 50%; left: 50%;
  transform: translate(-50%, -50%);
  animation: expandRing 6s ease-in-out infinite;
}
.ring1 { width: 300px; height: 300px; animation-delay: 0s; }
.ring2 { width: 500px; height: 500px; animation-delay: 1.5s; }
.ring3 { width: 700px; height: 700px; animation-delay: 3s; }
@keyframes expandRing {
  0%, 100% { opacity: 0.4; transform: translate(-50%, -50%) scale(1); }
  50% { opacity: 0.1; transform: translate(-50%, -50%) scale(1.05); }
}
.hero-content { position: relative; z-index: 1; max-width: 680px; }
.hero-title {
  display: flex; flex-direction: column; gap: 8px;
  margin-bottom: 20px;
}
.title-main {
  font-family: var(--font-display);
  font-size: 3.2rem;
  color: var(--accent-amber);
  letter-spacing: 0.12em;
  line-height: 1.1;
}
.title-sub {
  font-size: 1rem;
  color: var(--text-secondary);
  font-weight: 400;
  letter-spacing: 0.06em;
}
.hero-desc {
  color: var(--text-secondary);
  font-size: 1.05rem;
  margin-bottom: 36px;
  line-height: 1.8;
  max-width: 520px;
}
.hero-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 14px;
  margin-bottom: 24px;
}
.voice-hint {
  font-size: 0.9rem;
  color: var(--text-muted);
  display: flex;
  align-items: center;
  gap: 8px;
}
.voice-hint strong { color: var(--accent-amber); }

/* Status Grid */
.status-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}
@media (max-width: 900px) { .status-grid { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 500px) { .status-grid { grid-template-columns: 1fr; } }
.status-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
}
.sc-icon { font-size: 2rem; line-height: 1; }
.sc-value { font-size: 1.4rem; font-weight: 900; line-height: 1.2; }
.sc-label { font-size: 0.8rem; color: var(--text-muted); margin-top: 4px; letter-spacing: 0.04em; }

/* Detections */
.section-title {
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--text-secondary);
  letter-spacing: 0.06em;
  margin-bottom: 16px;
  text-transform: uppercase;
}
.detection-list { list-style: none; display: flex; flex-direction: column; gap: 10px; }
.detection-item {
  display: flex;
  align-items: center;
  gap: 14px;
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-sm);
  padding: 14px 18px;
}
.d-label { flex: 1; font-weight: 700; font-size: 1rem; }
.d-dist { color: var(--text-muted); font-size: 0.9rem; }

/* Feature Grid */
.feature-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}
@media (max-width: 700px) { .feature-grid { grid-template-columns: 1fr; } }
.feature-card {
  display: flex;
  align-items: center;
  gap: 16px;
  text-decoration: none;
  color: inherit;
  transition: all var(--transition);
  padding: 22px;
}
.feature-card:hover {
  border-color: var(--accent-amber);
  transform: translateY(-3px);
  box-shadow: var(--shadow-card), var(--shadow-glow-amber);
}
.fc-icon { font-size: 2.2rem; flex-shrink: 0; }
.fc-body { flex: 1; }
.fc-title { font-size: 1rem; font-weight: 700; margin-bottom: 4px; }
.fc-desc { font-size: 0.85rem; color: var(--text-muted); line-height: 1.5; }
.fc-arrow { font-size: 1.6rem; color: var(--text-muted); transition: all var(--transition); }
.feature-card:hover .fc-arrow { color: var(--accent-amber); transform: translateX(4px); }
</style>
