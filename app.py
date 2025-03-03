__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
import streamlit as st
import os
import json
import markdown
import base64
from crewai import LLM, Agent, Crew, Process, Task
from crewai_tools import RagTool
from dotenv import load_dotenv
from templates import query_template, summarization_template
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="InfoLegal Agent - Qest.ai",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for brown gradient legal theme
def add_custom_css():
    st.markdown("""
    <style>
    /* Main background and text colors - Brown legal theme */
    .stApp {
        background: linear-gradient(135deg, #2E1E12 0%, #5D4037 100%);
        color: #F5F5DC;
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background: rgba(46, 30, 18, 0.9);
        border-right: 1px solid rgba(205, 133, 63, 0.3);
    }
    
    /* Header styling */
    h1, h2, h3 {
        color: #CD853F !important;
        font-weight: 600;
        font-family: 'Garamond', serif;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(90deg, #8B4513, #A0522D);
        color: #F5F5DC;
        border: none;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background: linear-gradient(90deg, #A0522D, #8B4513);
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(139, 69, 19, 0.4);
    }
    
    /* Input fields styling */
    .stTextInput > div > div > input, .stTextArea > div > div > textarea {
        background-color: rgba(245, 245, 220, 0.1);
        color: #F5F5DC;
        border: 1px solid rgba(205, 133, 63, 0.4);
        border-radius: 5px;
    }
    
    /* File uploader styling */
    .stFileUploader > div > button {
        background: linear-gradient(90deg, #8B4513, #A0522D);
        color: #F5F5DC;
    }
    
    /* Cards or containers */
    .css-1r6slb0, .css-18e3th9 {
        background-color: rgba(46, 30, 18, 0.7);
        border: 1px solid rgba(205, 133, 63, 0.3);
        border-radius: 10px;
        padding: 1.5rem;
        margin-bottom: 1rem;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background-color: rgba(46, 30, 18, 0.9);
        color: #CD853F;
        border: 1px solid rgba(205, 133, 63, 0.3);
        border-radius: 5px;
    }
    
    /* Success messages */
    .stSuccess {
        background-color: rgba(76, 175, 80, 0.2);
        color: #C5E1A5;
        border: 1px solid rgba(76, 175, 80, 0.3);
    }
    
    /* Info messages */
    .stInfo {
        background-color: rgba(100, 181, 246, 0.2);
        color: #BBDEFB;
        border: 1px solid rgba(100, 181, 246, 0.3);
    }
    
    /* Warning messages */
    .stWarning {
        background-color: rgba(255, 152, 0, 0.2);
        color: #FFE0B2;
        border: 1px solid rgba(255, 152, 0, 0.3);
    }
    
    /* Error messages */
    .stError {
        background-color: rgba(244, 67, 54, 0.2);
        color: #FFCDD2;
        border: 1px solid rgba(244, 67, 54, 0.3);
    }
    
    /* Logo container */
    .logo-container {
        display: flex;
        justify-content: center;
        align-items: center;
        margin-bottom: 2rem;
    }
    
    /* Results container */
    .results-container {
        background-color: rgba(46, 30, 18, 0.7);
        border: 1px solid rgba(205, 133, 63, 0.3);
        border-radius: 10px;
        padding: 1.5rem;
        margin-top: 1rem;
    }
    
    /* Documentation section */
    .doc-section {
        padding: 1rem;
        background-color: rgba(46, 30, 18, 0.5);
        border-radius: 5px;
        border-left: 3px solid #CD853F;
        margin-bottom: 1rem;
    }
    
    /* Legal header with logo and title */
    .legal-header {
        display: flex;
        flex-direction: column;
        align-items: center;
        margin-bottom: 2rem;
        text-align: center;
    }
    
    .legal-header img {
        height: 100px;
        margin-bottom: 1rem;
        filter: sepia(0.5);
    }
    
    .legal-header h1 {
        font-family: 'Garamond', serif;
        font-size: 2.5rem;
        color: #CD853F !important;
        margin: 0;
    }
    
    /* Document list styling */
    .document-item {
        display: flex;
        align-items: center;
        background-color: rgba(205, 133, 63, 0.1);
        border: 1px solid rgba(205, 133, 63, 0.2);
        border-radius: 5px;
        padding: 0.75rem;
        margin-bottom: 0.5rem;
    }
    
    .document-item-name {
        flex-grow: 1;
        font-weight: 500;
        color: #DEB887;
    }
    
    .document-item-icon {
        margin-right: 0.5rem;
        font-size: 1.2rem;
    }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(46, 30, 18, 0.7);
    }
    
    ::-webkit-scrollbar-thumb {
        background: #8B4513;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #A0522D;
    }
    
    /* Divider styling */
    .custom-divider {
        border: 0;
        height: 1px;
        background-image: linear-gradient(to right, rgba(205, 133, 63, 0), rgba(205, 133, 63, 0.75), rgba(205, 133, 63, 0));
        margin: 1.5rem 0;
    }
    
    /* Footer styling */
    .legal-footer {
        text-align: center;
        margin-top: 3rem;
        padding: 1rem;
        border-top: 1px solid rgba(205, 133, 63, 0.2);
        color: #CD853F;
        font-family: 'Garamond', serif;
    }
    </style>
    """, unsafe_allow_html=True)

