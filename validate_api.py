"""
Comprehensive API validation script
Tests all requirements for the hackrx submission
"""

import requests
import json
import time
import sys

def test_api_compliance(base_url="http://127.0.0.1:8000"):
    """Test API compliance with all requirements"""
    
    print("🧪 Starting API Compliance Tests...")
    print(f"Testing URL: {base_url}")
    print("=" * 50)
    
    # Test data
    api_key = "9fcf52ab0952ca875021a92ff7bd5557eedb4f49f016e0894610e1014498a402"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    test_request = {
        "documents": "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D",
        "questions": [
            "What is the grace period for premium payment under the National Parivar Mediclaim Plus Policy?",
            "What is the waiting period for pre-existing diseases (PED) to be covered?"
        ]
    }
    
    results = {
        "endpoint_exists": False,
        "https_ready": False,
        "auth_required": False,
        "correct_format": False,
        "response_time_ok": False,
        "json_response": False,
        "all_questions_answered": False
    }
    
    # Test 1: Check if endpoint exists
    print("1️⃣ Testing endpoint existence...")
    try:
        response = requests.post(f"{base_url}/hackrx/run", headers=headers, json=test_request, timeout=120)
        results["endpoint_exists"] = True
        print("✅ Endpoint /hackrx/run exists")
    except Exception as e:
        print(f"❌ Endpoint test failed: {e}")
        return results
    
    # Test 2: Check HTTPS readiness (if URL is HTTPS)
    if base_url.startswith("https://"):
        results["https_ready"] = True
        print("✅ HTTPS enabled")
    else:
        print("⚠️ Testing on HTTP (HTTPS required for submission)")
    
    # Test 3: Test authentication
    print("2️⃣ Testing authentication...")
    try:
        # Test without auth
        no_auth_response = requests.post(f"{base_url}/hackrx/run", json=test_request, timeout=10)
        if no_auth_response.status_code == 401:
            results["auth_required"] = True
            print("✅ Authentication required (401 without token)")
        else:
            print("⚠️ Authentication not enforced")
    except:
        pass
    
    # Test 4: Test correct request/response format
    print("3️⃣ Testing request/response format...")
    try:
        start_time = time.time()
        response = requests.post(f"{base_url}/hackrx/run", headers=headers, json=test_request, timeout=30)
        end_time = time.time()
        
        response_time = end_time - start_time
        results["response_time_ok"] = response_time < 30
        
        if response.status_code == 200:
            results["correct_format"] = True
            print(f"✅ Correct response status (200)")
            print(f"✅ Response time: {response_time:.2f}s {'(OK)' if response_time < 30 else '(TOO SLOW)'}")
        else:
            print(f"❌ Wrong status code: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return results
    
    # Test 5: Test JSON response format
    print("4️⃣ Testing JSON response format...")
    try:
        response_data = response.json()
        if "answers" in response_data and isinstance(response_data["answers"], list):
            results["json_response"] = True
            print("✅ Correct JSON format with 'answers' array")
            
            # Test 6: Check if all questions are answered
            if len(response_data["answers"]) == len(test_request["questions"]):
                results["all_questions_answered"] = True
                print(f"✅ All {len(test_request['questions'])} questions answered")
                
                # Show sample answers
                for i, answer in enumerate(response_data["answers"][:2]):
                    print(f"   Q{i+1}: {test_request['questions'][i][:50]}...")
                    print(f"   A{i+1}: {answer[:100]}...")
                    print()
            else:
                print(f"❌ Expected {len(test_request['questions'])} answers, got {len(response_data['answers'])}")
        else:
            print("❌ Invalid JSON format - missing 'answers' array")
            print(f"Response: {response_data}")
            
    except Exception as e:
        print(f"❌ JSON parsing failed: {e}")
        print(f"Raw response: {response.text[:200]}...")
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 COMPLIANCE SUMMARY")
    print("=" * 50)
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    for test, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test.replace('_', ' ').title()}: {status}")
    
    print(f"\nOverall Score: {passed_tests}/{total_tests} ({passed_tests/total_tests*100:.1f}%)")
    
    if passed_tests == total_tests:
        print("🎉 ALL TESTS PASSED! Ready for submission!")
    else:
        print("⚠️ Some tests failed. Please fix before submission.")
    
    return results

def test_performance(base_url="http://127.0.0.1:8000", runs=3):
    """Test API performance"""
    print(f"\n🚀 Performance Testing ({runs} runs)...")
    
    api_key = "9fcf52ab0952ca875021a92ff7bd5557eedb4f49f016e0894610e1014498a402"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    test_request = {
        "documents": "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D",
        "questions": [
            "What is the grace period for premium payment?",
            "What is the waiting period for pre-existing diseases?"
        ]
    }
    
    times = []
    for i in range(runs):
        try:
            start_time = time.time()
            response = requests.post(f"{base_url}/hackrx/run", headers=headers, json=test_request, timeout=30)
            end_time = time.time()
            
            if response.status_code == 200:
                times.append(end_time - start_time)
                print(f"Run {i+1}: {times[-1]:.2f}s")
            else:
                print(f"Run {i+1}: Failed ({response.status_code})")
                
        except Exception as e:
            print(f"Run {i+1}: Error - {e}")
    
    if times:
        avg_time = sum(times) / len(times)
        print(f"\n📈 Performance Results:")
        print(f"Average: {avg_time:.2f}s")
        print(f"Min: {min(times):.2f}s")
        print(f"Max: {max(times):.2f}s")
        print(f"Success Rate: {len(times)}/{runs} ({len(times)/runs*100:.1f}%)")

if __name__ == "__main__":
    # Get URL from command line or use default
    url = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000"
    
    # Run compliance tests
    results = test_api_compliance(url)
    
    # Run performance tests if basic tests pass
    if results["endpoint_exists"] and results["correct_format"]:
        test_performance(url)
    
    print("\n🏁 Validation Complete!")