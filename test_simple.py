"""
Simple API test without full document processing
"""

import requests
import json

def test_basic_endpoints():
    """Test basic endpoints first"""
    base_url = "http://127.0.0.1:8000"
    
    print("🔍 Testing basic endpoints...")
    
    # Test root endpoint
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        print(f"✅ Root endpoint: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"❌ Root endpoint failed: {e}")
        return False
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        print(f"✅ Health endpoint: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"❌ Health endpoint failed: {e}")
        return False
    
    return True

def test_auth():
    """Test authentication"""
    base_url = "http://127.0.0.1:8000"
    
    print("\n🔐 Testing authentication...")
    
    # Test without auth (should fail)
    try:
        response = requests.post(f"{base_url}/hackrx/run", 
                               json={"documents": "test", "questions": ["test"]}, 
                               timeout=5)
        if response.status_code == 401:
            print("✅ Authentication required (401 without token)")
        else:
            print(f"⚠️ Expected 401, got {response.status_code}")
    except Exception as e:
        print(f"❌ Auth test failed: {e}")
    
    # Test with valid auth but minimal data
    try:
        headers = {
            "Authorization": "Bearer 9fcf52ab0952ca875021a92ff7bd5557eedb4f49f016e0894610e1014498a402",
            "Content-Type": "application/json"
        }
        
        minimal_request = {
            "documents": "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf",
            "questions": ["What is this document about?"]
        }
        
        print("🔄 Testing with minimal request (10s timeout)...")
        response = requests.post(f"{base_url}/hackrx/run", 
                               headers=headers,
                               json=minimal_request, 
                               timeout=10)
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success! Got {len(result.get('answers', []))} answers")
        else:
            print(f"Response: {response.text[:200]}...")
            
    except requests.exceptions.Timeout:
        print("⏰ Request timed out - system is processing but too slow")
    except Exception as e:
        print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    if test_basic_endpoints():
        test_auth()
    else:
        print("❌ Basic endpoints failed - check if server is running")