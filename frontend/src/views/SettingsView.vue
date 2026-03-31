<template>
  <section class="settings" aria-labelledby="settings-title">
    <header class="page-header">
      <h1 id="settings-title" class="page-title">
        <span aria-hidden="true">⚙️</span> 系统设置
      </h1>
      <p class="page-desc">所有设置保存于本地，无需网络连接</p>
    </header>

    <div class="settings-layout">
      <!-- 语音设置 -->
      <article class="card settings-card" aria-labelledby="voice-settings-title">
        <h2 id="voice-settings-title" class="card-title">
          <span aria-hidden="true">🎙️</span> 语音设置
        </h2>
        <div class="form-group">
          <label class="form-label" for="voice-rate">语速：{{ settingsStore.voiceRate.toFixed(1) }}x</label>
          <input id="voice-rate" type="range" min="0.5" max="2" step="0.1"
            v-model.number="settingsStore.voiceRate"
            aria-label="语速调节，当前值" :aria-valuenow="settingsStore.voiceRate"
            aria-valuemin="0.5" aria-valuemax="2" />
          <div class="range-labels"><span>慢</span><span>正常</span><span>快</span></div>
        </div>
        <div class="form-group">
          <label class="form-label" for="voice-volume">音量：{{ Math.round(settingsStore.voiceVolume * 100) }}%</label>
          <input id="voice-volume" type="range" min="0" max="1" step="0.05"
            v-model.number="settingsStore.voiceVolume"
            aria-label="音量调节" />
          <div class="range-labels"><span>静音</span><span>中</span><span>最大</span></div>
        </div>
        <div class="form-group">
          <label class="form-label" for="feedback-mode">反馈模式</label>
          <select id="feedback-mode" class="form-select" v-model="settingsStore.feedbackMode"
            aria-label="选择反馈模式">
            <option value="voice+screen">语音 + 屏幕朗读</option>
            <option value="voice">仅语音</option>
          </select>
        </div>
        <button class="btn btn-ghost" style="width:100%" @click="testVoice"
          aria-label="测试语音播报效果">
          <span aria-hidden="true">▶</span> 测试语音
        </button>
      </article>

      <!-- 紧急联系人 -->
      <article class="card settings-card" aria-labelledby="contacts-title">
        <h2 id="contacts-title" class="card-title">
          <span aria-hidden="true">📞</span> 紧急联系人
          <span class="count-badge" aria-label="已添加联系人数量">{{ settingsStore.emergencyContacts.length }}/3</span>
        </h2>

        <ul class="contact-list" role="list" aria-label="紧急联系人列表">
          <li v-for="c in settingsStore.emergencyContacts" :key="c.id" class="contact-item">
            <div class="contact-info">
              <span class="contact-name">{{ c.name }}</span>
              <span class="contact-phone">{{ c.phone }}</span>
            </div>
            <button class="btn-icon" @click="settingsStore.removeContact(c.id)"
              :aria-label="`删除联系人 ${c.name}`">✕</button>
          </li>
          <li v-if="!settingsStore.emergencyContacts.length" class="contact-empty"
            aria-label="暂无紧急联系人">暂未添加联系人</li>
        </ul>

        <form v-if="settingsStore.emergencyContacts.length < 3"
          class="add-form" @submit.prevent="addContact"
          aria-label="添加紧急联系人表单">
          <div class="form-row">
            <div class="form-group">
              <label class="form-label" for="contact-name">姓名</label>
              <input id="contact-name" class="form-input" type="text"
                v-model="newContact.name" placeholder="联系人姓名"
                required maxlength="20" aria-required="true" />
            </div>
            <div class="form-group">
              <label class="form-label" for="contact-phone">电话</label>
              <input id="contact-phone" class="form-input" type="tel"
                v-model="newContact.phone" placeholder="手机号码"
                required pattern="[0-9]{7,15}" aria-required="true" />
            </div>
          </div>
          <button type="submit" class="btn btn-primary" style="width:100%"
            aria-label="添加联系人">
            <span aria-hidden="true">＋</span> 添加联系人
          </button>
        </form>
      </article>

      <!-- 常用路线 -->
      <article class="card settings-card" aria-labelledby="routes-title">
        <h2 id="routes-title" class="card-title">
          <span aria-hidden="true">🗺️</span> 常用路线
        </h2>

        <ul class="route-list" role="list" aria-label="常用路线列表">
          <li v-for="r in settingsStore.commonRoutes" :key="r.id" class="route-item">
            <div class="route-info">
              <span class="route-from">{{ r.from }}</span>
              <span class="route-arrow" aria-hidden="true">→</span>
              <span class="route-to">{{ r.to }}</span>
            </div>
            <button class="btn-icon" @click="settingsStore.removeRoute(r.id)"
              :aria-label="`删除路线 ${r.from} 到 ${r.to}`">✕</button>
          </li>
          <li v-if="!settingsStore.commonRoutes.length" class="contact-empty"
            aria-label="暂无常用路线">暂未添加路线</li>
        </ul>

        <form class="add-form" @submit.prevent="addRoute" aria-label="添加常用路线表单">
          <div class="form-row">
            <div class="form-group">
              <label class="form-label" for="route-from">起点</label>
              <input id="route-from" class="form-input" type="text"
                v-model="newRoute.from" placeholder="出发地" required />
            </div>
            <div class="form-group">
              <label class="form-label" for="route-to">终点</label>
              <input id="route-to" class="form-input" type="text"
                v-model="newRoute.to" placeholder="目的地" required />
            </div>
          </div>
          <button type="submit" class="btn btn-primary" style="width:100%"
            aria-label="添加路线">
            <span aria-hidden="true">＋</span> 添加路线
          </button>
        </form>
      </article>

      <!-- 关于系统 -->
      <article class="card settings-card about-card" aria-labelledby="about-title">
        <h2 id="about-title" class="card-title">
          <span aria-hidden="true">ℹ️</span> 关于系统
        </h2>
        <dl class="about-list">
          <div class="about-row"><dt>系统版本</dt><dd>v1.0.0</dd></div>
          <div class="about-row"><dt>识别引擎</dt><dd>YOLOv8（本地推理）</dd></div>
          <div class="about-row"><dt>前端框架</dt><dd>Vue 3 + Vite</dd></div>
          <div class="about-row"><dt>后端框架</dt><dd>Python FastAPI</dd></div>
          <div class="about-row"><dt>部署方式</dt><dd>本地部署，无需联网</dd></div>
          <div class="about-row">
            <dt>后端连接</dt>
            <dd>
              <span class="status-dot" :class="systemStore.connectionOk ? 'active' : 'danger'"></span>
              {{ systemStore.connectionOk ? '已连接' : '未连接' }}
            </dd>
          </div>
        </dl>
        <button class="btn btn-ghost" style="width:100%; margin-top:12px"
          @click="systemStore.pingBackend()" aria-label="检测后端服务连接状态">
          🔌 检测后端连接
        </button>
      </article>
    </div>
  </section>
