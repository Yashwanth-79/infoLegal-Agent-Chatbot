from crewai import LLM, Agent, Crew, Process, Task
from crewai.knowledge.source.crew_docling_source import CrewDoclingSource
from templates import query_template,summarization_template
import os
import markdown
import json
from dotenv import load_dotenv

load_dotenv()

llm = LLM(model="gemini/gemini-1.5-pro",api_key=os.environ.get("GEMINI_API_KEY"))

# Create a knowledge source
content_source = CrewDoclingSource(
    file_paths=[
        "https://kb.icai.org/pdfs/PDFFile5b28c9ce64e524.54675199.pdf",
        "https://www.cyrilshroff.com/wp-content/uploads/2020/09/Guide-to-Litigation-in-India.pdf",
    ],
)

query_agent = Agent(
    role="Legal Information Retrieval Specialist - India Focus",
    goal=" Efficiently and accurately retrieve relevant sections from Indian legal documents",
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
    knowledge_sources=content_source
    
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
    knowledge_sources=content_source,
    multimodal=True
)

query_task = Task(
    description="""
        Retrieve relevant sections from Indian legal documents based on the user's query.
        The documents to search are:
        - Guide to Litigation in India
        - Legal Compliance & Corporate Laws by ICAI
        
        Focus on accuracy and completeness.  Find ALL relevant sections, passages, and clauses.
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
    output_file= "summarization.md"
)


crew = Crew(
    agents=[query_agent, summarization_agent],
    tasks=[query_task, summarization_task],
    process=Process.sequential,
    knowledge_sources=content_source,
    memory=True,
    cache=True
)
taking_input = input("Enter your query: ")
result = crew.kickoff(inputs=taking_input)
clean_result = markdown.markdown(result)
print(clean_result)