import React, { createContext, useContext, useState, ReactNode } from 'react';

interface DocumentContextType {
  selectedDocuments: number[];
  setSelectedDocuments: (docs: number[]) => void;
  toggleDocument: (docId: number) => void;
  clearDocuments: () => void;
}

const DocumentContext = createContext<DocumentContextType | undefined>(undefined);

export const DocumentProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [selectedDocuments, setSelectedDocuments] = useState<number[]>(() => {
    // Try to load from localStorage on init
    try {
      const saved = localStorage.getItem('persistent-selected-docs');
      return saved ? JSON.parse(saved) : [];
    } catch {
      return [];
    }
  });

  const updateDocuments = (docs: number[]) => {
    setSelectedDocuments(docs);
    // Always save to localStorage
    localStorage.setItem('persistent-selected-docs', JSON.stringify(docs));
    console.log('📌 CONTEXT: Documents updated:', docs);
  };

  const toggleDocument = (docId: number) => {
    const newDocs = selectedDocuments.includes(docId)
      ? selectedDocuments.filter(id => id !== docId)
      : [...selectedDocuments, docId];
    updateDocuments(newDocs);
  };

  const clearDocuments = () => {
    updateDocuments([]);
  };

  return (
    <DocumentContext.Provider value={{
      selectedDocuments,
      setSelectedDocuments: updateDocuments,
      toggleDocument,
      clearDocuments
    }}>
      {children}
    </DocumentContext.Provider>
  );
};

export const useDocumentContext = () => {
  const context = useContext(DocumentContext);
  if (!context) {
    throw new Error('useDocumentContext must be used within DocumentProvider');
  }
  return context;
};
