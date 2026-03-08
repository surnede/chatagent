import os
import json
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

# Load .env file from the project root (agentic-ai-examples/)
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# --- Already implement tool 1: Check Health ---
def get_server_health(server_id: str) -> str:
    """Returns CPU and Memory usage for a given server."""
    print(f"-> TOOL: Checking health for {server_id}...")

    metrics = {
        # Scenario 1: High CPU (Needs Restart)
        "payment-server-01": {"cpu": "98%", "memory": "40%", "status": "Warning"},

        # Scenario 2: Healthy (No Action Needed)
        "db-node-02": {"cpu": "12%", "memory": "60%", "status": "Healthy"},

        # Scenario 3: High Memory Leak (Needs Restart or Escalation)
        "auth-service-03": {"cpu": "45%", "memory": "95%", "status": "Critical"},

        # Scenario 4: Network/Dependency Failure (Needs Escalation)
        "search-index-09": {"cpu": "10%", "memory": "15%", "status": "Error"},

        # Scenario 5: Completely Normal
        "frontend-node-04": {"cpu": "25%", "memory": "30%", "status": "Healthy"},
    }

    result = metrics.get(server_id, {"error": "Server not found. Check the ID."})
    return json.dumps(result)

def fetch_recent_logs(server_id: str, lines: int = 5) -> str:
    """Returns the last N lines of logs."""
    print(f"-> TOOL: Fetching last {lines} log lines for {server_id}...")

    # Different logs for different servers to trigger different agent behaviors
    log_database = {
        "payment-server-01": [
            "[INFO] Request received /pay/v1",
            "[WARN] CPU threshold exceeded 90%",
            "[WARN] Thread pool exhaustion",
            "[CRITICAL] Process hung, not accepting new connections",
            "[ERROR] Timeout waiting for thread"
        ],
        "db-node-02": [
            "[INFO] Backup started",
            "[INFO] Backup completed successfully",
            "[INFO] User query executed in 12ms",
            "[INFO] Health check: OK",
            "[INFO] Replication sync active"
        ],
        "auth-service-03": [
            "[INFO] Token validated user_882",
            "[WARN] Garbage collection taking too long (>5s)",
            "[ERROR] java.lang.OutOfMemoryError: Java heap space",
            "[CRITICAL] Application crashing due to memory leak",
            "[INFO] Restarting context..."
        ],
        "search-index-09": [
            "[INFO] Indexing started",
            "[ERROR] Connection refused: elastic-cluster-main:9200",
            "[ERROR] Failed to write document ID 4432",
            "[CRITICAL] Dependency Unreachable: Search Engine is down",
            "[ERROR] Retrying in 30s..."
        ],
        "frontend-node-04": [
            "[INFO] GET /home 200 OK",
            "[INFO] GET /assets/logo.png 200 OK",
            "[INFO] GET /login 200 OK",
            "[INFO] GET /api/v1/status 200 OK",
            "[INFO] Health check passed"
        ]
    }

    # Default logs if server not found in specific list
    default_logs = ["[INFO] System stable", "[INFO] Heartbeat signal received"]

    logs = log_database.get(server_id, default_logs)
    return json.dumps({"logs": logs[:lines]})

# --- TASK 1: Implement the Restart Tool ---
def restart_service(server_id: str) -> str:
    """
    Restarts the specified server service.
    """
    print(f"-> TOOL: Restarting service on {server_id}...")
    return json.dumps({"status": "success", "message": f"Server {server_id} restarted successfully"})

# --- TASK 2: Implement the Escalation Tool ---
def escalate_to_engineer(summary: str) -> str:
    """
    Escalates the issue to a human engineer.
    """
    print(f"-> TOOL: Escalating to human engineer...")
    return json.dumps({"status": "escalated", "message": f"Ticket created for engineer. Summary: {summary}"})

# Map functions for the agent execution loop
AVAILABLE_FUNCTIONS = {
    "get_server_health": get_server_health,
    "fetch_recent_logs": fetch_recent_logs,
    "restart_service": restart_service,
    "escalate_to_engineer": escalate_to_engineer,
}

#==========================================
##PART 2: DEFINE THE AGENT SCHEMA
#==========================================

tools_schema = [
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
    # --- >>>> TASK 3: Define Schema for restart_service ---
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
    # --- >>>> TASK 4: Define Schema for escalate_to_engineer ---
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

#==========================================
#PART 3: THE AGENT EXECUTION LOOP
#==========================================

def run_it_agent(user_issue: str):
    print(f"\n--- New Incident: {user_issue} ---")

    messages = [
        {"role": "system", "content": "You are a Level 1 IT Responder. Investigate server issues. "
                                      "If CPU or Memory is > 90%, restart the service. If logs show critical dependency errors (like connection refused) that a restart won't fix, escalate to an engineer."},
        {"role": "user", "content": user_issue}
    ]

    while True:
        print("\n[AI Thinking...]")
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=tools_schema,
            tool_choice="auto"
        )

        response_msg = response.choices[0].message
        messages.append(response_msg)

        if response_msg.tool_calls:
            for tool_call in response_msg.tool_calls:
                func_name = tool_call.function.name
                func_args = json.loads(tool_call.function.arguments)

                # Retrieve the actual python function based on name
                function_to_call = AVAILABLE_FUNCTIONS.get(func_name)

                if function_to_call:
                    # Execute the function
                    tool_output = function_to_call(**func_args)

                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": func_name,
                        "content": tool_output
                    })

        else:
            print(f"\n[FINAL RESPONSE]: {response_msg.content}")
            break

#==========================================
#PART 4: TEST SCENARIOS
#==========================================

# Scenario A: Should trigger a restart (CPU is 98%)
run_it_agent("The payment-server-01 is extremely slow and timing out.")

# Scenario B: Should trigger an escalation (DB is healthy but logs might be weird)
run_it_agent("Something is wrong with db-node-02")

# Scenario C: The High Memory Case (auth-service-03)
# Agent should see Memory 95% + OutOfMemoryError logs -> Restart
run_it_agent("Users are reporting login failures on auth-service-03.")

print("\n" + "="*50 + "\n")

# Scenario D: The Dependency Failure (search-index-09)
# Agent should see healthy CPU but "Connection Refused" logs -> Escalate
run_it_agent("Search isn't working. Can you check search-index-09?")

print("\n" + "="*50 + "\n")

# Scenario E: The Healthy Server (frontend-node-04)
# Agent should see normal stats and 200 OK logs -> Do nothing / Report healthy
run_it_agent("Check frontend-node-04 just to be safe.")