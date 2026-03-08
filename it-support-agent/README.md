# IT Support Agent

An autonomous Level 1 IT support agent powered by OpenAI GPT-4o-mini. It investigates server incidents by checking health metrics and logs, then decides whether to restart services or escalate to a human engineer.

## How It Works

```
User reports incident
  → Agent checks server health (CPU, memory)
  → Agent fetches recent logs
  → Decision:
      - CPU/Memory > 90% → Restart the service
      - Dependency failure (e.g., connection refused) → Escalate to engineer
      - Everything healthy → Report no issues
```

## Project Structure

```
it-support-agent/
├── README.md                    # This file
├── src/
│   ├── tools.py                 # PART 1: Tool functions (health, logs, restart, escalate)
│   ├── agent.py                 # PART 2: Agent schema, system prompt, execution loop
│   └── main.py                  # PART 3: Entry point — runs test scenarios
└── tests/
    └── test_scenarios.py        # PART 4: Unit tests for tool functions
```

## Setup

1. Install dependencies:

   ```bash
   pip install openai python-dotenv
   ```

2. Create a `.env` file in the `agentic-ai-examples/` root with your API key:
   ```
   OPENAI_API_KEY=sk-your-key-here
   ```

## Run

**Run the agent (all 5 scenarios):**

```bash
cd it-support-agent/src
python main.py
```

**Run unit tests:**

```bash
cd it-support-agent
python tests/test_scenarios.py
```

## Test Scenarios

| Scenario | Server            | Expected Action            |
| -------- | ----------------- | -------------------------- |
| A        | payment-server-01 | Restart (CPU 98%)          |
| B        | db-node-02        | Report healthy             |
| C        | auth-service-03   | Restart (Memory 95%)       |
| D        | search-index-09   | Escalate (dependency down) |
| E        | frontend-node-04  | Report healthy             |

## Tools

| Tool                   | Description                                       |
| ---------------------- | ------------------------------------------------- |
| `get_server_health`    | Returns CPU, memory, and status for a server      |
| `fetch_recent_logs`    | Returns the last N log lines from a server        |
| `restart_service`      | Restarts a server service                         |
| `escalate_to_engineer` | Creates an escalation ticket for a human engineer |
