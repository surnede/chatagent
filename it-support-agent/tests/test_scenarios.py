"""
PART 4: Test Scenarios
Verifies that tool functions return expected results.
Run with: python -m pytest tests/test_scenarios.py -v
Or simply: python tests/test_scenarios.py
"""

import json
import sys
from pathlib import Path

# Add src/ to path so we can import tools
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from tools import (
    get_server_health,
    fetch_recent_logs,
    restart_service,
    escalate_to_engineer,
    AVAILABLE_FUNCTIONS,
)


def test_server_health_known_server():
    """Test that a known server returns valid metrics."""
    result = json.loads(get_server_health("payment-server-01"))
    assert result["cpu"] == "98%"
    assert result["memory"] == "40%"
    assert result["status"] == "Warning"
    print("✓ test_server_health_known_server passed")


def test_server_health_unknown_server():
    """Test that an unknown server returns an error."""
    result = json.loads(get_server_health("unknown-server-99"))
    assert "error" in result
    print("✓ test_server_health_unknown_server passed")


def test_fetch_logs_returns_correct_count():
    """Test that fetching logs respects the line count."""
    result = json.loads(fetch_recent_logs("db-node-02", lines=3))
    assert len(result["logs"]) == 3
    print("✓ test_fetch_logs_returns_correct_count passed")


def test_fetch_logs_default_server():
    """Test that an unknown server returns default logs."""
    result = json.loads(fetch_recent_logs("nonexistent-server"))
    assert result["logs"][0] == "[INFO] System stable"
    print("✓ test_fetch_logs_default_server passed")


def test_restart_service():
    """Test that restart returns a success status."""
    result = json.loads(restart_service("auth-service-03"))
    assert result["status"] == "success"
    assert "auth-service-03" in result["message"]
    print("✓ test_restart_service passed")


def test_escalate_to_engineer():
    """Test that escalation returns an escalated status."""
    result = json.loads(escalate_to_engineer("Search engine down"))
    assert result["status"] == "escalated"
    assert "Search engine down" in result["message"]
    print("✓ test_escalate_to_engineer passed")


def test_all_functions_registered():
    """Test that all 4 tools are in the AVAILABLE_FUNCTIONS map."""
    expected = ["get_server_health", "fetch_recent_logs", "restart_service", "escalate_to_engineer"]
    for name in expected:
        assert name in AVAILABLE_FUNCTIONS, f"Missing function: {name}"
    print("✓ test_all_functions_registered passed")


if __name__ == "__main__":
    print("\n=== Running IT Support Agent Tests ===\n")
    test_server_health_known_server()
    test_server_health_unknown_server()
    test_fetch_logs_returns_correct_count()
    test_fetch_logs_default_server()
    test_restart_service()
    test_escalate_to_engineer()
    test_all_functions_registered()
    print("\n=== All tests passed! ===")
