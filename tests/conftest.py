"""
pytest configuration for test suite
"""
import sys
import os

# Add the repository root to the path so we can import modules
repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

# Add scripts directory to path for test imports
scripts_dir = os.path.join(repo_root, 'scripts')
if scripts_dir not in sys.path:
    sys.path.insert(0, scripts_dir)
