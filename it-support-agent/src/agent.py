"""
PART 2: Agent Schema & Setup
Defines the tool schemas for OpenAI function-calling, the system prompt,
and the agent execution loop.
"""

import os
import json
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

from tools import AVAILABLE_FUNCTIONS

# Load .env file from the project root (agentic-ai-examples/)
load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env")

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Model configuration
MODEL = "gpt-4o-mini"

# System prompt — defines the agent's role and decision rules
SYSTEM_PROMPT = (
    "You are a Level 1 IT Responder. Investigate server issues. "
    "If CPU or Memory is > 90%, restart the service. "
    "If logs show critical dependency errors (like connection refused) "
    "that a restart won't fix, escalate to an engineer."
)

# Tool schemas — tells the LLM what functions are available and their parameters
TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "get_server_health",
            "description": "Checks the current CPU and memory usage of a specific server.",
            "parameters": {
                "type": "object",
                "properties": {
                    "server_id": {"type": "string", "description": "The ID of the server, e.g., 'payment-server-01'"}
                },
                "required": ["server_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "fetch_recent_logs",
            "description": "Retrieves the most recent log entries from a server to diagnose errors.",
            "parameters": {
                "type": "object",
                "properties": {
                    "server_id": {"type": "string", "description": "The ID of the server."},
                    "lines": {"type": "integer", "description": "Number of log lines to fetch."}
                },
                "required": ["server_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "restart_service",
            "description": "Restarts a server service to recover from high CPU or memory issues.",
            "parameters": {
                "type": "object",
                "properties": {
                    "server_id": {"type": "string", "description": "The ID of the server to restart."}
                },
                "required": ["server_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "escalate_to_engineer",
            "description": "Escalates the issue to a human engineer when automated fixes fail or the error is unknown.",
            "parameters": {
                "type": "object",
                "properties": {
                    "summary": {"type": "string", "description": "A summary of the issue to include in the escalation ticket."}
                },
                "required": ["summary"]
            }
        }
    }
]


def run_it_agent(user_issue: str):
    """
    The agent execution loop.
    1. Sends the user issue to the LLM with available tools.
    2. If the LLM calls a tool, executes it and feeds the result back.
    3. Repeats until the LLM gives a final text response.
    """
    print(f"\n--- New Incident: {user_issue} ---")

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_issue}
    ]

    while True:
        print("\n[AI Thinking...]")
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=TOOLS_SCHEMA,
            tool_choice="auto"
        )

        response_msg = response.choices[0].message
        messages.append(response_msg)

        if response_msg.tool_calls:
            for tool_call in response_msg.tool_calls:
                func_name = tool_call.function.name
                func_args = json.loads(tool_call.function.arguments)

                # Look up and execute the function
                function_to_call = AVAILABLE_FUNCTIONS.get(func_name)

                if function_to_call:
                    tool_output = function_to_call(**func_args)

                    # Send the tool result back to the LLM
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": func_name,
                        "content": tool_output
                    })
        else:
            # No tool calls — the LLM has a final answer
            print(f"\n[FINAL RESPONSE]: {response_msg.content}")
            break
