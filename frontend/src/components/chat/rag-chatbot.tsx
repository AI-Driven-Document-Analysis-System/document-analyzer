"use client"

import type React from "react"
import { useState, useRef, useEffect } from "react"
import { chatService, type ChatMessage as ServiceChatMessage } from "../../services/chatService"
import type { Message, ExpandedSections } from './types'
import { initialMessages, sampleDocuments, sampleChatHistory } from './data/sampleData'
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
  const [messages, setMessages] = useState<Message[]>(initialMessages)
  const [inputValue, setInputValue] = useState("")
  const [isTyping, setIsTyping] = useState(false)
  const [conversationId, setConversationId] = useState<string | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const chatContainerRef = useRef<HTMLDivElement>(null)
  const [expandedSections, setExpandedSections] = useState<ExpandedSections>({
    sources: true,
    history: false,
    knowledge: false
  })
  const [selectedMessageSources, setSelectedMessageSources] = useState<any[]>(() => {
    // Find the latest assistant message with sources
    const latestAssistantMessage = [...initialMessages].reverse().find(msg => msg.type === 'assistant' && msg.sources);
    return latestAssistantMessage?.sources || [];
  })

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

  return (
    <div className="bg-gray-50" style={{ height: '100vh', overflow: 'hidden' }}>
      <div className="flex" style={{ height: '100vh', overflow: 'hidden' }}>
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
          chatHistory={sampleChatHistory}
          selectedDocuments={selectedDocuments}
          documents={sampleDocuments}
          onShowDocumentModal={() => setShowDocumentModal(true)}
          onRemoveDocument={removeDocument}
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