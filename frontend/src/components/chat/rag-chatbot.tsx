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
        <div className="flex-1 flex flex-col p-6 min-w-0">
          <div className="mb-6">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">AI Document Chat</h1>
            <p className="text-gray-600">Ask questions about your documents and get intelligent answers</p>
          </div>

          <div className="flex-1 flex flex-col bg-white rounded-xl shadow-md p-6">
            <div className="mb-4">
              <h2 className="text-xl font-semibold text-gray-800">Document Assistant</h2>
              <p className="text-gray-500 text-sm">Powered by RAG (Retrieval-Augmented Generation) technology</p>
            </div>

            <div className="flex-1 overflow-y-auto space-y-4 mb-4 pr-2" style={{ maxHeight: "calc(100vh - 250px)" }}>
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex gap-3 ${message.type === "user" ? "justify-end" : "justify-start"}`}
                >
                  {message.type === "assistant" && (
                    <div className="w-10 h-10 bg-blue-500 rounded-full flex items-center justify-center text-white flex-shrink-0">
                      <i className="fas fa-robot"></i>
                    </div>
                  )}

                  <div className={`max-w-[80%] ${message.type === "user" ? "order-2" : ""}`}>
                    <div
                      className={`p-4 rounded-lg ${
                        message.type === "user" ? "bg-blue-500 text-white" : "bg-gray-100 text-gray-900"
                      }`}
                    >
                      <p className="text-sm leading-relaxed">{message.content}</p>
                    </div>

                    {message.sources && (
                      <div className="mt-3 space-y-2">
                        <p className="text-xs text-gray-500 font-medium">Sources:</p>
                        {message.sources.map((source, index) => (
                          <div key={index} className="flex items-center gap-2 p-3 bg-blue-50 rounded-lg border border-blue-200">
                            <i className="fas fa-file-pdf text-red-400"></i>
                            <div className="flex-1 min-w-0">
                              <p className="text-sm font-medium truncate">{source.title}</p>
                              <div className="flex items-center gap-2">
                                <span className="text-xs text-gray-500">{source.type}</span>
                                <span className="text-xs bg-green-100 text-green-800 px-2 py-0.5 rounded-full">{source.confidence}% match</span>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}

                    {message.type === "assistant" && (
                      <div className="flex items-center gap-2 mt-3">
                        <button className="p-2 border border-gray-300 rounded text-gray-500 hover:bg-gray-100 transition-colors">
                          <i className="far fa-copy"></i>
                        </button>
                        <button className="p-2 border border-gray-300 rounded text-gray-500 hover:bg-gray-100 transition-colors">
                          <i className="far fa-thumbs-up"></i>
                        </button>
                        <button className="p-2 border border-gray-300 rounded text-gray-500 hover:bg-gray-100 transition-colors">
                          <i className="far fa-thumbs-down"></i>
                        </button>
                      </div>
                    )}
                  </div>

                  {message.type === "user" && (
                    <div className="w-10 h-10 bg-gray-500 rounded-full flex items-center justify-center text-white flex-shrink-0">
                      <i className="fas fa-user"></i>
                    </div>
                  )}
                </div>
              ))}

              {isTyping && (
                <div className="flex gap-3">
                  <div className="w-10 h-10 bg-blue-500 rounded-full flex items-center justify-center text-white flex-shrink-0">
                    <i className="fas fa-robot"></i>
                  </div>
                  <div className="bg-gray-100 p-4 rounded-lg">
                    <div className="flex gap-1">
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "0.1s" }}></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "0.2s" }}></div>
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <div className="flex gap-2">
              <input
                type="text"
                placeholder="Ask a question about your documents..."
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={handleKeyPress}
                className="flex-1 border border-gray-300 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <button 
                onClick={handleSendMessage} 
                disabled={!inputValue.trim() || isTyping} 
                className="bg-blue-500 hover:bg-blue-600 text-white rounded-lg px-5 py-3 transition duration-200 flex items-center disabled:opacity-50"
              >
                <i className="fas fa-paper-plane"></i>
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