const pptxgen = require('pptxgenjs');
const html2pptx = require('/Users/yzhang/Library/CloudStorage/OneDrive-Personal/ML/2026/agent/X-IPE/.github/skills/pptx/scripts/html2pptx.js');
const fs = require('fs');
const path = require('path');

// Color palette: Deep Purple & Emerald (enterprise AI theme)
const colors = {
  purple: '9B59B6',
  darkBg: '1C2833',
  emerald: '40695B',
  white: 'FFFFFF',
  lightGray: 'F4F6F6',
  accent: 'E74C3C'
};

async function createPresentation() {
  const pptx = new pptxgen();
  pptx.layout = 'LAYOUT_16x9';
  pptx.title = 'AI-Integrated Enterprise Knowledge Base';
  pptx.author = 'X-IPE';
  pptx.subject = 'IDEA-011 - Alibaba Cloud Architecture';

  const slidesDir = __dirname;

  // Slide 1: Title
  await html2pptx(path.join(slidesDir, 'slide01-title.html'), pptx);

  // Slide 2: Problem Statement
  await html2pptx(path.join(slidesDir, 'slide02-problem.html'), pptx);

  // Slide 3: Solution Overview
  await html2pptx(path.join(slidesDir, 'slide03-solution.html'), pptx);

  // Slide 4: Target Users
  await html2pptx(path.join(slidesDir, 'slide04-users.html'), pptx);

  // Slide 5: Architecture - Functional
  await html2pptx(path.join(slidesDir, 'slide05-architecture.html'), pptx);

  // Slide 6: Alibaba Cloud Stack
  await html2pptx(path.join(slidesDir, 'slide06-alibaba.html'), pptx);

  // Slide 7: Build vs Buy
  const { slide: slide7, placeholders: ph7 } = await html2pptx(path.join(slidesDir, 'slide07-buildvsbuy.html'), pptx);
  if (ph7.length > 0) {
    slide7.addChart(pptx.charts.PIE, [{
      name: 'Systems',
      labels: ['Buy (10)', 'Build (9)', 'Configure (5)'],
      values: [10, 9, 5]
    }], {
      ...ph7[0],
      showPercent: true,
      showLegend: true,
      legendPos: 'b',
      chartColors: [colors.emerald, colors.purple, 'AAB7B8']
    });
  }

  // Slide 8: Key Features
  await html2pptx(path.join(slidesDir, 'slide08-features.html'), pptx);

  // Slide 9: Implementation Roadmap
  await html2pptx(path.join(slidesDir, 'slide09-roadmap.html'), pptx);

  // Slide 10: Cost & Next Steps
  await html2pptx(path.join(slidesDir, 'slide10-cost.html'), pptx);

  await pptx.writeFile({ fileName: path.join(slidesDir, 'IDEA-011-Enterprise-Knowledge-Base.pptx') });
  console.log('Presentation created: IDEA-011-Enterprise-Knowledge-Base.pptx');
}

createPresentation().catch(console.error);
