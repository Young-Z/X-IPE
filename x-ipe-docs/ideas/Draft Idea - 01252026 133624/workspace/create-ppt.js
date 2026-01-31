const pptxgen = require('pptxgenjs');
const html2pptx = require('/Users/yzhang/Library/CloudStorage/OneDrive-Personal/ML/2026/agent/X-IPE/.github/skills/pptx/scripts/html2pptx.js');
const fs = require('fs');
const path = require('path');

const WORKSPACE = '/Users/yzhang/Library/CloudStorage/OneDrive-Personal/ML/2026/agent/X-IPE/x-ipe-docs/ideas/Draft Idea - 01252026 133624/workspace';

// Color palette: Charcoal & Red
const COLORS = {
  dark: '292929',
  red: 'E33737',
  gray: 'CCCBCB',
  white: 'FFFFFF',
  lightGray: 'F5F5F5'
};

// Slide 1: Title
const slide1Html = `<!DOCTYPE html>
<html>
<head>
<style>
html { background: #292929; }
body {
  width: 720pt; height: 405pt; margin: 0; padding: 0;
  background: #292929; font-family: Arial, sans-serif;
  display: flex; flex-direction: column; justify-content: center; align-items: center;
}
.title { color: #FFFFFF; font-size: 38pt; font-weight: bold; text-align: center; margin: 0 40pt; }
.subtitle { color: #E33737; font-size: 22pt; margin-top: 20pt; text-align: center; }
.date { color: #CCCBCB; font-size: 14pt; margin-top: 40pt; }
.accent-line { width: 120pt; height: 4pt; background: #E33737; margin-top: 30pt; }
</style>
</head>
<body>
<h1 class="title">AI开发工作流反馈报告</h1>
<p class="subtitle">Dify · MCP · 前端开发经验总结</p>
<div class="accent-line"></div>
<p class="date">2026年1月</p>
</body>
</html>`;

// Slide 2: Dify Workflow Challenges
const slide2Html = `<!DOCTYPE html>
<html>
<head>
<style>
html { background: #FFFFFF; }
body {
  width: 720pt; height: 405pt; margin: 0; padding: 0;
  background: #FFFFFF; font-family: Arial, sans-serif;
  display: flex; flex-direction: column;
}
.header { background: #292929; padding: 15pt 30pt; }
.header h1 { color: #FFFFFF; font-size: 22pt; margin: 0; }
.header-accent { color: #E33737; font-size: 12pt; margin-top: 4pt; }
.content { display: flex; flex: 1; padding: 18pt 30pt; gap: 20pt; }
.left { flex: 1; }
.right { width: 170pt; display: flex; flex-direction: column; gap: 12pt; }
.point { margin-bottom: 12pt; }
.point-title { color: #E33737; font-size: 12pt; font-weight: bold; margin-bottom: 3pt; }
.point-desc { color: #292929; font-size: 10pt; }
.time-tag { color: #CCCBCB; font-size: 9pt; margin-top: 2pt; }
.stat-box { background: #F5F5F5; border-left: 4pt solid #E33737; padding: 10pt; }
.stat-num { color: #E33737; font-size: 26pt; font-weight: bold; }
.stat-label { color: #292929; font-size: 9pt; margin-top: 2pt; }
.example { background: #292929; padding: 10pt; margin-top: 8pt; }
.example p { color: #CCCBCB; font-size: 9pt; margin: 0; }
</style>
</head>
<body>
<div class="header">
  <h1>Dify工作流的挑战</h1>
  <p class="header-accent">Slide 1 - 主要痛点分析</p>
</div>
<div class="content">
  <div class="left">
    <div class="point">
      <p class="point-title">调试诊断复杂</p>
      <p class="point-desc">Agent处理未达预期时的调试诊断特别复杂，且不直观</p>
      <p class="time-tag">耗时影响: ++</p>
    </div>
    <div class="point">
      <p class="point-title">AI无法高效接管</p>
      <p class="point-desc">Dify并非能让AI码代码，需要人工拖拉拽，功能越复杂边际成本越高</p>
      <p class="time-tag">耗时影响: +++</p>
    </div>
    <div class="point">
      <p class="point-title">高阶用法学习成本高</p>
      <p class="point-desc">需查找各类文档，向AI提问也不直观，且不一定有效</p>
      <p class="time-tag">耗时影响: ++</p>
    </div>
  </div>
  <div class="right">
    <div class="stat-box">
      <p class="stat-num">70%</p>
      <p class="stat-label">后期调优时间占比</p>
    </div>
    <div class="example">
      <p>实际案例：70%时间都在后期调优Agent输出结果稳定性</p>
    </div>
  </div>
</div>
</body>
</html>`;

