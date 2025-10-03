const { exec } = require('child_process');
const fs = require('fs');
const path = require('path');

// Create screenshots directory if it doesn't exist
const screenshotsDir = path.join(__dirname, 'screenshots');
if (!fs.existsSync(screenshotsDir)) {
  fs.mkdirSync(screenshotsDir, { recursive: true });
  console.log('Created screenshots directory');
}

// Run Playwright tests
console.log('Starting Playwright tests...');
const testProcess = exec('npx playwright test --reporter=html,list', { cwd: __dirname });

testProcess.stdout.on('data', (data) => {
  console.log(data.toString());
});

testProcess.stderr.on('data', (data) => {
  console.error(data.toString());
});

testProcess.on('close', (code) => {
  console.log(`Tests completed with code ${code}`);
  
  // Generate a simple HTML report
  generateHtmlReport();
});

function generateHtmlReport() {
  const reportPath = path.join(__dirname, 'test-report.html');
  const screenshots = fs.readdirSync(screenshotsDir)
    .filter(file => file.endsWith('.png'))
    .map(file => ({
      name: file.replace(/-/g, ' ').replace('.png', ''),
      path: `screenshots/${file}`
    }));

  const html = `
  <!DOCTYPE html>
  <html>
  <head>
    <title>Document Analyzer - Test Report</title>
    <style>
      body { font-family: Arial, sans-serif; margin: 0; padding: 20px; }
      h1 { color: #333; }
      .screenshot { margin: 20px 0; border: 1px solid #ddd; padding: 10px; }
      .screenshot img { max-width: 100%; border: 1px solid #eee; }
      .screenshot h3 { margin: 0 0 10px 0; color: #444; }
      .success { color: green; }
      .skipped { color: orange; }
    </style>
  </head>
  <body>
    <h1>Document Analyzer - Test Report</h1>
    <p>Generated on: ${new Date().toLocaleString()}</p>
    <p>Total screenshots: ${screenshots.length}</p>
    
    <h2>Screenshots</h2>
    <div class="screenshots">
      ${screenshots.map(screenshot => `
        <div class="screenshot">
          <h3>${screenshot.name}</h3>
          <img src="${screenshot.path}" alt="${screenshot.name}">
        </div>
      `).join('')}
    </div>
  </body>
  </html>
  `;

  fs.writeFileSync(reportPath, html);
  console.log(`Report generated: ${reportPath}`);
  console.log(`Open the report in your browser to view the screenshots.`);
}
