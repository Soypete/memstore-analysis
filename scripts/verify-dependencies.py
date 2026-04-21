#!/usr/bin/env python3
"""Verify all dependencies are installed and accessible."""

import sys
from pathlib import Path

def check_python_package(name, import_name=None):
    """Check if a Python package is installed."""
    import_name = import_name or name
    try:
        __import__(import_name)
        return True, "OK"
    except ImportError as e:
        return False, str(e)

def check_command(cmd):
    """Check if a command is available."""
    import shutil
    if shutil.which(cmd):
        return True, "OK"
    return False, "not found"

def check_url(url):
    """Check if a URL is accessible."""
    import urllib.request
    try:
        urllib.request.urlopen(url, timeout=5)
        return True, "OK"
    except Exception as e:
        return False, str(e)

def main():
    print("=" * 60)
    print("Dependency Verification")
    print("=" * 60)

    results = []

    # Core Python packages
    print("\n[Python Packages]")
    for pkg, import_name in [
        ("openai", "openai"),
        ("pyyaml", "yaml"),
        ("pandas", "pandas"),
        ("chromadb", "chromadb"),
        ("graphifyy", "graphify"),
    ]:
        ok, msg = check_python_package(pkg, import_name)
        status = "✅" if ok else "❌"
        print(f"  {status} {pkg}: {msg}")
        results.append(ok)

    # Commands
    print("\n[Commands]")
    for cmd in ["graphify", "mempalace"]:
        ok, msg = check_command(cmd)
        status = "✅" if ok else "❌"
        print(f"  {status} {cmd}: {msg}")
        results.append(ok)

    # Model gateway
    print("\n[Model Gateway]")
    # Don't fail on connection errors, just warn
    try:
        import urllib.request
        req = urllib.request.Request("http://pedrogpt:8080/v1/models")
        urllib.request.urlopen(req, timeout=5)
        print("  ⚠️  pedrogpt:8080: OK (connected)")
    except Exception as e:
        print(f"  ⚠️  pedrogpt:8080: not accessible ({e})")
        print("       (This is OK if running locally)")

    # Check local mempalace fork
    print("\n[Local Forks]")
    mempalace_path = Path(__file__).parent.parent.parent / "mempalace"
    if mempalace_path.exists():
        print(f"  ✅ mempalace fork: {mempalace_path}")
    else:
        print(f"  ⚠️  mempalace fork: not found at {mempalace_path}")

    # Check adapter files
    print("\n[Adapters]")
    base = Path(__file__).parent.parent
    for adapter in ["llmwiki", "graphify", "mempalace"]:
        path = base / "systems" / adapter / "adapter.py"
        if path.exists():
            print(f"  ✅ {adapter}/adapter.py")
        else:
            print(f"  ❌ {adapter}/adapter.py: missing")
            results.append(False)

    # Summary
    print("\n" + "=" * 60)
    if all(results):
        print("✅ All checks passed!")
        return 0
    else:
        print("❌ Some checks failed. See DEPLOYMENT.md for setup.")
        return 1

if __name__ == "__main__":
    sys.exit(main())