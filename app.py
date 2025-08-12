import requests
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts.chat import ChatPromptTemplate
from langchain.tools import tool, Tool
from langchain_together import ChatTogether
import streamlit as st
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
LANGSEARCH_API_KEY = os.getenv("LANGSEARCH_API_KEY")

# LangSearch Tool
def langsearch_websearch_tool(query: str, count: int = 5) -> str:
    url = "https://api.langsearch.com/v1/web-search"
    headers = {
        "Authorization": f"Bearer {LANGSEARCH_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "query": query,
        "freshness": "noLimit",
        "summary": True,
        "count": count
    }

    response = requests.post(url, headers=headers, json=data)
    if response.status_code != 200:
        return f"Search failed: {response.status_code}, {response.text}"

    try:
        json_response = response.json()
        webpages = json_response["data"]["webPages"]["value"]
        if not webpages:
            return "No relevant results found."
        
        formatted = ""
        for i, page in enumerate(webpages[:3], start=1):  # Limit to 3 results
            # Truncate summary to max 100 characters for conciseness
            summary = page['summary'][:100] + "..." if len(page['summary']) > 100 else page['summary']
            formatted += (
                f"\n--- Result {i} ---\n"
                f"Title: {page['name'][:80]}...\n"  # Truncate long titles
                f"Summary: {summary}\n"
            )
        return formatted.strip()
    except Exception as e:
        return f"Failed to parse LangSearch response: {str(e)}"

# Tool Registration
tools = [
    Tool(
        name="LangSearchWebSearch",
        func=langsearch_websearch_tool,
        description="Useful for searching the internet. Input should be a search query string."
    )
]

# Together AI model
llm = ChatTogether(
    model="deepseek-ai/DeepSeek-R1-Distill-Llama-70B-free",
    together_api_key=TOGETHER_API_KEY,
    temperature=0.7
)

# Prompt Template
prompt = ChatPromptTemplate.from_messages([
    ("system", """You're an expert analyst. Respond ONLY in this exact format. Do NOT show any thinking process, reasoning steps, or <think> tags.

**Verdict:**
[4 lines - clear conclusion]

**Explanation:**
[4-5 lines - brief reasoning]

**References:**
[Maximum 1-2 lines - sources/citations]

**Why consider this:**
[2 lines - practical advice]

STRICT RULES:
- Give  internal reasoning or thinking process but precise and question-context matched(use simple words for understanding of layman)
- NO <think> tags or verbose explanations
- ONLY the 4 sections above
- Be direct and concise
- Start immediately with **Verdict:**"""),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])

# Agent
agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# Streamlit App
st.set_page_config(page_title="Expert Analyst Assistant")
st.title("Expert Analyst Assistant")

st.write("""Welcome! This tool synthesizes information from documents and web research. Provide a question, and receive well-reasoned opinions.
    """)

user_question = st.text_area("Enter your question:", "")

if st.button("Submit") and user_question:
    with st.spinner("Searching and analyzing..."):
        # Show search process
        st.subheader("🔍 Search Process:")
        
        # First, show what we're searching for
        st.write(f"**Query:** {user_question}")
        
        # Perform web search first to show results
        search_results = langsearch_websearch_tool(user_question)
        
        # Display search results
        st.subheader("📊 Web Search Results:")
        with st.expander("View search results", expanded=True):
            st.text(search_results)
        
        # Now run the agent
        st.subheader("🤖 AI Analysis:")
        result = agent_executor.invoke({"input": user_question})

        # Clean up the output - remove any thinking tags
        clean_output = result["output"]
        # Remove <think> blocks completely
        import re
        clean_output = re.sub(r'<think>.*?</think>', '', clean_output, flags=re.DOTALL)
        clean_output = clean_output.strip()

        # Display final response
        st.subheader("✅ Final Response:")
        st.write(clean_output)

st.write("---")
st.caption("Made by SSK | Note: AI can make mistakes, Be careful")
