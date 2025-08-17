import './globals.css'  // Only this file should import CSS

export const metadata = {
  title: 'Document Analyzer',
  description: 'AI-powered document summarization',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}