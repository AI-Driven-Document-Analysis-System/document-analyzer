import React, { createContext, useContext, useState, useEffect } from 'react'

interface ThemeContextType {
  isDarkMode: boolean
  toggleDarkMode: () => void
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined)

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [isDarkMode, setIsDarkMode] = useState(() => {
    // Check localStorage for saved preference
    if (typeof window !== 'undefined') {
      const saved = localStorage.getItem('chat-dark-mode')
      return saved ? JSON.parse(saved) : false
    }
    return false
  })

  const toggleDarkMode = () => {
    setIsDarkMode(prev => {
      const newValue = !prev
      if (typeof window !== 'undefined') {
        localStorage.setItem('chat-dark-mode', JSON.stringify(newValue))
      }
      return newValue
    })
  }

  return (
    <ThemeContext.Provider value={{ isDarkMode, toggleDarkMode }}>
      {children}
    </ThemeContext.Provider>
  )
}

export function useTheme() {
  const context = useContext(ThemeContext)
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider')
  }
  return context
}
