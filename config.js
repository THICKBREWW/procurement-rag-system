/**
 * Configuration file for the Procurement Contract Assistant
 * Contains API endpoints, settings, and constants
 */

const CONFIG = {
    // API Configuration
    API: {
        BASE_URL: 'https://watts-saver-vid-hollywood.trycloudflare.com', // Flask API server
        ENDPOINTS: {
            // Health and Status
            HEALTH: '/health',
            STATUS: '/api/status',
            
            // API Key Management
            SET_API_KEY: '/api/set-api-key',
            
            // Document Management
            UPLOAD_POLICY: '/api/upload-policy',
            LIST_DOCUMENTS: '/api/list-documents',
            DELETE_DOCUMENT: '/api/delete-document',
            
            // Search
            SEARCH: '/api/search',
            
            // Compliance and Analysis
            CHECK_COMPLIANCE: '/api/check-compliance',
            GRAMMAR_CHECK: '/api/grammar-check',
            FIX_CONTRACT: '/api/fix-contract',
            SUGGEST_CLAUSES: '/api/suggest-clauses',
            
            // Contract Generation
            GENERATE_CONTRACT: '/api/generate-contract',
            
            // Workflow
            FULL_WORKFLOW: '/api/full-workflow',
            
            // Batch Operations
            BATCH_COMPLIANCE: '/api/batch-compliance',
            
            // Documentation
            API_DOCS: '/api/docs'
        },
        
        // Request timeout in milliseconds
        TIMEOUT: 30000,
        
        // Retry configuration
        RETRY: {
            ATTEMPTS: 3,
            DELAY: 1000
        }
    },
    
    // UI Configuration
    UI: {
        // Loading states
        LOADING_DELAY: 500,
        
        // Toast notification duration
        TOAST_DURATION: 8000,
        
        // File upload limits
        MAX_FILE_SIZE: 10 * 1024 * 1024, // 10MB
        ALLOWED_FILE_TYPES: {
            'text/plain': '.txt',
            'application/pdf': '.pdf',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx'
        },
        
        // Form validation
        VALIDATION: {
            MIN_TEXT_LENGTH: 10,
            MAX_TEXT_LENGTH: 100000,
            REQUIRED_FIELDS: {
                compliance: ['contractText'],
                generate: ['buyerName', 'vendorName', 'scope', 'contractValue', 'duration'],
                grammar: ['grammarText'],
                fix: ['fixText'],
                clauses: ['clauseText']
            }
        },
        
        // Pagination
        PAGINATION: {
            ITEMS_PER_PAGE: 10,
            MAX_VISIBLE_PAGES: 5
        }
    },
    
    // Contract Types
    CONTRACT_TYPES: [
        { value: 'service', label: 'Service' },
        { value: 'procurement', label: 'Procurement' },
        { value: 'vendor', label: 'Vendor' },
        { value: 'software', label: 'Software' },
        { value: 'consulting', label: 'Consulting' },
        { value: 'construction', label: 'Construction' },
        { value: 'general', label: 'General' }
    ],
    
    // Document Types
    DOCUMENT_TYPES: [
        { value: 'policy', label: 'Policy' },
        { value: 'vendor', label: 'Vendor' },
        { value: 'compliance', label: 'Compliance' }
    ],
    
    // Error Messages
    ERRORS: {
        NETWORK_ERROR: 'Network error. Please check your connection and try again.',
        API_ERROR: 'API error occurred. Please try again.',
        VALIDATION_ERROR: 'Please fill in all required fields.',
        FILE_SIZE_ERROR: 'File size exceeds the maximum limit of 10MB.',
        FILE_TYPE_ERROR: 'File type not supported. Please upload a PDF, TXT, or DOCX file.',
        API_KEY_ERROR: 'API key is required for this operation.',
        NO_POLICIES_ERROR: 'No policies uploaded. Please upload policy documents first.',
        GENERIC_ERROR: 'An unexpected error occurred. Please try again.'
    },
    
    // Success Messages
    SUCCESS: {
        API_KEY_SET: 'API key has been set successfully.',
        POLICY_UPLOADED: 'Policy document uploaded successfully.',
        DOCUMENT_DELETED: 'Document deleted successfully.',
        COMPLIANCE_CHECKED: 'Compliance check completed successfully.',
        CONTRACT_GENERATED: 'Contract generated successfully.',
        GRAMMAR_CHECKED: 'Grammar check completed successfully.',
        CONTRACT_FIXED: 'Contract fixed successfully.',
        CLAUSES_ANALYZED: 'Missing clause analysis completed successfully.'
    },
    
    // Local Storage Keys
    STORAGE: {
        API_KEY: 'procurement_api_key',
        USER_PREFERENCES: 'procurement_user_preferences',
        HISTORY: 'procurement_history',
        SETTINGS: 'procurement_settings'
    },
    
    // Default Settings
    DEFAULTS: {
        CONTRACT_TYPE: 'service',
        TOP_K: 10,
        INCLUDE_OPTIONAL: true,
        THEME: 'light'
    },
    
    // Chart Configuration
    CHARTS: {
        COLORS: [
            '#667eea',
            '#764ba2',
            '#48bb78',
            '#ed8936',
            '#f56565',
            '#4299e1',
            '#9f7aea',
            '#38b2ac'
        ],
        OPTIONS: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        usePointStyle: true,
                        padding: 20
                    }
                }
            }
        }
    },
    
    // Feature Flags
    FEATURES: {
        DARK_MODE: true,
        EXPORT_FUNCTIONALITY: true,
        BATCH_OPERATIONS: true,
        REAL_TIME_VALIDATION: true,
        AUTO_SAVE: true,
        KEYBOARD_SHORTCUTS: true
    },
    
    // Keyboard Shortcuts
    SHORTCUTS: {
        'Ctrl+S': 'save',
        'Ctrl+N': 'new',
        'Ctrl+O': 'open',
        'Ctrl+F': 'search',
        'Ctrl+Enter': 'submit',
        'Escape': 'close'
    }
};

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CONFIG;
}
