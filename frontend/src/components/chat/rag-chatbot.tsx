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
    content: "Hello! I'm your AI document assistant. I can help you find information, answer questions, and analyze content from your uploaded documents. What would you like to know?",
    timestamp: new Date()
  },
  {
    id: "2", 
    type: "user",
    content: "Can you summarize the key points from the Q4 financial report?",
    timestamp: new Date()
  },
  {
    id: "3",
    type: "assistant", 
    content: "Based on your documents, I found relevant information about financial performance. The Q4 report shows a 15% increase in revenue year-over-year, with strong growth in the technology sector. The market analysis indicates positive trends in consumer behavior and emerging technologies.",
    timestamp: new Date(),
    sources: [
      { title: "Financial Report Q4.pdf", type: "Quarterly financial summary with revenue analysis", confidence: 95 },
      { title: "Market Analysis.pdf", type: "Consumer trends and market predictions", confidence: 88 }
    ]
  },
  {
    id: "4",
    type: "user",
    content: "What are the upcoming product features mentioned in our roadmap?",
    timestamp: new Date()
  },
  {
    id: "5",
    type: "assistant",
    content: "According to the product roadmap and strategic planning documents, the upcoming features include AI-powered analytics, mobile app enhancements, and cloud integration capabilities. The development timeline spans Q1-Q3 2024 with phased rollouts.",
    timestamp: new Date(),
    sources: [
      { title: "Product Roadmap.docx", type: "Upcoming product features and timelines", confidence: 92 },
      { title: "Strategic Plan 2024.pdf", type: "Annual strategic planning document", confidence: 85 },
      { title: "Development Timeline.xlsx", type: "Project schedules and milestones", confidence: 78 }
    ]
  },
  {
    id: "6",
    type: "user",
    content: "Can you analyze our budget projections for next year?",
    timestamp: new Date()
  },
  {
    id: "7",
    type: "assistant",
    content: "The budget analysis shows projected revenue growth of 18% with controlled operational expenses. Key investments are planned for R&D and marketing initiatives. The financial forecast indicates strong profitability margins.",
    timestamp: new Date(),
    sources: [
      { title: "Budget Forecast 2024.xlsx", type: "Annual budget planning and projections", confidence: 94 },
      { title: "Financial Projections.pdf", type: "Revenue and expense forecasting", confidence: 89 }
    ]
  },
  {
    id: "8",
    type: "user",
    content: "What does our competitive analysis reveal?",
    timestamp: new Date()
  },
  {
    id: "9",
    type: "assistant",
    content: "The competitive analysis reveals strong market positioning with key advantages in technology innovation and customer satisfaction. Main competitors are focusing on pricing strategies while we maintain quality leadership.",
    timestamp: new Date(),
    sources: [
      { title: "Competitor Analysis.pdf", type: "Market competition and positioning study", confidence: 91 },
      { title: "Industry Report 2024.docx", type: "Comprehensive industry analysis", confidence: 86 },
      { title: "Customer Survey Results.xlsx", type: "Customer satisfaction and feedback data", confidence: 83 },
      { title: "Market Research.pdf", type: "Consumer behavior and trends analysis", confidence: 79 }
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
  const [selectedMessageSources, setSelectedMessageSources] = useState<any[]>(() => {
    // Find the latest assistant message with sources
    const latestAssistantMessage = [...initialMessages].reverse().find(msg => msg.type === 'assistant' && msg.sources);
    return latestAssistantMessage?.sources || [];
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
    <div className="bg-gray-50" style={{ height: '100vh', overflow: 'hidden' }}>
      <div className="flex" style={{ height: '100vh' }}>
        {/* Main Chat Area */}
        <div className="flex-1 flex flex-col" style={{ backgroundColor: '#f8fafc' }}>
          <div className="flex-1 flex flex-col bg-white" style={{ position: 'relative', height: 'calc(100vh - 60px)' }}>
            <div 
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
                  {message.type === "assistant" ? (
                    <div 
                      style={{ display: 'flex', gap: '12px', alignItems: 'flex-start', marginBottom: '16px', cursor: 'pointer' }}
                      onDoubleClick={() => {
                        if (message.sources) {
                          setSelectedMessageSources(message.sources);
                          setExpandedSections(prev => ({ ...prev, sources: true }));
                        }
                      }}
                    >
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
                          <div style={{ marginTop: '12px' }}>
                            <p style={{ fontSize: '12px', color: '#6b7280', fontWeight: '500', margin: '0 0 8px 0' }}>Sources:</p>
                            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                              {message.sources.map((source, index) => (
                                <div key={index} style={{ 
                                  display: 'inline-flex',
                                  alignItems: 'center',
                                  backgroundColor: '#f1f5f9',
                                  border: '1px solid #e2e8f0',
                                  borderRadius: '16px',
                                  padding: '4px 8px',
                                  fontSize: '10px',
                                  color: '#475569',
                                  cursor: 'pointer'
                                }}>
                                  <span style={{ fontWeight: '500' }}>{source.title}</span>
                                </div>
                              ))}
                            </div>
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

            {/* Input Bar */}
            <div style={{ 
              position: 'absolute', 
              bottom: '0', 
              left: '0', 
              right: '0', 
              backgroundColor: 'white', 
              borderTop: '1px solid #e5e7eb', 
              padding: '12px 16px',
              display: 'flex',
              alignItems: 'center',
              gap: '12px'
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
        <div 
          data-sidebar="true"
          style={{ 
            width: '350px', 
            minWidth: '350px', 
            flexShrink: 0, 
            backgroundColor: '#1f2937', 
            color: 'white', 
            height: '100vh',
            overflowY: 'auto',
            overflowX: 'hidden'
          }} 
          className="flex flex-col"
        >
          {/* Sidebar Header */}
          <div style={{ borderBottom: '1px solid #4b5563', padding: '16px' }}>
            <h2 style={{ fontSize: '18px', fontWeight: '600', color: 'white', margin: 0 }}>Assistant Panel</h2>
            <p style={{ fontSize: '12px', color: '#d1d5db', margin: '4px 0 0 0' }}>Document insights and controls</p>
          </div>

          {/* Sidebar Content */}
          <div style={{ flex: 1, overflowY: 'auto', overflowX: 'hidden' }}>
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
                <div style={{ padding: '16px' }}>
                  <p style={{ fontSize: '12px', color: '#d1d5db', margin: '0 0 12px 0' }}>Documents used for responses</p>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                    {selectedMessageSources.length > 0 ? (
                      selectedMessageSources.map((source, index) => (
                        <div key={index} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '8px 12px', backgroundColor: '#374151', borderRadius: '6px' }}>
                          <div style={{ display: 'flex', alignItems: 'center' }}>
                            <i className={
                              source.title.toLowerCase().includes('.pdf') ? 'fas fa-file-pdf' : 
                              source.title.toLowerCase().includes('.xlsx') ? 'fas fa-file-excel' : 
                              'fas fa-file-alt'
                            } style={{ 
                              color: source.title.toLowerCase().includes('.pdf') ? '#ef4444' : 
                                     source.title.toLowerCase().includes('.xlsx') ? '#10b981' : 
                                     '#3b82f6', 
                              marginRight: '8px' 
                            }}></i>
                            <div>
                              <p style={{ fontSize: '12px', fontWeight: '500', color: 'white', margin: 0 }}>{source.title}</p>
                              <p style={{ fontSize: '10px', color: '#d1d5db', margin: 0 }}>{source.type}</p>
                            </div>
                          </div>
                          <span style={{ fontSize: '10px', backgroundColor: '#10b981', color: 'white', padding: '2px 6px', borderRadius: '10px' }}>{source.confidence}%</span>
                        </div>
                      ))
                    ) : (
                      <div style={{ textAlign: 'center', padding: '20px', color: '#9ca3af' }}>
                        <i className="fas fa-info-circle" style={{ fontSize: '24px', marginBottom: '8px' }}></i>
                        <p style={{ fontSize: '12px', margin: 0 }}>No sources for this response</p>
                      </div>
                    )}
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