__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
import streamlit as st
import os
import markdown
import json
from dotenv import load_dotenv
from crewai import LLM, Agent, Crew, Process, Task
from crewai.knowledge.source.crew_docling_source import CrewDoclingSource
import tempfile
from templates import query_template, summarization_template

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="InfoLegal Agent",
    page_icon="⚖️",
    layout="wide",
)

# Custom CSS for the brown legal aesthetic
st.markdown("""
<style>
    .main {
        background-color: #f8f5f0;
    }
    .stApp {
        background-color: #f8f5f0;
    }
    h1, h2, h3 {
        color: #5d4037;
        font-family: 'Garamond', serif;
    }
    .stButton button {
        background-color: #8d6e63;
        color: white;
        font-weight: bold;
        border-radius: 5px;
        border: none;
        padding: 0.5rem 1rem;
    }
    .stButton button:hover {
        background-color: #6d4c41;
    }
    .css-1kyxreq {
        background-color: #d7ccc8;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
    }
    .custom-card {
        background-color: #efebe9;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        border-left: 5px solid #8d6e63;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .legal-header {
        display: flex;
        align-items: center;
        margin-bottom: 20px;
    }
    .legal-header img {
        height: 60px;
        margin-right: 15px;
    }
    .document-list {
        background-color: #efebe9;
        border-radius: 5px;
        padding: 10px;
        margin-top: 10px;
    }
    .stTextInput > div > div > input {
        background-color: #efebe9;
        color: #5d4037;
    }
    .stTextArea > div > div > textarea {
        background-color: #efebe9;
        color: #5d4037;
    }
</style>
""", unsafe_allow_html=True)

# Logo and title
st.markdown("""
<div class="legal-header">
    <img src="https://w7.pngwing.com/pngs/254/724/png-transparent-lawyer-statute-legislature-procedural-law-lawyers-silhouette-people-logo-man-silhouette.png" alt="InfoLegal Logo">
    <h1>InfoLegal Agent</h1>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="custom-card">
    <h3>Your AI-Powered Legal Research Assistant</h3>
    <p>InfoLegal Agent helps you navigate complex Indian legal documents with ease. Ask questions in plain language and get clear, concise answers based on authoritative legal sources.</p>
</div>
""", unsafe_allow_html=True)

# Initialize session state for document management
if 'documents' not in st.session_state:
    st.session_state.documents = [
        "https://kb.icai.org/pdfs/PDFFile5b28c9ce64e524.54675199.pdf",
        "https://www.cyrilshroff.com/wp-content/uploads/2020/09/Guide-to-Litigation-in-India.pdf",
    ]

if 'query_history' not in st.session_state:
    st.session_state.query_history = []

