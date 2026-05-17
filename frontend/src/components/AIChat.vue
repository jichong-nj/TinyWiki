<template>
  <div class="ai-chat-overlay" v-if="isOpen">
    <div class="ai-chat-panel" :class="{ maximized: isMaximized }">
      <div class="chat-header">
        <div class="chat-header-left">
          <span class="chat-icon">🤖</span>
          <span class="chat-title">AI 助手</span>
        </div>
        <div class="chat-header-right">
          <button class="maximize-btn" @click="toggleMaximize">
            {{ isMaximized ? '↩' : '⛶' }}
          </button>
          <button class="close-btn" @click="closeChat">×</button>
        </div>
      </div>
      
      <div class="chat-body">
        <div class="session-list" v-if="showSessionList && chatMode === 'builtin'">
          <div class="session-header">
            <h3>会话列表</h3>
            <button class="new-session-btn" @click="createNewSession">
              + 新会话
            </button>
          </div>
          <div class="session-items">
            <div 
              v-for="session in sessions" 
              :key="session.id"
              class="session-item"
              :class="{ active: currentSession?.id === session.id }"
              @click="loadSession(session)"
            >
              <div class="session-title">{{ session.title }}</div>
              <div class="session-meta">
                <span class="session-kb">{{ session.knowledge_base_name }}</span>
                <span class="session-time">{{ formatTime(session.updated_at) }}</span>
              </div>
            </div>
          </div>
        </div>
        
        <div class="chat-messages" v-else ref="messagesRef">
          <div class="message-list">
            <div v-if="messages.length === 0" class="empty-chat">
              <div class="empty-icon">💬</div>
              <p>选择知识库和 Agent 开始对话</p>
            </div>
            
            <div v-for="msg in messages" :key="msg.id" class="message" :class="msg.role">
              <div class="message-avatar">
                <span v-if="msg.role === 'user'">🧑</span>
                <span v-else>🤖</span>
              </div>
              <div class="message-content">
                <div class="message-text" v-html="formatMarkdown(msg.content)"></div>
                
                <div v-if="msg.role === 'assistant' && msg.retrieved_documents" class="sources">
                  <div class="sources-title">参考文档：</div>
                  <div 
                    v-for="(doc, idx) in msg.retrieved_documents" 
                    :key="idx"
                    class="source-item"弹
                  >
                    <span class="source-title">{{ doc.title }}</span>
                    <span class="source-score">相关性: {{ (doc.score * 100).toFixed(0) }}%</span>
                  </div>
                </div>
              </div>
            </div>
            
            <div v-if="isLoading" class="message assistant">
              <div class="message-avatar">🤖</div>
              <div class="message-content">
                <div class="typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div class="chat-footer" v-if="!(showSessionList && chatMode === 'builtin')">
        <div class="top-selectors">
          <div class="mode-selector">
            <label>
              <input type="radio" v-model="chatMode" value="builtin" />
              内置
            </label>
            <label>
              <input type="radio" v-model="chatMode" value="openclaw" />
              OpenClaw
            </label>
          </div>
          
          <div class="kb-selector" v-if="chatMode === 'builtin'">
            <select v-model="selectedKBId" @change="onKBChange">
              <option value="">选择知识库</option>
              <option v-for="kb in knowledgeBases" :key="kb.id" :value="kb.id">
                {{ kb.name }}
              </option>
            </select>
          </div>
          
          <div class="kb-selector" v-if="chatMode === 'openclaw'">
            <select v-model="selectedKBId">
              <option value="">知识库（可选）</option>
              <option v-for="kb in knowledgeBases" :key="kb.id" :value="kb.id">
                {{ kb.name }}
              </option>
            </select>
          </div>
          
          <div class="agent-selector" v-if="chatMode === 'openclaw'">
            <div class="custom-select-wrapper" :class="{ open: agentDropdownOpen }">
              <div class="custom-select-trigger" @click="agentDropdownOpen = !agentDropdownOpen">
                <span v-if="selectedAgent" class="selected-agent-display">
                  {{ selectedAgent.emoji }} {{ selectedAgent.display_name }}
                </span>
                <span v-else class="placeholder">选择 Agent</span>
                <span class="select-arrow"></span>
              </div>
              <transition name="dropdown">
                <div v-if="agentDropdownOpen" class="custom-select-dropdown">
                  <div 
                    v-for="agent in agents" 
                    :key="agent.id"
                    class="dropdown-item"
                    :class="{ active: selectedAgentId === agent.id }"
                    @click="selectAgent(agent)"
                  >
                    <span class="item-emoji">{{ agent.emoji }}</span>
                    <div class="item-info">
                      <span class="item-name">{{ agent.display_name }}</span>
                      <span class="item-theme" v-if="agent.theme">{{ agent.theme }}</span>
                    </div>
                  </div>
                </div>
              </transition>
            </div>
          </div>
        </div>

        <div class="attachment-list" v-if="openclawAttachments.length > 0">
          <div
            class="attachment-item"
            v-for="(file, index) in openclawAttachments"
            :key="file.name + file.size"
          >
            <span>{{ file.name }} ({{ formatFileSize(file.size) }})</span>
            <button type="button" @click="removeAttachment(index)">×</button>
          </div>
        </div>
        
        <div class="input-area">
          <div class="attachment-uploader" v-if="chatMode === 'openclaw'">
            <label class="attachment-label">
              <input
                type="file"
                multiple
                ref="attachmentInputRef"
                @change="handleAttachmentChange"
              />
              📎
            </label>
          </div>
          <textarea 
            v-model="inputMessage" 
            placeholder="输入问题或上传附件..." 
            @keydown.enter.prevent="sendMessage"
            rows="1"
            ref="textareaRef"
          ></textarea>
          <button 
            class="send-btn" 
            @click="sendMessage"
            :disabled="isLoading || !canSend"
          >
            发送
          </button>
        </div>
      </div>
      
      <div class="chat-footer" v-else>
        <button class="back-btn" @click="showSessionList = false">返回对话</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, nextTick, computed } from 'vue';
