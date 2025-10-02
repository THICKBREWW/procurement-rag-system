# Web UI
import streamlit as st
import sys
import os
from pathlib import Path
import json
from datetime import datetime
import tempfile

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from app.rag_engine import ProcurementRAG

# Page configuration
st.set_page_config(
    page_title="Procurement Contract Assistant",
    page_icon="🤝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        padding: 1rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .success-box {
        padding: 1rem;
        border-radius: 5px;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        margin: 1rem 0;
    }
    .warning-box {
        padding: 1rem;
        border-radius: 5px;
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        color: #856404;
        margin: 1rem 0;
    }
    .stTabs [data-baseweb="tab-list"] button {
        font-size: 1.1rem;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'rag' not in st.session_state:
    with st.spinner("🚀 Initializing Procurement RAG System..."):
        st.session_state.rag = ProcurementRAG()
        st.session_state.initialized = True

if 'history' not in st.session_state:
    st.session_state.history = []

# Sidebar
with st.sidebar:
    st.image("https://via.placeholder.com/150x50/667eea/ffffff?text=ProContract", use_container_width=True)
    st.markdown("---")
    
    st.subheader("📊 System Status")
    
    # Get document count
    docs = st.session_state.rag.get_document_list()
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("📚 Policies", len([d for d in docs if d['collection'] == 'policy']))
    with col2:
        st.metric("📋 Total Docs", len(docs))
    
    st.markdown("---")
    
    st.subheader("⚙️ Settings")
    
    contract_type = st.selectbox(
        "Default Contract Type",
        ["service", "procurement", "vendor", "software", "consulting", "construction"],
        help="Default type for contract operations"
    )
    
    include_optional = st.checkbox(
        "Include Optional Clauses",
        value=True,
        help="Include recommended clauses in generated contracts"
    )
    
    top_k = st.slider(
        "Search Results",
        min_value=3,
        max_value=20,
        value=10,
        help="Number of policy chunks to retrieve"
    )
    
    st.markdown("---")
    
    if st.button("🗑️ Clear History", use_container_width=True):
        st.session_state.history = []
        st.success("History cleared!")
    
    if st.button("🔄 Refresh System", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# Main header
st.markdown('<h1 class="main-header">🤝 Procurement Contract Assistant</h1>', unsafe_allow_html=True)
st.markdown("**AI-Powered Contract Compliance & Generation System**")
st.markdown("---")

# Main tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📋 Compliance Check", 
    "📝 Generate Contract", 
    "💡 Missing Clauses", 
    "📚 Policy Manager",
    "📊 Analytics"
])

# TAB 1: Compliance Check
with tab1:
    st.header("📋 Contract Compliance Checker")
    st.markdown("Verify if your contract complies with organizational policies")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        input_method = st.radio(
            "Input Method:",
            ["📝 Paste Text", "📄 Upload File"],
            horizontal=True
        )
    
    with col2:
        selected_type = st.selectbox(
            "Contract Type:",
            ["service", "procurement", "vendor", "software", "consulting"],
            key="compliance_type"
        )
    
    contract_text = ""
    
    if input_method == "📝 Paste Text":
        contract_text = st.text_area(
            "Paste your contract text:",
            height=300,
            placeholder="Enter the contract text you want to check for compliance..."
        )
    else:
        uploaded_file = st.file_uploader(
            "Upload contract file:",
            type=["txt", "pdf", "docx"],
            help="Supported formats: TXT, PDF, DOCX"
        )
        
        if uploaded_file:
            if uploaded_file.type == "text/plain":
                contract_text = uploaded_file.read().decode("utf-8")
            elif uploaded_file.type == "application/pdf":
                # Save temp file and extract
                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
                    tmp.write(uploaded_file.getvalue())
                    tmp_path = tmp.name
                
                try:
                    extracted = st.session_state.rag.extract_text_from_pdf(tmp_path)
                    contract_text = extracted['text']
                    st.success(f"✅ Extracted {len(contract_text)} characters from PDF")
                except Exception as e:
                    st.error(f"❌ Error extracting PDF: {e}")
                finally:
                    os.unlink(tmp_path)
    
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        check_button = st.button("🔍 Check Compliance", type="primary", use_container_width=True)
    
    with col2:
        if contract_text:
            st.download_button(
                "💾 Save Input",
                contract_text,
                file_name=f"contract_input_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                use_container_width=True
            )
    
    if check_button and contract_text:
        with st.spinner("🔍 Analyzing contract compliance..."):
            result = st.session_state.rag.check_compliance(
                input_text=contract_text,
                contract_type=selected_type
            )
            
            if result["status"] == "success":
                st.markdown('<div class="success-box">✅ Compliance check completed successfully!</div>', unsafe_allow_html=True)
                
                # Display analysis
                st.subheader("📊 Compliance Analysis")
                st.markdown(result["analysis"])
                
                # Metadata
                with st.expander("ℹ️ Analysis Details"):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Contract Length", f"{result['contract_length']} chars")
                    with col2:
                        st.metric("Policies Checked", result['policies_checked'])
                    with col3:
                        st.metric("Timestamp", datetime.now().strftime("%H:%M:%S"))
                
                # Download report
                report = f"""COMPLIANCE ANALYSIS REPORT
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Contract Type: {selected_type}
Policies Checked: {result['policies_checked']}

{result["analysis"]}

---
Original Contract Text:
{contract_text}
"""
                st.download_button(
                    "📥 Download Full Report",
                    report,
                    file_name=f"compliance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain"
                )
                
                # Save to history
                st.session_state.history.append({
                    "type": "compliance_check",
                    "timestamp": datetime.now().isoformat(),
                    "contract_type": selected_type,
                    "result": result
                })
                
            else:
                st.error(f"❌ Error: {result.get('error', 'Unknown error')}")
    
    elif check_button:
        st.warning("⚠️ Please provide contract text to check")

