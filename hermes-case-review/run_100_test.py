#!/usr/bin/env python3
"""
100 Test Runner - Simple Execution
Runs the standalone load test directly
"""
import sys
import os

# Add the correct path
sys.path.insert(0, os.path.abspath('/workspace/hermes-case-review/deployment/production/load_test'))

# Import and run
try:
    import subprocess
    result = subprocess.run([
        sys.executable, 
        '/workspace/hermes-case-review/deployment/production/load_test/100_test_standalone.py'
    ], capture_output=False, text=True)
    
    if result.returncode == 0:
        print("\n✅ Test completed successfully!")
    else:
        print(f"\n❌ Test failed with return code: {result.returncode}")
        
except Exception as e:
    print(f"\n❌ Error executing test: {e}")
    import traceback
    traceback.print_exc()
