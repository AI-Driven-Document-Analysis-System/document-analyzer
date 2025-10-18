$file = 'c:\Users\sahan\OneDrive\Desktop\document-analyzer\frontend\src\components\dashboard\dashboard.tsx'
$content = Get-Content $file -Raw

# Pattern to match the entire section from line 1698 to 1763
$pattern = '(?s)          /\* Left side - Search and Recent Documents \(50% width\) \*/\r?\n          <div className="feature-container".*?            </div>\r?\n          </div>'

# Replacement
$replacement = '          <RecentDocuments documents={documentsWithSummary} onSummarize={handleSummarizeDoc} onChatWithDoc={handleChatWithDoc} onPreview={previewDocumentHandler} />'

# Replace
$content = $content -replace $pattern, $replacement

# Save
Set-Content $file $content -NoNewline

Write-Host "Done! Dashboard.tsx has been updated."
