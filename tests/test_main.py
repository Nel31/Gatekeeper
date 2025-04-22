import pytest
import subprocess
import sys

def test_main_no_errors(tmp_path):
    # Ensure main.py runs with help option
    cmd = [sys.executable, "scripts/main.py", "--help"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    assert result.returncode == 0
    assert "usage" in result.stdout.lower()
