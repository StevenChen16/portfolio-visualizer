import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

// 导入语言文件
import translationEN from './locales/en.json';
import translationZH from './locales/zh.json';

// 资源配置
const resources = {
  en: {
    translation: translationEN
  },
  zh: {
    translation: translationZH
  }
};

i18n
  // 使用语言检测器
  .use(LanguageDetector)
  // 将i18n实例传递给react-i18next
  .use(initReactI18next)
  // 初始化i18next
  .init({
    resources,
    fallbackLng: 'zh', // 默认语言
    debug: process.env.NODE_ENV === 'development',
    interpolation: {
      escapeValue: false, // 不需要对React应用进行HTML转义
    },
    detection: {
      order: ['localStorage', 'navigator'],
      caches: ['localStorage'],
    }
  });

export default i18n;
