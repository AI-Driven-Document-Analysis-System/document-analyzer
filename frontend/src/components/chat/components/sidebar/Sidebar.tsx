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
  selectedDocuments: string[]
  documents: Document[]
  onShowDocumentModal: () => void
  onRemoveDocument: (docId: string) => void
  onNewChat: () => void
  onChatHistoryClick: (chatId: string) => void
  onDeleteChat: (chatId: string) => void
  selectedChatId?: string
  documentsLoading?: boolean
  documentsError?: string | null
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
  onChatHistoryClick,
  onDeleteChat,
  selectedChatId,
  documentsLoading = false,
  documentsError = null
}: SidebarProps) {
  return (
    <div 
      data-sidebar="true"
      style={{ 
        width: '320px',
        minWidth: '320px',
        maxWidth: '320px',
        flex: '0 0 320px',
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
          onDeleteChat={onDeleteChat}
          selectedChatId={selectedChatId}
        />
        
        <KnowledgeBaseSection 
          expandedSections={expandedSections}
          toggleSection={toggleSection}
          selectedDocuments={selectedDocuments}
          documents={documents}
          onShowDocumentModal={onShowDocumentModal}
          onRemoveDocument={onRemoveDocument}
          documentsLoading={documentsLoading}
          documentsError={documentsError}
        />
      </div>
    </div>
  )
}
