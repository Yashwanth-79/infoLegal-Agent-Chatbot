prompt_template = """
Input from Query Agent (JSON):

{query_agent_output}

Instructions:

1.  **Analyze:** Read the user's original query and the extracted legal text provided by the Query Agent.
2.  **Identify Key Information:** Determine the most important points, procedures, definitions, or arguments within the extracted text that are relevant to the user's query.
3.  **Simplify:** Translate any legal jargon or complex phrasing into plain, easy-to-understand language.  Replace technical terms with simpler equivalents where possible, *without losing accuracy*.
4.  **Summarize:** Condense the information into a concise summary. Focus on providing a clear and direct answer to the user's query.
5.  **Structure:** If appropriate, organize the summary into a logical structure, such as a numbered list of steps, bullet points, or a short paragraph.
6.  **Maintain Context:** Ensure the summary retains the original context and meaning of the legal text. Do not introduce any interpretations or opinions.
7. **Offer follow up:** Always end by offering more information.
8.  **Format:** Use the output format specified below.
"""
response_template = """
{summary}

{further_details_prompt}
"""