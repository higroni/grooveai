"""
Main entry point for Assertion Classifier module.
Runs FastAPI server on port 8109.
"""

import sys
import os
import uvicorn

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# Set console encoding to UTF-8 for Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')


def main():
    """Run the FastAPI server."""
    print("=" * 80)
    print("Starting Assertion Classifier Module")
    print("=" * 80)
    print(f"Port: 8109")
    print(f"API Docs: http://localhost:8109/docs")
    print(f"Health Check: http://localhost:8109/health")
    print("=" * 80)
    
    uvicorn.run(
        "modules.assertion_classifier.api:app",
        host="0.0.0.0",
        port=8109,
        reload=False,
        log_level="info"
    )


if __name__ == "__main__":
    main()

# Made with Bob
