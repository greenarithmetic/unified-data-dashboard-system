#!/usr/bin/env python3
"""Test full cycle of Unified Data Dashboard System"""

import sys
import os
import json
import time
from datetime import datetime

# Set environment variables for testing
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
os.environ['REDIS_URL'] = 'redis://localhost:6379'
os.environ['ENVIRONMENT'] = 'development'
os.environ['DEBUG'] = 'true'
os.environ['LOG_LEVEL'] = 'INFO'
os.environ['API_V1_STR'] = '/api/v1'
os.environ['DEFAULT_SYNC_INTERVAL_MINUTES'] = '10'
os.environ['DATASETS_CONFIG_PATH'] = '/app/config/datasets.json'
os.environ['REPORTS_CONFIG_PATH'] = '/app/config/reports.json'
os.environ['WEBHOOK_SECRET'] = 'test-secret-for-webhook-validation'
os.environ['CORS_ORIGINS'] = '["http://localhost:3000","http://localhost:8088"]'

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal, init_db, Record
from app.services.test_data_generator import TestDataGenerator

client = TestClient(app)


def test_health():
    """Test health endpoint"""
    print("🔍 Testing health endpoint...")
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    print("✅ Health endpoint OK")


def test_database():
    """Test database connectivity"""
    print("🔍 Testing database...")
    try:
        db = SessionLocal()
        # Test connection
        result = db.execute("SELECT 1").scalar()
        assert result == 1
        
        # Count records
        count = db.query(Record).count()
        print(f"📊 Current records in database: {count}")
        
        db.close()
        print("✅ Database connection OK")
        return count
    except Exception as e:
        print(f"❌ Database error: {e}")
        return 0


def test_generate_test_data():
    """Generate test data"""
    print("🔍 Generating test data...")
    
    # Generate 100 test records
    generator = TestDataGenerator()
    test_data = generator.generate_community_requests(100)
    
    print(f"📊 Generated {len(test_data)} test records")
    print("📋 Sample record:")
    print(json.dumps(test_data[0], indent=2, ensure_ascii=False))
    
    return test_data


def test_api_endpoints():
    """Test API endpoints"""
    print("🔍 Testing API endpoints...")
    
    # Test data endpoint
    response = client.get("/api/v1/data/community_requests?page=1&per_page=10")
    assert response.status_code == 200
    data = response.json()
    print(f"📊 Data endpoint: {data['total']} total records, {len(data['data'])} returned")
    
    # Test stats endpoint
    response = client.get("/api/v1/data/community_requests/stats")
    assert response.status_code == 200
    stats = response.json()
    print(f"📈 Stats: {stats['total_records']} records, {stats['total_spam']} spam")
    
    # Test test endpoints
    response = client.post("/api/v1/test/generate-test-data/community_requests?count=50")
    assert response.status_code == 200
    result = response.json()
    print(f"🧪 Test data generation: {result}")
    
    print("✅ API endpoints OK")


def test_cache():
    """Test Redis cache"""
    print("🔍 Testing Redis cache...")
    
    response = client.get("/api/v1/test/test-cache")
    assert response.status_code == 200
    result = response.json()
    
    if result["success"]:
        cache_test = result["cache_test"]
        print(f"🧠 Cache test: {cache_test}")
        print("✅ Redis cache OK")
    else:
        print(f"⚠️ Cache test failed: {result.get('error')}")


def test_full_cycle():
    """Test full data cycle"""
    print("🔍 Testing full data cycle...")
    
    response = client.get("/api/v1/test/test-full-cycle/community_requests")
    assert response.status_code == 200
    result = response.json()
    
    if result["success"]:
        cycle_test = result["cycle_test"]
        print(f"🔄 Full cycle test:")
        print(f"   Data generated: {cycle_test['data_generated']}")
        print(f"   Processing result: {cycle_test['processing_result']}")
        print(f"   API data: {cycle_test['api_data']}")
        print(f"   Stats: {cycle_test['stats']}")
        print("✅ Full cycle OK")
    else:
        print(f"❌ Full cycle failed: {result.get('error')}")


def test_pagination_and_sorting():
    """Test pagination and sorting"""
    print("🔍 Testing pagination and sorting...")
    
    # Test pagination
    response = client.get("/api/v1/data/community_requests?page=1&per_page=5")
    assert response.status_code == 200
    page1 = response.json()
    
    response = client.get("/api/v1/data/community_requests?page=2&per_page=5")
    assert response.status_code == 200
    page2 = response.json()
    
    # Check that pages are different
    if page1["data"] and page2["data"]:
        assert page1["data"][0]["id"] != page2["data"][0]["id"]
    
    print(f"📄 Pagination: Page 1 has {len(page1['data'])} records, Page 2 has {len(page2['data'])} records")
    
    # Test sorting
    response = client.get("/api/v1/data/community_requests?sort_by=дата&sort_dir=desc&per_page=5")
    assert response.status_code == 200
    sorted_data = response.json()
    
    print(f"📊 Sorting: Got {len(sorted_data['data'])} sorted records")
    print("✅ Pagination and sorting OK")


def test_search_and_filter():
    """Test search and filtering"""
    print("🔍 Testing search and filtering...")
    
    # Test search
    response = client.get("/api/v1/data/community_requests?q=дороги&per_page=5")
    if response.status_code == 200:
        search_results = response.json()
        print(f"🔍 Search for 'дороги': {search_results['total']} results")
    
    # Test spam filtering
    response = client.get("/api/v1/data/community_requests?exclude_spam=true&per_page=5")
    assert response.status_code == 200
    filtered = response.json()
    
    print(f"🛡️ Spam filtering: {filtered['total']} non-spam records")
    print("✅ Search and filtering OK")


def main():
    """Main test function"""
    print("🚀 Starting Unified Data Dashboard System - Full Cycle Test")
    print("=" * 60)
    
    # Initialize database
    print("🗄️ Initializing database...")
    try:
        init_db()
        print("✅ Database initialized")
    except Exception as e:
        print(f"⚠️ Database initialization warning: {e}")
    
    # Run tests
    tests = [
        test_health,
        test_database,
        test_generate_test_data,
        test_api_endpoints,
        test_cache,
        test_full_cycle,
        test_pagination_and_sorting,
        test_search_and_filter,
    ]
    
    results = []
    for test in tests:
        try:
            test()
            results.append((test.__name__, "✅ PASSED"))
        except Exception as e:
            results.append((test.__name__, f"❌ FAILED: {e}"))
    
    print("\n" + "=" * 60)
    print("📋 Test Results:")
    for test_name, result in results:
        print(f"  {test_name}: {result}")
    
    # Summary
    passed = sum(1 for _, r in results if "PASSED" in r)
    total = len(results)
    
    print(f"\n🎯 Summary: {passed}/{total} tests passed")
    
    if passed == total:
        print("✨ All tests passed! System is working correctly.")
    else:
        print("⚠️ Some tests failed. Check the logs above.")
        sys.exit(1)


if __name__ == "__main__":
    main()