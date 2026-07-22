/** FEATURE-060-A UI controller. */
class CrAssessmentPoller {
    constructor(callback, interval = 5000) { this.callback = callback; this.interval = interval; this.timer = null; this.inFlight = false; }
    start() { if (!this.timer) this.timer = setInterval(() => this.pollNow(), this.interval); }
    stop() { if (this.timer) clearInterval(this.timer); this.timer = null; }
    async pollNow() { if (this.inFlight || document.hidden) return; this.inFlight = true; try { await this.callback(); } finally { this.inFlight = false; } }
}

class CrAssessmentView {
    constructor(root, api = new CrAssessmentApi()) {
        this.root = root; this.api = api; this.summaries = []; this.selectedCase = null;
        this.markers = {}; this.dirty = new Set(); this.depth = 'standard'; this.slide = 0;
        this.poller = new CrAssessmentPoller(() => this._poll());
        this.picker = new LocalDirectoryPicker(api);
    }

    async init() {
        this._cache(); this._bind(); await this.loadCases(); this.poller.start();
        this._visibility = () => { if (!document.hidden) this.poller.pollNow(); };
        document.addEventListener('visibilitychange', this._visibility);
    }

    destroy() { this.poller.stop(); document.removeEventListener('visibilitychange', this._visibility); }

    _cache() {
        const q = (id) => this.root.querySelector(`#${id}`);
        this.el = { list:q('cr-case-list'), count:q('cr-case-count'), search:q('cr-search'), form:q('cr-case-form'), name:q('cr-case-name'), id:q('cr-case-id'), description:q('cr-description'), codebase:q('cr-codebase'), comments:q('cr-comments'), vendor:q('cr-vendor'), vendorFile:q('cr-vendor-file'), supporting:q('cr-supporting'), supportingList:q('cr-supporting-list'), title:q('cr-case-title'), number:q('cr-case-number'), alert:q('cr-alert'), readiness:q('cr-readiness-list'), estimate:q('cr-estimate'), depthMenu:q('cr-depth-menu'), depthLabel:q('cr-depth-label'), infoTab:q('cr-tab-information'), reportTab:q('cr-tab-report'), infoPanel:q('cr-information-panel'), reportPanel:q('cr-report-panel'), reportEmpty:q('cr-report-empty'), reportContent:q('cr-report-content'), stage:q('cr-slide-stage'), dots:q('cr-slide-dots'), position:q('cr-slide-position'), links:q('cr-report-links'), toast:q('cr-toast') };
    }

    _bind() {
        this.el.search.addEventListener('input', () => this.loadCases(this.el.search.value));
        this.root.querySelector('#cr-new-case').addEventListener('click', () => this.newCase());
        this.root.querySelector('#cr-mobile-list').addEventListener('click', () => { this.root.dataset.railOpen = this.root.dataset.railOpen !== 'true'; });
        this.el.form.addEventListener('submit', (e) => { e.preventDefault(); this.save(); });
        for (const control of this.el.form.querySelectorAll('input,textarea')) control.addEventListener('input', () => this.dirty.add(control.name));
        this.root.querySelector('#cr-browse').addEventListener('click', () => this.picker.open(this.el.codebase.value, (path) => { this.el.codebase.value = path; this.dirty.add('codebase_path'); this._validatePath(); }));
        this.el.codebase.addEventListener('change', () => this._validatePath());
        this.el.vendor.addEventListener('change', () => this._renderReadiness());
        this.el.estimate.addEventListener('click', () => { const open = this.el.depthMenu.hidden; this.el.depthMenu.hidden = !open; this.el.estimate.setAttribute('aria-expanded', String(open)); });
        for (const option of this.el.depthMenu.querySelectorAll('[data-depth]')) option.addEventListener('click', () => { this._chooseDepth(option.dataset.depth); this.prepare(); });
        this.root.querySelector('#cr-open-report').addEventListener('click', () => this._activateTab('report'));
        this.el.infoTab.addEventListener('click', () => this._activateTab('information'));
        this.el.reportTab.addEventListener('click', () => this._activateTab('report'));
        for (const tab of [this.el.infoTab, this.el.reportTab]) tab.addEventListener('keydown', (event) => this._tabKey(event));
        this.root.querySelector('#cr-prev-slide').addEventListener('click', () => this.showSlide(this.slide - 1));
        this.root.querySelector('#cr-next-slide').addEventListener('click', () => this.showSlide(this.slide + 1));
        document.addEventListener('keydown', (event) => { if (!this.el.reportPanel.hidden && !/INPUT|TEXTAREA|SELECT/.test(event.target.tagName)) { if (event.key === 'ArrowLeft') this.showSlide(this.slide - 1); if (event.key === 'ArrowRight') this.showSlide(this.slide + 1); } });
    }

