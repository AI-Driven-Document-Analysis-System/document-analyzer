$file = 'c:\Users\sahan\OneDrive\Desktop\document-analyzer\frontend\src\components\dashboard\dashboard.tsx'
$content = Get-Content $file -Raw

# Replace the inline Recent Documents code with the component
$pattern = '(?s)          {/\* Left side - Search and Recent Documents \(50% width\) \*/}.*?          </div>\s*(?=\s*{/\* Right side)'

$replacement = '          <RecentDocuments 
            documents={documentsWithSummary}
            onSummarize={handleSummarizeDoc}
            onChatWithDoc={handleChatWithDoc}
            onPreview={previewDocumentHandler}
          />'

$content = $content -replace $pattern, $replacement

Set-Content $file $content -NoNewline

Write-Host "Dashboard modularized successfully!"
