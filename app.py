import streamlit as st
from crewai import LLM, Agent, Crew, Process, Task
from crewai.knowledge.source.pdf_knowledge_source import PDFKnowledgeSource
from templates import query_template, summarization_template
import os
import markdown
import json
from dotenv import load_dotenv
import pathlib
import time

# Load environment variables
load_dotenv()

# Set page configuration
st.set_page_config(
    page_title="Indian Legal Assistant",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better aesthetics
st.markdown("""
<style>
    .main-header {
        font-family: 'Serif';
        color: #1E3A8A;
    }
    .subheader {
        color: #475569;
        font-size: 1.2rem;
    }
    .stTextInput > div > div > input {
        border-radius: 10px;
    }
    .stButton > button {
        border-radius: 10px;
        background-color: #1E3A8A;
        color: white;
        font-weight: bold;
        padding: 0.5rem 2rem;
        border: none;
    }
    .stButton > button:hover {
        background-color: #2563EB;
    }
    .result-container {
        background-color: #F8FAFC;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #E2E8F0;
    }
    .footer {
        text-align: center;
        color: #94A3B8;
        font-size: 0.8rem;
        margin-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# App header
st.markdown("<h1 class='main-header'>Indian Legal Information Retrieval System</h1>", unsafe_allow_html=True)
st.markdown("<p class='subheader'>Get simplified explanations for complex Indian legal queries</p>", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://www.svgrepo.com/show/430377/balance-justice-law.svg", width=100)
    st.title("About")
    st.markdown("""
    This application uses AI to parse and simplify Indian legal documents. 
    It can answer questions about:
    
    - Guide to Litigation in India
    - Legal Compliance & Corporate Laws by ICAI
    
    The system will retrieve relevant information and provide a simplified explanation.
    """)
    
    st.title("Sample Queries")
    st.markdown("""
    - What is the procedure for filing a civil suit in India?
    - How are commercial disputes resolved in Indian courts?
    - What are the different types of courts in India?
    - Explain the arbitration process in India
    """)
    
    st.title("Document Sources")
    with st.expander("View Source Documents"):
        st.markdown("- Guide to Litigation in India")
        st.markdown("- Legal Compliance & Corporate Laws by ICAI")

# Main content
def main():
    # Query input
    query = st.text_area("Enter your legal query:", height=100, placeholder="Example: What is the procedure for filing a civil suit in India?")
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        submit_button = st.button("Get Legal Information", use_container_width=True)
    
    # Initialize session state for results
    if 'results' not in st.session_state:
        st.session_state.results = None
    
    if submit_button and query:
        with st.spinner("Analyzing legal documents... This may take a moment..."):
            # Process the query
            results = process_query(query)
            st.session_state.results = results
    
    # Display results
    if st.session_state.results:
        st.markdown("### Simplified Explanation")
        st.markdown("<div class='result-container'>", unsafe_allow_html=True)
        st.markdown(st.session_state.results)
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Add option to view source extracts
        if st.button("View Source Extracts"):
            st.session_state.show_extracts = True
        
        # Show extracts if requested
        if 'show_extracts' in st.session_state and st.session_state.show_extracts:
            try:
                # This would need to be updated to store and display the query agent's raw results
                st.markdown("### Source Extracts")
                st.markdown("<div class='result-container'>", unsafe_allow_html=True)
                st.markdown("Source document extracts would appear here")
                st.markdown("</div>", unsafe_allow_html=True)
            except:
                st.error("Could not display source extracts.")
    
    # Footer
    st.markdown("<div class='footer'>Indian Legal Assistant • Powered by CrewAI</div>", unsafe_allow_html=True)

def process_query(query_text):
    # Setup LLM
    llm = LLM(model="gemini/gemini-1.5-pro", api_key=os.environ.get("GEMINI_API_KEY"))
    embedder = {
        "provider": "google",
        "config": {
            "model": "models/text-embedding-004",
            "api_key": os.environ.get("GEMINI_API_KEY")
        }
    }

    # Setup knowledge source
    base_dir = pathlib.Path(__file__).parent.resolve()
    file_paths = [
        str((base_dir / "knowledge" / "Guide-to-Litigation-in-India.pdf").resolve()),
        str((base_dir / "knowledge" / "PDFFile5b28c9ce64e524.54675199.pdf").resolve())
    ]
    content_source = PDFKnowledgeSource(file_paths=file_paths)

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
        knowledge_sources=content_source,
        embedder=embedder
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
        knowledge_sources=content_source
    )

    # Create tasks
    query_task = Task(
        description="""
            Retrieve relevant sections from Indian legal documents based on the user's query.
            The documents to search are:
            - Guide to Litigation in India
            - Legal Compliance & Corporate Laws by ICAI
            
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
    )

    # Create crew
    crew = Crew(
        agents=[query_agent, summarization_agent],
        tasks=[query_task, summarization_task],
        process=Process.sequential,
        knowledge_sources=content_source,
        memory=True,
        cache=True,
        embedder=embedder
    )
    
    # Process the query
    result = crew.kickoff(inputs=query_text)
    clean_result = markdown.markdown(result)
    
    return clean_result

if __name__ == "__main__":
    main()
