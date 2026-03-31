<template>
  <section class="emergency" aria-labelledby="emergency-title">
    <header class="page-header">
      <h1 id="emergency-title" class="page-title">
        <span aria-hidden="true">🆘</span> 应急求助
      </h1>
      <p class="page-desc">遇到紧急情况，立即触发语音预警并通知紧急联系人</p>
    </header>

    <!-- SOS 主按钮区 -->
    <div class="sos-zone" role="region" aria-label="一键求助区域">
      <div class="sos-ring" :class="{ triggered: isSosTriggered }" aria-hidden="true">
        <div class="sos-ring-inner"></div>
      </div>
      <button
        class="sos-btn"
        :class="{ triggered: isSosTriggered, loading: isSending }"
        @click="triggerSOS"
        :disabled="isSending"
        aria-label="一键应急求助"
      >
        <span class="sos-icon" aria-hidden="true">{{ isSending ? '⏳' : '🆘' }}</span>
        <span class="sos-label">{{ sosLabel }}</span>
      </button>
      <p class="sos-hint" role="status" aria-live="polite">
        {{ isSosTriggered ? '求助已发送，等待联系人响应...' : '按下按钮或说「小视 求助」触发应急' }}
      </p>
    </div>

    <!-- 位置 + 联系人 -->
    <div class="info-grid">
      <article class="card info-card" aria-labelledby="location-title">
        <h2 id="location-title" class="card-title">📍 当前位置</h2>
        <div v-if="location" class="location-info">
          <div class="loc-row"><span class="loc-label">纬度</span><span class="loc-val">{{ location.lat.toFixed(6) }}</span></div>
          <div class="loc-row"><span class="loc-label">经度</span><span class="loc-val">{{ location.lng.toFixed(6) }}</span></div>
          <div class="loc-row"><span class="loc-label">精度</span><span class="loc-val">±{{ Math.round(location.accuracy) }}m</span></div>
        </div>
        <div v-else class="loc-loading" role="status">
          <span aria-hidden="true">{{ locating ? '🔄' : '❌' }}</span>
          {{ locating ? '正在获取位置...' : '无法获取位置，请允许定位权限' }}
        </div>
        <button class="btn btn-ghost" style="width:100%;margin-top:12px" @click="getLocation">🔄 刷新位置</button>
      </article>

      <article class="card info-card" aria-labelledby="contacts-info-title">
        <h2 id="contacts-info-title" class="card-title">👥 紧急联系人</h2>
        <ul class="contact-list" role="list">
          <li v-for="c in settingsStore.emergencyContacts" :key="c.id" class="contact-item">
            <span class="contact-avatar" aria-hidden="true">👤</span>
            <div class="contact-detail">
              <span class="contact-name">{{ c.name }}</span>
              <span class="contact-phone">{{ c.phone }}</span>
            </div>
            <span v-if="notifyStatus[c.id]" class="notify-tag" :class="notifyStatus[c.id]">
              {{ notifyStatus[c.id] === 'sent' ? '✓ 已通知' : '✗ 失败' }}
            </span>
          </li>
          <li v-if="!settingsStore.emergencyContacts.length" class="contact-empty">
            暂无紧急联系人，请前往设置页面添加
          </li>
        </ul>
        <router-link to="/settings" class="btn btn-ghost" style="width:100%;margin-top:12px;display:flex">
          ⚙️ 前往添加联系人
        </router-link>
      </article>
    </div>

    <!-- 求助历史 -->
    <section class="card history-card" aria-labelledby="history-title">
      <h2 id="history-title" class="card-title">📋 求助记录</h2>
      <ul class="history-list" role="log" aria-live="polite">
        <li v-for="h in history" :key="h.id" class="history-item">
          <span class="h-time">{{ h.time }}</span>
          <span class="h-msg">{{ h.msg }}</span>
          <span class="h-status" :class="h.ok ? 'ok' : 'fail'">{{ h.ok ? '成功' : '失败' }}</span>
        </li>
        <li v-if="!history.length" class="h-empty">暂无求助记录</li>
      </ul>
    </section>
  </section>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import axios from 'axios'