# TAB 2: Generate Contract
with tab2:
    st.header("📝 Contract Generator")
    st.markdown("Generate policy-compliant contracts from your requirements")
    
    selected_gen_type = st.selectbox(
        "Contract Type:",
        ["service", "procurement", "vendor", "software", "consulting", "construction"],
        key="gen_type"
    )
    
    st.subheader("👥 Parties Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Buyer Information**")
        buyer_name = st.text_input("Company Name:", key="buyer_name")
        buyer_address = st.text_area("Address:", height=100, key="buyer_address")
        buyer_contact = st.text_input("Contact Person:", key="buyer_contact")
        buyer_email = st.text_input("Email:", key="buyer_email")
    
    with col2:
        st.markdown("**Vendor/Supplier Information**")
        vendor_name = st.text_input("Company Name:", key="vendor_name")
        vendor_address = st.text_area("Address:", height=100, key="vendor_address")
        vendor_contact = st.text_input("Contact Person:", key="vendor_contact")
        vendor_email = st.text_input("Email:", key="vendor_email")
    
    st.subheader("📋 Contract Details")
    
    col1, col2 = st.columns(2)
    
    with col1:
        contract_value = st.text_input("Contract Value:", placeholder="$100,000")
        start_date = st.date_input("Start Date:")
        payment_terms = st.text_input("Payment Terms:", value="Net 30 days")
    
    with col2:
        duration = st.text_input("Duration:", placeholder="2 years")
        delivery_date = st.date_input("Delivery/Completion Date:")
        
    scope = st.text_area(
        "Scope of Work:",
        height=150,
        placeholder="Describe the goods/services to be provided..."
    )
    
    special_terms = st.text_area(
        "Special Terms & Conditions:",
        height=100,
        placeholder="Any special requirements, SLAs, warranties, etc."
    )
    
    deliverables = st.text_area(
        "Deliverables:",
        height=100,
        placeholder="List key deliverables (one per line)"
    )
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        generate_button = st.button("🚀 Generate Contract", type="primary", use_container_width=True)
    
    if generate_button:
        # Validate required fields
        if not all([buyer_name, vendor_name, scope, contract_value, duration]):
            st.error("❌ Please fill in all required fields: Buyer Name, Vendor Name, Scope, Value, Duration")
        else:
            # Prepare parameters
            contract_params = {
                "parties": {
                    "buyer": {
                        "name": buyer_name,
                        "address": buyer_address,
                        "contact": buyer_contact,
                        "email": buyer_email
                    },
                    "vendor": {
                        "name": vendor_name,
                        "address": vendor_address,
                        "contact": vendor_contact,
                        "email": vendor_email
                    }
                },
                "scope": scope,
                "value": contract_value,
                "duration": duration,
                "start_date": start_date.strftime("%Y-%m-%d"),
                "delivery_date": delivery_date.strftime("%Y-%m-%d"),
                "payment_terms": payment_terms,
                "special_terms": [t.strip() for t in special_terms.split('\n') if t.strip()],
                "deliverables": [d.strip() for d in deliverables.split('\n') if d.strip()]
            }
            
            with st.spinner("📝 Generating contract... This may take 30-60 seconds..."):
                result = st.session_state.rag.generate_contract(
                    contract_params=contract_params,
                    contract_type=selected_gen_type,
                    include_optional_clauses=include_optional
                )
                
                if result["status"] == "success":
                    st.markdown('<div class="success-box">✅ Contract generated successfully!</div>', unsafe_allow_html=True)
                    
                    # Display contract
                    st.subheader("📄 Generated Contract")
                    st.text_area(
                        "Contract Text:",
                        result["contract"],
                        height=400,
                        key="generated_contract"
                    )
                    
                    # Metrics
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Word Count", result['word_count'])
                    with col2:
                        st.metric("Policies Referenced", result['policies_referenced'])
                    with col3:
                        st.metric("Contract Type", result['contract_type'])
                    
                    # Compliance check of generated contract
                    if result.get('compliance_check'):
                        with st.expander("🔍 Built-in Compliance Check"):
                            st.markdown(result['compliance_check']['analysis'])
                    
                    # Download options
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.download_button(
                            "📥 Download Contract (TXT)",
                            result["contract"],
                            file_name=f"contract_{selected_gen_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                            mime="text/plain",
                            use_container_width=True
                        )
                    
                    with col2:
                        # Parameters as JSON
                        st.download_button(
                            "📥 Download Parameters (JSON)",
                            json.dumps(contract_params, indent=2),
                            file_name=f"contract_params_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                            mime="application/json",
                            use_container_width=True
                        )
                    
                    with col3:
                        # Full report
                        full_report = f"""CONTRACT GENERATION REPORT
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Contract Type: {selected_gen_type}
Word Count: {result['word_count']}
Policies Referenced: {result['policies_referenced']}

PARAMETERS:
{json.dumps(contract_params, indent=2)}

GENERATED CONTRACT:
{result['contract']}

COMPLIANCE CHECK:
{result['compliance_check']['analysis'] if result.get('compliance_check') else 'N/A'}
"""
                        st.download_button(
                            "📥 Download Full Report",
                            full_report,
                            file_name=f"full_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                            mime="text/plain",
                            use_container_width=True
                        )
                    
                    # Save to history
                    st.session_state.history.append({
                        "type": "contract_generation",
                        "timestamp": datetime.now().isoformat(),
                        "contract_type": selected_gen_type,
                        "result": result
                    })
                    
                else:
                    st.error(f"❌ Error: {result.get('error', 'Unknown error')}")

