import type { Document, Message, ChatHistory } from '../types'

export const sampleDocuments: Document[] = [
  { id: 1, name: "Financial Report Q4.pdf", type: "pdf", size: "2.4 MB", date: "2023-10-15" },
  { id: 2, name: "Market Analysis.pdf", type: "pdf", size: "1.8 MB", date: "2023-09-22" },
  { id: 3, name: "Product Roadmap.docx", type: "doc", size: "1.1 MB", date: "2023-11-05" },
  { id: 4, name: "Sales Data Q4.xlsx", type: "xls", size: "3.2 MB", date: "2023-10-30" },
  { id: 5, name: "Presentation.pptx", type: "ppt", size: "5.7 MB", date: "2023-11-10" },
  { id: 6, name: "User Research.pdf", type: "pdf", size: "4.3 MB", date: "2023-08-17" },
  { id: 7, name: "Competitor Analysis.docx", type: "doc", size: "2.1 MB", date: "2023-09-05" },
  { id: 8, name: "Technical Specifications.pdf", type: "pdf", size: "3.5 MB", date: "2023-10-12" },
  { id: 9, name: "Marketing Plan.docx", type: "doc", size: "1.9 MB", date: "2023-11-01" },
  { id: 10, name: "Budget Proposal.xlsx", type: "xls", size: "0.8 MB", date: "2023-10-25" },
  { id: 11, name: "Customer Feedback.pdf", type: "pdf", size: "2.7 MB", date: "2023-09-18" },
  { id: 12, name: "Project Timeline.pptx", type: "ppt", size: "4.1 MB", date: "2023-11-08" }
]

export const initialMessages: Message[] = [
  {
    id: "1",
    type: "assistant",
    content: "Hello! I'm your AI document assistant. I can help you find information, answer questions, and analyze content from your uploaded documents. What would you like to know?",
    timestamp: new Date()
  }
]

export const sampleChatHistory: ChatHistory[] = [
  { id: "1", title: "Q4 Financial Analysis", timestamp: "Yesterday, 3:42 PM" },
  { id: "2", title: "Market Trends Discussion", timestamp: "Oct 12, 2023" },
  { id: "3", title: "Product Roadmap Review", timestamp: "Oct 10, 2023" },
  { id: "4", title: "Competitor Analysis", timestamp: "Oct 5, 2023" },
]
