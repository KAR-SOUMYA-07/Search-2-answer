Expert Analyst Assistant

An interactive Streamlit app that combines LangSearch Web Search with Together AI models to deliver concise, structured expert analysis.

🚀 Features

🌐 Web Search powered by [LangSearch API]

🤖 AI Analysis using Together AI’s DeepSeek-R1-Distill-Llama-70B

📊 Structured Output (Verdict, Explanation, References, Why Consider This)

🖥️ Simple UI built with Streamlit

Setup:

1.Clone this repo

2.Install dependencies

pip install -r requirements.txt

3.Set environment variables (Just replace keys in  .env file):

TOGETHER_API_KEY=your_together_api_key
LANGSEARCH_API_KEY=your_langsearch_api_key

4.Run the app

streamlit run app.py

🧩 Requirements

Python 3.9+

API Keys for: Together AI , LangSearch

📌 Example Workflow:

-Enter your question in the text box

--The app performs a web search

---AI agent analyzes and synthesizes results

----You get a structured, easy-to-read response

