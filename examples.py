#!/usr/bin/env python3
"""
Example usage of the SDN API
"""
import httpx
import json


BASE_URL = "http://localhost:8000"


def search_example():
    """Example search requests."""
    
    # Test queries
    queries = [
        {
            "query": "john mccain",
            "max_results": 5
        },
        {
            "query": "john mcain, 21/06/1955, american",
            "max_results": 5
        },
        {
            "query": "abbas, palestine",
            "max_results": 5
        },
        {
            "query": "banco cuba",
            "max_results": 5
        },
        {
            "query": "al zawahiri, 1951, egypt",
            "max_results": 5
        }
    ]
    
    with httpx.Client() as client:
        # Check health
        health = client.get(f"{BASE_URL}/health")
        print(f"Health check: {health.json()}")
        print()
        
        # Get stats
        stats = client.get(f"{BASE_URL}/stats")
        print(f"SDN Statistics: {stats.json()}")
        print()
        
        # Perform searches
        for query_data in queries:
            print(f"\n{'='*60}")
            print(f"Searching for: {query_data['query']}")
            print('='*60)
            
            response = client.post(
                f"{BASE_URL}/search",
                json=query_data
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"Found {data['total_matches']} matches")
                
                for i, result in enumerate(data['results'], 1):
                    print(f"\n{i}. {result['name']} ({result['type']})")
                    print(f"   Name Match Score: {result.get('name_match_score', 'N/A'):.3f}")
                    print(f"   LLM Score: {result.get('llm_score', result.get('score', 'N/A')):.3f}")
                    print(f"   Confidence: {result['confidence']}")
                    print(f"   Reasons: {', '.join(result['match_reasons'])}")
                    
                    details = result['details']
                    if details.get('nationality'):
                        print(f"   Nationality: {details['nationality']}")
                    if details.get('dob'):
                        print(f"   DOB: {details['dob']}")
                    if details.get('aliases'):
                        print(f"   Aliases: {', '.join(details['aliases'][:3])}")
            else:
                print(f"Error: {response.status_code} - {response.text}")


if __name__ == "__main__":
    print("SDN API Example Usage")
    print("Make sure the API is running: python run_api.py")
    print()
    
    try:
        search_example()
    except httpx.ConnectError:
        print("Error: Could not connect to API. Is it running?")
    except Exception as e:
        print(f"Error: {e}")