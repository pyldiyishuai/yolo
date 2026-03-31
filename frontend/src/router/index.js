import { createRouter, createWebHashHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import SettingsView from '../views/SettingsView.vue'
import EmergencyView from '../views/EmergencyView.vue'
import MonitorView from '../views/MonitorView.vue'

const routes = [
  { path: '/', component: HomeView, meta: { title: '主页' } },
  { path: '/monitor', component: MonitorView, meta: { title: '环境监测' } },
  { path: '/settings', component: SettingsView, meta: { title: '设置' } },
  { path: '/emergency', component: EmergencyView, meta: { title: '应急求助' } }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

router.afterEach((to) => {
  document.title = `视助系统 - ${to.meta.title || '主页'}`
})

export default router
