"use client"

import type React from "react"
import { useState, useRef, useEffect } from "react"
import { chatService, type ChatMessage as ServiceChatMessage } from "../../services/chatService"
import type { Message, ExpandedSections, ChatHistory } from './types'
import { initialMessages, sampleDocuments } from './data/sampleData'
import { useDocumentManagement } from './hooks/useDocumentManagement'
import { ChatMessage } from './components/ChatMessage'
import { TypingIndicator } from './components/TypingIndicator'
import { ChatInput } from './components/ChatInput'
import { Sidebar } from './components/sidebar/Sidebar'
import { DocumentModal } from './components/DocumentModal'

// Test user ID from database
const TEST_USER_ID = "79d0bed5-c1c1-4faf-82d4-fed1a28472d5"
const API_BASE_URL = "http://localhost:8000"

export function RAGChatbot() {
  // Load messages from localStorage or use initial messages
  const [messages, setMessages] = useState<Message[]>(() => {
    if (typeof window !== 'undefined') {
      const savedMessages = localStorage.getItem('rag-chatbot-messages')
      if (savedMessages) {
        try {
          const parsed = JSON.parse(savedMessages)
          // Convert timestamp strings back to Date objects
          return parsed.map((msg: any) => ({
            ...msg,
            timestamp: new Date(msg.timestamp)
          }))
        } catch (error) {
          console.error('Error parsing saved messages:', error)
        }
      }
    }
    return initialMessages
  })
  
  const [inputValue, setInputValue] = useState("")
  const [isTyping, setIsTyping] = useState(false)
  
  // Load conversation ID from localStorage
  const [conversationId, setConversationId] = useState<string | null>(() => {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('rag-chatbot-conversation-id')
    }
    return null
  })
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const chatContainerRef = useRef<HTMLDivElement>(null)
  const [expandedSections, setExpandedSections] = useState<ExpandedSections>({
    sources: true,
    history: false,
    knowledge: false
  })
  const [selectedMessageSources, setSelectedMessageSources] = useState<any[]>(() => {
    // Find the latest assistant message with sources from current messages
    const currentMessages = (() => {
      if (typeof window !== 'undefined') {
        const savedMessages = localStorage.getItem('rag-chatbot-messages')
        if (savedMessages) {
          try {
            return JSON.parse(savedMessages)
          } catch (error) {
            return initialMessages
          }
        }
      }
      return initialMessages
    })()
    
    const latestAssistantMessage = [...currentMessages].reverse().find(msg => msg.type === 'assistant' && msg.sources);
    return latestAssistantMessage?.sources || [];
  })

  // Chat history state
  const [chatHistory, setChatHistory] = useState<ChatHistory[]>([])
  const [isLoadingHistory, setIsLoadingHistory] = useState(true)

  // Save messages to localStorage whenever messages change
  useEffect(() => {
    if (typeof window !== 'undefined') {
      localStorage.setItem('rag-chatbot-messages', JSON.stringify(messages))
    }
  }, [messages])

  // Save conversation ID to localStorage whenever it changes
  useEffect(() => {
    if (typeof window !== 'undefined') {
      if (conversationId) {
        localStorage.setItem('rag-chatbot-conversation-id', conversationId)
      } else {
        localStorage.removeItem('rag-chatbot-conversation-id')
      }
    }
  }, [conversationId])

  // Fetch chat history from database on component mount
  useEffect(() => {
    const fetchChatHistory = async () => {
      try {
        setIsLoadingHistory(true)
        const response = await chatService.listConversations()
        
        if (response.conversations && Array.isArray(response.conversations)) {
          // Backend now filters empty conversations efficiently
          const transformedHistory: ChatHistory[] = response.conversations.map((conv: any) => ({
            id: conv.id,
            title: conv.title || 'Untitled Chat',
            timestamp: conv.created_at || new Date().toISOString(),
            messageCount: conv.message_count || 0
          }))
          
          setChatHistory(transformedHistory)
        }
      } catch (error) {
        console.error('Error fetching chat history:', error)
        setChatHistory([]) // Set empty array on error
      } finally {
        setIsLoadingHistory(false)
      }
    }

    fetchChatHistory()
  }, [])

  // Document management using custom hook
  const {
    showDocumentModal,
    setShowDocumentModal,
    selectedDocuments,
    documentFilter,
    setDocumentFilter,
    documentSearch,
    setDocumentSearch,
    sortDate,
    setSortDate,
    sortSize,
    setSortSize,
    toggleDocumentSelection,
    removeDocument,
    clearAllDocuments
  } = useDocumentManagement()

  const toggleSection = (section: keyof ExpandedSections) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }))
  }

  const scrollChatToBottom = () => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight
    }
  }

  useEffect(() => {
    scrollChatToBottom()
  }, [messages])

  // Reset page to top and disable body scroll when component mounts
  useEffect(() => {
    // Reset page to top
    window.scrollTo(0, 0)

    // Save original overflow values
    const originalBodyOverflow = document.body.style.overflow
    const originalHtmlOverflow = document.documentElement.style.overflow

    // Disable scrolling
    document.body.style.overflow = 'hidden'
    document.documentElement.style.overflow = 'hidden'

    // Cleanup function to restore original values
    return () => {
      document.body.style.overflow = originalBodyOverflow
      document.documentElement.style.overflow = originalHtmlOverflow
    }
  }, [])

  const handleSendMessage = async () => {
    if (!inputValue.trim()) return

    const userMessage: Message = {
      id: Date.now().toString(),
      type: "user",
      content: inputValue,
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, userMessage])
    const currentMessage = inputValue
    setInputValue("")
    setIsTyping(true)

    try {
      // Send message to backend
      const response = await chatService.sendMessage(currentMessage, conversationId || undefined)

      // Update conversation ID if this is a new conversation
      if (!conversationId && response.conversation_id) {
        setConversationId(response.conversation_id)
      }

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: "assistant",
        content: response.response,
        timestamp: new Date(),
        sources: response.sources || [],
      }

      setMessages((prev) => [...prev, assistantMessage])

      // Update selected message sources for sidebar
      if (response.sources && response.sources.length > 0) {
        setSelectedMessageSources(response.sources)
        setExpandedSections(prev => ({ ...prev, sources: true }))
      }

    } catch (error) {
      console.error('Error sending message:', error)

      // Show error message to user
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: "assistant",
        content: "I apologize, but I'm currently unable to process your request due to a technical issue. Please try again later.",
        timestamp: new Date(),
        sources: [],
      }

      setMessages((prev) => [...prev, errorMessage])
    } finally {
      setIsTyping(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  const handleSourcesClick = (sources: any[]) => {
    setSelectedMessageSources(sources)
    setExpandedSections(prev => ({ ...prev, sources: true }))
  }

  const handleNewChat = async () => {
    try {
      // Create a new conversation on the backend
      const newConversation = await chatService.createConversation("New Chat")
      
      // Clear current conversation
      setMessages(initialMessages)
      setConversationId(newConversation?.conversation_id || null)
      setInputValue("")
      setSelectedMessageSources([])
      
      // Clear localStorage
      if (typeof window !== 'undefined') {
        localStorage.removeItem('rag-chatbot-messages')
        localStorage.removeItem('rag-chatbot-conversation-id')
      }
      
      // Reset sidebar sources to initial state
      const latestAssistantMessage = [...initialMessages].reverse().find(msg => msg.type === 'assistant' && msg.sources);
      if (latestAssistantMessage?.sources) {
        setSelectedMessageSources(latestAssistantMessage.sources)
        setExpandedSections(prev => ({ ...prev, sources: true }))
      }
    } catch (error) {
      console.error('Error creating new chat:', error)
      // Fallback to local reset if backend fails
      setMessages(initialMessages)
      setConversationId(null)
      setInputValue("")
      setSelectedMessageSources([])
      
      if (typeof window !== 'undefined') {
        localStorage.removeItem('rag-chatbot-messages')
        localStorage.removeItem('rag-chatbot-conversation-id')
      }
    }
  }

  const handleChatHistoryClick = async (chatId: string) => {
    // Immediately set the selected conversation ID for instant visual feedback
    setConversationId(chatId)
    
    try {
      const conversationHistory = await chatService.getConversationHistory(chatId)
      
      if (conversationHistory?.messages && conversationHistory.messages.length > 0) {
        const transformedMessages: Message[] = conversationHistory.messages.map((msg: any) => ({
          id: msg.id || msg.message_id || Date.now().toString(),
          type: msg.role === 'user' ? 'user' : 'assistant',
          content: msg.content || msg.message,
          timestamp: new Date(msg.timestamp || msg.created_at || Date.now()),
          sources: msg.sources || []
        }))
        
        setMessages(transformedMessages)
        setInputValue("")
        
        if (typeof window !== 'undefined') {
          localStorage.setItem('rag-chatbot-messages', JSON.stringify(transformedMessages))
          localStorage.setItem('rag-chatbot-conversation-id', chatId)
        }
        
        const latestAssistantMessage = [...transformedMessages].reverse().find(msg => msg.type === 'assistant' && msg.sources);
        if (latestAssistantMessage?.sources) {
          setSelectedMessageSources(latestAssistantMessage.sources)
          setExpandedSections(prev => ({ ...prev, sources: true }))
        } else {
          setSelectedMessageSources([])
        }
      }
    } catch (error) {
      console.error('Error loading conversation history:', error)
      const errorMessage: Message = {
        id: Date.now().toString(),
        type: "assistant",
        content: "Sorry, I couldn't load this conversation. Please try again.",
        timestamp: new Date(),
        sources: [],
      }
      setMessages([errorMessage])
    }
  }

  return (
    <div className="bg-gray-50" style={{ height: '100vh', overflow: 'hidden' }}>
      <div className="flex" style={{ height: '100vh', overflow: 'hidden', flexDirection: 'row' }}>
        {/* Main Chat Area */}
        <div className="flex-1 flex flex-col" style={{ backgroundColor: '#f8fafc' }}>
          <div className="flex-1 flex flex-col bg-white" style={{ position: 'relative', height: 'calc(100vh - 60px)' }}>
            <div 
              ref={chatContainerRef}
              data-chat-messages="true"
              style={{ 
                flex: 1, 
                overflowY: 'auto', 
                overflowX: 'hidden',
                padding: '16px',
                paddingBottom: '80px',
                overscrollBehavior: 'contain',
                scrollBehavior: 'smooth'
              }}
              onWheel={(e) => {
                const element = e.currentTarget;
                const { scrollTop, scrollHeight, clientHeight } = element;
                
                // Prevent scrolling beyond content
                if (e.deltaY > 0 && scrollTop >= scrollHeight - clientHeight) {
                  e.preventDefault();
                }
                if (e.deltaY < 0 && scrollTop <= 0) {
                  e.preventDefault();
                }
              }}
            >
              {messages.map((message) => (
                <div key={message.id} style={{ marginBottom: '24px' }}>
                  <ChatMessage 
                    message={message} 
                    onSourcesClick={handleSourcesClick}
                  />
                </div>
              ))}

              {isTyping && <TypingIndicator />}
              <div ref={messagesEndRef} />
            </div>

            <ChatInput 
              inputValue={inputValue}
              setInputValue={setInputValue}
              onSendMessage={handleSendMessage}
              isTyping={isTyping}
              onKeyPress={handleKeyPress}
            />
          </div>
        </div>

        <Sidebar 
          expandedSections={expandedSections}
          toggleSection={toggleSection}
          selectedMessageSources={selectedMessageSources}
          chatHistory={chatHistory}
          selectedDocuments={selectedDocuments}
          documents={sampleDocuments}
          onShowDocumentModal={() => setShowDocumentModal(true)}
          onRemoveDocument={removeDocument}
          onNewChat={handleNewChat}
          onChatHistoryClick={handleChatHistoryClick}
          selectedChatId={conversationId || undefined}
        />
      </div>
      
      <DocumentModal 
        showModal={showDocumentModal}
        onClose={() => setShowDocumentModal(false)}
        documents={sampleDocuments}
        selectedDocuments={selectedDocuments}
        documentFilter={documentFilter}
        setDocumentFilter={setDocumentFilter}
        documentSearch={documentSearch}
        setDocumentSearch={setDocumentSearch}
        sortDate={sortDate}
        setSortDate={setSortDate}
        sortSize={sortSize}
        setSortSize={setSortSize}
        onToggleDocumentSelection={toggleDocumentSelection}
        onClearAllDocuments={clearAllDocuments}
      />
    </div>
  )
}