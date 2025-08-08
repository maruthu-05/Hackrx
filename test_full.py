"""
Full API test with proper timeout for the hackrx system
"""

import requests
import json
import time

def test_full_system():
    """Test the full system with all 10 questions"""
    
    base_url = "http://127.0.0.1:8000"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": "Bearer 9fcf52ab0952ca875021a92ff7bd5557eedb4f49f016e0894610e1014498a402"
    }
    
    # Full test request with all 10 questions
    test_request = {
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
    
    print("🧪 Testing Full System with All 10 Questions")
    print("=" * 60)
    print(f"📄 Document: Insurance Policy PDF")
    print(f"❓ Questions: {len(test_request['questions'])}")
    print(f"⏱️ Timeout: 2 minutes")
    print()
    
    try:
        print("🚀 Sending request...")
        start_time = time.time()
        
        response = requests.post(
            f"{base_url}/hackrx/run",
            headers=headers,
            json=test_request,
            timeout=120  # 2 minute timeout
        )
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        print(f"⏱️ Processing time: {processing_time:.1f} seconds")
        print(f"📊 Status code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            answers = result.get('answers', [])
            
            print(f"✅ SUCCESS! Received {len(answers)} answers")
            print()
            
            # Show first few answers
            for i, (question, answer) in enumerate(zip(test_request['questions'][:3], answers[:3])):
                print(f"Q{i+1}: {question}")
                print(f"A{i+1}: {answer[:150]}...")
                print()
            
            if len(answers) == len(test_request['questions']):
                print("🎉 ALL QUESTIONS ANSWERED SUCCESSFULLY!")
                print("✅ System is ready for hackrx submission!")
            else:
                print(f"⚠️ Expected {len(test_request['questions'])} answers, got {len(answers)}")
                
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text[:300]}...")
            
    except requests.exceptions.Timeout:
        print("⏰ Request timed out after 2 minutes")
        print("💡 The system might be working but needs optimization")
        
    except Exception as e:
        print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    test_full_system()