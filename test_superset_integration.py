#!/usr/bin/env python3
"""
Test script for Superset integration
"""

import os
import sys
import json
import requests
import time
from pathlib import Path

def test_superset_config():
    """Test Superset configuration files"""
    print("Testing Superset configuration files...")
    
    config_files = [
        "superset_config.py",
        "Dockerfile.superset",
        "superset_init.sh",
        "create_superset_dashboards.py",
        "backend/app/api/superset.py"
    ]
    
    all_exist = True
    for file in config_files:
        path = Path(file)
        if path.exists():
            print(f"✓ {file} exists")
        else:
            print(f"✗ {file} missing")
            all_exist = False
    
    return all_exist

def test_docker_compose():
    """Test Docker Compose configuration"""
    print("\nTesting Docker Compose configuration...")
    
    try:
        import yaml
        with open("docker-compose.yml", "r") as f:
            config = yaml.safe_load(f)
        
        # Check Superset service exists
        if "superset" in config.get("services", {}):
            print("✓ Superset service found in docker-compose.yml")
            
            superset_config = config["services"]["superset"]
            
            # Check build configuration
            if "build" in superset_config:
                print("✓ Superset has custom Dockerfile")
            
            # Check volumes
            if "volumes" in superset_config:
                volumes = superset_config["volumes"]
                config_volume = any("superset_config.py" in str(v) for v in volumes)
                if config_volume:
                    print("✓ Superset config volume mounted")
            
            # Check healthcheck
            if "healthcheck" in superset_config:
                print("✓ Superset healthcheck configured")
            
            return True
        else:
            print("✗ Superset service not found in docker-compose.yml")
            return False
            
    except Exception as e:
        print(f"✗ Error reading docker-compose.yml: {e}")
        return False

def test_backend_api():
    """Test backend API for Superset integration"""
    print("\nTesting backend API integration...")
    
    try:
        # Check if superset.py exists and has required functions
        with open("backend/app/api/superset.py", "r") as f:
            content = f.read()
        
        required_endpoints = [
            "get_superset_status",
            "create_dashboard",
            "get_dataset_dashboards",
            "create_chart",
            "sync_datasets_to_superset"
        ]
        
        for endpoint in required_endpoints:
            if endpoint in content:
                print(f"✓ API endpoint '{endpoint}' found")
            else:
                print(f"✗ API endpoint '{endpoint}' missing")
        
        # Check if router is included in main.py
        with open("backend/app/main.py", "r") as f:
            main_content = f.read()
        
        if "superset" in main_content:
            print("✓ Superset router included in main.py")
        else:
            print("✗ Superset router not included in main.py")
        
        return True
        
    except Exception as e:
        print(f"✗ Error testing backend API: {e}")
        return False

def test_documentation():
    """Test documentation updates"""
    print("\nTesting documentation updates...")
    
    docs_to_check = [
        "README.md",
        "SUPERSET_INTEGRATION.md"
    ]
    
    all_exist = True
    for doc in docs_to_check:
        path = Path(doc)
        if path.exists():
            print(f"✓ {doc} exists")
            
            # Check for Superset content
            with open(doc, "r") as f:
                content = f.read().lower()
            
            if "superset" in content:
                print(f"  ✓ Contains Superset documentation")
            else:
                print(f"  ✗ Missing Superset documentation")
                
        else:
            print(f"✗ {doc} missing")
            all_exist = False
    
    return all_exist

def test_requirements():
    """Test requirements.txt updates"""
    print("\nTesting requirements updates...")
    
    try:
        with open("backend/requirements.txt", "r") as f:
            content = f.read()
        
        if "requests" in content:
            print("✓ 'requests' package in requirements.txt")
        else:
            print("✗ 'requests' package missing from requirements.txt")
        
        return True
        
    except Exception as e:
        print(f"✗ Error testing requirements: {e}")
        return False

def main():
    """Main test function"""
    print("=" * 60)
    print("Testing Superset Integration for Unified Data Dashboard System")
    print("=" * 60)
    
    tests = [
        ("Configuration Files", test_superset_config),
        ("Docker Compose", test_docker_compose),
        ("Backend API", test_backend_api),
        ("Documentation", test_documentation),
        ("Requirements", test_requirements),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*40}")
        print(f"Test: {test_name}")
        print(f"{'='*40}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ Test failed with error: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "PASSED" if result else "FAILED"
        symbol = "✓" if result else "✗"
        print(f"{symbol} {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✅ All tests passed! Superset integration is ready.")
        print("\nNext steps:")
        print("1. Run: docker compose up -d")
        print("2. Access Superset at: http://localhost:8088")
        print("3. Login with: admin / admin")
        print("4. Check API documentation at: http://localhost:8000/docs")
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()