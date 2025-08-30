"use client"

import type React from "react"
import { useState } from "react"

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

interface ChatSidebarProps {
  messages: Message[]
  selectedDocuments: string[]
  availableDocuments: Array<{
    id: string
    name: string
    type: string
    size: string
  }>
  onToggleDocumentSelection: (docName: string) => void
}

export function ChatSidebar({ 
  messages, 
  selectedDocuments, 
  availableDocuments, 
  onToggleDocumentSelection 
}: ChatSidebarProps) {
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

  // Get unique chat titles from messages
  const getChatHistory = () => {
    const userMessages = messages.filter(m => m.type === "user")
    return userMessages.map((msg, index) => ({
      id: msg.id,
      title: msg.content.length > 30 ? msg.content.substring(0, 30) + "..." : msg.content,
      timestamp: msg.timestamp
    }))
  }

  return (
    <div className="bg-white rounded-lg shadow-sm w-full h-full flex flex-col border border-gray-200">
      {/* Sidebar Header */}
      <div className="p-4 border-b border-gray-200">
        <h2 className="text-lg font-semibold text-gray-800">Assistant Panel</h2>
        <p className="text-xs text-gray-500">Document insights and controls</p>
      </div>

      {/* Sidebar Content */}
      <div className="flex-1 overflow-y-auto">
        {/* Sources Section */}
        <div className="border-b border-gray-200">
          <div
            className="p-4 flex items-center justify-between cursor-pointer hover:bg-gray-50 transition-colors"
            onClick={() => toggleSection('sources')}
          >
            <div className="flex items-center">
              <i className="fas fa-book text-blue-500 mr-3"></i>
              <div>
                <h3 className="font-medium text-gray-800">Sources</h3>
                <p className="text-xs text-gray-500">Documents used for responses</p>
              </div>
            </div>
            <i className={`fas ${expandedSections.sources ? 'fa-chevron-up' : 'fa-chevron-down'} text-gray-400 transition-transform duration-200`}></i>
          </div>

          {expandedSections.sources && (
            <div className="px-4 pb-4 space-y-3">
              {messages
                .filter(m => m.type === 'assistant' && m.sources)
                .slice(-3)
                .map(message =>
                  message.sources?.map((source, index) => (
                    <div key={index} className="p-3 bg-blue-50 rounded-lg border border-blue-200">
                      <div className="flex items-start gap-2">
                        <i className="fas fa-file-pdf text-red-500 mt-0.5"></i>
                        <div className="flex-1 min-w-0">
                          <p className="font-medium text-sm truncate">{source.title}</p>
                          <div className="flex items-center gap-2 mt-1">
                            <span className="text-xs text-gray-500">{source.type}</span>
                            <span className="text-xs bg-green-100 text-green-800 px-2 py-0.5 rounded-full">{source.confidence}% match</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))
                )}
              {messages.filter(m => m.type === 'assistant' && m.sources).length === 0 && (
                <p className="text-xs text-gray-500 text-center py-4">No sources available yet</p>
              )}
            </div>
          )}
        </div>

        {/* Chat History Section */}
        <div className="border-b border-gray-200">
          <div
            className="p-4 flex items-center justify-between cursor-pointer hover:bg-gray-50 transition-colors"
            onClick={() => toggleSection('history')}
          >
            <div className="flex items-center">
              <i className="fas fa-history text-blue-500 mr-3"></i>
              <div>
                <h3 className="font-medium text-gray-800">Chat History</h3>
                <p className="text-xs text-gray-500">Previous conversations</p>
              </div>
            </div>
            <i className={`fas ${expandedSections.history ? 'fa-chevron-up' : 'fa-chevron-down'} text-gray-400 transition-transform duration-200`}></i>
          </div>

          {expandedSections.history && (
            <div className="px-4 pb-4 space-y-2">
              {getChatHistory().length > 0 ? (
                getChatHistory().map((chat) => (
                  <div key={chat.id} className="p-3 bg-gray-50 rounded-lg border border-gray-200 hover:bg-gray-100 transition-colors cursor-pointer">
                    <div className="flex items-center gap-2">
                      <i className="fas fa-comment text-gray-500"></i>
                      <p className="font-medium text-sm truncate">{chat.title}</p>
                    </div>
                    <p className="text-xs text-gray-500 mt-1">
                      {chat.timestamp.toLocaleDateString()} at {chat.timestamp.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                    </p>
                  </div>
                ))
              ) : (
                <p className="text-xs text-gray-500 text-center py-4">No chat history yet</p>
              )}
            </div>
          )}
        </div>

        {/* Knowledge Base Section */}
        <div>
          <div
            className="p-4 flex items-center justify-between cursor-pointer hover:bg-gray-50 transition-colors"
            onClick={() => toggleSection('knowledge')}
          >
            <div className="flex items-center">
              <i className="fas fa-database text-blue-500 mr-3"></i>
              <div>
                <h3 className="font-medium text-gray-800">Knowledge Base</h3>
                <p className="text-xs text-gray-500">Manage document sources</p>
              </div>
            </div>
            <i className={`fas ${expandedSections.knowledge ? 'fa-chevron-up' : 'fa-chevron-down'} text-gray-400 transition-transform duration-200`}></i>
          </div>

          {expandedSections.knowledge && (
            <div className="px-4 pb-4">
              <div className="text-center py-8 text-gray-500">
                <i className="fas fa-file-alt text-3xl mb-2"></i>
                <p className="text-sm">No documents selected</p>
                <p className="text-xs mt-1">Upload documents to start analyzing</p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Sidebar Footer */}
      <div className="p-4 border-t border-gray-200 text-center">
        <button className="text-sm text-gray-500 hover:text-gray-700 flex items-center justify-center mx-auto">
          <i className="fas fa-cog mr-1"></i> Settings
        </button>
      </div>
    </div>
  )
}