</template>

<script setup>
import { reactive } from 'vue'
import { useSettingsStore } from '../stores/settings.js'
import { useSystemStore } from '../stores/system.js'

const settingsStore = useSettingsStore()
const systemStore = useSystemStore()

const newContact = reactive({ name: '', phone: '' })
const newRoute = reactive({ from: '', to: '' })

function addContact() {
  const ok = settingsStore.addContact({ name: newContact.name, phone: newContact.phone })
  if (ok) {
    systemStore.speak(`已添加联系人 ${newContact.name}`)
    newContact.name = ''
    newContact.phone = ''
  } else {
    systemStore.showAlert('最多添加3位紧急联系人', 'low')
  }
}

function addRoute() {
  settingsStore.addRoute({ from: newRoute.from, to: newRoute.to })
  systemStore.speak(`已添加路线：${newRoute.from} 到 ${newRoute.to}`)
  newRoute.from = ''
  newRoute.to = ''
}

function testVoice() {
  systemStore.speak('语音测试：视助系统正在运行，当前语速和音量设置已生效')
}
</script>

<style scoped>
.settings { display: flex; flex-direction: column; gap: 28px; }
.page-header { margin-bottom: 4px; }
.page-title {
  font-size: 1.8rem; font-weight: 900;
  color: var(--text-primary); display: flex; align-items: center; gap: 10px;
  margin-bottom: 6px;
}
.page-desc { color: var(--text-muted); font-size: 0.9rem; }

.settings-layout {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  align-items: start;
}
@media (max-width: 800px) { .settings-layout { grid-template-columns: 1fr; } }

.settings-card { display: flex; flex-direction: column; gap: 18px; }
.card-title {
  font-size: 1.1rem; font-weight: 700;
  color: var(--text-primary);
  display: flex; align-items: center; gap: 10px;
  padding-bottom: 14px;
  border-bottom: 1px solid var(--border-subtle);
}
.count-badge {
  margin-left: auto;
  font-size: 0.8rem; font-weight: 400;
  color: var(--text-muted);
  background: var(--bg-primary);
  padding: 2px 10px; border-radius: 20px;
  border: 1px solid var(--border-subtle);
}

.range-labels {
  display: flex; justify-content: space-between;
  font-size: 0.75rem; color: var(--text-muted);
  margin-top: 4px; padding: 0 2px;
}

/* Contacts */
.contact-list { list-style: none; display: flex; flex-direction: column; gap: 8px; }
.contact-item {
  display: flex; align-items: center; justify-content: space-between;
  background: var(--bg-primary);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-sm);
  padding: 12px 14px;
}
.contact-info { display: flex; flex-direction: column; gap: 2px; }
.contact-name { font-weight: 700; font-size: 0.95rem; }
.contact-phone { font-size: 0.85rem; color: var(--text-muted); font-family: monospace; }
.contact-empty { font-size: 0.9rem; color: var(--text-muted); padding: 8px 0; }
.btn-icon {
  background: none; border: none;
  color: var(--text-muted); cursor: pointer;
  font-size: 1.1rem; padding: 4px 8px;
  border-radius: var(--radius-sm);
  transition: all var(--transition);
}
.btn-icon:hover { color: var(--accent-red); background: rgba(255,71,87,0.1); }

.add-form { display: flex; flex-direction: column; gap: 12px; }
.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
@media (max-width: 500px) { .form-row { grid-template-columns: 1fr; } }

/* Routes */
.route-list { list-style: none; display: flex; flex-direction: column; gap: 8px; }
.route-item {
  display: flex; align-items: center; justify-content: space-between;
  background: var(--bg-primary);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-sm);
  padding: 12px 14px;
}
.route-info { display: flex; align-items: center; gap: 8px; font-size: 0.9rem; }
.route-from, .route-to { font-weight: 600; }
.route-arrow { color: var(--text-muted); }

/* About */
.about-card { grid-column: span 2; }
@media (max-width: 800px) { .about-card { grid-column: span 1; } }
.about-list { list-style: none; display: flex; flex-direction: column; }
.about-row {
  display: flex; justify-content: space-between; align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid var(--border-subtle);
  font-size: 0.95rem;
}
.about-row:last-child { border-bottom: none; }
.about-row dt { color: var(--text-muted); }
.about-row dd { font-weight: 600; display: flex; align-items: center; gap: 8px; }
</style>
