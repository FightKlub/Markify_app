#!/usr/bin/env python3
import sys
print("Testing imports...")

try:
    from app import app
    print("SUCCESS: App imported")
    print(f"App name: {app.name}")
except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1)

print("All tests passed!")
