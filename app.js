/**
 * Procurement Contract Assistant - Main Application
 * Frontend JavaScript application for the procurement RAG system
 */

class ProcurementApp {
    constructor() {
        this.apiKey = null;
        this.documents = [];
        this.history = [];
        this.settings = this.loadSettings();
        this.chart = null;
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadUserPreferences();
        this.updateSystemStatus();
        this.loadHistory();
        this.initializeCharts();
    }

    // ========================================
    // API Communication
    // ========================================

    async apiRequest(endpoint, options = {}) {
        const url = `${CONFIG.API.BASE_URL}${endpoint}`;
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
            },
            timeout: CONFIG.API.TIMEOUT
        };

        const requestOptions = { ...defaultOptions, ...options };

        try {
            const response = await fetch(url, requestOptions);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            return data;
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    }

    async setApiKey(apiKey) {
        try {
            const result = await this.apiRequest(CONFIG.API.ENDPOINTS.SET_API_KEY, {
                method: 'POST',
                body: JSON.stringify({ api_key: apiKey })
            });

            if (result.status === 'success') {
                this.apiKey = apiKey;
                localStorage.setItem(CONFIG.STORAGE.API_KEY, apiKey);
                this.updateApiStatus('success');
                this.showToast('API key set successfully', 'success');
                return true;
            }
        } catch (error) {
            this.showToast('Failed to set API key', 'error');
            return false;
        }
    }

    async getSystemStatus() {
        try {
            const status = await this.apiRequest(CONFIG.API.ENDPOINTS.STATUS);
            return status;
        } catch (error) {
            console.error('Failed to get system status:', error);
            return null;
        }
    }

    async uploadPolicy(file, metadata = {}) {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('doc_type', metadata.docType || 'policy');
        if (metadata.version) formData.append('version', metadata.version);
        if (metadata.department) formData.append('department', metadata.department);

        try {
            const url = `${CONFIG.API.BASE_URL}${CONFIG.API.ENDPOINTS.UPLOAD_POLICY}`;
            const response = await fetch(url, {
                method: 'POST',
                body: formData,
                // Don't set Content-Type header - let browser set it for FormData
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();

            if (result.status === 'success') {
                this.showToast('Policy uploaded successfully', 'success');
                this.updateSystemStatus();
                this.loadDocuments();
                return result;
            } else {
                throw new Error(result.error || 'Upload failed');
            }
        } catch (error) {
            console.error('Upload error:', error);
            this.showToast(`Failed to upload policy: ${error.message}`, 'error');
            throw error;
        }
    }

    async loadDocuments() {
        try {
            const result = await this.apiRequest(CONFIG.API.ENDPOINTS.LIST_DOCUMENTS);
            if (result.status === 'success') {
                this.documents = result.documents;
                this.renderDocuments();
                return result.documents;
            }
        } catch (error) {
            console.error('Failed to load documents:', error);
            return [];
        }
    }

    async deleteDocument(docHash) {
        try {
            const result = await this.apiRequest(`${CONFIG.API.ENDPOINTS.DELETE_DOCUMENT}/${docHash}`, {
                method: 'DELETE'
            });

            if (result.status === 'success') {
                this.showToast('Document deleted successfully', 'success');
                this.updateSystemStatus();
                this.loadDocuments();
                return true;
            }
        } catch (error) {
            this.showToast('Failed to delete document', 'error');
            return false;
        }
    }

    // ========================================
    // Compliance Check
    // ========================================

    async checkCompliance(contractText, contractType) {
        if (!this.apiKey) {
            this.showToast('API key is required for compliance checking', 'error');
            return null;
        }

        try {
            const result = await this.apiRequest(CONFIG.API.ENDPOINTS.CHECK_COMPLIANCE, {
                method: 'POST',
                body: JSON.stringify({
                    contract_text: contractText,
                    contract_type: contractType
                })
            });

            if (result.status === 'success') {
                this.addToHistory('compliance_check', {
                    contractType,
                    result,
                    timestamp: new Date().toISOString()
                });
                return result;
            }
        } catch (error) {
            this.showToast('Compliance check failed', 'error');
            throw error;
        }
    }

    // ========================================
    // Contract Generation
    // ========================================

    async generateContract(parameters, contractType, includeOptional = true) {
        if (!this.apiKey) {
            this.showToast('API key is required for contract generation', 'error');
            return null;
        }

        try {
            const result = await this.apiRequest(CONFIG.API.ENDPOINTS.GENERATE_CONTRACT, {
                method: 'POST',
                body: JSON.stringify({
                    parameters,
                    contract_type: contractType,
                    include_optional_clauses: includeOptional
                })
            });

            if (result.status === 'success') {
                this.addToHistory('contract_generation', {
                    contractType,
                    parameters,
                    result,
                    timestamp: new Date().toISOString()
                });
                return result;
            }
        } catch (error) {
            this.showToast('Contract generation failed', 'error');
            throw error;
        }
    }

    // ========================================
    // Grammar Check
    // ========================================

    async grammarCheck(contractText, contractType) {
        try {
            const result = await this.apiRequest(CONFIG.API.ENDPOINTS.GRAMMAR_CHECK, {
                method: 'POST',
                body: JSON.stringify({
                    contract_text: contractText,
                    contract_type: contractType
                })
            });

            if (result.status === 'success') {
                this.addToHistory('grammar_check', {
                    contractType,
                    result,
                    timestamp: new Date().toISOString()
                });
                return result;
            }
        } catch (error) {
            this.showToast('Grammar check failed', 'error');
            throw error;
        }
    }

    // ========================================
    // Fix Contract
    // ========================================

    async fixContract(contractText, contractType) {
        if (!this.apiKey) {
            this.showToast('API key is required for contract fixing', 'error');
            return null;
        }

        try {
            const result = await this.apiRequest(CONFIG.API.ENDPOINTS.FIX_CONTRACT, {
                method: 'POST',
                body: JSON.stringify({
                    contract_text: contractText,
                    contract_type: contractType
                })
            });

            if (result.status === 'success') {
                this.addToHistory('contract_fix', {
                    contractType,
                    result,
                    timestamp: new Date().toISOString()
                });
                return result;
            }
        } catch (error) {
            this.showToast('Contract fixing failed', 'error');
            throw error;
        }
    }

    // ========================================
    // Missing Clauses Analysis
    // ========================================

    async suggestMissingClauses(contractText, contractType) {
        if (!this.apiKey) {
            this.showToast('API key is required for clause analysis', 'error');
            return null;
        }

        try {
            const result = await this.apiRequest(CONFIG.API.ENDPOINTS.SUGGEST_CLAUSES, {
                method: 'POST',
                body: JSON.stringify({
                    contract_text: contractText,
                    contract_type: contractType
                })
            });

            if (result.status === 'success') {
                this.addToHistory('missing_clause_analysis', {
                    contractType,
                    result,
                    timestamp: new Date().toISOString()
                });
                return result;
            }
        } catch (error) {
            this.showToast('Clause analysis failed', 'error');
            throw error;
        }
    }

    // ========================================
    // UI Management
    // ========================================

    setupEventListeners() {
        // Tab navigation
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.switchTab(e.target.dataset.tab);
            });
        });

        // API Key management
        document.getElementById('apiKeyBtn').addEventListener('click', () => {
            this.showApiKeyModal();
        });

        document.getElementById('applyApiKey').addEventListener('click', () => {
            const apiKey = document.getElementById('apiKeyInput').value;
            if (apiKey) {
                this.setApiKey(apiKey);
            }
        });

        // Settings
        document.getElementById('contractType').addEventListener('change', (e) => {
            this.settings.defaultContractType = e.target.value;
            this.saveSettings();
        });

        document.getElementById('includeOptional').addEventListener('change', (e) => {
            this.settings.includeOptional = e.target.checked;
            this.saveSettings();
        });

        document.getElementById('topK').addEventListener('input', (e) => {
            this.settings.topK = parseInt(e.target.value);
            document.querySelector('.slider-value').textContent = e.target.value;
            this.saveSettings();
        });

        // Compliance check
        this.setupComplianceListeners();
        
        // Contract generation
        this.setupGenerationListeners();
        
        // Grammar check
        this.setupGrammarListeners();
        
        // Fix contract
        this.setupFixListeners();
        
        // Missing clauses
        this.setupClauseListeners();
        
        // Policy management
        this.setupPolicyListeners();
        
        // Analytics
        this.setupAnalyticsListeners();

        // Modal controls
        this.setupModalListeners();

        // File input handlers
        this.setupFileInputListeners();
    }

    switchTab(tabName) {
        // Update tab buttons
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');

        // Update tab panels
        document.querySelectorAll('.tab-panel').forEach(panel => {
            panel.classList.remove('active');
        });
        document.getElementById(tabName).classList.add('active');

        // Load tab-specific data
        if (tabName === 'policies') {
            this.loadDocuments();
        } else if (tabName === 'analytics') {
            this.updateAnalytics();
        }
    }

    showLoading(text = 'Processing...') {
        const overlay = document.getElementById('loadingOverlay');
        const loadingText = document.getElementById('loadingText');
        loadingText.textContent = text;
        overlay.classList.remove('hidden');
    }

    hideLoading() {
        const overlay = document.getElementById('loadingOverlay');
        overlay.classList.add('hidden');
    }

    showToast(message, type = 'info') {
        const container = document.getElementById('toastContainer');
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = message;

        // Add click to close functionality
        toast.addEventListener('click', () => {
            toast.remove();
        });

        container.appendChild(toast);

        // Auto remove after duration
        setTimeout(() => {
            if (toast.parentNode) {
                toast.style.animation = 'slideOut 0.3s ease-in forwards';
                setTimeout(() => toast.remove(), 300);
            }
        }, CONFIG.UI.TOAST_DURATION);
    }

    // ========================================
    // Settings Management
    // ========================================

    loadSettings() {
        const saved = localStorage.getItem(CONFIG.STORAGE.SETTINGS);
        return saved ? { ...CONFIG.DEFAULTS, ...JSON.parse(saved) } : CONFIG.DEFAULTS;
    }

    saveSettings() {
        localStorage.setItem(CONFIG.STORAGE.SETTINGS, JSON.stringify(this.settings));
    }

    loadUserPreferences() {
        // Load API key
        const savedApiKey = localStorage.getItem(CONFIG.STORAGE.API_KEY);
        if (savedApiKey) {
            this.apiKey = savedApiKey;
            document.getElementById('apiKeyInput').value = savedApiKey;
            this.updateApiStatus('success');
        }

        // Load settings
        document.getElementById('contractType').value = this.settings.defaultContractType;
        document.getElementById('includeOptional').checked = this.settings.includeOptional;
        document.getElementById('topK').value = this.settings.topK;
        document.querySelector('.slider-value').textContent = this.settings.topK;
    }

    updateApiStatus(status) {
        const statusElement = document.getElementById('apiStatus');
        statusElement.className = `api-status ${status}`;
        
        if (status === 'success') {
            statusElement.innerHTML = '<i class="fas fa-check-circle"></i> Configured';
        } else if (status === 'error') {
            statusElement.innerHTML = '<i class="fas fa-exclamation-circle"></i> Error';
        } else {
            statusElement.innerHTML = '<i class="fas fa-info-circle"></i> Not set';
        }
    }

    // ========================================
    // History Management
    // ========================================

    loadHistory() {
        const saved = localStorage.getItem(CONFIG.STORAGE.HISTORY);
        this.history = saved ? JSON.parse(saved) : [];
    }

    addToHistory(type, data) {
        this.history.push({
            type,
            timestamp: new Date().toISOString(),
            ...data
        });

        // Keep only last 100 entries
        if (this.history.length > 100) {
            this.history = this.history.slice(-100);
        }

        localStorage.setItem(CONFIG.STORAGE.HISTORY, JSON.stringify(this.history));
    }

    clearHistory() {
        this.history = [];
        localStorage.removeItem(CONFIG.STORAGE.HISTORY);
        this.showToast('History cleared', 'success');
        this.updateAnalytics();
    }

    // ========================================
    // System Status
    // ========================================

    async updateSystemStatus() {
        const status = await this.getSystemStatus();
        if (status) {
            document.getElementById('policyCount').textContent = status.statistics.policy_documents;
            document.getElementById('totalDocs').textContent = status.statistics.total_documents;
        }
    }

    // ========================================
    // Utility Functions
    // ========================================

    formatDate(dateString) {
        return new Date(dateString).toLocaleString();
    }

    downloadFile(content, filename, mimeType = 'text/plain') {
        const blob = new Blob([content], { type: mimeType });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    validateForm(formType, data) {
        const requiredFields = CONFIG.UI.VALIDATION.REQUIRED_FIELDS[formType];
        if (!requiredFields) return true;

        for (const field of requiredFields) {
            let value = '';
            
            // Handle nested structure for contract generation
            if (formType === 'generate' && data.parties) {
                switch (field) {
                    case 'buyerName':
                        value = data.parties.buyer?.name || '';
                        break;
                    case 'vendorName':
                        value = data.parties.vendor?.name || '';
                        break;
                    case 'scope':
                        value = data.scope || '';
                        break;
                    case 'contractValue':
                        value = data.value || '';
                        break;
                    case 'duration':
                        value = data.duration || '';
                        break;
                    default:
                        value = data[field] || '';
                }
            } else {
                value = data[field] || '';
            }
            
            if (!value || value.trim() === '') {
                this.showToast(`Please fill in the ${field} field`, 'error');
                return false;
            }
        }

        return true;
    }

    // ========================================
    // Chart Management
    // ========================================

    initializeCharts() {
        const ctx = document.getElementById('documentChart');
        if (ctx) {
            this.chart = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: [],
                    datasets: [{
                        data: [],
                        backgroundColor: CONFIG.CHARTS.COLORS,
                        borderWidth: 2,
                        borderColor: '#fff'
                    }]
                },
                options: CONFIG.CHARTS.OPTIONS
            });
        }
    }

    updateDocumentChart() {
        if (!this.chart) return;

        const typeCounts = {};
        this.documents.forEach(doc => {
            const type = doc.doc_type || 'unknown';
            typeCounts[type] = (typeCounts[type] || 0) + 1;
        });

        const labels = Object.keys(typeCounts);
        const data = Object.values(typeCounts);

        this.chart.data.labels = labels;
        this.chart.data.datasets[0].data = data;
        this.chart.update();

        // Update legend
        const legend = document.getElementById('chartLegend');
        legend.innerHTML = labels.map((label, index) => `
            <div class="legend-item">
                <div class="legend-color" style="background-color: ${CONFIG.CHARTS.COLORS[index]}"></div>
                <span>${label.charAt(0).toUpperCase() + label.slice(1)}: ${data[index]}</span>
            </div>
        `).join('');
    }

    // ========================================
    // Compliance Check Implementation
    // ========================================

    setupComplianceListeners() {
        // Input method toggle
        document.querySelectorAll('input[name="complianceInput"]').forEach(radio => {
            radio.addEventListener('change', (e) => {
                const textSection = document.getElementById('complianceTextSection');
                const fileSection = document.getElementById('complianceFileSection');
                
                if (e.target.value === 'text') {
                    textSection.classList.remove('hidden');
                    fileSection.classList.add('hidden');
                } else {
                    textSection.classList.add('hidden');
                    fileSection.classList.remove('hidden');
                }
            });
        });

        // Check compliance button
        document.getElementById('checkComplianceBtn').addEventListener('click', async () => {
            const contractText = this.getComplianceText();
            const contractType = document.getElementById('complianceContractType').value;

            if (!contractText) {
                this.showToast('Please provide contract text to check', 'error');
                return;
            }

            this.showLoading('Checking compliance...');
            try {
                const result = await this.checkCompliance(contractText, contractType);
                if (result) {
                    this.displayComplianceResults(result);
                }
            } catch (error) {
                console.error('Compliance check error:', error);
            } finally {
                this.hideLoading();
            }
        });

        // Save input button
        document.getElementById('saveComplianceInputBtn').addEventListener('click', () => {
            const text = this.getComplianceText();
            if (text) {
                const filename = `contract_input_${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.txt`;
                this.downloadFile(text, filename);
            }
        });

        // Download report button
        document.getElementById('downloadComplianceReportBtn').addEventListener('click', () => {
            const result = this.lastComplianceResult;
            if (result) {
                const report = this.generateComplianceReport(result);
                const filename = `compliance_report_${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.txt`;
                this.downloadFile(report, filename);
            }
        });
    }

    getComplianceText() {
        const inputMethod = document.querySelector('input[name="complianceInput"]:checked').value;
        
        if (inputMethod === 'text') {
            return document.getElementById('complianceText').value;
        } else {
            const fileInput = document.getElementById('complianceFile');
            if (fileInput.files.length > 0) {
                return fileInput.files[0];
            }
        }
        return null;
    }

    displayComplianceResults(result) {
        this.lastComplianceResult = result;
        
        document.getElementById('complianceAnalysis').textContent = result.analysis;
        document.getElementById('complianceLength').textContent = `${result.contract_length} chars`;
        document.getElementById('compliancePoliciesChecked').textContent = result.policies_checked;
        document.getElementById('complianceTimestamp').textContent = this.formatDate(new Date());
        
        document.getElementById('complianceResults').classList.remove('hidden');
        document.getElementById('saveComplianceInputBtn').disabled = false;
    }

    generateComplianceReport(result) {
        const contractText = this.getComplianceText();
        const contractType = document.getElementById('complianceContractType').value;
        
        return `COMPLIANCE ANALYSIS REPORT
Generated: ${new Date().toLocaleString()}
Contract Type: ${contractType}
Policies Checked: ${result.policies_checked}

${result.analysis}

---
Original Contract Text:
${contractText}`;
    }

    // ========================================
    // Contract Generation Implementation
    // ========================================

    setupGenerationListeners() {
        document.getElementById('generateContractBtn').addEventListener('click', async () => {
            const parameters = this.getContractParameters();
            
            if (!this.validateForm('generate', parameters)) {
                return;
            }

            const contractType = document.getElementById('generateContractType').value;
            const includeOptional = document.getElementById('includeOptional').checked;

            this.showLoading('Generating contract...');
            try {
                const result = await this.generateContract(parameters, contractType, includeOptional);
                if (result) {
                    this.displayGeneratedContract(result);
                }
            } catch (error) {
                console.error('Contract generation error:', error);
            } finally {
                this.hideLoading();
            }
        });

        // Download buttons
        document.getElementById('downloadContractBtn').addEventListener('click', () => {
            const contract = document.getElementById('generatedContract').value;
            if (contract) {
                const filename = `contract_${this.lastGeneratedContract?.contract_type}_${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.txt`;
                this.downloadFile(contract, filename);
            }
        });

        document.getElementById('downloadParamsBtn').addEventListener('click', () => {
            if (this.lastGeneratedContract?.parameters_used) {
                const filename = `contract_params_${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.json`;
                this.downloadFile(JSON.stringify(this.lastGeneratedContract.parameters_used, null, 2), filename, 'application/json');
            }
        });

        document.getElementById('downloadFullReportBtn').addEventListener('click', () => {
            if (this.lastGeneratedContract) {
                const report = this.generateContractReport(this.lastGeneratedContract);
                const filename = `full_report_${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.txt`;
                this.downloadFile(report, filename);
            }
        });
    }

    getContractParameters() {
        return {
            parties: {
                buyer: {
                    name: document.getElementById('buyerName').value,
                    address: document.getElementById('buyerAddress').value,
                    contact: document.getElementById('buyerContact').value,
                    email: document.getElementById('buyerEmail').value
                },
                vendor: {
                    name: document.getElementById('vendorName').value,
                    address: document.getElementById('vendorAddress').value,
                    contact: document.getElementById('vendorContact').value,
                    email: document.getElementById('vendorEmail').value
                }
            },
            scope: document.getElementById('scope').value,
            value: document.getElementById('contractValue').value,
            duration: document.getElementById('duration').value,
            start_date: document.getElementById('startDate').value,
            delivery_date: document.getElementById('deliveryDate').value,
            payment_terms: document.getElementById('paymentTerms').value,
            special_terms: document.getElementById('specialTerms').value.split('\n').filter(t => t.trim()),
            deliverables: document.getElementById('deliverables').value.split('\n').filter(d => d.trim())
        };
    }

    displayGeneratedContract(result) {
        this.lastGeneratedContract = result;
        
        document.getElementById('generatedContract').value = result.contract;
        document.getElementById('contractWordCount').textContent = result.word_count;
        document.getElementById('contractPoliciesReferenced').textContent = result.policies_referenced;
        document.getElementById('contractTypeGenerated').textContent = result.contract_type;
        
        document.getElementById('generateResults').classList.remove('hidden');
    }

    generateContractReport(result) {
        return `CONTRACT GENERATION REPORT
Generated: ${new Date().toLocaleString()}
Contract Type: ${result.contract_type}
Word Count: ${result.word_count}
Policies Referenced: ${result.policies_referenced}

PARAMETERS:
${JSON.stringify(result.parameters_used, null, 2)}

GENERATED CONTRACT:
${result.contract}

COMPLIANCE CHECK:
${result.compliance_check?.analysis || 'N/A'}`;
    }

    // ========================================
    // Grammar Check Implementation
    // ========================================

    setupGrammarListeners() {
        // Input method toggle
        document.querySelectorAll('input[name="grammarInput"]').forEach(radio => {
            radio.addEventListener('change', (e) => {
                const textSection = document.getElementById('grammarTextSection');
                const fileSection = document.getElementById('grammarFileSection');
                
                if (e.target.value === 'text') {
                    textSection.classList.remove('hidden');
                    fileSection.classList.add('hidden');
                } else {
                    textSection.classList.add('hidden');
                    fileSection.classList.remove('hidden');
                }
            });
        });

        document.getElementById('runGrammarCheckBtn').addEventListener('click', async () => {
            const contractText = this.getGrammarText();
            const contractType = document.getElementById('grammarContractType').value;

            if (!contractText) {
                this.showToast('Please provide contract text to check', 'error');
                return;
            }

            this.showLoading('Running grammar check...');
            try {
                const result = await this.grammarCheck(contractText, contractType);
                if (result) {
                    this.displayGrammarResults(result);
                }
            } catch (error) {
                console.error('Grammar check error:', error);
            } finally {
                this.hideLoading();
            }
        });

        document.getElementById('saveGrammarInputBtn').addEventListener('click', () => {
            const text = this.getGrammarText();
            if (text) {
                const filename = `grammar_input_${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.txt`;
                this.downloadFile(text, filename);
            }
        });

        document.getElementById('downloadCorrectedTextBtn').addEventListener('click', () => {
            const correctedText = document.getElementById('grammarCorrectedText').value;
            if (correctedText) {
                const filename = `grammar_corrected_${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.txt`;
                this.downloadFile(correctedText, filename);
            }
        });
    }

    getGrammarText() {
        const inputMethod = document.querySelector('input[name="grammarInput"]:checked').value;
        
        if (inputMethod === 'text') {
            return document.getElementById('grammarText').value;
        } else {
            const fileInput = document.getElementById('grammarFile');
            if (fileInput.files.length > 0) {
                return fileInput.files[0];
            }
        }
        return null;
    }

    displayGrammarResults(result) {
        document.getElementById('grammarCorrectedText').value = result.corrected_text;
        
        const issuesList = document.getElementById('grammarIssues');
        if (result.issues && result.issues.length > 0) {
            issuesList.innerHTML = result.issues.slice(0, 20).map(issue => `
                <div class="issue-item">
                    - ${issue.message}${issue.replacements ? ` → ${issue.replacements.slice(0, 3).join(', ')}` : ''}
                </div>
            `).join('');
        } else {
            issuesList.innerHTML = '<div class="issue-item">No notable issues found.</div>';
        }
        
        document.getElementById('grammarResults').classList.remove('hidden');
        document.getElementById('saveGrammarInputBtn').disabled = false;
    }

    // ========================================
    // Fix Contract Implementation
    // ========================================

    setupFixListeners() {
        // Input method toggle
        document.querySelectorAll('input[name="fixInput"]').forEach(radio => {
            radio.addEventListener('change', (e) => {
                const textSection = document.getElementById('fixTextSection');
                const fileSection = document.getElementById('fixFileSection');
                
                if (e.target.value === 'text') {
                    textSection.classList.remove('hidden');
                    fileSection.classList.add('hidden');
                } else {
                    textSection.classList.add('hidden');
                    fileSection.classList.remove('hidden');
                }
            });
        });

        document.getElementById('fixContractBtn').addEventListener('click', async () => {
            const contractText = this.getFixText();
            const contractType = document.getElementById('fixContractType').value;

            if (!contractText) {
                this.showToast('Please provide contract text to fix', 'error');
                return;
            }

            this.showLoading('Fixing contract...');
            try {
                const result = await this.fixContract(contractText, contractType);
                if (result) {
                    this.displayFixResults(result);
                }
            } catch (error) {
                console.error('Contract fix error:', error);
            } finally {
                this.hideLoading();
            }
        });

        document.getElementById('downloadFixedContractBtn').addEventListener('click', () => {
            const fixedText = document.getElementById('fixCorrectedText').value;
            if (fixedText) {
                const filename = `fixed_contract_${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.txt`;
                this.downloadFile(fixedText, filename);
            }
        });
    }

    getFixText() {
        const inputMethod = document.querySelector('input[name="fixInput"]:checked').value;
        
        if (inputMethod === 'text') {
            return document.getElementById('fixText').value;
        } else {
            const fileInput = document.getElementById('fixFile');
            if (fileInput.files.length > 0) {
                return fileInput.files[0];
            }
        }
        return null;
    }

    displayFixResults(result) {
        document.getElementById('fixCorrectedText').value = result.corrected_contract;
        
        if (result.compliance_check && result.compliance_check.status === 'success') {
            document.getElementById('fixComplianceCheck').textContent = result.compliance_check.analysis;
        }
        
        document.getElementById('fixResults').classList.remove('hidden');
    }

    // ========================================
    // Missing Clauses Implementation
    // ========================================

    setupClauseListeners() {
        // Input method toggle
        document.querySelectorAll('input[name="clauseInput"]').forEach(radio => {
            radio.addEventListener('change', (e) => {
                const textSection = document.getElementById('clauseTextSection');
                const fileSection = document.getElementById('clauseFileSection');
                
                if (e.target.value === 'text') {
                    textSection.classList.remove('hidden');
                    fileSection.classList.add('hidden');
                } else {
                    textSection.classList.add('hidden');
                    fileSection.classList.remove('hidden');
                }
            });
        });

        document.getElementById('analyzeClausesBtn').addEventListener('click', async () => {
            const contractText = this.getClauseText();
            const contractType = document.getElementById('clauseContractType').value;

            if (!contractText) {
                this.showToast('Please provide contract text to analyze', 'error');
                return;
            }

            this.showLoading('Analyzing missing clauses...');
            try {
                const result = await this.suggestMissingClauses(contractText, contractType);
                if (result) {
                    this.displayClauseResults(result);
                }
            } catch (error) {
                console.error('Clause analysis error:', error);
            } finally {
                this.hideLoading();
            }
        });

        document.getElementById('downloadClauseReportBtn').addEventListener('click', () => {
            if (this.lastClauseResult) {
                const report = this.generateClauseReport(this.lastClauseResult);
                const filename = `missing_clauses_${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.txt`;
                this.downloadFile(report, filename);
            }
        });
    }

    getClauseText() {
        const inputMethod = document.querySelector('input[name="clauseInput"]:checked').value;
        
        if (inputMethod === 'text') {
            return document.getElementById('clauseText').value;
        } else {
            const fileInput = document.getElementById('clauseFile');
            if (fileInput.files.length > 0) {
                return fileInput.files[0];
            }
        }
        return null;
    }

    displayClauseResults(result) {
        this.lastClauseResult = result;
        
        document.getElementById('clauseAnalysis').textContent = result.suggestions;
        document.getElementById('clausePoliciesReferenced').textContent = result.policies_referenced;
        document.getElementById('clauseTimestamp').textContent = this.formatDate(new Date());
        
        document.getElementById('clauseResults').classList.remove('hidden');
    }

    generateClauseReport(result) {
        const contractText = this.getClauseText();
        const contractType = document.getElementById('clauseContractType').value;
        
        return `MISSING CLAUSE ANALYSIS REPORT
Generated: ${new Date().toLocaleString()}
Contract Type: ${contractType}
Policies Referenced: ${result.policies_referenced}

${result.suggestions}

---
Original Contract Text:
${contractText}`;
    }

    // ========================================
    // Policy Management Implementation
    // ========================================

    setupPolicyListeners() {
        document.getElementById('uploadPolicyBtn').addEventListener('click', async () => {
            const fileInput = document.getElementById('policyFile');
            if (!fileInput.files.length) {
                this.showToast('Please select a PDF file to upload', 'error');
                return;
            }

            const file = fileInput.files[0];
            const metadata = {
                docType: document.getElementById('policyType').value,
                version: document.getElementById('policyVersion').value,
                department: document.getElementById('policyDepartment').value,
                effectiveDate: document.getElementById('policyEffectiveDate').value,
                author: document.getElementById('policyAuthor').value
            };

            this.showLoading('Uploading policy...');
            try {
                await this.uploadPolicy(file, metadata);
                this.clearPolicyForm();
            } catch (error) {
                console.error('Policy upload error:', error);
            } finally {
                this.hideLoading();
            }
        });

        // Document search and filter
        document.getElementById('searchDocuments').addEventListener('input', () => {
            this.filterDocuments();
        });

        document.getElementById('filterDocuments').addEventListener('change', () => {
            this.filterDocuments();
        });

        // Bulk operations
        document.getElementById('exportDocumentListBtn').addEventListener('click', () => {
            const docList = JSON.stringify(this.documents, null, 2);
            const filename = `document_list_${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.json`;
            this.downloadFile(docList, filename, 'application/json');
        });

        document.getElementById('testPolicySearchBtn').addEventListener('click', () => {
            const query = prompt('Enter search query:');
            if (query) {
                this.testPolicySearch(query);
            }
        });
    }

    clearPolicyForm() {
        document.getElementById('policyFile').value = '';
        document.getElementById('policyVersion').value = '';
        document.getElementById('policyDepartment').value = '';
        document.getElementById('policyEffectiveDate').value = '';
        document.getElementById('policyAuthor').value = '';
    }

    renderDocuments() {
        const container = document.getElementById('documentsList');
        
        if (this.documents.length === 0) {
            container.innerHTML = `
                <div class="no-documents">
                    <i class="fas fa-inbox"></i>
                    <p>No policy documents uploaded yet. Upload your first policy above!</p>
                </div>
            `;
            return;
        }

        container.innerHTML = this.documents.map((doc, index) => `
            <div class="document-item">
                <div class="document-header">
                    <div class="document-title">📄 ${doc.filename}</div>
                    <div class="document-type">${doc.doc_type || 'unknown'}</div>
                </div>
                <div class="document-details">
                    <div><strong>Type:</strong> ${doc.doc_type || 'unknown'}</div>
                    <div><strong>Chunks:</strong> ${doc.chunks || 'N/A'}</div>
                    <div><strong>Uploaded:</strong> ${doc.upload_time ? doc.upload_time.slice(0, 10) : 'N/A'}</div>
                    <div><strong>Hash:</strong> <code>${doc.doc_hash ? doc.doc_hash.slice(0, 16) + '...' : 'N/A'}</code></div>
                </div>
                <div class="document-actions">
                    <button class="btn btn-outline btn-sm" onclick="app.deleteDocument('${doc.doc_hash}')">
                        <i class="fas fa-trash"></i> Delete
                    </button>
                </div>
            </div>
        `).join('');
    }

    filterDocuments() {
        const searchTerm = document.getElementById('searchDocuments').value.toLowerCase();
        const filterType = document.getElementById('filterDocuments').value;
        
        let filteredDocs = this.documents;
        
        if (searchTerm) {
            filteredDocs = filteredDocs.filter(doc => 
                doc.filename.toLowerCase().includes(searchTerm)
            );
        }
        
        if (filterType !== 'All') {
            filteredDocs = filteredDocs.filter(doc => doc.doc_type === filterType);
        }
        
        // Update the display with filtered documents
        const container = document.getElementById('documentsList');
        if (filteredDocs.length === 0) {
            container.innerHTML = `
                <div class="no-documents">
                    <i class="fas fa-search"></i>
                    <p>No documents match your search criteria.</p>
                </div>
            `;
            return;
        }

        container.innerHTML = filteredDocs.map((doc, index) => `
            <div class="document-item">
                <div class="document-header">
                    <div class="document-title">📄 ${doc.filename}</div>
                    <div class="document-type">${doc.doc_type || 'unknown'}</div>
                </div>
                <div class="document-details">
                    <div><strong>Type:</strong> ${doc.doc_type || 'unknown'}</div>
                    <div><strong>Chunks:</strong> ${doc.chunks || 'N/A'}</div>
                    <div><strong>Uploaded:</strong> ${doc.upload_time ? doc.upload_time.slice(0, 10) : 'N/A'}</div>
                    <div><strong>Hash:</strong> <code>${doc.doc_hash ? doc.doc_hash.slice(0, 16) + '...' : 'N/A'}</code></div>
                </div>
                <div class="document-actions">
                    <button class="btn btn-outline btn-sm" onclick="app.deleteDocument('${doc.doc_hash}')">
                        <i class="fas fa-trash"></i> Delete
                    </button>
                </div>
            </div>
        `).join('');
    }

    async testPolicySearch(query) {
        try {
            const result = await this.apiRequest(CONFIG.API.ENDPOINTS.SEARCH, {
                method: 'POST',
                body: JSON.stringify({
                    query,
                    top_k: 5
                })
            });

            if (result.status === 'success') {
                const resultsText = result.results.map(r => 
                    `- ${r.metadata.filename || 'Unknown'}: ${r.text.slice(0, 100)}...`
                ).join('\n');
                
                alert(`Found ${result.results_count} results:\n\n${resultsText}`);
            }
        } catch (error) {
            this.showToast('Search test failed', 'error');
        }
    }

    // ========================================
    // Analytics Implementation
    // ========================================

    setupAnalyticsListeners() {
        document.getElementById('exportHistoryBtn').addEventListener('click', () => {
            const historyJson = JSON.stringify(this.history, null, 2);
            const filename = `activity_history_${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.json`;
            this.downloadFile(historyJson, filename, 'application/json');
        });
    }

    updateAnalytics() {
        // Update metrics
        document.getElementById('analyticsTotalDocs').textContent = this.documents.length;
        document.getElementById('analyticsTotalOps').textContent = this.history.length;
        
        const policyCount = this.documents.filter(doc => doc.doc_type === 'policy').length;
        const complianceCount = this.documents.filter(doc => doc.doc_type === 'compliance').length;
        
        document.getElementById('analyticsPolicyDocs').textContent = policyCount;
        document.getElementById('analyticsComplianceDocs').textContent = complianceCount;

        // Update activity list
        this.renderActivityList();
        
        // Update chart
        this.updateDocumentChart();
    }

    renderActivityList() {
        const container = document.getElementById('activityList');
        
        if (this.history.length === 0) {
            container.innerHTML = `
                <div class="no-activity">
                    <i class="fas fa-history"></i>
                    <p>No activity recorded yet. Start using the system to see analytics!</p>
                </div>
            `;
            return;
        }

        const recentActivities = this.history.slice(-10).reverse();
        container.innerHTML = recentActivities.map(activity => `
            <div class="activity-item">
                <div class="activity-header">
                    <div class="activity-title">${activity.type.replace(/_/g, ' ').toUpperCase()}</div>
                    <div class="activity-time">${this.formatDate(activity.timestamp)}</div>
                </div>
                <div class="activity-details">
                    <pre>${JSON.stringify(activity, null, 2)}</pre>
                </div>
            </div>
        `).join('');
    }

    // ========================================
    // Modal Management
    // ========================================

    setupModalListeners() {
        // API Key modal
        document.getElementById('closeApiKeyModal').addEventListener('click', () => {
            this.hideApiKeyModal();
        });

        document.getElementById('cancelApiKeyBtn').addEventListener('click', () => {
            this.hideApiKeyModal();
        });

        document.getElementById('saveApiKeyBtn').addEventListener('click', () => {
            const apiKey = document.getElementById('modalApiKey').value;
            if (apiKey) {
                this.setApiKey(apiKey);
                this.hideApiKeyModal();
            }
        });

        // Close modal on outside click
        document.getElementById('apiKeyModal').addEventListener('click', (e) => {
            if (e.target.id === 'apiKeyModal') {
                this.hideApiKeyModal();
            }
        });
    }

    showApiKeyModal() {
        document.getElementById('apiKeyModal').classList.remove('hidden');
        document.getElementById('modalApiKey').value = this.apiKey || '';
    }

    hideApiKeyModal() {
        document.getElementById('apiKeyModal').classList.add('hidden');
    }

    // ========================================
    // File Input Management
    // ========================================

    setupFileInputListeners() {
        // File input validation
        document.querySelectorAll('input[type="file"]').forEach(input => {
            input.addEventListener('change', (e) => {
                const file = e.target.files[0];
                if (file) {
                    this.validateFile(file, e.target);
                }
            });
        });
    }

    validateFile(file, inputElement) {
        // Check file size
        if (file.size > CONFIG.UI.MAX_FILE_SIZE) {
            this.showToast(`File size exceeds ${CONFIG.UI.MAX_FILE_SIZE / (1024 * 1024)}MB limit`, 'error');
            inputElement.value = '';
            return false;
        }

        // Check file type
        const allowedTypes = Object.keys(CONFIG.UI.ALLOWED_FILE_TYPES);
        if (!allowedTypes.includes(file.type)) {
            this.showToast('File type not supported', 'error');
            inputElement.value = '';
            return false;
        }

        return true;
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new ProcurementApp();
});
