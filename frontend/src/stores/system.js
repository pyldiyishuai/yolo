import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'

export const useSystemStore = defineStore('system', () => {
  const isRunning = ref(false)
  const isLoading = ref(false)
  const alertMessage = ref('')
  const alertLevel = ref('low')   // 'low' | 'medium' | 'high'
  const lastDetections = ref([])
  const fps = ref(0)
  const connectionOk = ref(false)

  const riskLevel = computed(() => {
    if (!lastDetections.value.length) return 'none'
    const maxRisk = lastDetections.value.reduce((max, d) => {
      const order = { high: 3, medium: 2, low: 1 }
      return (order[d.risk] || 0) > (order[max] || 0) ? d.risk : max
    }, 'low')
    return maxRisk
  })

  async function startSystem() {
    isLoading.value = true
    try {
      await axios.post('/api/system/start')
      isRunning.value = true
      speak('系统已启动，开始环境感知')
    } catch (e) {
      showAlert('后端连接失败，请确认服务已启动', 'medium')
    } finally {
      isLoading.value = false
    }
  }

  async function stopSystem() {
    try {
      await axios.post('/api/system/stop')
    } catch (_) { /* 本地部署，忽略连接错误 */ }
    isRunning.value = false
    lastDetections.value = []
    speak('系统已关闭')
  }

  function showAlert(msg, level = 'medium') {
    alertMessage.value = msg
    alertLevel.value = level
    speak(msg)
    if (level !== 'high') {
      setTimeout(() => clearAlert(), 5000)
    }
  }

  function clearAlert() {
    alertMessage.value = ''
    alertLevel.value = 'low'
  }

  function updateDetections(detections, fpsVal) {
    lastDetections.value = detections
    fps.value = fpsVal || 0
    // 高风险自动触发预警
    const highRisk = detections.find(d => d.risk === 'high')
    if (highRisk) showAlert(`高风险：${highRisk.label} 距离约 ${highRisk.distance}`, 'high')
  }

  function speak(text) {
    if (!window.speechSynthesis) return
    window.speechSynthesis.cancel()
    const utt = new SpeechSynthesisUtterance(text)
    const settings = JSON.parse(localStorage.getItem('voiceSettings') || '{}')
    utt.lang = 'zh-CN'
    utt.rate = settings.rate || 1.0
    utt.volume = settings.volume || 1.0
    window.speechSynthesis.speak(utt)
  }

  async function pingBackend() {
    try {
      await axios.get('/api/ping', { timeout: 2000 })
      connectionOk.value = true
    } catch (_) {
      connectionOk.value = false
    }
  }

  return {
    isRunning, isLoading, alertMessage, alertLevel,
    lastDetections, fps, connectionOk, riskLevel,
    startSystem, stopSystem, showAlert, clearAlert,
    updateDetections, speak, pingBackend
  }
})
