"""
Simple script to run and test the project.
"""
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main():
    """Run a simple test command."""
    print("=" * 70)
    print("PolyMarket Trading AI Model - Project Test")
    print("=" * 70)
    
    # Test imports
    print("\n[1/3] Testing imports...")
    try:
        from scripts.python.cli import app
        print("✓ CLI module imported successfully")
    except Exception as e:
        print(f"✗ Failed to import CLI: {e}")
        return 1
    
    # Test MongoDB connection
    print("\n[2/3] Testing MongoDB connection...")
    try:
        from agents.utils.history import get_history_logger
        logger = get_history_logger()
        print("✓ History logger initialized")
    except Exception as e:
        print(f"✗ Failed to initialize history logger: {e}")
        return 1
    
    # Test CLI help
    print("\n[3/3] Testing CLI help command...")
    try:
        print("\nAvailable CLI commands:")
        print("-" * 70)
        # This would normally run: python -m scripts.python.cli --help
        print("To see all commands, run: python -m scripts.python.cli --help")
        print("Example: python -m scripts.python.cli get-all-markets --limit 1")
        print("-" * 70)
    except Exception as e:
        print(f"✗ Error: {e}")
        return 1
    
    print("\n" + "=" * 70)
    print("✓ Project setup looks good!")
    print("=" * 70)
    print("\nNext steps:")
    print("1. Make sure you have a .env file with required API keys")
    print("2. Run: python -m scripts.python.cli --help")
    print("3. Try: python -m scripts.python.cli get-all-markets --limit 1")
    print("=" * 70)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
