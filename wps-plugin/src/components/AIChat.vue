<template>
  <div class="ai-chat-wrapper">
    <div class="chat-header">
      <div class="chat-header-left">
        <span class="chat-icon">🤖</span>
        <span class="chat-title">AI 助手</span>
      </div>
      <div class="chat-header-right">
        <button class="logout-btn" @click="handleLogout">退出登录</button>
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
                  class="source-item"
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
          <select v-model="selectedAgentId">
            <option value="">选择 Agent</option>
            <option v-for="agent in agents" :key="agent.id" :value="agent.id">
              {{ agent.name }}
            </option>
          </select>
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
</template>

<script setup lang="ts">
import { ref, watch, nextTick, computed, onMounted } from 'vue'
import axios from '../axios'
import { marked } from 'marked'

const emit = defineEmits(['logout'])

const isMaximized = ref(false)
const messagesRef = ref<HTMLElement | null>(null)
const textareaRef = ref<HTMLTextAreaElement | null>(null)
const attachmentInputRef = ref<HTMLInputElement | null>(null)
const openclawAttachments = ref<File[]>([])
const showSessionList = ref(false)
const sessions = ref<any[]>([])
const currentSession = ref<any>(null)
const messages = ref<any[]>([])
const inputMessage = ref('')
const isLoading = ref(false)
const knowledgeBases = ref<any[]>([])
const selectedKBId = ref<string>('')
const chatMode = ref<'builtin' | 'openclaw'>('builtin')
const agents = ref<any[]>([])
const selectedAgentId = ref<string>('')

const canSend = computed(() => {
  if (chatMode.value === 'builtin') {
    return selectedKBId.value !== ''
  } else {
    return selectedAgentId.value !== '' && (inputMessage.value.trim() !== '' || openclawAttachments.value.length > 0)
  }
})

const handleLogout = () => {
  emit('logout')
}

const loadKnowledgeBases = async () => {
  try {
    const response = await axios.get('/documents/knowledge-bases/')
    knowledgeBases.value = response.data
    if (knowledgeBases.value.length > 0 && !selectedKBId.value) {
      selectedKBId.value = String(knowledgeBases.value[0].id)
    }
  } catch (error) {
    console.error('Failed to load knowledge bases:', error)
  }
}

const loadAgents = async () => {
  try {
    const response = await axios.get('/openclaw/agents/')
    if (response.data.success) {
      agents.value = response.data.data || []
      if (agents.value.length > 0 && !selectedAgentId.value) {
        selectedAgentId.value = String(agents.value[0].id)
      }
    }
  } catch (error) {
    console.error('Failed to load agents:', error)
  }
}

const loadSessions = async () => {
  if (!selectedKBId.value) return
  try {
    const response = await axios.get('/documents/chat/sessions/', {
      params: { knowledge_base_id: selectedKBId.value }
    })
    sessions.value = response.data
  } catch (error) {
    console.error('Failed to load sessions:', error)
  }
}

const createNewSession = async () => {
  if (!selectedKBId.value) {
    alert('请先选择知识库')
    return
  }

  try {
    const response = await axios.post('/documents/chat/sessions/', {
      knowledge_base_id: parseInt(selectedKBId.value),
      title: '新对话'
    })
    currentSession.value = response.data
    messages.value = []
    showSessionList.value = false
  } catch (error) {
    console.error('Failed to create session:', error)
  }
}

const loadSession = async (session: any) => {
  currentSession.value = session
  showSessionList.value = false
  try {
    const response = await axios.get(`/documents/chat/sessions/${session.id}/`)
    messages.value = response.data.messages
  } catch (error) {
    console.error('Failed to load session:', error)
  }
}

const onKBChange = async () => {
  await loadSessions()
  if (sessions.value.length > 0) {
    await loadSession(sessions.value[0])
  } else {
    currentSession.value = null
    messages.value = []
  }
}

