const pptxgen = require('pptxgenjs');
const html2pptx = require('/Users/yzhang/Library/CloudStorage/OneDrive-Personal/ML/2026/agent/X-IPE/.github/skills/pptx/scripts/html2pptx.js');
const path = require('path');

async function createPresentation() {
  const pptx = new pptxgen();
  pptx.layout = 'LAYOUT_16x9';
  pptx.title = 'Personal Checklist App';
  pptx.author = 'X-IPE';
  pptx.subject = 'IDEA-012 - Polished Task Management for Quick Demos';

  const slidesDir = __dirname;

  // Slide 1: Title
  await html2pptx(path.join(slidesDir, 'slide01-title.html'), pptx);

  // Slide 2: Problem & Users
  await html2pptx(path.join(slidesDir, 'slide02-problem.html'), pptx);

  // Slide 3: Features
  await html2pptx(path.join(slidesDir, 'slide03-features.html'), pptx);

  // Slide 4: Technical Approach
  await html2pptx(path.join(slidesDir, 'slide04-tech.html'), pptx);

  // Slide 5: Demo Script
  await html2pptx(path.join(slidesDir, 'slide05-demo.html'), pptx);

  // Slide 6: Success Criteria
  await html2pptx(path.join(slidesDir, 'slide06-criteria.html'), pptx);

  const outputPath = path.join(slidesDir, '..', 'IDEA-012-Checklist-App.pptx');
  await pptx.writeFile({ fileName: outputPath });
  console.log('Presentation created: IDEA-012-Checklist-App.pptx');
}

createPresentation().catch(console.error);
