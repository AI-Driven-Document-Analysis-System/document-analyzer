// tests/utils/browser-comparison.ts

import { test, Page, expect } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';

interface BrowserMetrics {
  browserName: string;
  loadTime: number;
  domContentLoaded: number;
  firstPaint: number;
  memory?: number;
  errors: string[];
  warnings: string[];
}

interface VisualDifference {
  browser1: string;
  browser2: string;
  difference: number;
  screenshot1: string;
  screenshot2: string;
}

/**
 * Collect performance metrics for browser comparison
 */
export async function collectMetrics(page: Page, browserName: string): Promise<BrowserMetrics> {
  const errors: string[] = [];
  const warnings: string[] = [];

  page.on('pageerror', error => errors.push(error.message));
  page.on('console', msg => {
    if (msg.type() === 'error') errors.push(msg.text());
    if (msg.type() === 'warning') warnings.push(msg.text());
  });

  const metrics = await page.evaluate(() => {
    const perf = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
    const paint = performance.getEntriesByType('paint');
    
    return {
      loadTime: perf.loadEventEnd - perf.fetchStart,
      domContentLoaded: perf.domContentLoadedEventEnd - perf.fetchStart,
      firstPaint: paint.find(p => p.name === 'first-paint')?.startTime || 0,
      memory: (performance as any).memory?.usedJSHeapSize,
    };
  });

  return {
    browserName,
    ...metrics,
    errors: [...new Set(errors)],
    warnings: [...new Set(warnings)],
  };
}

/**
 * Compare CSS rendering across browsers
 */
export async function compareCSSRendering(
  page: Page, 
  selector: string
): Promise<Record<string, any>> {
  const element = page.locator(selector).first();
  
  return await element.evaluate(el => {
    const computed = window.getComputedStyle(el);
    const rect = el.getBoundingClientRect();
    
    return {
      // Layout
      display: computed.display,
      position: computed.position,
      width: rect.width,
      height: rect.height,
      
      // Flexbox
      flexDirection: computed.flexDirection,
      justifyContent: computed.justifyContent,
      alignItems: computed.alignItems,
      gap: computed.gap,
      
      // Spacing
      margin: computed.margin,
      padding: computed.padding,
      
      // Typography
      fontSize: computed.fontSize,
      fontFamily: computed.fontFamily,
      lineHeight: computed.lineHeight,
      
      // Colors
      color: computed.color,
      backgroundColor: computed.backgroundColor,
      
      // Borders
      border: computed.border,
      borderRadius: computed.borderRadius,
      
      // Effects
      boxShadow: computed.boxShadow,
      opacity: computed.opacity,
      transform: computed.transform,
    };
  });
}

/**
 * Test JavaScript API compatibility
 */
export async function testJSCompatibility(page: Page): Promise<Record<string, boolean>> {
  return await page.evaluate(() => {
    return {
      // ES6+ Features
      promises: typeof Promise !== 'undefined',
      asyncAwait: (async () => true)() instanceof Promise,
      arrowFunctions: (() => true)() === true,
      destructuring: (() => { const [a] = [1]; return a === 1; })(),
      spread: (() => { const arr = [...[1, 2]]; return arr.length === 2; })(),
      templateLiterals: `test` === 'test',
      
      // Web APIs
      fetch: typeof fetch !== 'undefined',
      localStorage: typeof localStorage !== 'undefined',
      sessionStorage: typeof sessionStorage !== 'undefined',
      webWorkers: typeof Worker !== 'undefined',
      serviceWorker: 'serviceWorker' in navigator,
      intersectionObserver: typeof IntersectionObserver !== 'undefined',
      resizeObserver: typeof ResizeObserver !== 'undefined',
      
      // Modern APIs
      webGL: (() => {
        try {
          const canvas = document.createElement('canvas');
          return !!(canvas.getContext('webgl') || canvas.getContext('experimental-webgl'));
        } catch { return false; }
      })(),
      webAssembly: typeof WebAssembly !== 'undefined',
      webRTC: typeof RTCPeerConnection !== 'undefined',
      
      // CSS Features (via JS)
      cssFlex: CSS.supports('display', 'flex'),
      cssGrid: CSS.supports('display', 'grid'),
      cssVariables: CSS.supports('color', 'var(--test)'),
    };
  });
}

/**
 * Generate comparison report
 */
