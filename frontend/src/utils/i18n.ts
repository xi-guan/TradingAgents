import i18n from 'i18next'
import { initReactI18next } from 'react-i18next'

// 导入翻译资源
const resources = {
  'zh-CN': {
    translation: await fetch('/locales/zh-CN/translation.json').then((res) => res.json()),
  },
  'en-US': {
    translation: await fetch('/locales/en-US/translation.json').then((res) => res.json()),
  },
}

i18n
  .use(initReactI18next)
  .init({
    resources,
    lng: localStorage.getItem('language') || 'zh-CN',
    fallbackLng: 'zh-CN',
    interpolation: {
      escapeValue: false,
    },
  })
  .catch((error) => {
    console.error('Failed to initialize i18n:', error)
  })

export default i18n