    async loadCases(query = '') {
        try { const data = await this.api.listCases(query); this.summaries = data.cases; this.markers = Object.fromEntries(this.summaries.map((item) => [item.id, item.marker])); this.renderList(); if (!this.selectedCase && this.summaries.length) await this.selectCase(this.summaries[0].id); else if (!this.selectedCase && !this.summaries.length && !query) this.newCase(); }
        catch (error) { this.el.list.textContent = `Cases could not be loaded: ${error.message}`; }
    }

    renderList() {
        this.el.count.textContent = this.summaries.length; this.el.list.replaceChildren();
        if (!this.summaries.length) { const empty = document.createElement('p'); empty.className='cr-list-empty'; empty.textContent = this.el.search.value ? 'No matching cases.' : 'No assessment cases yet.'; this.el.list.appendChild(empty); return; }
        for (const item of this.summaries) { const button=document.createElement('button'); button.type='button'; button.className='cr-case-card'; button.dataset.caseId=item.id; button.setAttribute('aria-current', String(this.selectedCase?.case?.id===item.id)); button.innerHTML=`<span class="cr-case-card__top"><strong></strong><span class="cr-status cr-status--${item.status.toLowerCase()}"></span></span><small class="cr-case-card__id"></small><small class="cr-case-card__updated"></small>`; button.querySelector('strong').textContent=item.name; button.querySelector('.cr-status').textContent=item.status; button.querySelector('.cr-case-card__id').textContent=item.id; button.querySelector('.cr-case-card__updated').textContent=`Updated ${this._relativeTime(item.updated_at)}`; button.addEventListener('click',()=>this.selectCase(item.id)); this.el.list.appendChild(button); }
    }

    async selectCase(caseId) {
        if (this.dirty.size && !window.confirm('Discard unsaved changes?')) return;
        this.root.setAttribute('aria-busy','true'); this.el.title.textContent='Loading case…'; this.el.number.textContent=caseId.split('-').pop();
        try { this.selectedCase=await this.api.getCase(caseId); this.dirty.clear(); this.renderCase(); this.root.dataset.railOpen='false'; }
        catch(error){ this._alert(error.message); }
        finally { this.root.setAttribute('aria-busy','false'); }
    }

    newCase() { if (this.dirty.size && !window.confirm('Discard unsaved changes?')) return; this.selectedCase=null; this.dirty.clear(); this.el.form.reset(); this.el.id.value='Assigned on save'; this.el.title.textContent='New Assessment Case'; this.el.number.textContent='NEW'; this._renderReadiness(); this.renderList(); this.el.name.focus(); }

    renderCase() {
        const data=this.selectedCase, inputs=data.inputs||{}; this.el.name.value=data.case.name||''; this.el.id.value=data.case.id; this.el.description.value=inputs.cr_description?.text||''; this.el.codebase.value=inputs.codebase_path||''; this.el.comments.value=inputs.comments||''; this.el.title.textContent=data.case.name; this.el.number.textContent=data.case.id.split('-').pop(); this.depth=data.invocation?.analysis_depth||'standard'; this.el.depthLabel.textContent=this._title(this.depth); this._renderFiles(inputs); this._renderReadiness(); this._renderReports(); this.renderList(); const disabled=data.case.status==='Evaluating'; for(const element of this.el.form.querySelectorAll('input,textarea')) if(!element.readOnly) element.disabled=disabled; this.el.estimate.disabled=disabled||!this._isReady(); }

    _formData() { const data=new FormData(this.el.form); if(this.selectedCase) data.set('expected_revision',String(this.selectedCase.record_revision)); return data; }

    async save() { this._clearErrors(); try { this.selectedCase=this.selectedCase ? await this.api.updateCase(this.selectedCase.case.id,this._formData()) : await this.api.createCase(this._formData()); this.dirty.clear(); await this.loadCases(this.el.search.value); this.renderCase(); this._toast('Case saved'); } catch(error){ this._showErrors(error); } }

