import streamlit as st
import pandas as pd
from pathlib import Path
import os

import sys
st.write("Python executable:", sys.executable)
try:
    import langchain
    st.write("langchain import OK, version:", getattr(langchain, "__version__", "unknown"))
except Exception as e:
    st.write("langchain import error:", str(e))
	
# Optional: LangChain imports will be used when initializing the agent
ChatOpenAI = None
create_pandas_dataframe_agent = None

try:
	# Try newer LangChain structure first (1.0+)
	from langchain_openai import ChatOpenAI
	from langchain.agents import create_pandas_dataframe_agent
except ImportError:
	try:
		# ChatOpenAI is in langchain_openai, but agent might be elsewhere
		from langchain_openai import ChatOpenAI
		from langchain_experimental.agents import create_pandas_dataframe_agent
	except ImportError:
		try:
			# Fall back to older structure
			from langchain.chat_models import ChatOpenAI
			from langchain.agents import create_pandas_dataframe_agent
		except ImportError as e:
			st.write(f"Import warning (will show in UI): {e}")

st.title("My First App")
st.write("Hello world!")

# Get OpenAI API key from environment or sidebar input (password)
api_key = st.sidebar.text_input("OpenAI API Key", type="password", value=os.environ.get("OPENAI_API_KEY", ""))
if api_key:
	st.sidebar.success("API key set")
	st.session_state["OPENAI_API_KEY"] = api_key
else:
	st.sidebar.info("No API key provided — set OPENAI_API_KEY env var or enter it here.")

# Default directory (change if needed)
default_path = r"C:\Users\sures\OneDrive\Desktop\Suresh\Profesional\ik\assignments\week0"

st.write("Choose a CSV file or folder to load — enter a path or upload files.")
data_path = st.text_input("CSV file path or folder", value=default_path)
uploaded = st.file_uploader("Or upload CSV(s)", type="csv", accept_multiple_files=True)

# Load dataframes from uploads or from path (file or folder)
dataframes = []
loaded_names = []
combined = None

if uploaded is not None and len(uploaded) > 0:
	for f in uploaded:
		try:
			df = pd.read_csv(f)
			dataframes.append(df)
			loaded_names.append(f.name)
			st.write(f"SUCCESS: Loaded '{f.name}' ({len(df)} rows)")
		except Exception as e:
			st.error(f"Failed to read uploaded file {f.name}: {e}")
elif data_path:
	p = Path(data_path)
	if p.exists():
		if p.is_dir():
			csv_files = sorted(p.glob("*.csv"))
			if not csv_files:
				st.error(f"No CSV files found in folder: {p}")
			else:
				try:
					for f in csv_files:
						df = pd.read_csv(f)
						dataframes.append(df)
						loaded_names.append(f.name)
						st.write(f"SUCCESS: Loaded '{f.name}' ({len(df)} rows)")
				except Exception as e:
					st.error(f"Failed to read files in {p}: {e}")
		elif p.is_file():
			try:
				df = pd.read_csv(p)
				dataframes.append(df)
				loaded_names.append(p.name)
				st.write(f"SUCCESS: Loaded '{p.name}' ({len(df)} rows)")
			except Exception as e:
				st.error(f"Failed to read file {p}: {e}")
	else:
		st.error(f"File or folder not found: {p}")

if dataframes:
	# add source column and concatenate
	frames = []
	for name, df in zip(loaded_names, dataframes):
		tmp = df.copy()
		tmp["__source_file__"] = name
		frames.append(tmp)
	try:
		combined = pd.concat(frames, ignore_index=True, sort=False)
	except Exception as e:
		st.error(f"Failed to concatenate dataframes: {e}")

	# UI: choose combined or individual file
	view_options = ["Combined"] + loaded_names
	choice = st.selectbox("View data", view_options)
	if choice == "Combined":
		st.write(f"Combined dataframe ({len(frames)} files)")
		st.dataframe(combined)
		st.line_chart(combined.select_dtypes(include=["number"]))
	else:
		st.write(choice)
		idx = loaded_names.index(choice)
		st.dataframe(dataframes[idx])
		st.line_chart(dataframes[idx].select_dtypes(include=["number"]))

# -----------------------------
# 3. DEFINE THE RULES + AGENT
# -----------------------------
system_prompt = """
You are a smart data assistant capable of reading multiple CSV files.
- You have access to 4 different datasets: SaaS Docs, Credit Card Terms, Hospital Policy, and Ecommerce FAQs.
- When asked a question, determine which DataFrame is most relevant.
- Do NOT answer from general knowledge.
- Answer in plain English.
"""

agent = None
if dataframes:
	# make sure OPENAI_API_KEY is available to the LLM
	if api_key:
		os.environ.setdefault("OPENAI_API_KEY", api_key)

	# Show whether API key is present (masked)
	key = os.environ.get("OPENAI_API_KEY")
	if key:
		masked = key[:4] + "..." + key[-4:] if len(key) > 8 else "(set)"
		st.write("✓ OPENAI_API_KEY configured (masked):", masked)
	else:
		st.warning("OPENAI_API_KEY not set. Set it in the sidebar or as an env var before initializing the agent.")

	if ChatOpenAI is None or create_pandas_dataframe_agent is None:
		st.error(f"LangChain imports failed: ChatOpenAI={ChatOpenAI}, create_pandas_dataframe_agent={create_pandas_dataframe_agent}")
	else:
		try:
			llm = ChatOpenAI(model="gpt-4o", temperature=0.0)
			agent = create_pandas_dataframe_agent(
				llm,
				dataframes,
				verbose=True,
				agent_type="openai-functions",
				allow_dangerous_code=True,
			)
			st.success("✓ AI Agent is ready! You can ask questions across ALL files.")
		except Exception as e:
			import traceback
			tb = traceback.format_exc()
			st.error(f"Error initializing agent: {e}")
			st.code(tb, language="text")
else:
	st.info("No dataframes loaded yet — load CSV files to initialize the AI agent.")

if agent is not None:
	# Initialize chat history in session state
	if "chat_history" not in st.session_state:
		st.session_state.chat_history = []  # list of (role, text)

	# Chat input
	st.subheader("Chat with the data assistant")
	user_text = st.text_input("You:")
	send = st.button("Send")

	if send and user_text:
		# support exit keywords
		if user_text.strip().lower() in ["exit", "quit", "q"]:
			st.session_state.chat_history.append(("system", "Goodbye!"))
		elif user_text.strip():
			final_query = system_prompt + "\n\nQuestion: " + user_text
			st.session_state.chat_history.append(("user", user_text))
			try:
					# prefer `invoke` if available, otherwise fall back to `run`
					if hasattr(agent, "invoke"):
						res = agent.invoke(final_query)
						# res may be dict-like or have attribute 'output'
						if isinstance(res, dict) and "output" in res:
							response = res["output"]
						elif hasattr(res, "output"):
							response = getattr(res, "output")
						else:
							response = str(res)
					elif hasattr(agent, "run"):
						response = agent.run(final_query)
					else:
						response = "Agent does not support invoke/run API."
			except Exception as e:
				import traceback
				tb = traceback.format_exc()
				response = f"Agent error: {e}\n\nTrace:\n{tb}"

			st.session_state.chat_history.append(("ai", response))
		
		# Force re-run to show the updated chat and clear input
		st.rerun()

	# Render chat history
	for role, text in st.session_state.chat_history:
		if role == "user":
			st.markdown(f"**You:** {text}")
		elif role == "ai":
			st.markdown(f"**AI:** {text}")
		else:
			st.info(text)


