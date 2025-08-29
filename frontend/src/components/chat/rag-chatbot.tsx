"use client"

import type React from "react"
import { useState, useRef, useEffect } from "react"

interface Message {
  id: string
  type: "user" | "assistant"
  content: string
  timestamp: Date
  sources?: Array<{
    title: string
    type: string
    confidence: number
  }>
}

const initialMessages: Message[] = [
  {
    id: "1",
    type: "assistant",
    content:
      "Hello! I'm your AI document assistant. I can help you find information, answer questions, and analyze content from your uploaded documents. What would you like to know?",
    timestamp: new Date(),
  },
  {
    id: "2",
    type: "user", 
    content: "Can you summarize the key points from the Q4 financial report?",
    timestamp: new Date(),
  },
  {
    id: "3",
    type: "assistant",
    content: "Based on your documents, I found relevant information about financial performance. The Q4 report shows a 15% increase in revenue year-over-year, with strong growth in the technology sector. The market analysis indicates positive trends in consumer behavior and emerging technologies.",
    timestamp: new Date(),
    sources: [
      { title: "Financial Report Q4.pdf", type: "Financial Document", confidence: 95 },
      { title: "Market Analysis.pdf", type: "Research Paper", confidence: 88 }
    ]
  }
]

export function RAGChatbot() {
  const [messages, setMessages] = useState<Message[]>(initialMessages)
  const [inputValue, setInputValue] = useState("")
  const [isTyping, setIsTyping] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const [expandedSections, setExpandedSections] = useState({
    sources: true,
    history: false,
    knowledge: false
  })

  const toggleSection = (section: keyof typeof expandedSections) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }))
  }

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSendMessage = async () => {
    if (!inputValue.trim()) return

    const userMessage: Message = {
      id: Date.now().toString(),
      type: "user",
      content: inputValue,
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, userMessage])
    setInputValue("")
    setIsTyping(true)

    // Simulate AI response
    setTimeout(() => {
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: "assistant",
        content:
          "Based on your documents, I found relevant information about financial performance. The Q4 report shows a 15% increase in revenue year-over-year, with strong growth in the technology sector. The market analysis indicates positive trends in consumer behavior and emerging technologies.",
        timestamp: new Date(),
        sources: [
          { title: "Financial Report Q4.pdf", type: "Financial Document", confidence: 95 },
          { title: "Market Analysis.pdf", type: "Research Paper", confidence: 88 },
        ],
      }
      setMessages((prev) => [...prev, assistantMessage])
      setIsTyping(false)
    }, 2000)
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  // Get chat history from messages
  const getChatHistory = () => {
    const userMessages = messages.filter(m => m.type === "user")
    return [
      { id: "1", title: "Q4 Financial Analysis", timestamp: "Yesterday, 3:42 PM" },
      { id: "2", title: "Market Trends Discussion", timestamp: "Oct 12, 2023" },
      { id: "3", title: "Product Roadmap Review", timestamp: "Oct 10, 2023" },
      { id: "4", title: "Competitor Analysis", timestamp: "Oct 5, 2023" },
    ]
  }

  return (
    <div className="bg-gray-50 min-h-screen">
      <div className="flex h-screen overflow-hidden">
        {/* Main Chat Area */}
        <div className="flex-1 flex flex-col p-6" style={{ backgroundColor: '#f8fafc' }}>
          <div className="flex-1 flex flex-col bg-white rounded-xl shadow-md" style={{ position: 'relative', height: 'calc(100vh - 100px)' }}>
            <div style={{ 
              flex: 1, 
              overflowY: 'auto', 
              padding: '24px',
              paddingBottom: '100px'
            }}>
              {messages.map((message) => (
                <div key={message.id} style={{ marginBottom: '24px' }}>
                  {message.type === "assistant" ? (
                    <div style={{ display: 'flex', gap: '12px', alignItems: 'flex-start', marginBottom: '16px' }}>
                      <div style={{ 
                        width: '40px', 
                        height: '40px', 
                        borderRadius: '50%', 
                        backgroundColor: '#3b82f6', 
                        display: 'flex', 
                        alignItems: 'center', 
                        justifyContent: 'center',
                        flexShrink: 0,
                        color: 'white'
                      }}>
                        <i className="fas fa-robot" style={{ fontSize: '16px' }}></i>
                      </div>
                      <div className="max-w-[80%]">
                        <div className="p-4 rounded-lg" style={{ backgroundColor: '#f3f4f6', color: '#111827' }}>
                          <p className="text-sm leading-relaxed">{message.content}</p>
                        </div>
                        {message.sources && (
                          <div className="mt-3 space-y-2">
                            <p className="text-xs text-gray-500 font-medium">Sources:</p>
                            {message.sources.map((source, index) => (
                              <div key={index} className="flex items-center gap-2 p-3 rounded-lg border" style={{ backgroundColor: '#eff6ff', borderColor: '#bfdbfe' }}>
                                <i className="fas fa-file-pdf" style={{ color: '#ef4444' }}></i>
                                <div className="flex-1 min-w-0">
                                  <p className="text-sm font-medium truncate" style={{ color: '#111827' }}>{source.title}</p>
                                  <div className="flex items-center gap-2">
                                    <span className="text-xs" style={{ color: '#6b7280' }}>{source.type}</span>
                                    <span className="text-xs px-2 py-0.5 rounded-full" style={{ backgroundColor: '#dcfce7', color: '#166534' }}>{source.confidence}% match</span>
                                  </div>
                                </div>
                              </div>
                            ))}
                          </div>
                        )}
                        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: '8px', marginTop: '12px' }}>
                          <button style={{ 
                            padding: '6px 8px', 
                            border: '1px solid #e5e7eb', 
                            borderRadius: '6px', 
                            backgroundColor: 'transparent',
                            color: '#6b7280',
                            cursor: 'pointer',
                            fontSize: '12px'
                          }} onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#f9fafb'} onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}>
                            <i className="far fa-thumbs-up"></i>
                          </button>
                          <button style={{ 
                            padding: '6px 8px', 
                            border: '1px solid #e5e7eb', 
                            borderRadius: '6px', 
                            backgroundColor: 'transparent',
                            color: '#6b7280',
                            cursor: 'pointer',
                            fontSize: '12px'
                          }} onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#f9fafb'} onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}>
                            <i className="far fa-thumbs-down"></i>
                          </button>
                          <button style={{ 
                            padding: '6px 8px', 
                            border: '1px solid #e5e7eb', 
                            borderRadius: '6px', 
                            backgroundColor: 'transparent',
                            color: '#6b7280',
                            cursor: 'pointer',
                            fontSize: '12px'
                          }} onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#f9fafb'} onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}>
                            <i className="far fa-copy"></i>
                          </button>
                        </div>
                      </div>
                    </div>
                  ) : (
                    <div style={{ width: '100%', display: 'flex', justifyContent: 'flex-end', marginBottom: '16px' }}>
                      <div style={{ display: 'flex', gap: '12px', alignItems: 'flex-end', maxWidth: '70%' }}>
                        <div style={{ 
                          backgroundColor: '#3b82f6', 
                          color: 'white', 
                          padding: '12px 16px', 
                          borderRadius: '18px',
                          maxWidth: '100%',
                          wordWrap: 'break-word'
                        }}>
                          <p style={{ margin: 0, fontSize: '14px', lineHeight: '1.5' }}>{message.content}</p>
                        </div>
                        <div style={{ 
                          width: '40px', 
                          height: '40px', 
                          borderRadius: '50%', 
                          backgroundColor: '#6b7280', 
                          display: 'flex', 
                          alignItems: 'center', 
                          justifyContent: 'center',
                          flexShrink: 0,
                          color: 'white'
                        }}>
                          <i className="fas fa-user" style={{ fontSize: '16px' }}></i>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              ))}

              {isTyping && (
                <div style={{ display: 'flex', gap: '12px', alignItems: 'flex-start', marginBottom: '16px' }}>
                  <div style={{ 
                    width: '40px', 
                    height: '40px', 
                    borderRadius: '50%', 
                    backgroundColor: '#3b82f6', 
                    display: 'flex', 
                    alignItems: 'center', 
                    justifyContent: 'center',
                    flexShrink: 0,
                    color: 'white'
                  }}>
                    <i className="fas fa-robot" style={{ fontSize: '16px' }}></i>
                  </div>
                  <div style={{ backgroundColor: '#f3f4f6', padding: '16px', borderRadius: '12px' }}>
                    <div style={{ display: 'flex', gap: '4px' }}>
                      <div style={{ width: '8px', height: '8px', backgroundColor: '#9ca3af', borderRadius: '50%', animation: 'bounce 1.4s infinite ease-in-out' }}></div>
                      <div style={{ width: '8px', height: '8px', backgroundColor: '#9ca3af', borderRadius: '50%', animation: 'bounce 1.4s infinite ease-in-out', animationDelay: '0.16s' }}></div>
                      <div style={{ width: '8px', height: '8px', backgroundColor: '#9ca3af', borderRadius: '50%', animation: 'bounce 1.4s infinite ease-in-out', animationDelay: '0.32s' }}></div>
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <div style={{ 
              display: 'flex', 
              alignItems: 'center', 
              gap: '12px', 
              padding: '16px 24px',
              borderTop: '1px solid #e5e7eb',
              backgroundColor: 'white',
              position: 'absolute',
              bottom: 0,
              left: 0,
              right: 0,
              borderBottomLeftRadius: '12px',
              borderBottomRightRadius: '12px'
            }}>
              <input
                type="text"
                placeholder="Ask a question about your documents..."
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={handleKeyPress}
                style={{
                  flex: 1,
                  padding: '12px 16px',
                  border: '1px solid #d1d5db',
                  borderRadius: '24px',
                  fontSize: '14px',
                  backgroundColor: '#f9fafb',
                  outline: 'none',
                  transition: 'all 0.2s ease'
                }}
                onFocus={(e) => {
                  e.target.style.borderColor = '#3b82f6'
                  e.target.style.backgroundColor = 'white'
                  e.target.style.boxShadow = '0 0 0 3px rgba(59, 130, 246, 0.1)'
                }}
                onBlur={(e) => {
                  e.target.style.borderColor = '#d1d5db'
                  e.target.style.backgroundColor = '#f9fafb'
                  e.target.style.boxShadow = 'none'
                }}
              />
              <button 
                onClick={handleSendMessage} 
                disabled={!inputValue.trim() || isTyping}
                style={{
                  width: '44px',
                  height: '44px',
                  borderRadius: '50%',
                  backgroundColor: inputValue.trim() && !isTyping ? '#3b82f6' : '#d1d5db',
                  border: 'none',
                  color: 'white',
                  cursor: inputValue.trim() && !isTyping ? 'pointer' : 'not-allowed',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  transition: 'all 0.2s ease',
                  flexShrink: 0
                }}
                onMouseEnter={(e) => {
                  if (inputValue.trim() && !isTyping) {
                    e.currentTarget.style.backgroundColor = '#2563eb'
                  }
                }}
                onMouseLeave={(e) => {
                  if (inputValue.trim() && !isTyping) {
                    e.currentTarget.style.backgroundColor = '#3b82f6'
                  }
                }}
              >
                <i className="fas fa-paper-plane" style={{ fontSize: '16px' }}></i>
              </button>
            </div>
          </div>
        </div>

        {/* Improved Sidebar */}
        <div style={{ width: '350px', minWidth: '350px', flexShrink: 0, backgroundColor: '#1f2937', color: 'white', minHeight: '100vh' }} className="flex flex-col">
          {/* Sidebar Header */}
          <div style={{ borderBottom: '1px solid #4b5563', padding: '16px' }}>
            <h2 style={{ fontSize: '18px', fontWeight: '600', color: 'white', margin: 0 }}>Assistant Panel</h2>
            <p style={{ fontSize: '12px', color: '#d1d5db', margin: '4px 0 0 0' }}>Document insights and controls</p>
          </div>

          {/* Sidebar Content */}
          <div className="flex-1 overflow-y-auto">
            {/* Sources Section */}
            <div style={{ borderBottom: '1px solid #4b5563' }}>
              <div 
                style={{ padding: '16px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', cursor: 'pointer', transition: 'background-color 0.2s' }}
                onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#374151'}
                onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
                onClick={() => toggleSection('sources')}
              >
                <div style={{ display: 'flex', alignItems: 'center' }}>
                  <i className="fas fa-book" style={{ color: '#60a5fa', marginRight: '8px' }}></i>
                  <div>
                    <h3 style={{ fontWeight: '500', color: 'white', margin: 0 }}>Sources</h3>
                    <p style={{ fontSize: '12px', color: '#d1d5db', margin: '2px 0 0 0' }}>Documents used for responses</p>
                  </div>
                </div>
                <i className={`fas ${expandedSections.sources ? 'fa-chevron-up' : 'fa-chevron-down'}`} style={{ color: '#d1d5db' }}></i>
              </div>
              {expandedSections.sources && (
                <div style={{ padding: '0 16px 16px 16px' }}>
                  <div style={{ padding: '12px', backgroundColor: '#374151', borderRadius: '8px', border: '1px solid #4b5563', marginBottom: '12px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                      <i className="fas fa-file-pdf" style={{ color: '#f87171' }}></i>
                      <p style={{ fontWeight: '500', fontSize: '14px', color: 'white', flex: 1, wordBreak: 'break-words' }}>Financial Report Q4.pdf</p>
                      <span style={{ fontSize: '12px', backgroundColor: '#059669', color: '#dcfce7', padding: '2px 8px', borderRadius: '9999px' }}>95%</span>
                    </div>
                    <p style={{ fontSize: '10px', color: '#d1d5db', lineHeight: '1.2' }}>Quarterly financial summary with revenue analysis</p>
                  </div>
                  <div style={{ padding: '12px', backgroundColor: '#374151', borderRadius: '8px', border: '1px solid #4b5563', marginBottom: '12px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                      <i className="fas fa-file-pdf" style={{ color: '#f87171' }}></i>
                      <p style={{ fontWeight: '500', fontSize: '14px', color: 'white', flex: 1, wordBreak: 'break-words' }}>Market Analysis.pdf</p>
                      <span style={{ fontSize: '12px', backgroundColor: '#059669', color: '#dcfce7', padding: '2px 8px', borderRadius: '9999px' }}>88%</span>
                    </div>
                    <p style={{ fontSize: '10px', color: '#d1d5db', lineHeight: '1.2' }}>Consumer trends and market predictions</p>
                  </div>
                  <div style={{ padding: '12px', backgroundColor: '#374151', borderRadius: '8px', border: '1px solid #4b5563' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                      <i className="fas fa-file-word" style={{ color: '#3b82f6' }}></i>
                      <p style={{ fontWeight: '500', fontSize: '14px', color: 'white', flex: 1, wordBreak: 'break-words' }}>Product Roadmap.docx</p>
                      <span style={{ fontSize: '12px', backgroundColor: '#059669', color: '#dcfce7', padding: '2px 8px', borderRadius: '9999px' }}>76%</span>
                    </div>
                    <p style={{ fontSize: '10px', color: '#d1d5db', lineHeight: '1.2' }}>Upcoming product features and timelines</p>
                  </div>
                </div>
              )}
            </div>

            {/* Chat History Section */}
            <div style={{ borderBottom: '1px solid #4b5563' }}>
              <div 
                style={{ padding: '16px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', cursor: 'pointer', transition: 'background-color 0.2s' }}
                onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#374151'}
                onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
                onClick={() => toggleSection('history')}
              >
                <div style={{ display: 'flex', alignItems: 'center' }}>
                  <i className="fas fa-history" style={{ color: '#60a5fa', marginRight: '8px' }}></i>
                  <div>
                    <h3 style={{ fontWeight: '500', color: 'white', margin: 0 }}>Chat History</h3>
                    <p style={{ fontSize: '12px', color: '#d1d5db', margin: '2px 0 0 0' }}>Previous conversations</p>
                  </div>
                </div>
                <i className={`fas ${expandedSections.history ? 'fa-chevron-up' : 'fa-chevron-down'}`} style={{ color: '#d1d5db' }}></i>
              </div>
              {expandedSections.history && (
                <div style={{ padding: '0 16px 16px 16px' }}>
                  {getChatHistory().map((chat) => (
                    <div key={chat.id} style={{ padding: '12px', backgroundColor: '#374151', borderRadius: '8px', border: '1px solid #4b5563', marginBottom: '8px', cursor: 'pointer', transition: 'background-color 0.2s' }}
                         onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#4b5563'}
                         onMouseLeave={(e) => e.currentTarget.style.backgroundColor = '#374151'}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <i className="fas fa-comment" style={{ color: '#d1d5db' }}></i>
                        <p style={{ fontWeight: '500', fontSize: '14px', color: 'white', wordBreak: 'break-words' }}>{chat.title}</p>
                      </div>
                      <p style={{ fontSize: '12px', color: '#d1d5db', marginTop: '4px' }}>{chat.timestamp}</p>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Knowledge Base Section */}
            <div>
              <div 
                style={{ padding: '16px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', cursor: 'pointer', transition: 'background-color 0.2s' }}
                onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#374151'}
                onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
                onClick={() => toggleSection('knowledge')}
              >
                <div style={{ display: 'flex', alignItems: 'center' }}>
                  <i className="fas fa-database" style={{ color: '#60a5fa', marginRight: '8px' }}></i>
                  <div>
                    <h3 style={{ fontWeight: '500', color: 'white', margin: 0 }}>Knowledge Base</h3>
                    <p style={{ fontSize: '12px', color: '#d1d5db', margin: '2px 0 0 0' }}>Manage document sources</p>
                  </div>
                </div>
                <i className={`fas ${expandedSections.knowledge ? 'fa-chevron-up' : 'fa-chevron-down'}`} style={{ color: '#d1d5db' }}></i>
              </div>
              {expandedSections.knowledge && (
                <div style={{ padding: '0 16px 16px 16px' }}>
                  <div style={{ textAlign: 'center', padding: '32px 0', color: '#d1d5db' }}>
                    <i className="fas fa-file-alt" style={{ fontSize: '48px', marginBottom: '8px', display: 'block' }}></i>
                    <p style={{ fontSize: '14px', margin: '8px 0 4px 0' }}>No documents selected</p>
                    <p style={{ fontSize: '12px', margin: 0 }}>Upload documents to start analyzing</p>
                  </div>
                </div>
              )}
            </div>
          </div>

        </div>
      </div>
    </div>
  )
}