const sendMessage = async () => {
  const hasAttachments = chatMode.value === 'openclaw' && openclawAttachments.value.length > 0
  if ((!inputMessage.value.trim() && !hasAttachments) || isLoading.value || !canSend.value) {
    return
  }

  isLoading.value = true
  let userContent = inputMessage.value.trim()
  if (!userContent && hasAttachments) {
    userContent = '请分析附件内容'
  }
  inputMessage.value = ''

  const tempUserMsg = {
    id: Date.now(),
    role: 'user',
    content: userContent,
    created_at: new Date().toISOString()
  }
  messages.value.push(tempUserMsg)
  await scrollToBottom()

  try {
    if (chatMode.value === 'builtin') {
      await sendBuiltinMessage(userContent, tempUserMsg.id)
    } else {
      await sendOpenClawMessage(userContent, tempUserMsg.id)
    }

    await scrollToBottom()
  } catch (error) {
    console.error('Failed to send message:', error)
    messages.value = messages.value.filter(m => m.id !== tempUserMsg.id)
    alert('发送消息失败，请重试')
  } finally {
    isLoading.value = false
  }
}

const sendBuiltinMessage = async (userContent: string, tempMsgId: number) => {
  if (!currentSession.value) {
    await createNewSession()
    if (!currentSession.value) {
      return
    }
  }

  const response = await axios.post(`/documents/chat/sessions/${currentSession.value.id}/send/`, {
    content: userContent
  })

  messages.value = messages.value.filter(m => m.id !== tempMsgId)
  messages.value.push(response.data.user_message)
  messages.value.push(response.data.assistant_message)

  await loadSessions()
}

const sendOpenClawMessage = async (userContent: string, tempMsgId: number) => {
  const formData = new FormData()
  formData.append('agent_id', selectedAgentId.value)
  formData.append('query', userContent)
  if (selectedKBId.value) {
    formData.append('knowledge_base_id', selectedKBId.value)
  }
  openclawAttachments.value.forEach((file) => {
    formData.append('attachments', file)
  })

  const response = await axios.post('/openclaw/chat/', formData)

  openclawAttachments.value = []
  if (attachmentInputRef.value) {
    attachmentInputRef.value.value = ''
  }

  messages.value = messages.value.filter(m => m.id !== tempMsgId)

  messages.value.push({
    id: Date.now() - 1,
    role: 'user',
    content: userContent,
    created_at: new Date().toISOString()
  })

  messages.value.push({
    id: Date.now(),
    role: 'assistant',
    content: response.data.data?.response || response.data.data || '未获取到响应',
    created_at: new Date().toISOString()
  })
}

const handleAttachmentChange = (event: Event) => {
  const target = event.target as HTMLInputElement
  const files = target.files ? Array.from(target.files) : []
  openclawAttachments.value = files
}

const removeAttachment = (index: number) => {
  openclawAttachments.value.splice(index, 1)
}

const formatFileSize = (bytes: number): string => {
  if (bytes < 1024) return `${bytes} B`
  const kb = bytes / 1024
  if (kb < 1024) return `${kb.toFixed(1)} KB`
  const mb = kb / 1024
  if (mb < 1024) return `${mb.toFixed(1)} MB`
  const gb = mb / 1024
  return `${gb.toFixed(1)} GB`
}

const formatMarkdown = (content: string): string => {
  if (!content) return ''
  return marked.parse(content, { breaks: true, gfm: true }) as string
}

const formatTime = (dateStr: string): string => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const scrollToBottom = async () => {
  await nextTick()
  if (messagesRef.value) {
    messagesRef.value.scrollTop = messagesRef.value.scrollHeight
  }
}

watch(chatMode, async (newMode) => {
  if (newMode === 'openclaw') {
    await loadAgents()
  }
})

onMounted(async () => {
  await loadKnowledgeBases()
  await loadSessions()
  if (chatMode.value === 'openclaw') {
    await loadAgents()
  }
})
</script>

<style scoped>
.ai-chat-wrapper {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  background: white;
  overflow: hidden;
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 16px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  flex-shrink: 0;
}

.chat-header-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.chat-header-right {
  display: flex;
  gap: 8px;
}

.chat-icon {
  font-size: 20px;
}

.chat-title {
  font-size: 15px;
  font-weight: 500;
}

.logout-btn {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: white;
  font-size: 12px;
  cursor: pointer;
  padding: 6px 12px;
  border-radius: 6px;
  transition: background 0.2s;
}

.logout-btn:hover {
  background: rgba(255, 255, 255, 0.3);
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
  padding: 10px 16px;
  border-bottom: 1px solid #eee;
}

.session-header h3 {
  margin: 0;
  font-size: 13px;
  color: #333;
}

.new-session-btn {
  padding: 6px 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 12px;
}