add_custom_css()

# Initialize session state
if 'documents' not in st.session_state:
    st.session_state.documents = [
        {
            "type": "web_page",
            "url": "https://kb.icai.org/pdfs/PDFFile5b28c9ce64e524.54675199.pdf",
            "name": "ICAI Knowledge Base"
        },
        {
            "type": "web_page",
            "url": "https://www.cyrilshroff.com/wp-content/uploads/2020/09/Guide-to-Litigation-in-India.pdf",
            "name": "Guide to Litigation in India"
        }
    ]
if 'processing' not in st.session_state:
    st.session_state.processing = False
if 'results' not in st.session_state:
    st.session_state.results = None
if 'api_key_set' not in st.session_state:
    st.session_state.api_key_set = False

# Logo and title
st.markdown("""
<div class="legal-header">
    <img src="https://cdn-icons-png.flaticon.com/512/126/126345.png" alt="InfoLegal Logo">
    <h1>InfoLegal Agent</h1>
    <h3>Powered by Qest.ai</h3>
</div>
""", unsafe_allow_html=True)

# Main content layout
col_main, col_sidebar = st.columns([3, 1])

with col_sidebar:
    st.markdown("<h2 style='text-align: center;'>Document Repository</h2>", unsafe_allow_html=True)
    
    # Document Sources
    st.markdown("<div class='custom-divider'></div>", unsafe_allow_html=True)
    st.markdown("<h3>Add Documents</h3>", unsafe_allow_html=True)
    
    doc_tabs = st.tabs(["📄 File Upload", "🌐 Web URL"])
    
    with doc_tabs[0]:  # File Upload tab
        uploaded_file = st.file_uploader(
            "Upload Document", 
            type=["pdf", "csv", "json", "txt", "docx"],
            help="Supported formats: PDF, CSV, JSON, TXT, DOCX"
        )
        
        if uploaded_file is not None:
            # Save the file temporarily
            file_path = f"temp_{uploaded_file.name}"
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
                
            add_file = st.button("Add Document", key="add_file_btn")
            if add_file:
                st.session_state.documents.append({
                    "type": "file",
                    "path": file_path,
                    "name": uploaded_file.name
                })
                st.success(f"Added: {uploaded_file.name}")
    
    with doc_tabs[1]:  # Web URL tab
        url_input = st.text_input(
            "Website URL",
            placeholder="https://example.com",
            help="Enter a valid URL to a website or document"
        )
        
        add_url = st.button("Add URL", key="add_url_btn")
        if add_url and url_input:
            if url_input.startswith(("http://", "https://")):
                st.session_state.documents.append({
                    "type": "web_page",
                    "url": url_input,
                    "name": url_input.split("/")[-1] if url_input.split("/")[-1] else url_input
                })
                st.success(f"Added: {url_input}")
            else:
                st.error("Please enter a valid URL starting with http:// or https://")
    
    # Show current documents
    if st.session_state.documents:
        st.markdown("<div class='custom-divider'></div>", unsafe_allow_html=True)
        st.markdown("<h3>Current Documents</h3>", unsafe_allow_html=True)
        
        for i, doc in enumerate(st.session_state.documents):
            st.markdown(
                f"""
                <div class="document-item">
                    <div class="document-item-icon">{"📄" if doc["type"] == "file" else "🌐"}</div>
                    <div class="document-item-name">{doc["name"]}</div>
                </div>
                """, 
                unsafe_allow_html=True
            )
            col1, col2 = st.columns([4, 1])
            with col2:
                if st.button("Remove", key=f"remove_{i}"):
                    st.session_state.documents.pop(i)
                    st.experimental_rerun()
        
        if st.button("Clear All Documents"):
            # Reset to default documents
            st.session_state.documents = [
                {
                    "type": "web_page",
                    "url": "https://kb.icai.org/pdfs/PDFFile5b28c9ce64e524.54675199.pdf",
                    "name": "ICAI Knowledge Base"
                },
                {
                    "type": "web_page",
                    "url": "https://www.cyrilshroff.com/wp-content/uploads/2020/09/Guide-to-Litigation-in-India.pdf",
                    "name": "Guide to Litigation in India"
                }
            ]
            st.experimental_rerun()
    
    # Document support information
    st.markdown("<div class='custom-divider'></div>", unsafe_allow_html=True)
    st.markdown("<h3>Supported Documents</h3>", unsafe_allow_html=True)
    st.markdown("""
    * 📄 PDF files
    * 📊 CSV files
    * 📃 JSON files
    * 📝 Text files
    * 📋 DOCX files
    * 🌐 Web pages
    """)

