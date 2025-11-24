<template>
  <div class="main">
    <div class="chat-container">
      <header class="header">
        <h1>🤖 TopTire AI Chat</h1>
        <p>متصل بـ Railway Backend</p>
      </header>

      <div class="messages-container" ref="messagesContainer">
        <div
          v-for="(message, index) in messages"
          :key="index"
          :class="['message', message.role === 'user' ? 'user-message' : 'ai-message']"
        >
          <strong>{{ message.role === 'user' ? 'أنت' : 'AI' }}:</strong> {{ message.content }}
        </div>
        <div v-if="isLoading" class="loading">
          🤖 يكتب...
        </div>
      </div>

      <div class="input-area">
        <input
          type="text"
          v-model="input"
          @keypress.enter="sendMessage"
          placeholder="اكتب رسالتك هنا..."
          class="input"
          :disabled="isLoading"
        />
        <button
          @click="sendMessage"
          :disabled="isLoading || !input.trim()"
          class="send-button"
        >
          إرسال
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, nextTick } from 'vue';

export default {
  name: 'App',
  setup() {
    const messages = ref([
      { role: 'assistant', content: 'مرحباً! كيف يمكنني مساعدتك اليوم؟' }
    ]);
    const input = ref('');
    const isLoading = ref(false);
    const messagesContainer = ref(null);

    const scrollToBottom = () => {
      nextTick(() => {
        if (messagesContainer.value) {
          messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
        }
      });
    };

    const sendMessage = async () => {
      if (!input.value.trim() || isLoading.value) return;

      const userMessage = { role: 'user', content: input.value };
      messages.value.push(userMessage);
      input.value = '';
      isLoading.value = true;
      scrollToBottom();

      try {
        const apiUrl = import.meta.env.VITE_API_URL || 'https://top-tier-global-hub-ai-production.up.railway.app/v1/ai/infer';
        const response = await fetch(apiUrl, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            messages: messages.value.map(m => ({ role: m.role, content: m.content }))
          }),
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        const aiMessage = {
          role: 'assistant',
          content: data.content || data.message?.content || 'لم أتمكن من الحصول على إجابة.'
        };
        messages.value.push(aiMessage);
        scrollToBottom();
      } catch (error) {
        console.error('Error:', error);
        const errorMessage = {
          role: 'assistant',
          content: '⚠️ فشل الاتصال بالخادم. تأكد من أن الـ API يعمل.'
        };
        messages.value.push(errorMessage);
        scrollToBottom();
      } finally {
        isLoading.value = false;
      }
    };

    return {
      messages,
      input,
      isLoading,
      messagesContainer,
      sendMessage
    };
  }
};
</script>

<style scoped>
.main {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.chat-container {
  width: 100%;
  max-width: 800px;
  background: white;
  border-radius: 20px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
  display: flex;
  flex-direction: column;
  height: 90vh;
  max-height: 700px;
}

.header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 20px;
  border-radius: 20px 20px 0 0;
  text-align: center;
}

.header h1 {
  margin: 0;
  font-size: 24px;
}

.header p {
  margin: 5px 0 0;
  font-size: 14px;
  opacity: 0.9;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.message {
  padding: 12px 16px;
  border-radius: 12px;
  max-width: 80%;
  word-wrap: break-word;
  animation: fadeIn 0.3s ease-in;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.user-message {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  align-self: flex-end;
  text-align: right;
}

.ai-message {
  background: #f0f0f0;
  color: #333;
  align-self: flex-start;
}

.loading {
  padding: 12px 16px;
  border-radius: 12px;
  background: #f0f0f0;
  color: #666;
  align-self: flex-start;
  font-style: italic;
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.6;
  }
}

.input-area {
  display: flex;
  gap: 10px;
  padding: 20px;
  border-top: 1px solid #e0e0e0;
  background: #fafafa;
  border-radius: 0 0 20px 20px;
}

.input {
  flex: 1;
  padding: 12px 16px;
  border: 2px solid #e0e0e0;
  border-radius: 25px;
  font-size: 16px;
  outline: none;
  transition: border-color 0.3s;
}

.input:focus {
  border-color: #667eea;
}

.input:disabled {
  background: #f5f5f5;
  cursor: not-allowed;
}

.send-button {
  padding: 12px 30px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 25px;
  font-size: 16px;
  font-weight: bold;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.send-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
}

.send-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

@media (max-width: 768px) {
  .chat-container {
    height: 100vh;
    max-height: 100vh;
    border-radius: 0;
  }

  .header {
    border-radius: 0;
  }

  .input-area {
    border-radius: 0;
  }

  .message {
    max-width: 90%;
  }
}
</style>
