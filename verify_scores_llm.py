#!/usr/bin/env python3
"""
Direct test of the search service with LLM to verify both scores are preserved
"""
import sys
import os

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sdn_api.core.search_service import SDNSearchService

def test_scores_with_llm():
    """Test that both name_match_score and llm_score are preserved with LLM enabled."""
    
    try:
        # Check if OpenAI key is available
        openai_key = os.getenv("OPENAI_API_KEY")
        if not openai_key:
            print("OPENAI_API_KEY not found, testing with LLM disabled...")
            use_llm = False
        else:
            print("OPENAI_API_KEY found, testing with LLM enabled...")
            use_llm = True
        
        # Initialize the search service
        print("Initializing search service...")
        search_service = SDNSearchService("sdn.csv", use_llm=use_llm)
        
        print(f"Loaded {len(search_service.entries)} entries")
        
        # Test search with a name that should have some matches
        query = "abbas"
        print(f"\nSearching for: '{query}'")
        
        results = search_service.search(query, max_results=2)
        
        if results:
            print(f"Found {len(results)} results:")
            for i, result in enumerate(results, 1):
                print(f"\n{i}. {result.name} ({result.type})")
                print(f"   Name Match Score: {result.name_match_score:.3f}")
                print(f"   LLM Score: {result.llm_score:.3f}")
                print(f"   Legacy Score: {result.score:.3f}")
                
                # Verify consistency
                if result.score == result.llm_score:
                    print("   ✓ Score consistency verified")
                else:
                    print(f"   ✗ Score mismatch: {result.score} != {result.llm_score}")
                
                print(f"   Confidence: {result.confidence}")
                print(f"   Reasons: {', '.join(result.match_reasons[:2])}...")  # Show first 2 reasons
                
                # Verify both scores exist and are different when LLM is used
                if hasattr(result, 'name_match_score') and result.name_match_score > 0:
                    print("   ✓ Name match score present and valid")
                    
                    if use_llm and result.name_match_score != result.llm_score:
                        print("   ✓ Scores are different (LLM processing applied)")
                    elif not use_llm and result.name_match_score == result.llm_score:
                        print("   ✓ Scores are same (no LLM processing)")
                else:
                    print("   ✗ Name match score missing or invalid")
        else:
            print("No results found")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("Verifying dual score implementation with LLM...")
    test_scores_with_llm()