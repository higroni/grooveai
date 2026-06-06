"""
Script to run all tests for File Reader module
"""
import sys
import subprocess


def main():
    """Run pytest with coverage"""
    print("=" * 80)
    print("Running File Reader Module Tests")
    print("=" * 80)
    
    # Run pytest
    result = subprocess.run(
        [
            sys.executable, "-m", "pytest",
            "modules/file_reader/tests",
            "-v",
            "--tb=short",
            "--cov=modules.file_reader",
            "--cov-report=term-missing",
            "--cov-report=html:modules/file_reader/htmlcov"
        ],
        cwd="."
    )
    
    if result.returncode == 0:
        print("\n" + "=" * 80)
        print("ALL TESTS PASSED")
        print("=" * 80)
        print("\nCoverage report generated in: modules/file_reader/htmlcov/index.html")
    else:
        print("\n" + "=" * 80)
        print("TESTS FAILED")
        print("=" * 80)
    
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())

# Made with Bob