with col_main:
    # Query input section
    st.markdown("<h2>Ask Your Legal Question</h2>", unsafe_allow_html=True)
    
    user_query = st.text_area(
        "Enter Your Legal Inquiry",
        placeholder="E.g., What are the steps to file a civil lawsuit in India?",
        height=120
    )
    
    query_col1, query_col2 = st.columns([1, 4])
    with query_col1:
        process_button = st.button(
            "Process Query", 
            disabled=not st.session_state.documents or not user_query
        )

    if not st.session_state.documents:
        st.warning("⚠️ Please add at least one document in the Document Repository.")
    
    # Results section
    if process_button:
        st.session_state.processing = True
    
    if st.session_state.processing:
        with st.spinner("Processing your legal query... This might take a minute."):
            try:
                # Initialize tools and agents
                # Create a RAG tool with custom configuration
                config = {
                    "llm": {
                        "provider": "google",
                        "config": {
                            "model": "gemini-1.5-pro",
                            "api_key": os.environ.get("GEMINI_API_KEY"), }
                    },
                    "embedder": {
                        "provider": "huggingface",
                        "config": {
                            "model": "sentence-transformers/all-MiniLM-L6-v2",
                        }
                    }
                }

                rag_tool = RagTool(config=config)
                
                # Add documents to RAG tool
                for doc in st.session_state.documents:
                    if doc["type"] == "file":
                        rag_tool.add(data_type="file", path=doc["path"])
                    elif doc["type"] == "web_page":
                        rag_tool.add(data_type="web_page", url=doc["url"])
                
                # Initialize LLM
                llm = LLM(model="google/gemini-1.5-pro", api_key=os.environ.get("GEMINI_API_KEY"),temperature=0.25)
                
                # Initialize agents
                query_agent = Agent(
                    role="Legal Information Retrieval Specialist - India Focus",
                    goal="Efficiently and accurately retrieve relevant sections from Indian legal documents",
                    backstory="You are a highly specialized AI agent with deep indexing and search capabilities within a specific corpus of Indian legal texts."
                    "You understand legal terminology and can quickly pinpoint the most relevant passages, sections, and clauses related to a user's natural language query."
                    "You prioritize precision and recall, ensuring that all potentially relevant information is identified" 
                    "while minimizing irrelevant results. You are optimized for speed and accuracy in a legal context..",
                    llm=llm,
                    memory=True,  
                    respect_context_window=True, 
                    use_system_prompt=True,
                    cache=True, 
                    system_template=query_template.system_template,  
                    prompt_template=query_template.prompt_template,  
                    response_template=query_template.response_template,
                    tools=[rag_tool]
                )
                
                summarization_agent = Agent(
                    role="Legal Text Simplification and Explanation Expert",
                    goal="Transform complex legal passages into clear, concise, and easy-to-understand summaries, preserving accuracy.",
                    backstory="You are an advanced AI agent trained in legal text summarization and simplification. You understand legal principles and can explain complex concepts in plain language."
                    "You prioritize making legal information accessible to non-experts without losing crucial details or introducing inaccuracies."
                    "You are adept at handling legal jargon and converting it into understandable terms. You can structure summaries logically.",
                    llm=llm, 
                    memory=True, 
                    respect_context_window=True, 
                    use_system_prompt=True,
                    cache=True,  
                    system_template=summarization_template.system_template, 
                    prompt_template=summarization_template.prompt_template,
                    response_template=summarization_template.response_template,  
                    tools=[rag_tool],
                    multimodal=True
                )
                
                # Initialize tasks
                query_task = Task(
                    description="""
                        Retrieve relevant sections from Indian legal documents based on the user's query.
                        Focus on accuracy and completeness. Find ALL relevant sections, passages, and clauses.
                        Do NOT summarize the content. Only extract the verbatim text and provide citations.
                    """,
                    expected_output="""
                        A JSON object containing the original user query and a list of results.  
                        Each result should include the document title, a full citation (section, chapter, page, etc.),
                        and the exact text of the relevant section.  Follow this format:

                        {
                          "query": "<User's original query>",
                          "results": [
                            {
                              "document": "<Document Title>",
                              "citation": "<Full Citation (Section, Chapter, Page, etc.)>",
                              "extract": "<Exact text of the relevant section>"
                            },
                            {
                              "document": "<Document Title>",
                              "citation": "<Full Citation (Section, Chapter, Page, etc.)>",
                              "extract": "<Exact text of the relevant section>"
                            }
                          ]
                        }
                    """,
                    agent=query_agent,
                )
                
                summarization_task = Task(
                    description="""
                        Take the output from the Legal Information Retrieval Specialist (Query Agent) and 
                        transform it into a clear, concise, and easy-to-understand summary.  
                        Preserve the original legal meaning and accuracy.  
                        Replace legal jargon with plain language where possible.
                        Structure the summary logically (e.g., using bullet points or numbered steps if appropriate).
                        Conclude by offering to provide more details.
                    """,
                    expected_output="""
                        A plain text summary of the legal information, followed by a question prompting the user
                        if they want more details. For example:

                        Filing a lawsuit in India involves preparing legal documents, submitting a petition in court,
                        serving a notice to the opposing party, and attending hearings.

                        Would you like more details on any step?
                    """,
                    agent=summarization_agent,
                    context=[query_task],
                    output_file="summarization.md"
                )
                
                # Initialize crew
                crew = Crew(
                    agents=[query_agent, summarization_agent],
                    tasks=[query_task, summarization_task],
                    process=Process.sequential,
                    ktools=[rag_tool],
                    memory=True,
                    cache=True
                )
                
                # Run the query
                result = crew.kickoff(inputs=user_query)
                clean_result = markdown.markdown(result)
                
                # Store the result
                st.session_state.results = {
                    "raw": result,
                    "html": clean_result
                }
                
                # Reset processing state
                st.session_state.processing = False
                
                # Force a rerun to show results
                st.experimental_rerun()
                
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                st.session_state.processing = False
    
    # Display results
    if st.session_state.results:
        st.markdown("<div class='results-container'>", unsafe_allow_html=True)
        st.markdown("<h2>Legal Analysis Results</h2>", unsafe_allow_html=True)
        
        # Display the formatted results
        st.markdown(st.session_state.results["html"], unsafe_allow_html=True)
        
        # Option to download results
        result_col1, result_col2 = st.columns([1, 4])
        with result_col1:
            download_btn = st.download_button(
                label="Download Results",
                data=st.session_state.results["raw"],
                file_name="legal_analysis.md",
                mime="text/markdown"
            )
                
        st.markdown("</div>", unsafe_allow_html=True)

# How to Use section
with st.expander("How to Use InfoLegal Agent"):
    st.markdown("""
    ### Quick Start Guide
    
    1. **Document Repository**
       - Default documents are already loaded
       - Upload additional files or add web pages via URL
       - Each document will be analyzed for legal information
       
    2. **Ask Your Question**
       - Type your legal query in the text area
       - Be specific about Indian legal matters for best results
       - Click "Process Query" to start the analysis
       
    3. **Review Results**
       - The system retrieves relevant legal information
       - A simplified summary is presented in plain language
       - Download the results for your records
       
    ### Tips for Best Results
    
    - Be specific in your legal queries
    - Include relevant document keywords in your questions
    - For Indian legal questions, mention specific acts or sections if known
    - The more specific your question, the more precise the answer
    """)

# Footer
st.markdown("""
<div class="legal-footer">
    <p>© 2025 Qest.ai | InfoLegal Agent | All Rights Reserved</p>
    <p style="font-size: 0.8rem; margin-top: 0.5rem;">Legal information provided is for educational purposes only and does not constitute legal advice</p>
</div>
""", unsafe_allow_html=True)
