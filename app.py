__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
import streamlit as st
import os
import json
import markdown
from dotenv import load_dotenv

from crewai import LLM, Agent, Crew, Process, Task
from crewai_tools import RagTool
import os
import markdown
import json
from dotenv import load_dotenv
import pathlib

# Ensure directories exist
os.makedirs('history', exist_ok=True)
os.makedirs('uploads', exist_ok=True)

def initialize_crew(pdf_sources):
    """Initialize the CrewAI setup with dynamic PDF sources"""
    load_dotenv()

    # Initialize LLM
    llm = LLM(
        model="gemini/gemini-1.5-pro",
        api_key=os.environ.get("GEMINI_API_KEY"),
        temperature=0.25
    )

    # Configure RAG Tool
    config = {
        "llm": {
            "provider": "google",
            "config": {
                "model": "gemini-1.5-pro",
                "api_key": os.environ.get("GEMINI_API_KEY"), 
            }
        },
        "embedder": {
            "provider": "google",
            "config": {
                "model": "models/text-embedding-004",
            }
        }
    }

    # Setup RAG Tool
    rag_tool = RagTool(config=config)
    for source in pdf_sources:
        rag_tool.add(source, data_type="pdf_file")

    # Query Agent
    query_agent = Agent(
        role="Legal Information Retrieval Specialist - India Focus",
        goal=" Efficiently and accurately retrieve relevant sections from Indian legal documents",
        backstory="You are a highly specialized AI agent with deep indexing and search capabilities within a specific corpus of Indian legal texts."
        "You understand legal terminology and can quickly pinpoint the most relevant passages, sections, and clauses related to a user's natural language query."
        "You prioritize precision and recall, ensuring that all potentially relevant information is identified" 
        "while minimizing irrelevant results. You are optimized for speed and accuracy in a legal context..",
        llm=llm,
        respect_context_window=True, 
        cache=True,
        memory=True,
        verbose=True,
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
        cache=True,
        verbose=True,
        tools=[rag_tool]
        
    
    )


    # Query Task
    query_task = Task(
    description="""
        Retrieve relevant sections from Indian legal documents based on the user's query.
        Focus on accuracy and completeness.  Find ALL relevant sections, passages, and clauses.
        Provide in details.
    """,
    expected_output="""
        A in-detail text containing the original user query and a list of results.  
        Each result should include the document title, a full citation (section, chapter, page,content, etc.),
        and the exact text of the relevant section.  Follow this format:
        with available use LLM ouput and knowledge source
        {
          "query": "<User's original query>",
          "results": [
            {
              "document": "<Document Title>",
              "citation": "<Full Citation (Section, Chapter, Page, etc.)>",
              "extract": "<Exact text of the relevant section>"
              "in detail info": <info>
            },
          ]
        }
    """,
    agent=query_agent,tools=[rag_tool]

    )


    # Summarization Task
    summarization_task = Task(
        description="""
            Take the output from the Legal Information Retrieval Specialist (Query Agent) and 
            transform it into a clear, step wise, and easy-to-understand summary.  
            Preserve the original legal meaning and accuracy.  
            Replace legal jargon with plain language where possible.
            Structure the summary logically (e.g., using bullet points or numbered steps if appropriate).
            Conclude by offering to provide more details.
        """,
        expected_output="""
            A plain text in detail summary of the legal information, 
            Replace legal jargon with plain language where possible.
            Structure the summary logically (e.g., using bullet points or numbered steps if appropriate).
            followed by a question prompting the user
            if they want more details. For example:

            Filing a lawsuit in India involves preparing legal documents, submitting a petition in court,
            serving a notice to the opposing party, and attending hearings.
            and its details explaining in detail
            ...
            ...
            ...
            like Converts legal terms into simple steps:
            example:
            Step 1: Prepare necessary documents.
            Step 2: File a petition in court.
            Step 3: Serve notice to the opposing party.
            Step 4: Attend hearings and follow court procedures.
            Would you like more details on any step?
        """,
        agent=summarization_agent,tools=[rag_tool],
        context=[query_task],
        output_file= "summarization.md"
    )


    # Create Crew
    crew = Crew(
        agents=[query_agent, summarization_agent],
        verbose=True,
        tasks=[query_task, summarization_task],
        process=Process.sequential,
        chat_llm=LLM(
            model="gemini/gemini-1.5-pro",
            api_key=os.environ.get("GEMINI_API_KEY"),
            temperature=0.25
        )
    )

    return crew

