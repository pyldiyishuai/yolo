import { defineStore } from 'pinia'
import { ref, watch } from 'vue'

const STORAGE_KEYS = {
  voice: 'voiceSettings',
  contacts: 'emergencyContacts',
  routes: 'commonRoutes',
  feedback: 'feedbackMode'
}

export const useSettingsStore = defineStore('settings', () => {
  // 语音设置
  const voiceRate   = ref(1.0)
  const voiceVolume = ref(1.0)
  const feedbackMode = ref('voice+screen') // 'voice+screen' | 'voice'

  // 紧急联系人 (最多3名)
  const emergencyContacts = ref([])

  // 常用路线
  const commonRoutes = ref([])

  // 初始化：从 localStorage 读取
  function load() {
    try {
      const vs = JSON.parse(localStorage.getItem(STORAGE_KEYS.voice) || '{}')
      voiceRate.value   = vs.rate   || 1.0
      voiceVolume.value = vs.volume || 1.0
      feedbackMode.value = localStorage.getItem(STORAGE_KEYS.feedback) || 'voice+screen'
      emergencyContacts.value = JSON.parse(localStorage.getItem(STORAGE_KEYS.contacts) || '[]')
      commonRoutes.value      = JSON.parse(localStorage.getItem(STORAGE_KEYS.routes)   || '[]')
    } catch (_) {}
  }

  // 监听变化自动持久化
  watch([voiceRate, voiceVolume], () => {
    localStorage.setItem(STORAGE_KEYS.voice, JSON.stringify({ rate: voiceRate.value, volume: voiceVolume.value }))
  })
  watch(feedbackMode, (v) => localStorage.setItem(STORAGE_KEYS.feedback, v))
  watch(emergencyContacts, (v) => localStorage.setItem(STORAGE_KEYS.contacts, JSON.stringify(v)), { deep: true })
  watch(commonRoutes,      (v) => localStorage.setItem(STORAGE_KEYS.routes,   JSON.stringify(v)), { deep: true })

  function addContact(contact) {
    if (emergencyContacts.value.length >= 3) return false
    emergencyContacts.value.push({ id: Date.now(), ...contact })
    return true
  }

  function removeContact(id) {
    emergencyContacts.value = emergencyContacts.value.filter(c => c.id !== id)
  }

  function addRoute(route) {
    commonRoutes.value.push({ id: Date.now(), ...route })
  }

  function removeRoute(id) {
    commonRoutes.value = commonRoutes.value.filter(r => r.id !== id)
  }

  load()

  return {
    voiceRate, voiceVolume, feedbackMode,
    emergencyContacts, commonRoutes,
    addContact, removeContact, addRoute, removeRoute
  }
})
