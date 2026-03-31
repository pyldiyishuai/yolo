<template>
  <a href="#main-content" class="skip-link">跳过导航，直接到主内容</a>

  <div class="app-shell" :class="{ 'system-active': systemStore.isRunning }">
    <!-- 顶部导航 -->
    <header class="app-header" role="banner">
      <div class="header-inner">
        <div class="brand" aria-label="视助系统">
          <span class="brand-icon" aria-hidden="true">👁</span>
          <span class="brand-name">视助系统</span>
          <span class="brand-sub">环境感知平台</span>
        </div>

        <div class="header-status" aria-live="polite" aria-atomic="true">
          <span
            class="status-dot"
            :class="systemStore.isRunning ? 'active' : 'inactive'"
            role="img"
            :aria-label="systemStore.isRunning ? '系统运行中' : '系统已停止'"
          ></span>
          <span class="status-text">{{ systemStore.isRunning ? '系统运行中' : '系统已停止' }}</span>
        </div>

        <nav class="app-nav" role="navigation" aria-label="主导航">
          <router-link to="/" class="nav-link" aria-label="主页">主页</router-link>
          <router-link to="/monitor" class="nav-link" aria-label="环境监测">监测</router-link>
          <router-link to="/settings" class="nav-link" aria-label="系统设置">设置</router-link>
          <router-link to="/emergency" class="nav-link nav-link--emergency" aria-label="应急求助">求助</router-link>
        </nav>
      </div>
    </header>

    <!-- 语音状态提示条 -->
    <div v-if="voiceStore.isListening" class="voice-bar" role="status" aria-live="assertive">
      <span class="voice-wave" aria-hidden="true">
        <span></span><span></span><span></span><span></span><span></span>
      </span>
      <span>正在聆听语音指令...</span>
      <button class="voice-bar-stop" @click="voiceStore.stopListening()" aria-label="停止语音监听">停止</button>
    </div>

    <!-- 麦克风权限被拒绝提示条 -->
    <div v-if="voiceStore.micPermission === 'denied'" class="mic-denied-bar" role="alert">
      <span aria-hidden="true">🎤</span>
      <span>麦克风权限被拒绝，语音控制不可用。</span>
      <a href="#" @click.prevent="voiceStore.requestMicPermission()" class="mic-retry">重新授权</a>
    </div>

    <!-- 主内容 -->
    <main id="main-content" class="app-main">
      <router-view v-slot="{ Component }">
        <transition name="page" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>

    <!-- 全局风险预警悬浮层 -->
    <Teleport to="body">
      <div
        v-if="systemStore.alertMessage"
        class="global-alert"
        role="alert"
        aria-live="assertive"
        aria-atomic="true"
        :class="`alert-${systemStore.alertLevel}`"
      >
        <span class="alert-icon" aria-hidden="true">{{ alertIcon }}</span>
        <span class="alert-text">{{ systemStore.alertMessage }}</span>
        <button class="alert-close" @click="systemStore.clearAlert" aria-label="关闭预警">×</button>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useSystemStore } from './stores/system.js'
import { useVoiceStore } from './stores/voice.js'

const systemStore = useSystemStore()
const voiceStore = useVoiceStore()

const alertIcon = computed(() => {
  const icons = { high: '🚨', medium: '⚠️', low: 'ℹ️' }
  return icons[systemStore.alertLevel] || 'ℹ️'
})
</script>

<style scoped>
.app-shell {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background: var(--bg-primary);
  background-image:
    radial-gradient(ellipse at 20% 0%, rgba(0, 212, 255, 0.04) 0%, transparent 50%),
    radial-gradient(ellipse at 80% 100%, rgba(245, 166, 35, 0.04) 0%, transparent 50%);
}

/* ---- Header ---- */
.app-header {
  position: sticky;
  top: 0;
  z-index: 100;
  background: rgba(10, 14, 26, 0.92);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--border-subtle);
}
.header-inner {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
  height: 64px;
  display: flex;
  align-items: center;
  gap: 24px;
}
.brand {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
}
.brand-icon { font-size: 1.6rem; }
.brand-name {
  font-family: var(--font-display);
  font-size: 1.3rem;
  color: var(--accent-amber);
  letter-spacing: 0.08em;
}
.brand-sub {
  font-size: 0.75rem;
  color: var(--text-muted);
  letter-spacing: 0.06em;
}
.header-status {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-left: auto;
}
.status-text { font-size: 0.85rem; color: var(--text-secondary); }