# TAB 3: Missing Clauses
with tab3:
    st.header("💡 Missing Clause Analyzer")
    st.markdown("Identify missing critical clauses in your contract")
    
    col1, col2 = st.columns([3, 1])
    
    with col2:
        clause_contract_type = st.selectbox(
            "Contract Type:",
            ["service", "procurement", "vendor", "software", "consulting"],
            key="clause_type"
        )
    
    clause_input_method = st.radio(
        "Input Method:",
        ["📝 Paste Text", "📄 Upload File"],
        horizontal=True,
        key="clause_input"
    )
    
    clause_text = ""
    
    if clause_input_method == "📝 Paste Text":
        clause_text = st.text_area(
            "Paste your contract text:",
            height=300,
            placeholder="Enter the contract text to analyze for missing clauses...",
            key="clause_text_area"
        )
    else:
        clause_file = st.file_uploader(
            "Upload contract file:",
            type=["txt", "pdf"],
            key="clause_file_upload"
        )
        
        if clause_file:
            if clause_file.type == "text/plain":
                clause_text = clause_file.read().decode("utf-8")
            elif clause_file.type == "application/pdf":
                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
                    tmp.write(clause_file.getvalue())
                    tmp_path = tmp.name
                
                try:
                    extracted = st.session_state.rag.extract_text_from_pdf(tmp_path)
                    clause_text = extracted['text']
                    st.success(f"✅ Extracted text from PDF")
                except Exception as e:
                    st.error(f"❌ Error: {e}")
                finally:
                    os.unlink(tmp_path)
    
    analyze_button = st.button("🔍 Analyze Missing Clauses", type="primary", use_container_width=True)
    
    if analyze_button and clause_text:
        with st.spinner("💡 Analyzing contract for missing clauses..."):
            result = st.session_state.rag.suggest_missing_clauses(
                input_text=clause_text,
                contract_type=clause_contract_type
            )
            
            if result["status"] == "success":
                st.markdown('<div class="success-box">✅ Analysis completed!</div>', unsafe_allow_html=True)
                
                st.subheader("📋 Missing Clause Analysis")
                st.markdown(result["suggestions"])
                
                # Metadata
                with st.expander("ℹ️ Analysis Details"):
                    st.metric("Policies Referenced", result['policies_referenced'])
                    st.metric("Analysis Time", datetime.now().strftime("%H:%M:%S"))
                
                # Download report
                report = f"""MISSING CLAUSE ANALYSIS REPORT
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Contract Type: {clause_contract_type}
Policies Referenced: {result['policies_referenced']}

{result["suggestions"]}

---
Original Contract Text:
{clause_text}
"""
                st.download_button(
                    "📥 Download Analysis Report",
                    report,
                    file_name=f"missing_clauses_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain"
                )
                
                # Save to history
                st.session_state.history.append({
                    "type": "missing_clause_analysis",
                    "timestamp": datetime.now().isoformat(),
                    "contract_type": clause_contract_type,
                    "result": result
                })
                
            else:
                st.error(f"❌ Error: {result.get('error', 'Unknown error')}")
    
    elif analyze_button:
        st.warning("⚠️ Please provide contract text to analyze")