    async prepare() { if(this.el.estimate.disabled) return; this._clearErrors(); try { const data=this._formData(); data.set('depth',this.depth); const result=await this.api.prepareAssessment(this.selectedCase.case.id,data); this.selectedCase=await this.api.getCase(this.selectedCase.case.id); this.renderCase(); this._insertCommand(result.command); this._toast('Assessment prompt is ready in the Console'); } catch(error){ this._showErrors(error); } }

    _insertCommand(command) { window.terminalPanel?.expand?.(); if(window.terminalManager?.sendCopilotPromptCommandNoEnter) window.terminalManager.sendCopilotPromptCommandNoEnter(command); else window.terminalManager?.sendCopilotPromptCommand?.(command); }

    async _validatePath() { const result=await this.api.validatePath(this.el.codebase.value); this._setError('codebase_path',result.valid?'':result.reason); this._renderReadiness(result.valid); }

    _renderReadiness(codebaseOverride) { const data=this.selectedCase?.readiness||{}; const descriptionFile=this.root.querySelector('#cr-description-file'); const states={ 'CR Brief':Boolean(this.el.description.value||descriptionFile?.files?.length||data.cr_brief), 'Codebase':codebaseOverride??Boolean(data.codebase||this.el.codebase.value), 'Vendor Estimate':Boolean(data.vendor_estimate||this.el.vendor.files.length) }; this.el.readiness.replaceChildren(); for(const [label,ready] of Object.entries(states)){const row=document.createElement('div');row.className='cr-ready';row.dataset.ready=ready;row.innerHTML=`<i class="bi ${ready?'bi-check-lg':'bi-dash'}" aria-hidden="true"></i><span></span><small></small>`;row.querySelector('span').textContent=label;row.querySelector('small').textContent=ready?'Ready':'Required';this.el.readiness.appendChild(row);} this.el.estimate.disabled=!this.selectedCase||this.selectedCase.case.status==='Evaluating'||!Object.values(states).every(Boolean); }

    _isReady(){ return !this.el.estimate.disabled; }
    _chooseDepth(depth){this.depth=depth;this.el.depthLabel.textContent=this._title(depth);for(const option of this.el.depthMenu.querySelectorAll('[data-depth]')) option.classList.toggle('active',option.dataset.depth===depth);this.el.depthMenu.hidden=true;this.el.estimate.setAttribute('aria-expanded','false');}
    _activateTab(name){const report=name==='report';this.el.infoTab.setAttribute('aria-selected',String(!report));this.el.reportTab.setAttribute('aria-selected',String(report));this.el.infoTab.tabIndex=report?-1:0;this.el.reportTab.tabIndex=report?0:-1;this.el.infoPanel.hidden=report;this.el.reportPanel.hidden=!report;(report?this.el.reportTab:this.el.infoTab).focus();}
    _tabKey(event){const tabs=[this.el.infoTab,this.el.reportTab];let index=tabs.indexOf(event.currentTarget);if(event.key==='ArrowRight')index=(index+1)%2;else if(event.key==='ArrowLeft')index=(index+1)%2;else if(event.key==='Home')index=0;else if(event.key==='End')index=1;else return;event.preventDefault();this._activateTab(index?'report':'information');}

