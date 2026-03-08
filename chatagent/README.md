# CSV Data Chat Assistant — webapp.py

A Streamlit web app that lets you chat with your CSV data using an AI agent powered by OpenAI GPT-4o and LangChain.

## Features

- Load CSV files via **file upload** or **local folder path**
- View data as individual files or a combined DataFrame
- Auto-generated **line charts** for numeric columns
- **Conversational AI** — ask natural language questions about your data
- Persistent **chat history** across interactions

## Requirements

```
streamlit
pandas
langchain
langchain-openai
langchain-experimental
tabulate
openai
```

Install all dependencies:

```bash
pip install streamlit pandas langchain langchain-openai langchain-experimental tabulate openai
```

## How to Run

```bash
streamlit run webapp.py
```

Then open http://localhost:8501 in your browser.

## OpenAI API Key

Provide your key in one of two ways:

1. **Environment variable:** `set OPENAI_API_KEY=sk-...` (before running)
2. **Sidebar input:** Enter it in the password field in the app's sidebar

## Code Structure

| Module | Lines | Purpose |
|--------|-------|---------|
| **1. Imports & Diagnostics** | 1–33 | Import libraries, test LangChain with version fallbacks |
| **2. API Key Config** | 38–45 | Sidebar input for OpenAI key, or read from env var |
| **3. CSV Loading** | 47–98 | Upload files or load from a folder/file path on disk |
| **4. Data Display** | 100–119 | Combine DataFrames, show tables and line charts |
| **5. Agent Init** | 124–161 | Create LangChain pandas agent with GPT-4o |
| **6. Chat Interface** | 163–218 | Text input, send button, chat history rendering |

## App Flow

```
User loads CSVs → Data displayed in table/chart
                → LangChain agent initialized with all DataFrames
                → User asks questions in chat
                → Agent runs Pandas code internally to answer
                → Response displayed in chat history
```

## Notes

- The agent uses `allow_dangerous_code=True` to execute Python/Pandas code on the loaded data.
- `temperature=0.0` ensures deterministic, consistent answers.
- The system prompt instructs the AI to answer **only from the loaded data**, not from general knowledge.