// Slide 3: MCP Server Creation
const slide3Html = `<!DOCTYPE html>
<html>
<head>
<style>
html { background: #FFFFFF; }
body {
  width: 720pt; height: 405pt; margin: 0; padding: 0;
  background: #FFFFFF; font-family: Arial, sans-serif;
  display: flex; flex-direction: column;
}
.header { background: #292929; padding: 15pt 30pt; }
.header h1 { color: #FFFFFF; font-size: 22pt; margin: 0; }
.header-accent { color: #E33737; font-size: 12pt; margin-top: 4pt; }
.content { display: flex; flex: 1; padding: 18pt 30pt; gap: 25pt; }
.section { flex: 1; }
.section-header { border-bottom: 2pt solid #E33737; padding-bottom: 6pt; margin-bottom: 12pt; }
.section-title { color: #292929; font-size: 12pt; font-weight: bold; }
.item { margin-bottom: 12pt; }
.item-label { color: #E33737; font-size: 10pt; font-weight: bold; }
.item-desc { color: #292929; font-size: 10pt; margin-top: 2pt; }
.time-tag { color: #CCCBCB; font-size: 9pt; margin-top: 2pt; }
.highlight-box { background: #F5F5F5; border-left: 4pt solid #E33737; padding: 12pt; margin-top: 12pt; }
.highlight-box p { color: #292929; font-size: 10pt; margin: 0; }
.zero { color: #E33737; font-size: 18pt; font-weight: bold; }
</style>
</head>
<body>
<div class="header">
  <h1>MCP服务端创建</h1>
  <p class="header-accent">Slide 2 - API对接与服务器创建</p>
</div>
<div class="content">
  <div class="section">
    <div class="section-header">
      <p class="section-title">对接目标应用API</p>
    </div>
    <div class="item">
      <p class="item-label">第三方团队学习</p>
      <p class="item-desc">基于接口文档和业务文档学习API含义、字段含义</p>
      <p class="time-tag">耗时影响: +++ (双方都产生耗时)</p>
    </div>
    <div class="item">
      <p class="item-label">原团队梳理</p>
      <p class="item-desc">基于需求梳理接口文档和业务逻辑</p>
      <p class="time-tag">耗时影响: +</p>
    </div>
  </div>
  <div class="section">
    <div class="section-header">
      <p class="section-title">MCP服务器创建</p>
    </div>
    <div class="item">
      <p class="item-desc">基于API文档及业务逻辑文档，AI可自动生成</p>
      <p class="time-tag">耗时影响: <span class="zero">≈ 0</span></p>
    </div>
    <div class="highlight-box">
      <p><b>实际案例：</b>Fred花了2天梳理业务逻辑和接口，但MCP创建仅需1小时</p>
    </div>
  </div>
</div>
</body>
</html>`;