import axios from '../axios';
import { marked } from 'marked';

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  }
});

const emit = defineEmits(['update:modelValue']);

const isOpen = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
});

const isMaximized = ref(false);
const messagesRef = ref(null);
const textareaRef = ref(null);
const attachmentInputRef = ref(null);
const openclawAttachments = ref([]);
const showSessionList = ref(false);
const sessions = ref([]);
const currentSession = ref(null);
const messages = ref([]);
const inputMessage = ref('');
const isLoading = ref(false);
const knowledgeBases = ref([]);
const selectedKBId = ref(null);
const chatMode = ref('builtin');
const agents = ref([]);
const selectedAgentId = ref(null);
const agentDropdownOpen = ref(false);

const selectedAgent = computed(() => {
  return agents.value.find(a => a.id === selectedAgentId.value) || null;
});

const selectAgent = (agent) => {
  selectedAgentId.value = agent.id;
  agentDropdownOpen.value = false;
};

const canSend = computed(() => {
  if (chatMode.value === 'builtin') {
    return selectedKBId.value !== null && selectedKBId.value !== '';
  } else {
    return selectedAgentId.value !== null && selectedAgentId.value !== '' && (inputMessage.value.trim() !== '' || openclawAttachments.value.length > 0);
  }
});

const closeChat = () => {
  isOpen.value = false;
};

const toggleMaximize = () => {
  isMaximized.value = !isMaximized.value;
};

const loadKnowledgeBases = async () => {
  try {
    const response = await axios.get('/documents/knowledge-bases/');
    knowledgeBases.value = response.data;
    if (knowledgeBases.value.length > 0) {
      selectedKBId.value = knowledgeBases.value[0].id;
    }
  } catch (error) {
    console.error('Failed to load knowledge bases:', error);
  }
};

const loadAgents = async () => {
  try {
    const response = await axios.get('/openclaw/agents/');
    if (response.data.success) {
      agents.value = response.data.data || [];
      if (agents.value.length > 0) {
        selectedAgentId.value = agents.value[0].id;
      }
    }
  } catch (error) {
    console.error('Failed to load agents:', error);
  }
};

const loadSessions = async () => {
  try {
    const response = await axios.get('/documents/chat/sessions/', {
      params: { knowledge_base_id: selectedKBId.value }
    });
    sessions.value = response.data;
  } catch (error) {
    console.error('Failed to load sessions:', error);
  }
};

const createNewSession = async () => {
  if (!selectedKBId.value) {
    alert('请先选择知识库');
    return;
  }
  
  try {
    const response = await axios.post('/documents/chat/sessions/', {
      knowledge_base_id: selectedKBId.value,
      title: '新对话'
    });
    currentSession.value = response.data;
    messages.value = [];
    showSessionList.value = false;
  } catch (error) {
    console.error('Failed to create session:', error);
  }
};

