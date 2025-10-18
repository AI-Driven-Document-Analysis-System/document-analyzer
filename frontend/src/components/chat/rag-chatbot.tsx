"use client"

import type React from "react"
import { useState, useRef, useEffect } from "react"
import { chatService, type ChatMessage as ServiceChatMessage } from '../../services/chatService'
import { streamingChatService } from '../../services/streamingChatService'
import type { Message, ExpandedSections, ChatHistory } from './types'
import { initialMessages } from './data/sampleData'
import { useDocumentManagement } from './hooks/useDocumentManagement'
import { useDocuments } from './hooks/useDocuments'
import { ChatMessage } from './components/ChatMessage'
import { TypingIndicator } from './components/TypingIndicator'
import { ChatInput } from './components/ChatInput'
import { Sidebar } from './components/sidebar/Sidebar'
import { DocumentModal } from './components/DocumentModal'
import { NewChatConfirmModal } from './components/NewChatConfirmModal'
import { ThemeProvider, useTheme } from './contexts/ThemeContext'

const API_BASE_URL = "http://localhost:8000"

function RAGChatbotContent() {
  // State for current user ID
  const [currentUserId, setCurrentUserId] = useState<string | null>(null)
  
  const [messages, setMessages] = useState<Message[]>([])
  
  const [inputValue, setInputValue] = useState("")
  const [isTyping, setIsTyping] = useState(false)
  const [isSending, setIsSending] = useState(false) // Prevent double submission
  const generatingMessageIdRef = useRef<string | null>(null) // Use ref instead of state - prevents re-render issues
  const [searchMode, setSearchMode] = useState<'standard' | 'rephrase' | 'multiple_queries'>('standard')
  const [selectedModel, setSelectedModel] = useState<{ provider: string; model: string; name: string } | undefined>({
    provider: 'groq',
    model: 'llama-3.1-8b-instant', 
    name: 'Llama-3.1-8b-instant'
  })
  const [useStreaming, setUseStreaming] = useState(true) // Enable streaming by default
  // Load conversation ID from localStorage (user-specific)
  const [conversationId, setConversationId] = useState<string | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const chatContainerRef = useRef<HTMLDivElement>(null)
  const [expandedSections, setExpandedSections] = useState<ExpandedSections>({
    sources: true,
    history: false,
    knowledge: false
  })
  const [selectedMessageSources, setSelectedMessageSources] = useState<any[]>([])

  // Chat history state
  const [chatHistory, setChatHistory] = useState<ChatHistory[]>([])
  const [isLoadingHistory, setIsLoadingHistory] = useState(true)
  const [isLoadingConversation, setIsLoadingConversation] = useState(false)

  // Delete confirmation state
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false)
  const [chatToDelete, setChatToDelete] = useState<{ id: string, title: string } | null>(null)
  
  // New chat loading state
  const [isCreatingNewChat, setIsCreatingNewChat] = useState(false)

  // New chat confirmation modal state
  const [showNewChatConfirm, setShowNewChatConfirm] = useState(false)
  const [pendingDocumentModal, setPendingDocumentModal] = useState(false)

  // Handle feedback from messages
  const handleFeedback = async (messageId: string, feedback: 'thumbs_up' | 'thumbs_down', reason?: string) => {
    console.log('Feedback received:', { messageId, feedback, reason })
    
    // TODO: Send feedback to backend for analytics
  }

  // Handle answer regeneration with different search methods
  const handleRegenerateAnswer = async (messageId: string, method: 'rephrase' | 'multiple_queries') => {
    if (isSending) return // Prevent multiple regenerations
    
    console.log('Regenerating answer:', { messageId, method })
    
    setIsSending(true) // Prevent double submission
    
    // Find the message to regenerate
    const messageIndex = messages.findIndex(msg => msg.id === messageId)
    if (messageIndex === -1) {
      setIsSending(false)
      return
    }
    
    // Find the user message that prompted this assistant response
    let userMessage: Message | null = null
    for (let i = messageIndex - 1; i >= 0; i--) {
      if (messages[i].type === 'user') {
        userMessage = messages[i]
        break
      }
    }
    
    if (!userMessage) {
      setIsSending(false)
      return
    }
    
    // Remove the assistant message we're regenerating
    const updatedMessages = messages.slice(0, messageIndex)
    setMessages(updatedMessages)
    setIsTyping(true)
    
    try {
      // Create placeholder message for streaming regeneration
      const assistantMessageId = Date.now().toString()
      generatingMessageIdRef.current = assistantMessageId
      const newAssistantMessage: Message = {
        id: assistantMessageId,
        type: "assistant",
        content: "",
        timestamp: new Date(),
        sources: [],
      }
      
      // Add empty assistant message that will be updated in real-time
      setMessages(prev => [...prev, newAssistantMessage])
      
      // Use streaming service for real-time regeneration
      await streamingChatService.sendStreamingMessage(
        userMessage.content,
        conversationId || undefined,
        method,
        selectedDocuments.length > 0 ? selectedDocuments : undefined,
        selectedModel,
        {
          onToken: (token) => {
            // Update the assistant message content in real-time
            setMessages((prev) => 
              prev.map(msg => 
                msg.id === assistantMessageId 
                  ? { ...msg, content: msg.content + token }
                  : msg
              )
            )
          },
          onSources: (sources) => {
            // Update sources when received
            generatingMessageIdRef.current = null
            setMessages((prev) => 
              prev.map(msg => 
                msg.id === assistantMessageId 
                  ? { ...msg, sources: sources }
                  : msg
              )
            )
            // Update sidebar sources
            setSelectedMessageSources(sources)
            setExpandedSections(prev => ({ ...prev, sources: true }))
          },
          onStart: () => {
            console.log('🚀 Regeneration streaming started')
          },
          onComplete: (response) => {
            console.log('✅ Regeneration completed')
            setIsTyping(false)
            setIsSending(false) // Re-enable sending
            generatingMessageIdRef.current = null
          },
          onError: (error) => {
            console.error('❌ Regeneration error:', error)
            setIsTyping(false)
            setIsSending(false) // Re-enable sending
            generatingMessageIdRef.current = null
            // Update message with error
            setMessages((prev) => 
              prev.map(msg => 
                msg.id === assistantMessageId 
                  ? { ...msg, content: `Error: ${error}` }
                  : msg
              )
            )
          }
        }
      )
      
    } catch (error) {
      console.error('Error regenerating answer:', error)
      
      // Show error message to user
      const errorMessage: Message = {
        id: Date.now().toString(),
        type: "assistant",
        content: "I apologize, but I encountered an error while regenerating the answer. Please try again.",
        timestamp: new Date(),
        sources: [],
      }
      
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsTyping(false)
      setIsSending(false) // Re-enable sending
      generatingMessageIdRef.current = null
    }
  }



  // Initialize user ID and load user-specific data
  useEffect(() => {
    const initializeUser = async () => {
      try {
        const userId = await chatService.getCurrentUserId()
        if (userId) {
          // If user ID changed, clear current state first
          if (currentUserId && currentUserId !== userId) {
            setMessages(initialMessages)
            setConversationId(null)
            setSelectedMessageSources([])
          }
          
          setCurrentUserId(userId)
          
          // Load user-specific messages from localStorage
          const userMessagesKey = `rag-chatbot-messages-${userId}`
          const savedMessages = localStorage.getItem(userMessagesKey)
          if (savedMessages) {
            try {
              const parsed = JSON.parse(savedMessages)
              const messagesWithDates = parsed.map((msg: any) => ({
                ...msg,
                timestamp: new Date(msg.timestamp)
              }))
              setMessages(messagesWithDates)
              
              // Set sources from latest assistant message
              const latestAssistantMessage = [...messagesWithDates].reverse().find(msg => msg.type === 'assistant' && msg.sources)
              if (latestAssistantMessage?.sources) {
                setSelectedMessageSources(latestAssistantMessage.sources)
              }
            } catch (error) {
              console.error('Error parsing saved messages:', error)
              setMessages(initialMessages)
            }
          } else {
            // No saved messages for this user, use initial messages
            setMessages(initialMessages)
          }
          
          // Load user-specific conversation ID
          const userConversationKey = `rag-chatbot-conversation-id-${userId}`
          const savedConversationId = localStorage.getItem(userConversationKey)
          if (savedConversationId) {
            setConversationId(savedConversationId)
          } else {
            setConversationId(null)
          }
        } else {
          // No user ID, reset to initial state
          setCurrentUserId(null)
          setMessages(initialMessages)
          setConversationId(null)
          setSelectedMessageSources([])
        }
      } catch (error) {
        console.error('Error initializing user:', error)
        // Reset to initial state on error
        setMessages(initialMessages)
        setConversationId(null)
        setSelectedMessageSources([])
      }
    }
    
    initializeUser()
  }, [currentUserId])

  // Save messages to localStorage whenever messages change (user-specific)
  useEffect(() => {
    if (typeof window !== 'undefined' && currentUserId && messages.length > 0 && messages !== initialMessages) {
      const userMessagesKey = `rag-chatbot-messages-${currentUserId}`
      localStorage.setItem(userMessagesKey, JSON.stringify(messages))
    }
  }, [messages, currentUserId])

  // Save conversation ID to localStorage whenever it changes (user-specific)
  useEffect(() => {
    if (typeof window !== 'undefined' && currentUserId) {
      const userConversationKey = `rag-chatbot-conversation-id-${currentUserId}`
      if (conversationId) {
        localStorage.setItem(userConversationKey, conversationId)
      } else {
        localStorage.removeItem(userConversationKey)
      }
    }
  }, [conversationId, currentUserId])

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
            timestamp: conv.created_at ? new Date(conv.created_at + 'Z').toLocaleString([], {
              year: 'numeric',
              month: 'short',
              day: 'numeric',
              hour: '2-digit',
              minute: '2-digit'
            }) : new Date().toLocaleString([], {
              year: 'numeric',
              month: 'short',
              day: 'numeric',
              hour: '2-digit',
              minute: '2-digit'
            }),
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
    clearAllDocuments,
    clearingDocuments
  } = useDocumentManagement()

  // Fetch documents from API
  const {
    documents,
    isLoading: documentsLoading,
    error: documentsError,
    refetch: refetchDocuments
  } = useDocuments()

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
    if (!inputValue.trim() || isSending) return

    setIsSending(true) // Prevent double submission
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
      // Send message to backend with selected documents for Knowledge Base mode
      console.log('🔍 FRONTEND: Sending message with selected documents:', {
        selectedDocuments: selectedDocuments,
        selectedDocumentsLength: selectedDocuments.length,
        selectedDocumentTypes: selectedDocuments.map(id => typeof id),
        selectedModel: selectedModel
      })
      
      // Create new assistant message for streaming
      const assistantMessageId = (Date.now() + 1).toString()
      generatingMessageIdRef.current = assistantMessageId
      const assistantMessage: Message = {
        id: assistantMessageId,
        type: "assistant",
        content: "",
        timestamp: new Date(),
        sources: [],
      }

      // Add empty assistant message that will be updated in real-time
      setMessages((prev) => [...prev, assistantMessage])

      // Use streaming service for real-time responses
      await streamingChatService.sendStreamingMessage(
        currentMessage,
        conversationId || undefined,
        searchMode,
        selectedDocuments.length > 0 ? selectedDocuments : undefined,
        selectedModel,
        {
          onStart: () => {
            console.log('🚀 Streaming started')
          },
          onToken: (token) => {
            // Update the assistant message content in real-time
            setMessages((prev) => 
              prev.map(msg => 
                msg.id === assistantMessageId 
                  ? { ...msg, content: msg.content + token }
                  : msg
              )
            )
          },
          onSources: (sources) => {
            // Update sources when received
            console.log('📚 STREAMING: Updating message sources:', sources.length, sources)
            // Stop spinner when sources received (response complete, before source extraction)
            setIsTyping(false)
            generatingMessageIdRef.current = null
            setMessages((prev) => 
              prev.map(msg => 
                msg.id === assistantMessageId 
                  ? { ...msg, sources: sources }
                  : msg
              )
            )
            // Update sidebar sources
            setSelectedMessageSources(sources)
            setExpandedSections(prev => ({ ...prev, sources: true }))
          },
          onComplete: (response) => {
            console.log('✅ Streaming completed')
            setIsSending(false) // Re-enable sending
            generatingMessageIdRef.current = null
            // Update conversation ID if needed
            if (response.conversation_id && response.conversation_id !== conversationId) {
              setConversationId(response.conversation_id)
              if (currentUserId) {
                localStorage.setItem(`rag-chatbot-conversation-id-${currentUserId}`, response.conversation_id)
              }
            }
          },
          onError: (error) => {
            console.error('❌ Streaming error:', error)
            setIsTyping(false) // Stop typing indicator
            setIsSending(false) // Re-enable sending
            generatingMessageIdRef.current = null
            // Update message with error
            setMessages((prev) => 
              prev.map(msg => 
                msg.id === assistantMessageId 
                  ? { ...msg, content: `Error: ${error}` }
                  : msg
              )
            )
          }
        }
      )

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
      setIsSending(false) // Re-enable sending
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
    setIsCreatingNewChat(true)
    
    try {
      // Create a new conversation on the backend
      const newConversation = await chatService.createConversation("New Chat")
      
      // Clear current conversation
      setMessages(initialMessages)
      setConversationId(newConversation?.conversation_id || null)
      setInputValue("")
      setSelectedMessageSources([])
      
      // Clear selected documents in Knowledge Base
      clearAllDocuments()
      
      // Clear user-specific localStorage
      if (typeof window !== 'undefined' && currentUserId) {
        localStorage.removeItem(`rag-chatbot-messages-${currentUserId}`)
        localStorage.removeItem(`rag-chatbot-conversation-id-${currentUserId}`)
      }
      
      // Reset sidebar sources to initial state
      const latestAssistantMessage = [...initialMessages].reverse().find(msg => msg.type === 'assistant' && msg.sources);
      if (latestAssistantMessage?.sources) {
        setSelectedMessageSources(latestAssistantMessage.sources)
        setExpandedSections(prev => ({ ...prev, sources: true }))
      }

      // If this was triggered by document modal request, open it
      if (pendingDocumentModal) {
        setPendingDocumentModal(false)
        setShowDocumentModal(true)
      }
    } catch (error) {
      console.error('Error creating new chat:', error)
      // Fallback to local reset if backend fails
      setMessages(initialMessages)
      setConversationId(null)
      setInputValue("")
      setSelectedMessageSources([])
      
      if (typeof window !== 'undefined' && currentUserId) {
        localStorage.removeItem(`rag-chatbot-messages-${currentUserId}`)
        localStorage.removeItem(`rag-chatbot-conversation-id-${currentUserId}`)
      }

      // If this was triggered by document modal request, open it anyway
      if (pendingDocumentModal) {
        setPendingDocumentModal(false)
        setShowDocumentModal(true)
      }
    } finally {
      setIsCreatingNewChat(false)
    }
  }

  const handleChatHistoryClick = async (chatId: string) => {
    // Immediately set the selected conversation ID for instant visual feedback
    setConversationId(chatId)
    setIsLoadingConversation(true)
    
    try {
      const conversationHistory = await chatService.getConversationHistory(chatId)
      
      if (conversationHistory?.messages && conversationHistory.messages.length > 0) {
        const transformedMessages: Message[] = conversationHistory.messages.map((msg: any) => ({
          id: msg.id || msg.message_id || Date.now().toString(),
          type: msg.role === 'user' ? 'user' : 'assistant',
          content: msg.content || msg.message,
          timestamp: new Date((msg.timestamp || msg.created_at || Date.now()) + (typeof (msg.timestamp || msg.created_at) === 'string' ? 'Z' : '')),
          sources: msg.sources || (msg.metadata?.sources) || []
        }))
        
        setMessages(transformedMessages)
        setInputValue("")
        
        if (typeof window !== 'undefined' && currentUserId) {
          localStorage.setItem(`rag-chatbot-messages-${currentUserId}`, JSON.stringify(transformedMessages))
          localStorage.setItem(`rag-chatbot-conversation-id-${currentUserId}`, chatId)
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
    } finally {
      setIsLoadingConversation(false)
    }
  }

  const handleDeleteChat = (chatId: string) => {
    // Find the chat to get its title for the confirmation dialog
    const chatToDelete = chatHistory.find(chat => chat.id === chatId)
    if (chatToDelete) {
      setChatToDelete({ id: chatId, title: chatToDelete.title })
      setShowDeleteConfirm(true)
    }
  }

  const confirmDeleteChat = async () => {
    if (!chatToDelete) return
    
    try {
      await chatService.deleteConversation(chatToDelete.id)
      
      // Remove the deleted chat from the chat history
      setChatHistory(prev => prev.filter(chat => chat.id !== chatToDelete.id))
      
      // If the deleted chat was the current conversation, reset to initial state
      if (conversationId === chatToDelete.id) {
        setMessages(initialMessages)
        setConversationId(null)
        setInputValue("")
        setSelectedMessageSources([])
        
        // Clear user-specific localStorage
        if (typeof window !== 'undefined' && currentUserId) {
          localStorage.removeItem(`rag-chatbot-messages-${currentUserId}`)
          localStorage.removeItem(`rag-chatbot-conversation-id-${currentUserId}`)
        }
        
        // Reset sidebar sources to initial state
        const latestAssistantMessage = [...initialMessages].reverse().find(msg => msg.type === 'assistant' && msg.sources);
        if (latestAssistantMessage?.sources) {
          setSelectedMessageSources(latestAssistantMessage.sources)
          setExpandedSections(prev => ({ ...prev, sources: true }))
        }
      }
    } catch (error) {
      console.error('Error deleting conversation:', error)
      // You could add a toast notification here to inform the user of the error
    } finally {
      // Close the confirmation dialog
      setShowDeleteConfirm(false)
      setChatToDelete(null)
    }
  }

  const cancelDeleteChat = () => {
    setShowDeleteConfirm(false)
    setChatToDelete(null)
  }

  // Check if current chat is new (only has initial assistant message)
  const isNewChat = () => {
    // A new chat has only the initial assistant message or no messages
    const userMessages = messages.filter(msg => msg.type === 'user')
    return userMessages.length === 0
  }

  // Handle document modal with new chat check
  const handleShowDocumentModal = () => {
    if (isNewChat()) {
      // It's a new chat, allow document selection
      setShowDocumentModal(true)
    } else {
      // There are existing messages, show confirmation modal
      setShowNewChatConfirm(true)
    }
  }

  // Handle new chat confirmation
  const handleNewChatConfirm = async () => {
    setShowNewChatConfirm(false)
    setPendingDocumentModal(true)
    await handleNewChat()
  }

  const handleNewChatCancel = () => {
    setShowNewChatConfirm(false)
    setPendingDocumentModal(false)
  }

  const { isDarkMode, toggleDarkMode } = useTheme()

  return (
    <div className={isDarkMode ? "bg-gray-900" : "bg-gray-50"} style={{ height: '100vh', overflow: 'hidden' }}>
      <div className="flex" style={{ height: '100vh', overflow: 'hidden', flexDirection: 'row' }}>
        {/* Main Chat Area */}
        <div style={{ flex: '1 1 0%', minWidth: '0', display: 'flex', flexDirection: 'column', backgroundColor: isDarkMode ? '#1a202c' : '#f8fafc' }}>
          <div className={`flex-1 flex flex-col`} style={{ position: 'relative', height: 'calc(100vh - 60px)', backgroundColor: isDarkMode ? '#2d3748' : 'white' }}>
            {/* Dark Mode Toggle */}
            <div style={{
              position: 'absolute',
              top: '16px',
              right: '16px',
              zIndex: 100
            }}>
              <button
                onClick={toggleDarkMode}
                style={{
                  padding: '8px',
                  borderRadius: '8px',
                  border: `1px solid ${isDarkMode ? '#374151' : '#e5e7eb'}`,
                  backgroundColor: isDarkMode ? '#374151' : '#f9fafb',
                  color: isDarkMode ? '#f9fafb' : '#374151',
                  cursor: 'pointer',
                  fontSize: '14px',
                  transition: 'all 0.2s ease'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.backgroundColor = isDarkMode ? '#4b5563' : '#f3f4f6'
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.backgroundColor = isDarkMode ? '#374151' : '#f9fafb'
                }}
              >
                <i className={`fas ${isDarkMode ? 'fa-sun' : 'fa-moon'}`}></i>
              </button>
            </div>
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
              {isLoadingConversation || isCreatingNewChat ? (
                <div style={{ 
                  display: 'flex', 
                  flexDirection: 'column', 
                  alignItems: 'center', 
                  justifyContent: 'center', 
                  height: '200px',
                  color: isDarkMode ? '#9ca3af' : '#6b7280'
                }}>
                  <div style={{
                    width: '40px',
                    height: '40px',
                    border: `3px solid ${isDarkMode ? '#374151' : '#e5e7eb'}`,
                    borderTop: '3px solid #3b82f6',
                    borderRadius: '50%',
                    animation: 'spin 1s linear infinite',
                    marginBottom: '16px'
                  }}></div>
                  <p style={{ margin: 0, fontSize: '14px' }}>
                    {isCreatingNewChat ? 'Creating new chat...' : 'Loading conversation...'}
                  </p>
                  <style jsx>{`
                    @keyframes spin {
                      0% { transform: rotate(0deg); }
                      100% { transform: rotate(360deg); }
                    }
                  `}</style>
                </div>
              ) : (
                <>
                  {messages.map((message, index) => {
                    // Show spinner on the message that's currently being generated
                    const shouldShowSpinner = message.id === generatingMessageIdRef.current
                    
                    return (
                      <div key={message.id} style={{ marginBottom: '24px' }}>
                        <ChatMessage 
                          message={message} 
                          onSourcesClick={handleSourcesClick}
                          onFeedback={handleFeedback}
                          onRephrasedQueryClick={() => {}}
                          onRegenerateAnswer={handleRegenerateAnswer}
                          isDarkMode={isDarkMode}
                          isGenerating={shouldShowSpinner}
                        />
                      </div>
                    )
                  })}

                  <div ref={messagesEndRef} />
                </>
              )}
            </div>

            <ChatInput 
              inputValue={inputValue}
              setInputValue={setInputValue}
              onSendMessage={handleSendMessage}
              isTyping={isTyping}
              onKeyPress={handleKeyPress}
              searchMode={searchMode}
              setSearchMode={setSearchMode}
              selectedModel={selectedModel}
              setSelectedModel={setSelectedModel}
              isDarkMode={isDarkMode}
            />
          </div>
        </div>

        <Sidebar 
          expandedSections={expandedSections}
          toggleSection={toggleSection}
          selectedMessageSources={selectedMessageSources}
          chatHistory={chatHistory}
          selectedDocuments={selectedDocuments}
          documents={documents}
          onShowDocumentModal={handleShowDocumentModal}
          onRemoveDocument={removeDocument}
          onClearAllDocuments={clearAllDocuments}
          onNewChat={handleNewChat}
          onChatHistoryClick={handleChatHistoryClick}
          onDeleteChat={handleDeleteChat}
          selectedChatId={conversationId || undefined}
          documentsLoading={documentsLoading}
          documentsError={documentsError}
          clearingDocuments={clearingDocuments}
        />
      </div>
      
      <DocumentModal 
        showModal={showDocumentModal}
        onClose={() => setShowDocumentModal(false)}
        documents={documents}
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
        isLoading={documentsLoading}
        error={documentsError}
      />

      <NewChatConfirmModal 
        showModal={showNewChatConfirm}
        onClose={handleNewChatCancel}
        onConfirm={handleNewChatConfirm}
      />

      {/* Delete Confirmation Modal */}
      {showDeleteConfirm && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: 'rgba(0, 0, 0, 0.5)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000
        }}>
          <div style={{
            backgroundColor: isDarkMode ? '#1f2937' : 'white',
            borderRadius: '8px',
            padding: '24px',
            maxWidth: '400px',
            width: '90%',
            boxShadow: '0 10px 25px rgba(0, 0, 0, 0.2)'
          }}>
            <div style={{ marginBottom: '16px' }}>
              <h3 style={{ 
                margin: '0 0 8px 0', 
                fontSize: '18px', 
                fontWeight: '600', 
                color: isDarkMode ? '#f9fafb' : '#1f2937' 
              }}>
                Delete Conversation
              </h3>
              <p style={{ 
                margin: 0, 
                fontSize: '14px', 
                color: isDarkMode ? '#9ca3af' : '#6b7280',
                lineHeight: '1.5'
              }}>
                Are you sure you want to delete "{chatToDelete?.title}"? This action cannot be undone.
              </p>
            </div>
            
            <div style={{ 
              display: 'flex', 
              gap: '12px', 
              justifyContent: 'flex-end' 
            }}>
              <button
                onClick={cancelDeleteChat}
                style={{
                  padding: '8px 16px',
                  border: `1px solid ${isDarkMode ? '#374151' : '#d1d5db'}`,
                  borderRadius: '6px',
                  backgroundColor: isDarkMode ? '#374151' : 'white',
                  color: isDarkMode ? '#f9fafb' : '#374151',
                  fontSize: '14px',
                  fontWeight: '500',
                  cursor: 'pointer',
                  transition: 'all 0.2s ease'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.backgroundColor = isDarkMode ? '#4b5563' : '#f9fafb'
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.backgroundColor = isDarkMode ? '#374151' : 'white'
                }}
              >
                Cancel
              </button>
              <button
                onClick={confirmDeleteChat}
                style={{
                  padding: '8px 16px',
                  border: 'none',
                  borderRadius: '6px',
                  backgroundColor: '#ef4444',
                  color: 'white',
                  fontSize: '14px',
                  fontWeight: '500',
                  cursor: 'pointer',
                  transition: 'all 0.2s ease'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.backgroundColor = '#dc2626'
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.backgroundColor = '#ef4444'
                }}
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export function RAGChatbot() {
  return (
    <ThemeProvider>
      <RAGChatbotContent />
    </ThemeProvider>
  )
}