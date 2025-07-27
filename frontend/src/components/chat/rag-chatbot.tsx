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

  return (
    <div className="p-6 space-y-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">AI Document Chat</h1>
        <p className="text-gray-600">Ask questions about your documents and get intelligent answers</p>
      </div>

      <div className="grid grid-cols-4 gap-6">
        {/* Chat Interface */}
        <div className="card flex flex-col" style={{ gridColumn: "span 3", height: "700px" }}>
          <div className="card-header">
            <h2 className="card-title flex items-center gap-2">💬 Document Assistant</h2>
            <p className="card-description">Powered by RAG (Retrieval-Augmented Generation) technology</p>
          </div>

          <div className="card-content flex-1 flex flex-col">
            {/* Messages */}
            <div className="flex-1 overflow-y-auto space-y-4 mb-4" style={{ maxHeight: "500px" }}>
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex gap-3 ${message.type === "user" ? "justify-end" : "justify-start"}`}
                >
                  {message.type === "assistant" && (
                    <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center text-white font-bold">
                      🤖
                    </div>
                  )}

                  <div className={`max-w-[80%] ${message.type === "user" ? "order-2" : ""}`}>
                    <div
                      className={`p-4 rounded-lg ${
                        message.type === "user" ? "bg-blue-600 text-white" : "bg-gray-100 text-gray-900"
                      }`}
                    >
                      <p className="text-sm leading-relaxed">{message.content}</p>
                    </div>

                    {message.sources && (
                      <div className="mt-2 space-y-2">
                        <p className="text-xs text-gray-500 font-medium">Sources:</p>
                        {message.sources.map((source, index) => (
                          <div key={index} className="flex items-center gap-2 p-2 bg-gray-50 rounded border">
                            <span className="text-blue-600">📄</span>
                            <span className="text-sm font-medium">{source.title}</span>
                            <span className="badge badge-secondary text-xs">{source.confidence}% match</span>
                          </div>
                        ))}
                      </div>
                    )}

                    {message.type === "assistant" && (
                      <div className="flex items-center gap-2 mt-2">
                        <button className="btn btn-sm btn-outline">📋</button>
                        <button className="btn btn-sm btn-outline">👍</button>
                        <button className="btn btn-sm btn-outline">👎</button>
                      </div>
                    )}
                  </div>

                  {message.type === "user" && (
                    <div className="w-8 h-8 bg-gray-500 rounded-full flex items-center justify-center text-white font-bold order-3">
                      👤
                    </div>
                  )}
                </div>
              ))}

              {isTyping && (
                <div className="flex gap-3">
                  <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center text-white font-bold">
                    🤖
                  </div>
                  <div className="bg-gray-100 p-4 rounded-lg">
                    <div className="flex gap-1">
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                      <div
                        className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                        style={{ animationDelay: "0.1s" }}
                      ></div>
                      <div
                        className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                        style={{ animationDelay: "0.2s" }}
                      ></div>
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <div className="flex gap-2">
              <input
                type="text"
                placeholder="Ask a question about your documents..."
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={handleKeyPress}
                className="form-input flex-1"
              />
              <button onClick={handleSendMessage} disabled={!inputValue.trim() || isTyping} className="btn btn-primary">
                📤
              </button>
            </div>
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Quick Questions */}
          <div className="card">
            <div className="card-header">
              <h2 className="card-title">Quick Questions</h2>
              <p className="card-description">Try these common queries</p>
            </div>
            <div className="card-content space-y-2">
              {[
                "What are the key financial metrics?",
                "Summarize the main findings",
                "What are the risk factors?",
                "Show me the revenue trends",
              ].map((question) => (
                <button
                  key={question}
                  className="btn btn-outline w-full text-left text-xs p-3"
                  onClick={() => setInputValue(question)}
                >
                  ✨ {question}
                </button>
              ))}
            </div>
          </div>

          {/* Recent Documents */}
          <div className="card">
            <div className="card-header">
              <h2 className="card-title">Available Documents</h2>
              <p className="card-description">Documents in your knowledge base</p>
            </div>
            <div className="card-content space-y-3">
              {[
                { name: "Financial Report Q4.pdf", type: "Financial" },
                { name: "Market Analysis.pdf", type: "Research" },
                { name: "Legal Contract.pdf", type: "Legal" },
              ].map((doc) => (
                <div key={doc.name} className="flex items-center gap-2 p-2 bg-gray-50 rounded border">
                  <span className="text-blue-600">📄</span>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium">{doc.name}</p>
                    <span className="badge badge-secondary text-xs">{doc.type}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
