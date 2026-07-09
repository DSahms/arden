"""Phase 1 End-to-End Test for PersonaLock

Tests:
1. Health check - verify all systems operational
2. Chat with personal info
3. Follow-up to verify memory works
"""
import time
import requests
import sys

BASE_URL = "http://localhost:8000"


def print_header(text: str):
    """Print a formatted header."""
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")


def print_result(name: str, passed: bool, details: str = ""):
    """Print test result."""
    status = "[PASS]" if passed else "[FAIL]"
    print(f"{status} - {name}")
    if details:
        print(f"       {details}")


def test_health():
    """Test 1: Health check endpoint."""
    print_header("Test 1: Health Check")
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=30)
        data = response.json()
        
        print(f"Status: {data.get('status')}")
        print(f"Neo4j: {data.get('neo4j')}")
        print(f"ChromaDB: {data.get('chromadb')}")
        print(f"LLM: {data.get('llm')}")
        
        if data.get('details'):
            print(f"Details: {data.get('details')}")
        
        # Check if LLM is operational (minimum requirement)
        llm_ok = data.get('llm') == 'operational'
        
        # Memory systems can be degraded but should be noted
        neo4j_ok = data.get('neo4j') == 'connected'
        chroma_ok = data.get('chromadb') == 'connected'
        
        print_result("Health endpoint responds", True)
        print_result("LLM operational", llm_ok)
        print_result("Neo4j connected", neo4j_ok, "" if neo4j_ok else "(memory persistence unavailable)")
        print_result("ChromaDB connected", chroma_ok, "" if chroma_ok else "(semantic search unavailable)")
        
        return llm_ok, neo4j_ok and chroma_ok
        
    except requests.exceptions.ConnectionError:
        print_result("Health endpoint responds", False, "Connection refused - is the server running?")
        return False, False
    except Exception as e:
        print_result("Health endpoint responds", False, str(e))
        return False, False


def test_persona():
    """Test: Current persona endpoint."""
    print_header("Test: Persona Check")
    
    try:
        response = requests.get(f"{BASE_URL}/persona/current", timeout=10)
        data = response.json()
        
        print(f"Name: {data.get('name')}")
        print(f"Traits: {data.get('traits')}")
        print(f"Description: {data.get('description')}")
        
        print_result("Persona endpoint works", True)
        print_result("Has persona name", bool(data.get('name')))
        
        return True
    except Exception as e:
        print_result("Persona endpoint works", False, str(e))
        return False


def test_chat_memory():
    """Test 2 & 3: Chat with memory verification."""
    print_header("Test 2: Initial Chat")
    
    user_id = f"test_user_{int(time.time())}"
    
    # First message - introduce personal info
    try:
        first_message = "Hi, my name is Jordan and I love hiking"
        print(f"User: {first_message}")
        print(f"User ID: {user_id}")
        
        response = requests.post(
            f"{BASE_URL}/chat",
            json={"message": first_message, "user_id": user_id},
            timeout=60
        )
        data = response.json()
        
        first_response = data.get('response', '')
        processing_time = data.get('processing_time_ms', 0)
        
        print(f"\nAda: {first_response}")
        print(f"(Processing time: {processing_time}ms)")
        
        print_result("First chat successful", bool(first_response))
        
    except Exception as e:
        print_result("First chat successful", False, str(e))
        return False
    
    # Wait for memory to settle
    print_header("Test 3: Memory Verification")
    print("Waiting 2 seconds...")
    time.sleep(2)
    
    # Second message - ask about previous info
    try:
        second_message = "What's my name and what do I enjoy?"
        print(f"User: {second_message}")
        
        response = requests.post(
            f"{BASE_URL}/chat",
            json={"message": second_message, "user_id": user_id},
            timeout=60
        )
        data = response.json()
        
        second_response = data.get('response', '').lower()
        processing_time = data.get('processing_time_ms', 0)
        
        print(f"\nAda: {data.get('response', '')}")
        print(f"(Processing time: {processing_time}ms)")
        
        # Check if response contains the remembered info
        has_jordan = 'jordan' in second_response
        has_hiking = 'hiking' in second_response or 'hike' in second_response
        
        print()
        print_result("Response mentions 'Jordan'", has_jordan)
        print_result("Response mentions 'hiking'", has_hiking)
        print_result("MEMORY WORKING", has_jordan and has_hiking, 
                    "AI remembers information from previous message!" if has_jordan and has_hiking else "Memory retrieval may not be working")
        
        return has_jordan and has_hiking
        
    except Exception as e:
        print_result("Second chat successful", False, str(e))
        return False


def test_recent_memory():
    """Test: Recent memory endpoint."""
    print_header("Test: Recent Memory Retrieval")
    
    try:
        response = requests.get(f"{BASE_URL}/memory/recent?limit=5", timeout=10)
        
        if response.status_code == 503:
            print_result("Recent memory endpoint", False, "Neo4j not available")
            return False
            
        data = response.json()
        
        print(f"Retrieved {len(data)} recent conversations")
        
        if data:
            print("\nMost recent conversation:")
            print(f"  User: {data[0].get('user_message', '')[:50]}...")
            print(f"  Ada: {data[0].get('assistant_response', '')[:50]}...")
        
        print_result("Recent memory endpoint works", True)
        return True
        
    except Exception as e:
        print_result("Recent memory endpoint works", False, str(e))
        return False


def main():
    """Run all Phase 1 tests."""
    print("\n" + "="*60)
    print("       PERSONALOCK PHASE 1 - END TO END TEST")
    print("="*60)
    
    # Run tests
    llm_ok, memory_ok = test_health()
    
    if not llm_ok:
        print("\n[CRITICAL] LLM not operational. Cannot continue tests.")
        print("   Make sure LM Studio is running with a model loaded.")
        sys.exit(1)
    
    test_persona()
    memory_test_passed = test_chat_memory()
    
    if memory_ok:
        test_recent_memory()
    
    # Final summary
    print_header("PHASE 1 TEST SUMMARY")
    
    if memory_test_passed:
        print("[SUCCESS] PHASE 1 COMPLETE!")
        print("")
        print("   - API server running")
        print("   - Health check passing")
        print("   - Chat endpoint working")
        print("   - MEMORY IS WORKING - AI remembers previous conversations!")
        print("")
        print("Next: Verify data in Neo4j browser at http://localhost:7474")
        print("      Run: MATCH (n) RETURN n LIMIT 25")
        sys.exit(0)
    else:
        print("[WARNING] PHASE 1 PARTIALLY COMPLETE")
        print("")
        print("   - API server running")
        print("   - Chat endpoint working")
        print("   - Memory retrieval may need investigation")
        print("")
        if not memory_ok:
            print("   Note: Neo4j and/or ChromaDB may not be connected.")
            print("   Memory features require these services to be running.")
        sys.exit(1)


if __name__ == "__main__":
    main()
