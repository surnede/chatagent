"""
PART 1: Tool Functions
Contains all the business logic functions that the agent can use.
Each function is a "tool" that the agent can call.
"""

import json


# --- Tool 1: Check Server Health ---
def get_server_health(server_id: str) -> str:
    """Returns CPU and Memory usage for a given server."""
    print(f"-> TOOL: Checking health for {server_id}...")

    metrics = {
        "payment-server-01": {"cpu": "98%", "memory": "40%", "status": "Warning"},
        "db-node-02": {"cpu": "12%", "memory": "60%", "status": "Healthy"},
        "auth-service-03": {"cpu": "45%", "memory": "95%", "status": "Critical"},
        "search-index-09": {"cpu": "10%", "memory": "15%", "status": "Error"},
        "frontend-node-04": {"cpu": "25%", "memory": "30%", "status": "Healthy"},
    }

    result = metrics.get(server_id, {"error": "Server not found. Check the ID."})
    return json.dumps(result)


# --- Tool 2: Fetch Recent Logs ---
def fetch_recent_logs(server_id: str, lines: int = 5) -> str:
    """Returns the last N lines of logs."""
    print(f"-> TOOL: Fetching last {lines} log lines for {server_id}...")

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

    default_logs = ["[INFO] System stable", "[INFO] Heartbeat signal received"]
    logs = log_database.get(server_id, default_logs)
    return json.dumps({"logs": logs[:lines]})


# --- Tool 3: Restart Service ---
def restart_service(server_id: str) -> str:
    """Restarts the specified server service."""
    print(f"-> TOOL: Restarting service on {server_id}...")
    return json.dumps({"status": "success", "message": f"Server {server_id} restarted successfully"})


# --- Tool 4: Escalate to Engineer ---
def escalate_to_engineer(summary: str) -> str:
    """Escalates the issue to a human engineer."""
    print(f"-> TOOL: Escalating to human engineer...")
    return json.dumps({"status": "escalated", "message": f"Ticket created for engineer. Summary: {summary}"})


# Map of function names to actual functions (used by the agent loop)
AVAILABLE_FUNCTIONS = {
    "get_server_health": get_server_health,
    "fetch_recent_logs": fetch_recent_logs,
    "restart_service": restart_service,
    "escalate_to_engineer": escalate_to_engineer,
}
