import mermaid from './mermaid.esm.min.mjs';
mermaid.initialize({startOnLoad:false,securityLevel:'strict',theme:'base'});
for(const node of document.querySelectorAll('.mermaid')){try{await mermaid.run({nodes:[node]});}catch(error){node.classList.add('mermaid-error');node.textContent=`Diagram could not be rendered.\n${node.textContent}`;}}