import { useSystemStore } from '../stores/system.js'
import { useSettingsStore } from '../stores/settings.js'

const systemStore = useSystemStore()
const settingsStore = useSettingsStore()

const isSosTriggered = ref(false)
const isSending = ref(false)
const location = ref(null)
const locating = ref(false)
const notifyStatus = reactive({})
const history = ref([])

const sosLabel = computed(() => {
  if (isSending.value) return '发送中...'
  if (isSosTriggered.value) return '已求助'
  return '一键求助'
})

onMounted(() => getLocation())

function getLocation() {
  if (!navigator.geolocation) return
  locating.value = true
  navigator.geolocation.getCurrentPosition(
    (pos) => {
      location.value = { lat: pos.coords.latitude, lng: pos.coords.longitude, accuracy: pos.coords.accuracy }
      locating.value = false
    },
    () => { locating.value = false },
    { timeout: 8000, enableHighAccuracy: true }
  )
}

async function triggerSOS() {
  if (isSending.value) return
  isSending.value = true
  systemStore.speak('紧急求助已触发，正在通知联系人，请保持冷静')
  systemStore.showAlert('应急求助已触发！正在联系紧急联系人...', 'high')

  const payload = {
    contacts: settingsStore.emergencyContacts,
    location: location.value,
    risk_info: systemStore.alertMessage || '用户手动触发应急求助'
  }

  try {
    const res = await axios.post('/api/emergency', payload, { timeout: 10000 })
    const results = res.data.results || []
    results.forEach(r => { notifyStatus[r.contact_id] = r.ok ? 'sent' : 'fail' })
    isSosTriggered.value = true
    addHistory('应急求助已发送', true)
  } catch (_) {
    // 后端离线时本地播报
    isSosTriggered.value = true
    addHistory('后端离线，仅本地预警', false)
    systemStore.speak('警告：后端服务未启动，无法发送通知，请手动联系紧急联系人')
  } finally {
    isSending.value = false
    setTimeout(() => { isSosTriggered.value = false }, 30000)
  }
}

function addHistory(msg, ok) {
  const now = new Date()
  const time = `${now.getFullYear()}-${String(now.getMonth()+1).padStart(2,'0')}-${String(now.getDate()).padStart(2,'0')} ${String(now.getHours()).padStart(2,'0')}:${String(now.getMinutes()).padStart(2,'0')}`
  history.value.unshift({ id: Date.now(), time, msg, ok })
}
</script>

<style scoped>
.emergency { display: flex; flex-direction: column; gap: 32px; }
.page-header { margin-bottom: 4px; }
.page-title {
  font-size: 1.8rem; font-weight: 900;
  color: var(--accent-red); display: flex; align-items: center; gap: 10px; margin-bottom: 6px;
}
.page-desc { color: var(--text-muted); font-size: 0.9rem; }