const loadSession = async (session) => {
  currentSession.value = session;
  showSessionList.value = false;
  try {
    const response = await axios.get(`/documents/chat/sessions/${session.id}/`);
    messages.value = response.data.messages;
  } catch (error) {
    console.error('Failed to load session:', error);
  }
};

const onKBChange = async () => {
  await loadSessions();
  if (sessions.value.length > 0) {
    await loadSession(sessions.value[0]);
  } else {
    currentSession.value = null;
    messages.value = [];
  }
};

const sendMessage = async () => {
  const hasAttachments = chatMode.value === 'openclaw' && openclawAttachments.value.length > 0;
  if ((!inputMessage.value.trim() && !hasAttachments) || isLoading.value || !canSend.value) {
    return;
  }
  
  isLoading.value = true;
  let userContent = inputMessage.value.trim();
  if (!userContent && hasAttachments) {
    userContent = '请分析附件内容';
  }
  inputMessage.value = '';
  
  const tempUserMsg = {
    id: Date.now(),
    role: 'user',
    content: userContent,
    created_at: new Date().toISOString()
  };
  messages.value.push(tempUserMsg);
  await scrollToBottom();
  
  try {
    if (chatMode.value === 'builtin') {
      await sendBuiltinMessage(userContent, tempUserMsg.id);
    } else {
      await sendOpenClawMessage(userContent, tempUserMsg.id);
    }
    
    await scrollToBottom();
  } catch (error) {
    console.error('Failed to send message:', error);
    messages.value = messages.value.filter(m => m.id !== tempUserMsg.id);
    alert('发送消息失败，请重试');
  } finally {
    isLoading.value = false;
  }
};

const sendBuiltinMessage = async (userContent, tempMsgId) => {
  if (!currentSession.value) {
    await createNewSession();
    if (!currentSession.value) {
      return;
    }
  }
  
  const response = await axios.post(`/documents/chat/sessions/${currentSession.value.id}/send/`, {
    content: userContent
  });
  
  messages.value = messages.value.filter(m => m.id !== tempMsgId);
  messages.value.push(response.data.user_message);
  messages.value.push(response.data.assistant_message);
  
  await loadSessions();
};

const sendOpenClawMessage = async (userContent, tempMsgId) => {
  const formData = new FormData();
  formData.append('agent_id', selectedAgentId.value);
  formData.append('query', userContent);
  if (selectedKBId.value) {
    formData.append('knowledge_base_id', selectedKBId.value);
  }
  openclawAttachments.value.forEach((file) => {
    formData.append('attachments', file);
  });

  const response = await axios.post('/openclaw/chat/', formData);
  
  openclawAttachments.value = [];
  if (attachmentInputRef.value) {
    attachmentInputRef.value.value = '';
  }

  messages.value = messages.value.filter(m => m.id !== tempMsgId);
  
  messages.value.push({
    id: Date.now() - 1,
    role: 'user',
    content: userContent,
    created_at: new Date().toISOString()
  });
  
  messages.value.push({
    id: Date.now(),
    role: 'assistant',
    content: response.data.data?.response || response.data.data || '未获取到响应',
    created_at: new Date().toISOString()
  });
};

const handleAttachmentChange = (event) => {
  const files = event.target.files ? Array.from(event.target.files) : [];
  openclawAttachments.value = files;
};

const removeAttachment = (index) => {
  openclawAttachments.value.splice(index, 1);
};

const formatFileSize = (bytes) => {
  if (bytes < 1024) return `${bytes} B`;
  const kb = bytes / 1024;
  if (kb < 1024) return `${kb.toFixed(1)} KB`;
  const mb = kb / 1024;
  if (mb < 1024) return `${mb.toFixed(1)} MB`;
  const gb = mb / 1024;
  return `${gb.toFixed(1)} GB`;
};

const formatMarkdown = (content) => {
  if (!content) return '';
  return marked.parse(content, { breaks: true, gfm: true });
};

const formatTime = (dateStr) => {
  if (!dateStr) return '';
  const date = new Date(dateStr);
  return date.toLocaleDateString('zh-CN', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
};

const scrollToBottom = async () => {
  await nextTick();
  if (messagesRef.value) {
    messagesRef.value.scrollTop = messagesRef.value.scrollHeight;
  }
};

watch(chatMode, async (newMode) => {
  if (newMode === 'openclaw') {
    await loadAgents();
  }
});

watch(isOpen, async (val) => {
  if (val) {
    await loadKnowledgeBases();
    await loadSessions();
    if (chatMode.value === 'openclaw') {
      await loadAgents();
    }
  }
});
</script>

<style scoped>
.ai-chat-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;
}

