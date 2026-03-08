"""
PART 3: Main Entry Point
Sets up the agent and runs it against sample IT support incidents.
This is the script you run to see the agent in action.
"""

from agent import run_it_agent


def main():
    print("=" * 60)
    print("  IT Support Agent — Autonomous Incident Handler")
    print("=" * 60)

    # Scenario A: High CPU (98%) → should trigger restart
    run_it_agent("The payment-server-01 is extremely slow and timing out.")

    # Scenario B: Healthy server → should report no issues
    run_it_agent("Something is wrong with db-node-02")

    # Scenario C: High Memory (95%) + OutOfMemoryError → should restart
    run_it_agent("Users are reporting login failures on auth-service-03.")

    print("\n" + "=" * 50 + "\n")

    # Scenario D: Dependency failure (Connection Refused) → should escalate
    run_it_agent("Search isn't working. Can you check search-index-09?")

    print("\n" + "=" * 50 + "\n")

    # Scenario E: Completely healthy → should report all OK
    run_it_agent("Check frontend-node-04 just to be safe.")


if __name__ == "__main__":
    main()