/* SOS Zone */
.sos-zone {
  display: flex; flex-direction: column;
  align-items: center; gap: 24px;
  padding: 48px 24px;
  position: relative;
}
.sos-ring {
  position: absolute;
  width: 240px; height: 240px;
  border-radius: 50%;
  border: 2px solid rgba(255, 71, 87, 0.2);
  animation: ringPulse 3s ease-in-out infinite;
}
.sos-ring-inner {
  position: absolute; inset: 20px;
  border-radius: 50%;
  border: 1px solid rgba(255, 71, 87, 0.12);
}
.sos-ring.triggered {
  border-color: var(--accent-red);
  animation: ringPulse 0.8s ease-in-out infinite;
}
@keyframes ringPulse {
  0%, 100% { transform: scale(1); opacity: 0.5; }
  50% { transform: scale(1.08); opacity: 1; }
}
.sos-btn {
  position: relative; z-index: 1;
  width: 180px; height: 180px;
  border-radius: 50%;
  border: none; cursor: pointer;
  background: radial-gradient(circle at 35% 35%, #ff6b7a, var(--accent-red), #8b0000);
  box-shadow: 0 0 40px rgba(255,71,87,0.4), 0 8px 32px rgba(0,0,0,0.5);
  display: flex; flex-direction: column;
  align-items: center; justify-content: center; gap: 6px;
  transition: all 0.2s ease;
  color: #fff;
}
.sos-btn:hover:not(:disabled) {
  transform: scale(1.06);
  box-shadow: 0 0 60px rgba(255,71,87,0.6), 0 8px 32px rgba(0,0,0,0.5);
}
.sos-btn:active:not(:disabled) { transform: scale(0.97); }
.sos-btn.triggered {
  background: radial-gradient(circle at 35% 35%, #ff9500, #e67e00, #7a4000);
  box-shadow: 0 0 40px rgba(245,166,35,0.5);
  animation: sosPulse 1s ease-in-out infinite;
}
.sos-btn:disabled { opacity: 0.7; cursor: not-allowed; }
@keyframes sosPulse {
  0%, 100% { box-shadow: 0 0 40px rgba(245,166,35,0.4); }
  50% { box-shadow: 0 0 70px rgba(245,166,35,0.8); }
}
.sos-icon { font-size: 3rem; line-height: 1; }
.sos-label { font-size: 1.1rem; font-weight: 900; letter-spacing: 0.06em; }
.sos-hint { font-size: 0.9rem; color: var(--text-muted); text-align: center; }

/* Info grid */
.info-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
@media (max-width: 700px) { .info-grid { grid-template-columns: 1fr; } }
.info-card { display: flex; flex-direction: column; gap: 14px; }
.card-title { font-size: 1rem; font-weight: 700; padding-bottom: 12px; border-bottom: 1px solid var(--border-subtle); display: flex; align-items: center; gap: 8px; }

.location-info { display: flex; flex-direction: column; gap: 8px; }
.loc-row { display: flex; justify-content: space-between; font-size: 0.9rem; padding: 6px 0; border-bottom: 1px solid var(--border-subtle); }
.loc-row:last-child { border-bottom: none; }
.loc-label { color: var(--text-muted); }
.loc-val { font-family: monospace; font-weight: 600; color: var(--accent-cyan); }
.loc-loading { color: var(--text-muted); display: flex; align-items: center; gap: 8px; font-size: 0.9rem; }

.contact-list { list-style: none; display: flex; flex-direction: column; gap: 10px; }
.contact-item { display: flex; align-items: center; gap: 12px; padding: 10px 0; border-bottom: 1px solid var(--border-subtle); }
.contact-item:last-child { border-bottom: none; }
.contact-avatar { font-size: 1.8rem; }
.contact-detail { flex: 1; display: flex; flex-direction: column; gap: 2px; }
.contact-name { font-weight: 700; font-size: 0.95rem; }
.contact-phone { font-size: 0.82rem; color: var(--text-muted); font-family: monospace; }
.notify-tag { font-size: 0.78rem; font-weight: 700; padding: 3px 10px; border-radius: 12px; }
.notify-tag.sent { background: rgba(46,204,113,0.15); color: var(--accent-green); }
.notify-tag.fail { background: rgba(255,71,87,0.15); color: var(--accent-red); }
.contact-empty { font-size: 0.9rem; color: var(--text-muted); padding: 12px 0; }

/* History */
.history-card {}
.history-list { list-style: none; display: flex; flex-direction: column; gap: 8px; margin-top: 4px; }
.history-item { display: flex; align-items: center; gap: 14px; font-size: 0.88rem; padding: 8px 0; border-bottom: 1px solid var(--border-subtle); }
.history-item:last-child { border-bottom: none; }
.h-time { color: var(--text-muted); font-family: monospace; flex-shrink: 0; }
.h-msg { flex: 1; color: var(--text-secondary); }
.h-status { font-weight: 700; font-size: 0.8rem; }
.h-status.ok { color: var(--accent-green); }
.h-status.fail { color: var(--accent-red); }
.h-empty { color: var(--text-muted); font-size: 0.88rem; }
</style>