export function generateComparisonReport(results: BrowserMetrics[]): string {
  let report = '# Cross-Browser Test Results\n\n';
  
  // Performance Comparison
  report += '## Performance Metrics\n\n';
  report += '| Browser | Load Time (ms) | DOM Content Loaded (ms) | First Paint (ms) | Memory (MB) |\n';
  report += '|---------|----------------|-------------------------|------------------|-------------|\n';
  
  results.forEach(result => {
    const memory = result.memory ? (result.memory / 1024 / 1024).toFixed(2) : 'N/A';
    report += `| ${result.browserName} | ${result.loadTime.toFixed(0)} | ${result.domContentLoaded.toFixed(0)} | ${result.firstPaint.toFixed(0)} | ${memory} |\n`;
  });
  
  // Find fastest/slowest
  const fastest = results.reduce((min, r) => r.loadTime < min.loadTime ? r : min);
  const slowest = results.reduce((max, r) => r.loadTime > max.loadTime ? r : max);
  
  report += `\n**Fastest:** ${fastest.browserName} (${fastest.loadTime.toFixed(0)}ms)\n`;
  report += `**Slowest:** ${slowest.browserName} (${slowest.loadTime.toFixed(0)}ms)\n`;
  report += `**Performance difference:** ${((slowest.loadTime - fastest.loadTime) / fastest.loadTime * 100).toFixed(1)}%\n\n`;
  
  // Errors and Warnings
  report += '## Errors and Warnings\n\n';
  results.forEach(result => {
    if (result.errors.length > 0 || result.warnings.length > 0) {
      report += `### ${result.browserName}\n`;
      if (result.errors.length > 0) {
        report += `**Errors (${result.errors.length}):**\n`;
        result.errors.forEach(err => report += `- ${err}\n`);
      }
      if (result.warnings.length > 0) {
        report += `**Warnings (${result.warnings.length}):**\n`;
        result.warnings.forEach(warn => report += `- ${warn}\n`);
      }
      report += '\n';
    }
  });
  
  return report;
}

/**
 * Save comparison results to file
 */
export function saveResults(results: BrowserMetrics[], filename: string = 'browser-comparison.json') {
  const resultsDir = path.join(process.cwd(), 'test-results');
  if (!fs.existsSync(resultsDir)) {
    fs.mkdirSync(resultsDir, { recursive: true });
  }
  
  const filepath = path.join(resultsDir, filename);
  fs.writeFileSync(filepath, JSON.stringify(results, null, 2));
  
  // Also save markdown report
  const report = generateComparisonReport(results);
  fs.writeFileSync(filepath.replace('.json', '.md'), report);
  
  console.log(`Results saved to ${filepath}`);
}

/**
 * Test suite for comprehensive browser comparison
 */
test.describe('Browser Comparison Suite', () => {
  const allMetrics: BrowserMetrics[] = [];

  test('collect metrics from all browsers', async ({ page, browserName }) => {
    await page.goto('/chat');
    await page.waitForLoadState('networkidle');
    
    const metrics = await collectMetrics(page, browserName);
    allMetrics.push(metrics);
    
    console.log(`${browserName} metrics:`, metrics);
  });

  test('compare CSS rendering', async ({ page, browserName }) => {
    await page.goto('/chat');
    
    const selectors = [
      '[data-testid="message"]',
      '[data-testid="message-input"]',
      'button',
    ];
    
    for (const selector of selectors) {
      const exists = await page.locator(selector).first().count() > 0;
      if (exists) {
        const styles = await compareCSSRendering(page, selector);
        console.log(`${browserName} - ${selector}:`, styles);
        
        // Save to file for comparison
        const resultsDir = path.join(process.cwd(), 'test-results', 'css-comparison');
        if (!fs.existsSync(resultsDir)) {
          fs.mkdirSync(resultsDir, { recursive: true });
        }
        
        const filename = `${selector.replace(/[\[\]"]/g, '')}-${browserName}.json`;
        fs.writeFileSync(
          path.join(resultsDir, filename),
          JSON.stringify(styles, null, 2)
        );
      }
    }
  });

  test('test JavaScript compatibility', async ({ page, browserName }) => {
    await page.goto('/chat');
    
    const compatibility = await testJSCompatibility(page);
    console.log(`${browserName} JS compatibility:`, compatibility);
    
    // All modern features should be supported
    const unsupported = Object.entries(compatibility)
      .filter(([_, supported]) => !supported)
      .map(([feature]) => feature);
    
    if (unsupported.length > 0) {
      console.warn(`${browserName} missing features:`, unsupported);
    }
  });

  test.afterAll(() => {
    if (allMetrics.length > 0) {
      saveResults(allMetrics);
    }
  });
});