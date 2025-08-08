"""
Test script for the LLM-Powered Query-Retrieval System
Tests the API with sample data
"""

import requests
import json
import time

# API Configuration - Matches exact requirements
BASE_URL = "http://localhost:8000"
API_KEY = "9fcf52ab0952ca875021a92ff7bd5557eedb4f49f016e0894610e1014498a402"
HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}

# Sample test data - Exact format from requirements
TEST_REQUEST = {
    "documents": "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D",
    "questions": [
        "What is the grace period for premium payment under the National Parivar Mediclaim Plus Policy?",
        "What is the waiting period for pre-existing diseases (PED) to be covered?",
        "Does this policy cover maternity expenses, and what are the conditions?",
        "What is the waiting period for cataract surgery?",
        "Are the medical expenses for an organ donor covered under this policy?",
        "What is the No Claim Discount (NCD) offered in this policy?",
        "Is there a benefit for preventive health check-ups?",
        "How does the policy define a 'Hospital'?",
        "What is the extent of coverage for AYUSH treatments?",
        "Are there any sub-limits on room rent and ICU charges for Plan A?"
    ]
}

def test_health_check():
    """Test the health check endpoint"""
    print("🔍 Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_query_processing():
    """Test the main query processing endpoint"""
    print("\n🔍 Testing query processing...")
    try:
        start_time = time.time()
        
        response = requests.post(
            f"{BASE_URL}/hackrx/run",
            headers=HEADERS,
            json=TEST_REQUEST,
            timeout=120  # 2 minute timeout
        )
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        print(f"Status: {response.status_code}")
        print(f"Processing time: {processing_time:.2f} seconds")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Number of answers: {len(result['answers'])}")
            
            # Print first few answers for verification
            for i, answer in enumerate(result['answers'][:3]):
                print(f"\nQ{i+1}: {TEST_REQUEST['questions'][i]}")
                print(f"A{i+1}: {answer[:200]}...")
            
            return True
        else:
            print(f"❌ Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Query processing failed: {e}")
        return False

def run_performance_test():
    """Run a simple performance test"""
    print("\n🚀 Running performance test...")
    
    # Test with smaller question set for speed
    small_test = {
        "documents": TEST_REQUEST["documents"],
        "questions": TEST_REQUEST["questions"][:2]
    }
    
    times = []
    for i in range(3):
        print(f"Run {i+1}/3...")
        start_time = time.time()
        
        try:
            response = requests.post(
                f"{BASE_URL}/hackrx/run",
                headers=HEADERS,
                json=small_test,
                timeout=60
            )
            
            if response.status_code == 200:
                end_time = time.time()
                times.append(end_time - start_time)
                print(f"✅ Run {i+1} completed in {times[-1]:.2f}s")
            else:
                print(f"❌ Run {i+1} failed with status {response.status_code}")
                
        except Exception as e:
            print(f"❌ Run {i+1} failed: {e}")
    
    if times:
        avg_time = sum(times) / len(times)
        print(f"\n📊 Performance Results:")
        print(f"Average time: {avg_time:.2f}s")
        print(f"Min time: {min(times):.2f}s")
        print(f"Max time: {max(times):.2f}s")

if __name__ == "__main__":
    print("🧪 Starting API Tests...")
    
    # Test health check
    if not test_health_check():
        print("❌ Health check failed. Make sure the server is running.")
        exit(1)
    
    # Test query processing
    if test_query_processing():
        print("✅ Query processing test passed!")
        
        # Run performance test
        run_performance_test()
    else:
        print("❌ Query processing test failed!")
    
    print("\n🏁 Tests completed!")