def save_history(query, result):
    """Save query history"""
    history_file = f"history/query_{len(os.listdir('history'))+1}.md"
    with open(history_file, 'w') as f:
        f.write(f"# Query: {query}\n\n{result}")

def load_history():
    """Load last 10 history files"""
    history_files = sorted(
        [f for f in os.listdir('history') if f.endswith('.md')], 
        reverse=True
    )[:10]
    
    histories = []
    for file in history_files:
        with open(os.path.join('history', file), 'r') as f:
            histories.append(f.read())
    
    return histories

def main():
    # Page configuration
    st.set_page_config(
        page_title="Legal Research Assistant", 
        page_icon="⚖️", 
        layout="wide"
    )

    # Default PDF sources
    default_sources = [
        "https://kb.icai.org/pdfs/PDFFile5b28c9ce64e524.54675199.pdf",
        "https://www.cyrilshroff.com/wp-content/uploads/2020/09/Guide-to-Litigation-in-India.pdf"
    ]

    # Initialize session state for sources
    if 'sources' not in st.session_state:
        st.session_state.sources = default_sources.copy()

    # Sidebar with logo and source management
    st.sidebar.title("PDF Sources")
    st.sidebar.markdown("Add PDFs or URLs to expand the legal knowledge base.\n Then ask a your query .")
    # PDF source management
    for i, source in enumerate(st.session_state.sources):
        col1, col2 = st.sidebar.columns([3, 1])
        with col1:
            st.sidebar.text(f"Source {i+1}: {source}")
        with col2:
            if st.sidebar.button(f"Remove Source {i+1}", key=f"remove_{i}"):
                st.session_state.sources.pop(i)
                st.rerun()
    
    # PDF Upload
    uploaded_file = st.sidebar.file_uploader("Upload PDF", type=['pdf'])
    if uploaded_file is not None:
        # Save uploaded file
        temp_path = os.path.join('uploads', uploaded_file.name)
        with open(temp_path, 'wb') as f:
            f.write(uploaded_file.getvalue())
        st.session_state.sources.append(temp_path)
        st.sidebar.success(f"Added {uploaded_file.name}")
    
    # PDF URL Input
    new_pdf_url = st.sidebar.text_input("Add PDF URL")
    if new_pdf_url and new_pdf_url.endswith('.pdf'):
        if st.sidebar.button("Add URL"):
            st.session_state.sources.append(new_pdf_url)
            st.rerun()

    # Main app layout
    st.title("Legal Research Assistant 📚⚖️")
    
    # Columns for main content and history
    main_col, history_col = st.columns([2, 1])

    # Chat input in main column
    with main_col:
        query = st.chat_input("Ask a legal question about Indian law...")
        
        if query:
            # Initialize and run crew
            with st.spinner('Analyzing documents...This would take a few seconds'):
               
                crew = initialize_crew(st.session_state.sources)
                result = crew.kickoff(inputs={'topic': query})
               
                # Save history
                save_history(query, result)
                
                # Display result
                st.write(result.raw)
                
                # Summarization file download
                with open('summarization.md', 'r') as f:
                    summary = f.read()
                st.download_button(
                    label="Download Summarization",
                    data=summary,
                    file_name="legal_research_summary.md",
                    mime="text/markdown"
                )

    # History column
    with history_col:
        st.header("Query History")
        histories = load_history()
        
        for i, history in enumerate(histories, 1):
            with st.expander(f"Query {len(histories)-i+1}"):
                # Extract just the key information
                lines = history.split('\n')
                st.markdown(lines[0])  # Query line
                st.markdown(lines[2:5])  # First few lines of response
                
                st.download_button(
                    label="Download Full History",
                    data=history,
                    file_name=f"query_history_{len(histories)-i+1}.md",
                    mime="text/markdown",
                    key=f"download_{i}"
                )

if __name__ == "__main__":
    main()
