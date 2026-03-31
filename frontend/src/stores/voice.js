import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useSystemStore } from './system.js'

export const useVoiceStore = defineStore('voice', () => {
  const isListening = ref(false)
  const lastCommand = ref('')
  const wakeWord = '小视'  // 小视
  let recognition = null
  let autoListening = false

  // 麦克风权限状态: 'unknown' | 'granted' | 'denied'
  const micPermission = ref('unknown')

  function initRecognition() {
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition
    if (!SR) {
      console.warn('[Voice] SpeechRecognition not supported in this browser')
      return false
    }
    recognition = new SR()
    recognition.lang = 'zh-CN'
    recognition.continuous = true
    recognition.interimResults = false
    recognition.onresult = handleResult
    recognition.onend = () => {
      console.log('[Voice] ended, autoListening=', autoListening)
      isListening.value = false
      if (autoListening) startListening()
    }
    recognition.onerror = (e) => {
      console.error('[Voice] error:', e.error, e.message)
      if (e.error !== 'no-speech') isListening.value = false
    }
    console.log('[Voice] SpeechRecognition initialized')
    return true
  }

  async function requestMicPermission() {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      stream.getTracks().forEach(t => t.stop())
      micPermission.value = 'granted'
      console.log('[Voice] mic permission granted')
      return true
    } catch (e) {
      micPermission.value = 'denied'
      const systemStore = useSystemStore()
      const msgMap = {
        NotAllowedError: '麦克风权限被拒绝，请点击地址栏锁形图标 → 麦克风 → 允许，然后刷新页面',
        NotFoundError: '未检测到麦克风设备',
        NotReadableError: '麦克风被占用，请关闭其他应用',
        SecurityError: '页面不允许访问麦克风（需 localhost 或 HTTPS）',
      }
      const msg = msgMap[e.name] || ('麦克风错误：' + e.name + ' - ' + e.message)
      systemStore.showAlert(msg, 'medium')
      console.error('[Mic]', e.name, e.message)
      return false
    }
  }

  async function startListening() {
    console.log('[Voice] startListening called, micPermission=', micPermission.value)
    if (micPermission.value !== 'granted') {
      const ok = await requestMicPermission()
      if (!ok) return
    }
    if (!recognition && !initRecognition()) return
    try {
      recognition.start()
      isListening.value = true
      autoListening = true
      console.log('[Voice] recognition.start() OK')
    } catch (err) {
      console.warn('[Voice] start error (may already be running):', err.message)
    }
  }

  function stopListening() {
    console.log('[Voice] stopListening called')
    autoListening = false
    isListening.value = false
    recognition?.stop()
  }

  function handleResult(event) {
    const text = event.results[event.results.length - 1][0].transcript.trim()
    console.log('[Voice] heard:', text)
    lastCommand.value = text
    if (text.includes(wakeWord)) {
      processCommand(text.replace(wakeWord, '').trim())
    }
  }

  function processCommand(cmd) {
    console.log('[Voice] processCommand:', cmd)
    const systemStore = useSystemStore()
    const cmdMap = [
      { keys: ['启动', '开始', '打开'], action: () => systemStore.startSystem() },
      { keys: ['关闭', '停止', '退出'], action: () => systemStore.stopSystem() },
      { keys: ['求助', '帮助', '紧急'], action: () => { window.location.hash = '/emergency' } },
      { keys: ['设置', '配置'],               action: () => { window.location.hash = '/settings' } },
      { keys: ['监测', '查看', '识别'], action: () => { window.location.hash = '/monitor' } },
      { keys: ['回家', '主页', '首页'], action: () => { window.location.hash = '/' } },
    ]
    const matched = cmdMap.find(item => item.keys.some(k => cmd.includes(k)))
    if (matched) {
      matched.action()
      systemStore.speak('已执行：' + cmd)
    } else {
      systemStore.speak('未识别指令：' + cmd)
    }
  }

  return { isListening, lastCommand, micPermission, requestMicPermission, startListening, stopListening }
})
