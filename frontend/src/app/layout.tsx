import './globals.css'  // Only this file should import CSS

export const metadata = {
  title: 'Document Analyzer',
  description: 'AI-powered document summarization',
  themeColor: '#0f172a',
  backgroundColor: '#0f172a',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" style={{ backgroundColor: '#0f172a' }}>
      <head>
        <meta name="theme-color" content="#0f172a" />
        <meta name="background-color" content="#0f172a" />
        <style dangerouslySetInnerHTML={{
          __html: `
            html, body, #__next, #__next > div, .app-container {
              background-color: #0f172a !important;
              color: #f1f5f9 !important;
              margin: 0 !important;
              padding: 0 !important;
              min-height: 100vh !important;
            }
            * {
              margin: 0;
              padding: 0;
            }
            body::before {
              content: '';
              position: fixed;
              top: 0;
              left: 0;
              right: 0;
              bottom: 0;
              background-color: #0f172a;
              z-index: -1;
            }
          `
        }} />
      </head>
      <body style={{ backgroundColor: '#0f172a', color: '#f1f5f9', margin: 0, padding: 0 }}>
        {children}
      </body>
    </html>
  )
}