# TAB 4: Policy Manager
with tab4:
    st.header("📚 Policy Document Manager")
    st.markdown("Upload and manage procurement policy documents")
    
    # Upload section
    st.subheader("📤 Upload New Policy")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        policy_file = st.file_uploader(
            "Select policy document (PDF):",
            type=["pdf"],
            key="policy_upload"
        )
    
    with col2:
        policy_type = st.selectbox(
            "Document Type:",
            ["policy", "vendor", "compliance"],
            key="policy_type_select"
        )
    
    # Metadata fields
    with st.expander("📝 Add Metadata (Optional)"):
        col1, col2 = st.columns(2)
        
        with col1:
            version = st.text_input("Version:", placeholder="e.g., 2.1")
            department = st.text_input("Department:", placeholder="e.g., Procurement")
        
        with col2:
            effective_date = st.date_input("Effective Date:")
            author = st.text_input("Author/Approver:")
    
    if st.button("📤 Upload Policy", type="primary"):
        if policy_file:
            # Save temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
                tmp.write(policy_file.getvalue())
                tmp_path = tmp.name
            
            # Prepare metadata
            custom_metadata = {}
            if version:
                custom_metadata["version"] = version
            if department:
                custom_metadata["department"] = department
            if author:
                custom_metadata["author"] = author
            custom_metadata["effective_date"] = effective_date.strftime("%Y-%m-%d")
            custom_metadata["uploaded_at"] = datetime.now().isoformat()
            
            with st.spinner(f"📚 Processing {policy_file.name}..."):
                try:
                    result = st.session_state.rag.store_document(
                        tmp_path,
                        doc_type=policy_type,
                        custom_metadata=custom_metadata
                    )
                    
                    st.success(f"✅ Successfully uploaded {policy_file.name}")
                    st.info(f"📊 Created {result['chunks']} searchable chunks")
                    
                    # Save to history
                    st.session_state.history.append({
                        "type": "policy_upload",
                        "timestamp": datetime.now().isoformat(),
                        "filename": policy_file.name,
                        "doc_type": policy_type,
                        "chunks": result['chunks']
                    })
                    
                    # Clear cache to refresh document list
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Error uploading policy: {e}")
                finally:
                    os.unlink(tmp_path)
        else:
            st.warning("⚠️ Please select a PDF file to upload")
    
    st.markdown("---")
    
    # List existing documents
    st.subheader("📋 Stored Policy Documents")
    
    docs = st.session_state.rag.get_document_list()
    
    if docs:
        # Filter options
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            search_term = st.text_input("🔍 Search documents:", placeholder="Enter filename or keyword")
        
        with col2:
            filter_type = st.selectbox(
                "Filter by type:",
                ["All", "policy", "vendor", "compliance"]
            )
        
        # Filter documents
        filtered_docs = docs
        if search_term:
            filtered_docs = [d for d in filtered_docs if search_term.lower() in d['filename'].lower()]
        if filter_type != "All":
            filtered_docs = [d for d in filtered_docs if d['collection'] == filter_type]
        
        st.info(f"📊 Showing {len(filtered_docs)} of {len(docs)} documents")
        
        # Display documents
        for i, doc in enumerate(filtered_docs):
            with st.expander(f"📄 {doc['filename']} [{doc['collection']}]"):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.write(f"**Type:** {doc['collection']}")
                    st.write(f"**Pages:** {doc['page_count']}")
                    st.write(f"**Uploaded:** {doc['extraction_date'][:10] if doc['extraction_date'] else 'N/A'}")
                    st.write(f"**Hash:** `{doc['doc_hash'][:16]}...`")
                
                with col2:
                    if st.button(f"🗑️ Delete", key=f"delete_{i}"):
                        if st.session_state.get(f'confirm_delete_{i}'):
                            with st.spinner("Deleting..."):
                                deleted = st.session_state.rag.delete_document(doc['doc_hash'])
                                st.success(f"✅ Deleted {deleted} chunks")
                                st.rerun()
                        else:
                            st.session_state[f'confirm_delete_{i}'] = True
                            st.warning("⚠️ Click again to confirm deletion")
    else:
        st.info("📭 No policy documents uploaded yet. Upload your first policy above!")
    
    st.markdown("---")
    
    # Bulk operations
    st.subheader("🔧 Bulk Operations")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📊 Export Document List", use_container_width=True):
            doc_list_json = json.dumps(docs, indent=2)
            st.download_button(
                "📥 Download JSON",
                doc_list_json,
                file_name=f"document_list_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
    
    with col2:
        if st.button("🔍 Test Policy Search", use_container_width=True):
            test_query = st.text_input("Enter search query:", key="test_search")
            if test_query:
                results = st.session_state.rag.search(test_query, top_k=5)
                st.write(f"Found {len(results['results'])} results:")
                for r in results['results']:
                    st.write(f"- {r['metadata'].get('filename', 'Unknown')}: {r['text'][:100]}...")

# TAB 5: Analytics
with tab5:
    st.header("📊 Usage Analytics & Insights")
    
    # Summary metrics
    st.subheader("📈 System Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    docs = st.session_state.rag.get_document_list()
    history_count = len(st.session_state.history)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Total Documents", len(docs))
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Total Operations", history_count)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        policy_count = len([d for d in docs if d['collection'] == 'policy'])
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Policy Documents", policy_count)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        compliance_count = len([d for d in docs if d['collection'] == 'compliance'])
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Compliance Docs", compliance_count)
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Activity history
    st.subheader("📜 Recent Activity")
    
    if st.session_state.history:
        # Show last 10 activities
        for activity in reversed(st.session_state.history[-10:]):
            with st.expander(
                f"{activity['timestamp'][:19]} - {activity['type'].replace('_', ' ').title()}"
            ):
                st.json(activity)
        
        # Export history
        if st.button("📥 Export Activity History"):
            history_json = json.dumps(st.session_state.history, indent=2)
            st.download_button(
                "Download History (JSON)",
                history_json,
                file_name=f"activity_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
    else:
        st.info("📭 No activity recorded yet. Start using the system to see analytics!")
    
    st.markdown("---")
    
    # Document collection breakdown
    st.subheader("📊 Document Distribution")
    
    if docs:
        collection_counts = {}
        for doc in docs:
            coll = doc['collection']
            collection_counts[coll] = collection_counts.get(coll, 0) + 1
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.bar_chart(collection_counts)
        
        with col2:
            for coll, count in collection_counts.items():
                percentage = (count / len(docs)) * 100
                st.write(f"**{coll.title()}**: {count} documents ({percentage:.1f}%)")
    else:
        st.info("Upload documents to see distribution analytics")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem 0;'>
    <p><strong>Procurement Contract Assistant</strong> | Powered by Claude AI & ChromaDB</p>
    <p style='font-size: 0.9rem;'>Made with ❤️ for Procurement Teams</p>
</div>
""", unsafe_allow_html=True)