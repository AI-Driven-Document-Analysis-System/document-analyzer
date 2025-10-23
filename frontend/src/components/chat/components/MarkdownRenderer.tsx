import React, { useState } from 'react'
import ReactMarkdown from 'react-markdown'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism'
import remarkGfm from 'remark-gfm'
import rehypeRaw from 'rehype-raw'

interface MarkdownRendererProps {
  content: string
  className?: string
  isDarkMode?: boolean
}

interface CodeBlockProps {
  inline?: boolean
  className?: string
  children: React.ReactNode
}

export function MarkdownRenderer({ content, className = '', isDarkMode = false }: MarkdownRendererProps) {
  const [copiedBlocks, setCopiedBlocks] = useState<Set<string>>(new Set())

  const copyToClipboard = async (text: string, blockId: string) => {
    try {
      await navigator.clipboard.writeText(text)
      setCopiedBlocks(prev => new Set(prev).add(blockId))
      setTimeout(() => {
        setCopiedBlocks(prev => {
          const newSet = new Set(prev)
          newSet.delete(blockId)
          return newSet
        })
      }, 2000)
    } catch (err) {
      console.error('Failed to copy text: ', err)
    }
  }

  const CodeBlock = ({ inline, className, children, ...props }: CodeBlockProps) => {
    const match = /language-(\w+)/.exec(className || '')
    const language = match ? match[1] : ''
    const codeString = String(children).replace(/\n$/, '')
    const blockId = `${language}-${codeString.slice(0, 20)}-${Date.now()}`

    if (!inline && language) {
      return (
        <div style={{ position: 'relative', marginBottom: '16px' }}>
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            backgroundColor: '#282c34',
            padding: '8px 12px',
            borderTopLeftRadius: '6px',
            borderTopRightRadius: '6px',
            fontSize: '12px',
            color: '#abb2bf'
          }}>
            <span style={{ fontWeight: '500' }}>{language}</span>
            <button
              onClick={() => copyToClipboard(codeString, blockId)}
              style={{
                padding: '4px 8px',
                backgroundColor: copiedBlocks.has(blockId) ? '#4caf50' : 'transparent',
                border: '1px solid #4a5568',
                borderRadius: '4px',
                color: copiedBlocks.has(blockId) ? 'white' : '#abb2bf',
                fontSize: '11px',
                cursor: 'pointer',
                transition: 'all 0.2s ease'
              }}
              onMouseEnter={(e) => {
                if (!copiedBlocks.has(blockId)) {
                  e.currentTarget.style.backgroundColor = '#4a5568'
                }
              }}
              onMouseLeave={(e) => {
                if (!copiedBlocks.has(blockId)) {
                  e.currentTarget.style.backgroundColor = 'transparent'
                }
              }}
            >
              {copiedBlocks.has(blockId) ? '✓ Copied' : 'Copy'}
            </button>
          </div>
          <SyntaxHighlighter
            style={oneDark}
            language={language}
            PreTag="div"
            customStyle={{
              margin: 0,
              borderTopLeftRadius: 0,
              borderTopRightRadius: 0,
              borderBottomLeftRadius: '6px',
              borderBottomRightRadius: '6px'
            }}
            {...props}
          >
            {codeString}
          </SyntaxHighlighter>
        </div>
      )
    }

    return (
      <code
        style={{
          backgroundColor: isDarkMode ? '#1f2937' : '#f1f5f9',
          padding: '2px 6px',
          borderRadius: '4px',
          fontSize: '0.9em',
          fontFamily: 'Monaco, Consolas, "Courier New", monospace',
          color: isDarkMode ? '#f56565' : '#e53e3e'
        }}
        {...props}
      >
        {children}
      </code>
    )
  }

  return (
    <div className={`markdown-content ${className}`}>
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        rehypePlugins={[rehypeRaw]}
        components={{
          code: CodeBlock,
          h1: ({ children }) => (
            <h1 style={{
              fontSize: '24px',
              fontWeight: '700',
              marginBottom: '16px',
              marginTop: '24px',
              color: isDarkMode ? '#3b82f6' : '#1f2937',
              borderBottom: `2px solid ${isDarkMode ? '#4a5568' : '#e5e7eb'}`,
              paddingBottom: '8px'
            }}>
              {children}
            </h1>
          ),
          h2: ({ children }) => (
            <h2 style={{
              fontSize: '20px',
              fontWeight: '600',
              marginBottom: '12px',
              marginTop: '20px',
              color: isDarkMode ? '#3b82f6' : '#1f2937'
            }}>
              {children}
            </h2>
          ),
          h3: ({ children }) => (
            <h3 style={{
              fontSize: '18px',
              fontWeight: '600',
              marginBottom: '10px',
              marginTop: '16px',
              color: isDarkMode ? '#3b82f6' : '#374151'
            }}>
              {children}
            </h3>
          ),
          p: ({ children }) => (
            <p style={{
              marginBottom: '12px',
              lineHeight: '1.6',
              color: isDarkMode ? '#f7fafc' : '#374151'
            }}>
              {children}
            </p>
          ),
          ul: ({ children }) => (
            <ul style={{
              marginBottom: '12px',
              paddingLeft: '20px',
              listStyleType: 'disc'
            }}>
              {children}
            </ul>
          ),
          ol: ({ children }) => (
            <ol style={{
              marginBottom: '12px',
              paddingLeft: '20px',
              listStyleType: 'decimal'
            }}>
              {children}
            </ol>
          ),
          li: ({ children }) => (
            <li style={{
              marginBottom: '4px',
              lineHeight: '1.5',
              color: isDarkMode ? '#f7fafc' : '#374151'
            }}>
              {children}
            </li>
          ),
          blockquote: ({ children }) => (
            <blockquote style={{
              borderLeft: '4px solid #3b82f6',
              paddingLeft: '16px',
              marginLeft: '0',
              marginBottom: '12px',
              fontStyle: 'italic',
              backgroundColor: isDarkMode ? '#2d3748' : '#f8fafc',
              padding: '12px 16px',
              borderRadius: '0 6px 6px 0',
              color: isDarkMode ? '#cbd5e0' : '#475569'
            }}>
              {children}
            </blockquote>
          ),
          strong: ({ children }) => (
            <strong style={{
              fontWeight: '600',
              color: isDarkMode ? '#f7fafc' : '#1f2937'
            }}>
              {children}
            </strong>
          ),
          em: ({ children }) => (
            <em style={{
              fontStyle: 'italic',
              color: isDarkMode ? '#cbd5e0' : '#4b5563'
            }}>
              {children}
            </em>
          ),
          table: ({ children }) => (
            <div style={{ overflowX: 'auto', marginBottom: '16px' }}>
              <table style={{
                width: '100%',
                borderCollapse: 'collapse',
                border: `1px solid ${isDarkMode ? '#4a5568' : '#e5e7eb'}`,
                borderRadius: '6px',
                backgroundColor: isDarkMode ? '#2d3748' : 'white'
              }}>
                {children}
              </table>
            </div>
          ),
          thead: ({ children }) => (
            <thead style={{ backgroundColor: isDarkMode ? '#4a5568' : '#f9fafb' }}>
              {children}
            </thead>
          ),
          th: ({ children }) => (
            <th style={{
              padding: '12px',
              textAlign: 'left',
              fontWeight: '600',
              color: isDarkMode ? '#f7fafc' : '#374151',
              borderBottom: `1px solid ${isDarkMode ? '#4a5568' : '#e5e7eb'}`
            }}>
              {children}
            </th>
          ),
          td: ({ children }) => (
            <td style={{
              padding: '12px',
              borderBottom: `1px solid ${isDarkMode ? '#4a5568' : '#f3f4f6'}`,
              color: isDarkMode ? '#f7fafc' : '#374151'
            }}>
              {children}
            </td>
          ),
          a: ({ href, children }) => (
            <a
              href={href}
              target="_blank"
              rel="noopener noreferrer"
              style={{
                color: '#3b82f6',
                textDecoration: 'underline',
                cursor: 'pointer'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.color = '#1d4ed8'
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.color = '#3b82f6'
              }}
            >
              {children}
            </a>
          ),
          hr: () => (
            <hr style={{
              border: 'none',
              borderTop: `1px solid ${isDarkMode ? '#4a5568' : '#e5e7eb'}`,
              margin: '20px 0'
            }} />
          )
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  )
}
