/**
 * Translation strings for Arabic and English locales
 */

export type Locale = 'ar' | 'en';

export interface Translations {
  common: {
    appName: string;
    loading: string;
    error: string;
    success: string;
    submit: string;
    cancel: string;
  };
  theme: {
    light: string;
    dark: string;
    toggle: string;
  };
  language: {
    english: string;
    arabic: string;
    toggle: string;
  };
  nav: {
    home: string;
    admin: string;
    repliesConsole: string;
  };
  repliesConsole: {
    title: string;
    subtitle: string;
    placeholder: string;
    send: string;
    successMessage: string;
    errorMessage: string;
    delivered: string;
    notDelivered: string;
  };
}

export const translations: Record<Locale, Translations> = {
  en: {
    common: {
      appName: 'Top-TieR Global HUB AI',
      loading: 'Loading...',
      error: 'Error',
      success: 'Success',
      submit: 'Submit',
      cancel: 'Cancel',
    },
    theme: {
      light: 'Light',
      dark: 'Dark',
      toggle: 'Toggle theme',
    },
    language: {
      english: 'English',
      arabic: 'Arabic',
      toggle: 'Toggle language',
    },
    nav: {
      home: 'Home',
      admin: 'Admin',
      repliesConsole: 'Replies Console',
    },
    repliesConsole: {
      title: 'Replies Console',
      subtitle: 'Send messages to the backend API',
      placeholder: 'Enter your message here...',
      send: 'Send Message',
      successMessage: 'Message sent successfully!',
      errorMessage: 'Failed to send message',
      delivered: 'Delivered to Telegram',
      notDelivered: 'Not delivered to Telegram',
    },
  },
  ar: {
    common: {
      appName: 'Top-TieR Global HUB AI',
      loading: 'جاري التحميل...',
      error: 'خطأ',
      success: 'نجح',
      submit: 'إرسال',
      cancel: 'إلغاء',
    },
    theme: {
      light: 'فاتح',
      dark: 'داكن',
      toggle: 'تبديل السمة',
    },
    language: {
      english: 'الإنجليزية',
      arabic: 'العربية',
      toggle: 'تبديل اللغة',
    },
    nav: {
      home: 'الرئيسية',
      admin: 'المسؤول',
      repliesConsole: 'وحدة الردود',
    },
    repliesConsole: {
      title: 'وحدة الردود',
      subtitle: 'إرسال رسائل إلى واجهة برمجة التطبيقات',
      placeholder: 'أدخل رسالتك هنا...',
      send: 'إرسال رسالة',
      successMessage: 'تم إرسال الرسالة بنجاح!',
      errorMessage: 'فشل في إرسال الرسالة',
      delivered: 'تم التسليم إلى تيليجرام',
      notDelivered: 'لم يتم التسليم إلى تيليجرام',
    },
  },
};
