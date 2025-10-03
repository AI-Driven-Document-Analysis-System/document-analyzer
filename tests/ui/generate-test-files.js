const fs = require('fs');
const { PDFDocument, rgb } = require('pdf-lib');

async function createSamplePdf() {
  const pdfDoc = await PDFDocument.create();
  const page = pdfDoc.addPage([600, 400]);
  
  const { width, height } = page.getSize();
  const fontSize = 24;
  
  page.drawText('Sample PDF Document', {
    x: 50,
    y: height - 4 * fontSize,
    size: fontSize,
    color: rgb(0, 0, 0),
  });
  
  page.drawText('This is a test PDF file for document upload testing.', {
    x: 50,
    y: height - 8 * fontSize,
    size: 14,
    color: rgb(0, 0, 0),
  });
  
  // Create test-files directory if it doesn't exist
  if (!fs.existsSync('./test-files')) {
    fs.mkdirSync('./test-files');
  }
  
  // Save the PDF
  const pdfBytes = await pdfDoc.save();
  fs.writeFileSync('./test-files/sample.pdf', pdfBytes);
  
  // Create a large PDF for testing file size limits
  const largePdf = await PDFDocument.create();
  for (let i = 0; i < 50; i++) {
    const page = largePdf.addPage([600, 800]);
    page.drawText(`Page ${i + 1} of 50\n\n`.repeat(40), {
      x: 50,
      y: 750,
      size: 12,
      color: rgb(0, 0, 0),
    });
  }
  const largePdfBytes = await largePdf.save();
  fs.writeFileSync('./test-files/large.pdf', largePdfBytes);
  
  console.log('Test files generated successfully!');
}

// Create an invalid file type
function createInvalidFile() {
  if (!fs.existsSync('./test-files')) {
    fs.mkdirSync('./test-files');
  }
  fs.writeFileSync('./test-files/invalid.exe', 'This is not a valid document');
}

// Run the functions
createSamplePdf().catch(console.error);
createInvalidFile();