# Sidebar for document management
with st.sidebar:
    st.markdown("<h2>Document Management</h2>", unsafe_allow_html=True)
    
    # Display current documents
    st.markdown("<h3>Current Documents</h3>", unsafe_allow_html=True)
    with st.expander("View Documents"):
        for i, doc in enumerate(st.session_state.documents):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"📄 {doc}")
            with col2:
                if st.button("Remove", key=f"remove_{i}"):
                    st.session_state.documents.pop(i)
                    st.rerun()
    
    # Add new document
    st.markdown("<h3>Add Document</h3>", unsafe_allow_html=True)
    doc_method = st.radio("Select method:", ["URL", "Upload File"])
    
    if doc_method == "URL":
        new_doc_url = st.text_input("Enter document URL:", placeholder="https://example.com/document.pdf")
        if st.button("Add URL"):
            if new_doc_url and new_doc_url not in st.session_state.documents:
                st.session_state.documents.append(new_doc_url)
                st.success("Document added successfully!")
                st.rerun()
    else:
        uploaded_file = st.file_uploader("Upload document:", type=["pdf", "docx", "txt"])
        if uploaded_file is not None:
            # Save uploaded file temporarily
            temp_dir = tempfile.mkdtemp()
            temp_file_path = os.path.join(temp_dir, uploaded_file.name)
            with open(temp_file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            if st.button("Add Uploaded File"):
                st.session_state.documents.append(temp_file_path)
                st.success("Document added successfully!")
                st.rerun()
    
    # Query history
    st.markdown("<h3>Query History</h3>", unsafe_allow_html=True)
    with st.expander("View History"):
        for i, q in enumerate(st.session_state.query_history):
            st.markdown(f"**Q{i+1}:** {q}")
            
    # About
    st.markdown("---")
    st.markdown("### About InfoLegal Agent")
    st.markdown("© 2025 Qest.ai")

# Main content
st.markdown("<h2>Ask Your Legal Question</h2>", unsafe_allow_html=True)

# User query input
user_query = st.text_area("Enter your question:", placeholder="Example: What are the requirements for filing a civil lawsuit in India?", height=100)

# Process the query
if st.button("Submit Question"):
    if user_query:
        st.session_state.query_history.append(user_query)
        
        with st.spinner("Analyzing legal documents..."):
            try:
                # Initialize LLM
                llm = LLM(model="gemini/gemini-1.5-pro", api_key=os.environ.get("GEMINI_API_KEY"))
                
                # Create knowledge source with current documents
                content_source = CrewDoclingSource(
                    file_paths=st.session_state.documents,
                )
                
                # Create agents
                query_agent = Agent(
                    role="Legal Information Retrieval Specialist - India Focus",
                    goal="Efficiently and accurately retrieve relevant sections from Indian legal documents",
                    backstory="You are a highly specialized AI agent with deep indexing and search capabilities within a specific corpus of Indian legal texts. "
                    "You understand legal terminology and can quickly pinpoint the most relevant passages, sections, and clauses related to a user's natural language query. "
                    "You prioritize precision and recall, ensuring that all potentially relevant information is identified "
                    "while minimizing irrelevant results. You are optimized for speed and accuracy in a legal context.",
                    llm=llm,
                    memory=True,  
                    respect_context_window=True, 
                    use_system_prompt=True,
                    cache=True, 
                    system_template=query_template.system_template,  
                    prompt_template=query_template.prompt_template,  
                    response_template=query_template.response_template,
                    knowledge_sources=content_source
                )
                
                summarization_agent = Agent(
                    role="Legal Text Simplification and Explanation Expert",
                    goal="Transform complex legal passages into clear, concise, and easy-to-understand summaries, preserving accuracy.",
                    backstory="You are an advanced AI agent trained in legal text summarization and simplification. You understand legal principles and can explain complex concepts in plain language. "
                    "You prioritize making legal information accessible to non-experts without losing crucial details or introducing inaccuracies. "
                    "You are adept at handling legal jargon and converting it into understandable terms. You can structure summaries logically.",
                    llm=llm, 
                    memory=True, 
                    respect_context_window=True, 
                    use_system_prompt=True,
                    cache=True,  
                    system_template=summarization_template.system_template, 
                    prompt_template=summarization_template.prompt_template,
                    response_template=summarization_template.response_template,  
                    knowledge_sources=content_source,
                    multimodal=True
                )
                
                # Create tasks
                query_task = Task(
                    description="""
                        Retrieve relevant sections from Indian legal documents based on the user's query.
                        The documents to search are specific to the user's query.
                        
                        Focus on accuracy and completeness. Find ALL relevant sections, passages, and clauses.
                        Do NOT summarize the content. Only extract the verbatim text and provide citations.
                    """,
                    expected_output="""
                        A JSON object containing the original user query and a list of results.  
                        Each result should include the document title, a full citation (section, chapter, page, etc.),
                        and the exact text of the relevant section. Follow this format:

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
                
                # Create and run crew
                crew = Crew(
                    agents=[query_agent, summarization_agent],
                    tasks=[query_task, summarization_task],
                    process=Process.sequential,
                    knowledge_sources=content_source,
                    memory=True,
                    cache=True
                )
                
                result = crew.kickoff(inputs=user_query)
                
                # Display result
                st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
                st.markdown("<h3>Legal Analysis</h3>", unsafe_allow_html=True)
                st.markdown(markdown.markdown(result), unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
                
                # Sources section
                try:
                    # Try to parse and display the sources from the query agent's raw output
                    if hasattr(query_agent, 'last_output') and query_agent.last_output:
                        try:
                            query_data = json.loads(query_agent.last_output)
                            if 'results' in query_data and len(query_data['results']) > 0:
                                st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
                                st.markdown("<h3>Sources</h3>", unsafe_allow_html=True)
                                for i, source in enumerate(query_data['results']):
                                    with st.expander(f"Source {i+1}: {source.get('document', 'Document')} - {source.get('citation', 'Citation')}"):
                                        st.markdown(source.get('extract', 'No extract available'))
                                st.markdown("</div>", unsafe_allow_html=True)
                        except json.JSONDecodeError:
                            # If JSON parsing fails, don't display sources section
                            pass
                except Exception as e:
                    # In case of any error, don't display sources
                    pass
                    
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
    else:
        st.warning("Please enter a question to proceed.")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #8d6e63; font-size: 0.8em;">
    InfoLegal Agent | Crest.ai | Advancing Legal Research with AI
</div>
""", unsafe_allow_html=True)
