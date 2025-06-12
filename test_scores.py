#!/usr/bin/env python3
"""
Test script to verify both name_match_score and llm_score are returned in API response
"""
import httpx
import json
from time import sleep

BASE_URL = "http://localhost:8000"

def test_dual_scores():
    """Test that both name_match_score and llm_score are returned."""
    
    # Test query
    query_data = {
        "query": "john mccain",
        "max_results": 3
    }
    
    try:
        with httpx.Client(timeout=30.0) as client:
            # Check health
            print("Checking API health...")
            health = client.get(f"{BASE_URL}/health")
            print(f"Health check: {health.json()}")
            
            if not health.json().get("sdn_loaded", False):
                print("ERROR: SDN data not loaded!")
                return
            
            print(f"\nSearching for: {query_data['query']}")
            
            response = client.post(
                f"{BASE_URL}/search",
                json=query_data
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"Found {data['total_matches']} matches")
                
                for i, result in enumerate(data['results'], 1):
                    print(f"\n{i}. {result['name']} ({result['type']})")
                    
                    # Check if both scores are present
                    if 'name_match_score' in result and 'llm_score' in result:
                        print(f"   Name Match Score: {result['name_match_score']:.3f}")
                        print(f"   LLM Score: {result['llm_score']:.3f}")
                        print(f"   Legacy Score: {result.get('score', 'N/A'):.3f}")
                        print(f"   Confidence: {result['confidence']}")
                        print(f"   Reasons: {', '.join(result['match_reasons'])}")
                        
                        # Verify the legacy score matches LLM score
                        assert result['score'] == result['llm_score'], f"Legacy score mismatch: {result['score']} != {result['llm_score']}"
                        print("   ✓ Score consistency verified")
                    else:
                        print(f"   ERROR: Missing scores! Available keys: {list(result.keys())}")
                        
                print("\n✓ Test completed successfully!")
                        
            else:
                print(f"Error: {response.status_code} - {response.text}")
                
    except httpx.ConnectError:
        print("Error: Could not connect to API. Is it running?")
        print("Start the API with: python run_api.py")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("Testing dual score output...")
    test_dual_scores()