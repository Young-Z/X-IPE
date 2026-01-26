const pptxgen = require('/Users/yzhang/Library/CloudStorage/OneDrive-Personal/ML/2026/agent/X-IPE/.github/skills/pptx/scripts/node_modules/pptxgenjs');
const html2pptx = require('/Users/yzhang/Library/CloudStorage/OneDrive-Personal/ML/2026/agent/X-IPE/.github/skills/pptx/scripts/html2pptx.js');
const path = require('path');

async function createPresentation() {
    const pptx = new pptxgen();
    pptx.layout = 'LAYOUT_16x9';
    pptx.author = 'AI Capability Sharing';
    pptx.title = 'AI Capability Review Through Practice';
    pptx.subject = 'Internal Knowledge Sharing Session';

    const workspace = '/Users/yzhang/Library/CloudStorage/OneDrive-Personal/ML/2026/agent/X-IPE/x-ipe-docs/ideas/203. Playground-AI-Capability-Sharing/workspace';
    
    // Create all 8 slides
    for (let i = 1; i <= 8; i++) {
        const htmlFile = path.join(workspace, `slide${i}.html`);
        await html2pptx(htmlFile, pptx);
        console.log(`Slide ${i} created`);
    }

    // Save presentation
    const outputPath = '/Users/yzhang/Library/CloudStorage/OneDrive-Personal/ML/2026/agent/X-IPE/x-ipe-docs/ideas/203. Playground-AI-Capability-Sharing/AI-Capability-Sharing.pptx';
    await pptx.writeFile({ fileName: outputPath });
    console.log(`Presentation saved to: ${outputPath}`);
}

createPresentation().catch(err => {
    console.error('Error:', err);
    process.exit(1);
});
