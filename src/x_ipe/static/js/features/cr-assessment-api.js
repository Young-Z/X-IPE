/** HTTP adapter for FEATURE-060-A. */
class CrAssessmentApi {
    async _request(url, options = {}) {
        const response = await fetch(url, options);
        const payload = await response.json();
        if (!response.ok || payload.success === false) {
            const error = new Error(payload.error?.message || 'Request failed');
            error.code = payload.error?.code;
            error.details = payload.error?.details || {};
            error.status = response.status;
            throw error;
        }
        return payload.data;
    }

    listCases(query = '') { return this._request(`/api/cr-assessments?query=${encodeURIComponent(query)}`); }
    getCase(caseId) { return this._request(`/api/cr-assessments/${encodeURIComponent(caseId)}`); }
    createCase(formData) { return this._request('/api/cr-assessments', { method: 'POST', body: formData }); }
    updateCase(caseId, formData) { return this._request(`/api/cr-assessments/${encodeURIComponent(caseId)}`, { method: 'PUT', body: formData }); }
    prepareAssessment(caseId, formData) { return this._request(`/api/cr-assessments/${encodeURIComponent(caseId)}/prepare`, { method: 'POST', body: formData }); }
    validatePath(path) { return this._request('/api/cr-assessments/validate-path', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ path }) }); }
    listDirectories(path = '') { return this._request(`/api/cr-assessments/directories?path=${encodeURIComponent(path)}`); }
    pollChanges(markers) { return this._request('/api/cr-assessments/changes', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ markers }) }); }
}
globalThis.CrAssessmentApi = CrAssessmentApi;
