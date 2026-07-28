/**
 * 通知状态管理 (Pinia Store)
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useNotificationStore = defineStore('notification', () => {
  const unreadCount = ref<number>(0)

  function setUnreadCount(count: number) {
    unreadCount.value = count
  }

  function incrementUnread() {
    unreadCount.value++
  }

  function decrementUnread() {
    if (unreadCount.value > 0) unreadCount.value--
  }

  return {
    unreadCount,
    setUnreadCount,
    incrementUnread,
    decrementUnread,
  }
})