.app-nav {
  display: flex;
  gap: 4px;
}
.nav-link {
  padding: 8px 16px;
  border-radius: var(--radius-sm);
  color: var(--text-secondary);
  text-decoration: none;
  font-size: 0.95rem;
  font-weight: 600;
  transition: all var(--transition);
  letter-spacing: 0.04em;
}
.nav-link:hover, .nav-link.router-link-active {
  color: var(--accent-amber);
  background: rgba(245, 166, 35, 0.1);
}
.nav-link--emergency {
  color: var(--accent-red);
  border: 1px solid rgba(255, 71, 87, 0.3);
}
.nav-link--emergency:hover {
  background: rgba(255, 71, 87, 0.12);
  color: var(--accent-red);
  border-color: var(--accent-red);
}

/* ---- Voice Bar ---- */
.voice-bar {
  background: linear-gradient(90deg, rgba(0, 212, 255, 0.08), rgba(245, 166, 35, 0.08));
  border-bottom: 1px solid rgba(0, 212, 255, 0.2);
  padding: 10px 24px;
  display: flex;
  align-items: center;
  gap: 14px;
  font-size: 0.95rem;
  color: var(--accent-cyan);
  animation: fadeInUp 0.3s ease;
}
.voice-wave {
  display: flex;
  align-items: center;
  gap: 3px;
  height: 20px;
}
.voice-wave span {
  display: inline-block;
  width: 3px;
  border-radius: 2px;
  background: var(--accent-cyan);
  animation: wave 1.2s ease-in-out infinite;
}
.voice-wave span:nth-child(1) { height: 6px; animation-delay: 0s; }
.voice-wave span:nth-child(2) { height: 14px; animation-delay: 0.15s; }
.voice-wave span:nth-child(3) { height: 20px; animation-delay: 0.3s; }
.voice-wave span:nth-child(4) { height: 14px; animation-delay: 0.45s; }
.voice-wave span:nth-child(5) { height: 6px; animation-delay: 0.6s; }
@keyframes wave {
  0%, 100% { transform: scaleY(0.5); opacity: 0.5; }
  50% { transform: scaleY(1); opacity: 1; }
}

/* ---- Main ---- */
.app-main {
  flex: 1;
  max-width: 1200px;
  width: 100%;
  margin: 0 auto;
  padding: 32px 24px;
}

/* ---- Global Alert ---- */
.global-alert {
  position: fixed;
  top: 80px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 9999;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 28px;
  border-radius: var(--radius-md);
  font-size: 1.1rem;
  font-weight: 700;
  box-shadow: 0 8px 32px rgba(0,0,0,0.5);
  animation: slideDown 0.35s cubic-bezier(0.34, 1.56, 0.64, 1);
  min-width: 320px;
  max-width: 600px;
}
@keyframes slideDown {
  from { opacity: 0; transform: translateX(-50%) translateY(-20px); }
  to { opacity: 1; transform: translateX(-50%) translateY(0); }
}
.alert-high { background: #2a0a0d; border: 2px solid var(--accent-red); color: #ff8a94; }
.alert-medium { background: #1e1600; border: 2px solid var(--accent-amber); color: var(--accent-amber); }
.alert-low { background: #081a12; border: 2px solid var(--accent-green); color: var(--accent-green); }
.alert-icon { font-size: 1.4rem; }
.alert-text { flex: 1; }
.alert-close {
  background: none; border: none; color: inherit;
  font-size: 1.4rem; cursor: pointer; opacity: 0.7;
  line-height: 1; padding: 0 4px;
}
.alert-close:hover { opacity: 1; }

/* ---- Page Transition ---- */
.page-enter-active, .page-leave-active { transition: all 0.25s ease; }
.page-enter-from { opacity: 0; transform: translateX(12px); }
.page-leave-to { opacity: 0; transform: translateX(-12px); }

/* ---- Voice Bar Stop Button ---- */
.voice-bar-stop {
  margin-left: auto;
  background: rgba(0, 212, 255, 0.15);
  border: 1px solid rgba(0, 212, 255, 0.35);
  color: var(--accent-cyan);
  border-radius: var(--radius-sm);
  padding: 4px 14px;
  font-size: 0.82rem;
  cursor: pointer;
  transition: all var(--transition);
}
.voice-bar-stop:hover { background: rgba(0, 212, 255, 0.28); }

/* ---- Mic Denied Bar ---- */
.mic-denied-bar {
  background: rgba(255, 71, 87, 0.08);
  border-bottom: 1px solid rgba(255, 71, 87, 0.25);
  padding: 10px 24px;
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 0.9rem;
  color: var(--accent-red);
  animation: fadeInUp 0.3s ease;
}
.mic-retry {
  margin-left: auto;
  color: var(--accent-amber);
  font-weight: 700;
  text-decoration: underline;
  cursor: pointer;
  font-size: 0.85rem;
}
</style>
