#!/usr/bin/env python3
"""
Check if the local setup is ready to run the application
"""
import sys
import subprocess
import socket
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

def check_python_version():
    """Check Python version"""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 9:
        print(f"✓ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"✗ Python {version.major}.{version.minor}.{version.micro} (requires 3.9+)")
        return False

def check_mongodb():
    """Check if MongoDB is running"""
    try:
        # Try to connect to MongoDB
        client = MongoClient('mongodb://localhost:27017', serverSelectionTimeoutMS=2000)
        client.admin.command('ping')
        print("✓ MongoDB is running on localhost:27017")
        client.close()
        return True
    except ConnectionFailure:
        print("✗ MongoDB is not running or not accessible on localhost:27017")
        print("  Install MongoDB: https://www.mongodb.com/try/download/community")
        print("  Or use Docker: docker run -d -p 27017:27017 --name mongodb mongo:7.0")
        return False
    except Exception as e:
        print(f"✗ Error checking MongoDB: {e}")
        return False

def check_port_available(port):
    """Check if a port is available"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', port))
    sock.close()
    return result != 0

def check_dependencies():
    """Check if required Python packages are installed"""
    required_packages = [
        'fastapi',
        'uvicorn',
        'motor',
        'pymongo',
        'openai',
        'telegram',
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✓ {package} is installed")
        except ImportError:
            print(f"✗ {package} is not installed")
            missing.append(package)
    
    if missing:
        print(f"\n  Install missing packages: pip3 install -r requirements.txt")
        return False
    return True

def main():
    """Run all checks"""
    print("Checking local setup...\n")
    
    checks = [
        ("Python Version", check_python_version),
        ("MongoDB", check_mongodb),
        ("Dependencies", check_dependencies),
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\n{name}:")
        results.append(check_func())
    
    print("\n" + "="*50)
    if all(results):
        print("✓ All checks passed! You're ready to run the app.")
        print("\nRun the application with:")
        print("  python3 run.py")
    else:
        print("✗ Some checks failed. Please fix the issues above.")
        sys.exit(1)

if __name__ == "__main__":
    main()