    _renderReports(){const reports=this.selectedCase?.reports||{};const all=[...Object.values(reports.latest||{}),...(reports.history||[]).flatMap((item)=>Object.values(item.files||{}))].filter((value)=>typeof value==='string');this.el.reportEmpty.hidden=all.length>0;this.el.reportContent.hidden=!all.length;if(!all.length)return;this.slides=[{title:this.selectedCase.case.name,text:`Status: ${this.selectedCase.case.status}`},{title:'Assessment outputs',text:`${all.length} report file${all.length===1?'':'s'} available.`,disclosure:true}];this.el.dots.replaceChildren();this.slides.forEach((_,index)=>{const dot=document.createElement('button');dot.type='button';dot.setAttribute('aria-label',`Slide ${index+1}`);dot.addEventListener('click',()=>this.showSlide(index));this.el.dots.appendChild(dot);});this.el.links.replaceChildren();for(const path of all){const button=document.createElement('button');button.type='button';button.textContent=path.split('/').pop();button.addEventListener('click',async()=>{try{await new DeliverableViewer({workflowName:'cr-assessment'}).showPreview(path);}catch(_error){this._alert(`Report could not be opened: ${button.textContent}. Other report versions remain available.`);}});this.el.links.appendChild(button);}this.showSlide(0);}
    showSlide(index){if(!this.slides?.length)return;this.slide=(index+this.slides.length)%this.slides.length;const item=this.slides[this.slide];this.el.stage.replaceChildren();const article=document.createElement('article');const h=document.createElement('h3');h.textContent=item.title;const p=document.createElement('p');p.textContent=item.text;article.append(h,p);if(item.disclosure){const details=document.createElement('details');const summary=document.createElement('summary');summary.textContent='Module summary';const content=document.createElement('p');content.textContent='Open the report files below for module-level evidence and recommendations.';details.append(summary,content);article.appendChild(details);}this.el.stage.appendChild(article);[...this.el.dots.children].forEach((dot,i)=>dot.setAttribute('aria-current',String(i===this.slide)));this.el.position.textContent=`${this.slide+1} / ${this.slides.length}`;}

    async _poll(){try{const changes=await this.api.pollChanges(this.markers);this.markers=changes.markers;if(!changes.changed.length&&!changes.removed.length)return;for(const removed of changes.removed)this.summaries=this.summaries.filter((item)=>item.id!==removed);for(const item of changes.changed){const index=this.summaries.findIndex((candidate)=>candidate.id===item.id);if(index>=0)this.summaries[index]=item;else this.summaries.push(item);}this.summaries.sort((a,b)=>b.updated_at.localeCompare(a.updated_at));this.renderList();if(this.selectedCase&&changes.changed.some((item)=>item.id===this.selectedCase.case.id)){const fresh=await this.api.getCase(this.selectedCase.case.id);if(this.dirty.size){this.selectedCase={...fresh,inputs:this.selectedCase.inputs};this._alert('Assessment metadata changed. Save or discard your local edits.');}else{this.selectedCase=fresh;this.renderCase();}this._toast('Assessment status updated');}}catch(_error){/* next poll retries */}}

    _clearErrors(){for(const el of this.root.querySelectorAll('.cr-error'))el.textContent='';this.el.alert.hidden=true;}
    _setError(field,message){const el=this.root.querySelector(`[data-error="${field}"]`);if(el)el.textContent=message||'';}
    _showErrors(error){for(const [field,message] of Object.entries(error.details||{}))this._setError(field,message);this._alert(error.message);}
    _alert(message){this.el.alert.textContent=message;this.el.alert.hidden=false;}
    _toast(message){this.el.toast.textContent=message;this.el.toast.hidden=false;clearTimeout(this.toastTimer);this.toastTimer=setTimeout(()=>{this.el.toast.hidden=true;},2500);}
    _renderFiles(inputs){const supporting=inputs.supporting_documents||[];this.el.supportingList.replaceChildren(...supporting.map((file)=>this._fileChip(file.original_name||file.path)));const vendor=inputs.vendor_estimate||{};this.el.vendorFile.replaceChildren(...(vendor.original_name||vendor.path?[this._fileChip(vendor.original_name||vendor.path)]:[]));}
    _fileChip(name){const chip=document.createElement('span');chip.className='cr-file-chip';chip.textContent=name;chip.title='Stored evidence file; choose a new file to replace or supplement it.';return chip;}
    _relativeTime(value){const elapsed=Math.max(0,Date.now()-Date.parse(value||0));if(elapsed<60000)return'just now';const minutes=Math.floor(elapsed/60000);if(minutes<60)return`${minutes}m ago`;const hours=Math.floor(minutes/60);if(hours<24)return`${hours}h ago`;return`${Math.floor(hours/24)}d ago`;}
    _title(value){return value.charAt(0).toUpperCase()+value.slice(1);}
}

globalThis.CrAssessmentPoller=CrAssessmentPoller;globalThis.CrAssessmentView=CrAssessmentView;
if(typeof document!=='undefined')document.addEventListener('DOMContentLoaded',()=>{const root=document.querySelector('#cr-assessment-app');if(root){window.crAssessmentView=new CrAssessmentView(root);window.crAssessmentView.init();}});