.session-items {
  flex: 1;
  overflow-y: auto;
}

.session-item {
  padding: 10px 16px;
  border-bottom: 1px solid #f5f5f5;
  cursor: pointer;
}

.session-item:hover {
  background: #f8f9fa;
}

.session-item.active {
  background: #e8f0fe;
  border-left: 3px solid #667eea;
}

.session-title {
  font-size: 13px;
  font-weight: 500;
  color: #333;
  margin-bottom: 3px;
}

.session-meta {
  display: flex;
  gap: 8px;
  font-size: 11px;
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
  gap: 10px;
}

.empty-chat {
  text-align: center;
  padding: 40px 20px;
  color: #888;
}

.empty-icon {
  font-size: 40px;
  margin-bottom: 10px;
}

.message {
  display: flex;
  gap: 8px;
}

.message.user {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  flex-shrink: 0;
}

.message.user .message-avatar {
  background: #e3f2fd;
}

.message.assistant .message-avatar {
  background: #f3e5f5;
}

.message-content {
  max-width: 75%;
}

.message.user .message-content {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.message-text {
  padding: 8px 12px;
  border-radius: 10px;
  line-height: 1.5;
  word-wrap: break-word;
  font-size: 13px;
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
  margin: 5px 0;
}

.message-text :deep(pre) {
  background: #2d2d2d;
  color: #ccc;
  padding: 8px;
  border-radius: 6px;
  overflow-x: auto;
  margin: 8px 0;
}

.message-text :deep(code) {
  background: rgba(0, 0, 0, 0.1);
  padding: 2px 5px;
  border-radius: 4px;
  font-family: monospace;
  font-size: 12px;
}

.message.user .message-text :deep(code) {
  background: rgba(255, 255, 255, 0.2);
}

.sources {
  margin-top: 6px;
  padding: 6px 10px;
  background: #f8f9fa;
  border-radius: 6px;
  font-size: 11px;
}

.sources-title {
  font-weight: 500;
  color: #555;
  margin-bottom: 5px;
}

.source-item {
  display: flex;
  justify-content: space-between;
  padding: 3px 0;
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
  padding: 8px 10px;
}

.typing-indicator span {
  width: 6px;
  height: 6px;
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
    transform: translateY(-4px);
  }
}

.chat-footer {
  padding: 10px 14px;
  border-top: 1px solid #eee;
  flex-shrink: 0;
}

.top-selectors {
  display: flex;
  gap: 10px;
  margin-bottom: 8px;
  align-items: center;
  flex-wrap: wrap;
}

.mode-selector {
  display: flex;
  gap: 10px;
  flex-shrink: 0;
}

.mode-selector label {
  display: flex;
  align-items: center;
  gap: 4px;
  cursor: pointer;
  font-size: 12px;
  color: #555;
}

.kb-selector,
.agent-selector {
  flex: 1;
  min-width: 100px;
}

.kb-selector select,
.agent-selector select {
  width: 100%;
  padding: 6px 10px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 12px;
  outline: none;
}

.kb-selector select:focus,
.agent-selector select:focus {
  border-color: #667eea;
}

.attachment-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-bottom: 6px;
}

.attachment-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 5px 8px;
  border: 1px solid #eee;
  border-radius: 6px;
  background: #fbfbff;
  font-size: 11px;
}

.attachment-item button {
  border: none;
  background: transparent;
  color: #d23f3f;
  cursor: pointer;
  font-size: 14px;
  padding: 0;
}

.input-area {
  display: flex;
  gap: 8px;
  align-items: flex-end;
}

.attachment-uploader {
  flex-shrink: 0;
}

.attachment-label {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 34px;
  height: 34px;
  border: 1px dashed #667eea;
  border-radius: 6px;
  color: #667eea;
  font-size: 18px;
  cursor: pointer;
}

.attachment-label:hover {
  background: #f0f2ff;
}

.attachment-label input[type="file"] {
  display: none;
}

.input-area textarea {
  flex: 1;
  padding: 8px 10px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 13px;
  resize: none;
  outline: none;
  max-height: 80px;
  font-family: inherit;
}

.input-area textarea:focus {
  border-color: #667eea;
}

.send-btn {
  padding: 8px 16px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
  font-weight: 500;
  transition: transform 0.2s, opacity 0.2s;
  height: 34px;
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
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
  color: #555;
}
</style>
