import type { ExpandedSections, Document, ChatHistory } from '../../types'
import { SidebarHeader } from './SidebarHeader'
import { SourcesSection } from './SourcesSection'
import { ChatHistorySection } from './ChatHistorySection'
import { KnowledgeBaseSection } from './KnowledgeBaseSection'

interface SidebarProps {
  expandedSections: ExpandedSections
  toggleSection: (section: keyof ExpandedSections) => void
  selectedMessageSources: any[]
  chatHistory: ChatHistory[]
  selectedDocuments: number[]
  documents: Document[]
  onShowDocumentModal: () => void
  onRemoveDocument: (docId: number) => void
  onNewChat: () => void
  onChatHistoryClick: (chatId: string) => void
}

export function Sidebar({
  expandedSections,
  toggleSection,
  selectedMessageSources,
  chatHistory,
  selectedDocuments,
  documents,
  onShowDocumentModal,
  onRemoveDocument,
  onNewChat,
  onChatHistoryClick
}: SidebarProps) {
  return (
    <div 
      data-sidebar="true"
      style={{ 
        width: '320px',
        minWidth: '320px',
        flexShrink: 0, 
        backgroundColor: '#1f2937', 
        color: 'white', 
        height: '100vh',
        overflowY: 'auto',
        overflowX: 'hidden'
      }} 
      className="flex flex-col"
    >
      <SidebarHeader onNewChat={onNewChat} />
      
      <div style={{ flex: 1, overflowY: 'auto', overflowX: 'hidden', display: 'flex', flexDirection: 'column' }}>
        <SourcesSection 
          expandedSections={expandedSections}
          toggleSection={toggleSection}
          selectedMessageSources={selectedMessageSources}
        />
        
        <ChatHistorySection 
          expandedSections={expandedSections}
          toggleSection={toggleSection}
          chatHistory={chatHistory}
          onChatHistoryClick={onChatHistoryClick}
        />
        
        <KnowledgeBaseSection 
          expandedSections={expandedSections}
          toggleSection={toggleSection}
          selectedDocuments={selectedDocuments}
          documents={documents}
          onShowDocumentModal={onShowDocumentModal}
          onRemoveDocument={onRemoveDocument}
        />
      </div>
    </div>
  )
}