// Slide 4: Frontend Dev & Requirement Waiting
const slide4Html = `<!DOCTYPE html>
<html>
<head>
<style>
html { background: #FFFFFF; }
body {
  width: 720pt; height: 405pt; margin: 0; padding: 0;
  background: #FFFFFF; font-family: Arial, sans-serif;
  display: flex; flex-direction: column;
}
.header { background: #292929; padding: 15pt 30pt; }
.header h1 { color: #FFFFFF; font-size: 22pt; margin: 0; }
.header-accent { color: #E33737; font-size: 12pt; margin-top: 4pt; }
.content { display: flex; flex: 1; padding: 18pt 30pt; gap: 25pt; }
.section { flex: 1; }
.section-header { border-bottom: 2pt solid #E33737; padding-bottom: 6pt; margin-bottom: 12pt; }
.section-title { color: #292929; font-size: 12pt; font-weight: bold; }
.item { margin-bottom: 10pt; }
.item-label { color: #E33737; font-size: 10pt; font-weight: bold; }
.item-desc { color: #292929; font-size: 10pt; margin-top: 2pt; }
.time-tag { color: #CCCBCB; font-size: 9pt; margin-top: 2pt; }
.key-insight { background: #292929; padding: 12pt; margin-top: 10pt; }
.key-insight p { color: #FFFFFF; font-size: 10pt; margin: 0; }
.key-insight .accent { color: #E33737; }
.timeline { background: #F5F5F5; padding: 12pt; margin-top: 8pt; }
.timeline p { color: #292929; font-size: 10pt; margin: 0; }
.timeline .highlight { color: #E33737; font-weight: bold; }
</style>
</head>
<body>
<div class="header">
  <h1>前端开发与需求等待</h1>
  <p class="header-accent">Slide 3 - 开发效率与瓶颈分析</p>
</div>
<div class="content">
  <div class="section">
    <div class="section-header">
      <p class="section-title">前端开发</p>
    </div>
    <div class="item">
      <p class="item-label">代码实现</p>
      <p class="item-desc">如果对实现方法、代码结构没有太高要求，基本没啥成本</p>
      <p class="time-tag">耗时影响: +</p>
    </div>
    <div class="item">
      <p class="item-label">设计稿确认</p>
      <p class="item-desc">简单设计基本没成本，复杂功能需要更频繁沟通</p>
      <p class="time-tag">耗时影响: +</p>
    </div>
    <div class="item">
      <p class="item-label">精细化设计 (To C)</p>
      <p class="item-desc">面向消费者的精细化设计稿</p>
      <p class="time-tag">耗时影响: ++</p>
    </div>
  </div>
  <div class="section">
    <div class="section-header">
      <p class="section-title">需求等待</p>
    </div>
    <div class="key-insight">
      <p>开发确实简单很多，更多是<span class="accent">等待需求输入</span>、确认设计稿并验收调优</p>
    </div>
    <div class="timeline">
      <p><b>实际案例：</b>Mark和Fred在接到需求后<span class="highlight">2-3天</span>完成开发</p>
      <p style="margin-top: 6pt; color: #CCCBCB; font-size: 9pt;">注：并非最优开发模式，demo复杂度也较低</p>
    </div>
  </div>
</div>
</body>
</html>`;

async function createPresentation() {
  // Write HTML files
  fs.writeFileSync(path.join(WORKSPACE, 'slide1.html'), slide1Html);
  fs.writeFileSync(path.join(WORKSPACE, 'slide2.html'), slide2Html);
  fs.writeFileSync(path.join(WORKSPACE, 'slide3.html'), slide3Html);
  fs.writeFileSync(path.join(WORKSPACE, 'slide4.html'), slide4Html);

  const pptx = new pptxgen();
  pptx.layout = 'LAYOUT_16x9';
  pptx.title = 'AI开发工作流反馈报告';
  pptx.author = 'X-IPE';

  // Create slides
  await html2pptx(path.join(WORKSPACE, 'slide1.html'), pptx);
  await html2pptx(path.join(WORKSPACE, 'slide2.html'), pptx);
  await html2pptx(path.join(WORKSPACE, 'slide3.html'), pptx);
  await html2pptx(path.join(WORKSPACE, 'slide4.html'), pptx);

  // Save
  const outputPath = path.join(WORKSPACE, 'AI开发工作流反馈报告.pptx');
  await pptx.writeFile({ fileName: outputPath });
  console.log('Presentation created:', outputPath);
}

createPresentation().catch(console.error);
