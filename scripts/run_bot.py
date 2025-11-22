#!/usr/bin/env python3
"""Fallback Python runner for bot_run_all.sh"""
import subprocess
import sys
import json
import os
from datetime import datetime

def main():
    print("🔄 Running bot_run_all.sh via Python fallback...")
    
    script_path = os.path.join(os.path.dirname(__file__), 'bot_run_all.sh')
    
    try:
        # Make executable
        os.chmod(script_path, 0o755)
        
        # Run the script
        result = subprocess.run(
            ['bash', script_path],
            capture_output=True,
            text=True,
            cwd='/workspaces/Top-TieR-Global-HUB-AI'
        )
        
        print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        
        return result.returncode
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return 1

if __name__ == '__main__':
    sys.exit(main())