.ai-chat-panel {
  width: 800px;
  max-width: 95vw;
  height: 70vh;
  max-height: 800px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.ai-chat-panel.maximized {
  width: 100%;
  height: 100%;
  max-width: 100%;
  max-height: 100%;
  border-radius: 0;
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  flex-shrink: 0;
}

.chat-header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.chat-header-right {
  display: flex;
  gap: 8px;
}

.chat-icon {
  font-size: 24px;
}

.chat-title {
  font-size: 16px;
  font-weight: 600;
}

.close-btn,
.maximize-btn {
  background: none;
  border: none;
  color: white;
  font-size: 24px;
  cursor: pointer;
  padding: 4px 12px;
  border-radius: 8px;
  transition: background 0.2s;
  line-height: 1;
}

.close-btn:hover,
.maximize-btn:hover {
  background: rgba(255, 255, 255, 0.2);
}

.chat-body {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.session-list {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.session-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 20px;
  border-bottom: 1px solid #eee;
}

.session-header h3 {
  margin: 0;
  font-size: 14px;
  color: #333;
}

.new-session-btn {
  padding: 8px 14px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 13px;
  transition: transform 0.2s;
}

.new-session-btn:hover {
  transform: translateY(-1px);
}

.session-items {
  flex: 1;
  overflow-y: auto;
}

.session-item {
  padding: 12px 20px;
  border-bottom: 1px solid #f5f5f5;
  cursor: pointer;
  transition: background 0.2s;
}

.session-item:hover {
  background: #f8f9fa;
}

.session-item.active {
  background: #e8f0fe;
  border-left: 4px solid #667eea;
}

.session-title {
  font-size: 14px;
  font-weight: 500;
  color: #333;
  margin-bottom: 4px;
}

.session-meta {
  display: flex;
  gap: 10px;
  font-size: 12px;
  color: #888;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
}

.message-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.empty-chat {
  text-align: center;
  padding: 40px 20px;
  color: #888;
}

.empty-icon {
  font-size: 40px;
  margin-bottom: 12px;
}

.message {
  display: flex;
  gap: 10px;
}

.message.user {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  flex-shrink: 0;
}

.message.user .message-avatar {
  background: #e3f2fd;
}

.message.assistant .message-avatar {
  background: #f3e5f5;
}

.message-content {
  max-width: 70%;
}

.ai-chat-panel.maximized .message-content {
  max-width: 85%;
}

.message.user .message-content {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.message-text {
  padding: 8px 12px;
  border-radius: 12px;
  line-height: 1.5;
  word-wrap: break-word;
  font-size: 14px;
}

.message.user .message-text {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-bottom-right-radius: 4px;
}

.message.assistant .message-text {
  background: #f5f5f5;
  color: #333;
  border-bottom-left-radius: 4px;
}

.message-text :deep(p) {
  margin: 6px 0;
}

.message-text :deep(pre) {
  background: #2d2d2d;
  color: #ccc;
  padding: 10px;
  border-radius: 8px;
  overflow-x: auto;
  margin: 10px 0;
}

.message-text :deep(code) {
  background: rgba(0, 0, 0, 0.1);
  padding: 2px 5px;
  border-radius: 4px;
  font-family: monospace;
  font-size: 13px;
}

.message.user .message-text :deep(code) {
  background: rgba(255, 255, 255, 0.2);
}

.sources {
  margin-top: 8px;
  padding: 8px 10px;
  background: #f8f9fa;
  border-radius: 8px;
  font-size: 12px;
}

.sources-title {
  font-weight: 600;
  color: #555;
  margin-bottom: 6px;
}

.source-item {
  display: flex;
  justify-content: space-between;
  padding: 4px 0;
  border-bottom: 1px solid #eee;
}

.source-item:last-child {
  border-bottom: none;
}

.source-title {
  color: #667eea;
  font-weight: 500;
}

.source-score {
  color: #888;
}

.typing-indicator {
  display: flex;
  gap: 4px;
  padding: 10px 12px;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  background: #888;
  border-radius: 50%;
  animation: typing 1.4s infinite;
}

.typing-indicator span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-indicator span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typing {
  0%, 60%, 100% {
    transform: translateY(0);
  }
  30% {
    transform: translateY(-6px);
  }
}

.chat-footer {
  padding: 10px 16px;
  border-top: 1px solid #eee;
  flex-shrink: 0;
}

.top-selectors {
  display: flex;
  gap: 12px;
  margin-bottom: 10px;
  align-items: center;
  flex-wrap: wrap;
}

.mode-selector {
  display: flex;
  gap: 12px;
  flex-shrink: 0;
}

.mode-selector label {
  display: flex;
  align-items: center;
  gap: 5px;
  cursor: pointer;
  font-size: 13px;
  color: #555;
}

.mode-selector input[type="radio"] {
  cursor: pointer;
}

.kb-selector,
.agent-selector {
  flex: 1;
  min-width: 140px;
}

.kb-selector select,
.agent-selector select {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 13px;
  outline: none;
}

.agent-selector {
  flex: 1;
  min-width: 140px;
  max-width: 100%;
  position: relative;
}

.custom-select-wrapper {
  position: relative;
  width: 100%;
  box-sizing: border-box;
}

.custom-select-trigger {
  width: 100%;
  padding: 8px 32px 8px 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 13px;
  outline: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: white;
  transition: border-color 0.2s;
  user-select: none;
  overflow: hidden;
  box-sizing: border-box;
}

.custom-select-trigger:hover {
  border-color: #bbb;
}

.custom-select-wrapper.open .custom-select-trigger {
  border-color: #667eea;
}

.selected-agent-display {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
  min-width: 0;
  flex: 1;
}

.selected-agent-display .emoji {
  flex-shrink: 0;
}

.placeholder {
  color: #999;
  flex: 1;
  min-width: 0;
}

.select-arrow {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  width: 0;
  height: 0;
  border-left: 5px solid transparent;
  border-right: 5px solid transparent;
  border-top: 6px solid #888;
  pointer-events: none;
}

.custom-select-dropdown {
  position: absolute;
  bottom: calc(100% + 4px);
  left: 0;
  width: 100%;
  background: white;
  border: 1px solid #ddd;
  border-radius: 8px;
  box-shadow: 0 -4px 12px rgba(0, 0, 0, 0.15);
  z-index: 1000;
  max-height: 300px;
  overflow-y: auto;
  box-sizing: border-box;
}

.dropdown-item {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 10px 12px;
  cursor: pointer;
  transition: background 0.15s;
  border-bottom: 1px solid #f5f5f5;
}

.dropdown-item:last-child {
  border-bottom: none;
}

.dropdown-item:hover {
  background: #f8f9fa;
}

.dropdown-item.active {
  background: #e8f0fe;
}

.item-emoji {
  font-size: 20px;
  flex-shrink: 0;
  line-height: 1.4;
}

.item-info {
  display: flex;
  flex-direction: column;
  gap: 3px;
  min-width: 0;
}

.item-name {
  font-size: 13px;
  font-weight: 500;
  color: #333;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.item-theme {
  font-size: 12px;
  color: #888;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* Dropdown transition */
.dropdown-enter-active,
.dropdown-leave-active {
  transition: opacity 0.15s ease, transform 0.15s ease;
}

.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}

.attachment-list {
  display: flex;
  flex-direction: column;
  gap: 5px;
  margin-bottom: 8px;
}

.attachment-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 6px 10px;
  border: 1px solid #eee;
  border-radius: 8px;
  background: #fbfbff;
  font-size: 12px;
}

.attachment-item button {
  border: none;
  background: transparent;
  color: #d23f3f;
  cursor: pointer;
  font-size: 16px;
  padding: 0;
}

.input-area {
  display: flex;
  gap: 10px;
  align-items: flex-end;
}

.attachment-uploader {
  flex-shrink: 0;
}

.attachment-label {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border: 1px dashed #667eea;
  border-radius: 8px;
  color: #667eea;
  font-size: 20px;
  cursor: pointer;
  transition: background 0.2s;
}

.attachment-label:hover {
  background: #f0f2ff;
}

.attachment-label input[type="file"] {
  display: none;
}

.input-area textarea {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 14px;
  resize: none;
  outline: none;
  max-height: 100px;
  font-family: inherit;
}

.input-area textarea:focus {
  border-color: #667eea;
}

.send-btn {
  padding: 8px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: transform 0.2s, opacity 0.2s;
  height: 36px;
}

.send-btn:hover:not(:disabled) {
  transform: translateY(-1px);
}

.send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.back-btn {
  width: 100%;
  padding: 10px;
  background: #f5f5f5;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 13px;
  color: #555;
  transition: background 0.2s;
}

.back-btn:hover {
  background: #e8e8e8;
}
</style>
