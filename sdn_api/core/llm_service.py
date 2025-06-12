import os
import json
import asyncio
from typing import List, Dict, Optional
from openai import OpenAI, AsyncOpenAI

from ..utils.logger import setup_logger

logger = setup_logger(__name__)


class LLMService:
    """Service for LLM-based operations including name generation and match assessment."""
    
    def __init__(self, api_key: Optional[str] = None):
        # Load environment variables
        from dotenv import load_dotenv
        load_dotenv()
        
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY environment variable.")
        
        self.client = OpenAI(api_key=self.api_key)
        self.async_client = AsyncOpenAI(api_key=self.api_key)
        self.model = "gpt-4-turbo-preview"  # Using GPT-4.1 equivalent
    
    def generate_name_variations(self, name: str, max_variations: int = 10) -> List[str]:
        """Generate name variations using LLM while preserving identity."""
        logger.info(f"Generating name variations for '{name}'")
        prompt = f"""Generate up to {max_variations} name variations for the person: "{name}"
        
        Include variations such as:
        - Different name orders (first last, last first)
        - Common nicknames and diminutives
        - Alternative transliterations
        - With/without middle names or initials
        - Common spelling variations
        
        Return ONLY a JSON array of name strings, nothing else.
        Example: ["John Smith", "Smith, John", "J. Smith", "Johnny Smith"]"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a name variation generator. Return only JSON arrays."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            result = response.choices[0].message.content.strip()
            if not result:
                logger.warning("Empty response from OpenAI API")
                return [name]
            
            # Remove markdown code block formatting if present
            if result.startswith('```json'):
                result = result[7:]  # Remove ```json
            if result.startswith('```'):
                result = result[3:]   # Remove ```
            if result.endswith('```'):
                result = result[:-3]  # Remove trailing ```
            result = result.strip()
            
            logger.debug(f"OpenAI response: {result}")
            variations = json.loads(result)
            
            # Always include the original name
            if name not in variations:
                variations.insert(0, name)
            
            return variations[:max_variations]
            
        except Exception as e:
            # Fallback to original name only
            logger.error(f"Error generating name variations: {e}")
            return [name]
    
    def assess_match(self, query_info: Dict, candidate: Dict) -> Dict[str, any]:
        """Use LLM to assess if a candidate is a true match for the query."""
        entry = candidate['entry']
        initial_score = candidate.get('score', 0)
        logger.info(f"Assessing match for '{entry.name}' (initial score: {initial_score:.3f})")
        
        prompt = f"""Assess if this is a true match for the search query.

Search Query:
- Name: {query_info['name']}
- Date of Birth: {query_info.get('dob', 'Not specified')}
- Nationality/Country: {query_info.get('nationality', 'Not specified')}

Candidate:
- Name: {entry.name}
- Type: {entry.type}
- Date of Birth: {entry.dob or 'Not specified'}
- Place of Birth: {entry.pob or 'Not specified'}
- Nationality: {entry.nationality or 'Not specified'}
- Program: {entry.program}
- Aliases: {', '.join(entry.aliases) if entry.aliases else 'None'}
- Remarks: {entry.remarks or 'None'}

Analyze the match considering:
1. Name similarity (including aliases)
2. DOB match (if provided)
3. Nationality/country match (if provided)
4. Overall context and likelihood

Return a JSON object with:
{{
    "is_match": true/false,
    "confidence": "HIGH"/"MEDIUM"/"LOW",
    "score": 0.0-1.0,
    "reasoning": "Brief explanation"
}}"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at identity matching and sanctions screening. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=300
            )
            
            result = response.choices[0].message.content.strip()
            
            # Remove markdown code block formatting if present
            if result.startswith('```json'):
                result = result[7:]  # Remove ```json
            if result.startswith('```'):
                result = result[3:]   # Remove ```
            if result.endswith('```'):
                result = result[:-3]  # Remove trailing ```
            result = result.strip()
            
            assessment = json.loads(result)
            
            result_data = {
                'is_match': assessment.get('is_match', False),
                'confidence': assessment.get('confidence', 'LOW'),
                'llm_score': assessment.get('score', 0.0),
                'reasoning': assessment.get('reasoning', '')
            }
            
            logger.info(f"LLM assessment result: match={result_data['is_match']}, confidence={result_data['confidence']}, score={result_data['llm_score']:.3f}")
            
            return result_data
            
        except Exception as e:
            logger.error(f"Error in LLM assessment: {e}")
            # Fallback to original score
            return {
                'is_match': candidate.get('score', 0) > 0.5,
                'confidence': 'LOW',
                'llm_score': candidate.get('score', 0),
                'reasoning': 'LLM assessment failed, using fuzzy match score'
            }
    
    async def assess_match_async(self, query_info: Dict, candidate: Dict) -> Dict[str, any]:
        """Async version of assess_match for parallel processing."""
        entry = candidate['entry']
        initial_score = candidate.get('score', 0)
        logger.info(f"Assessing match for '{entry.name}' (initial score: {initial_score:.3f})")
        
        prompt = f"""Assess if this is a true match for the search query.

Search Query:
- Name: {query_info['name']}
- Date of Birth: {query_info.get('dob', 'Not specified')}
- Nationality/Country: {query_info.get('nationality', 'Not specified')}

Candidate:
- Name: {entry.name}
- Type: {entry.type}
- Date of Birth: {entry.dob or 'Not specified'}
- Place of Birth: {entry.pob or 'Not specified'}
- Nationality: {entry.nationality or 'Not specified'}
- Program: {entry.program}
- Aliases: {', '.join(entry.aliases) if entry.aliases else 'None'}
- Remarks: {entry.remarks or 'None'}

Analyze the match considering:
1. Name similarity (including aliases)
2. DOB match (if provided)
3. Nationality/country match (if provided)
4. Overall context and likelihood

Return a JSON object with:
{{
    "is_match": true/false,
    "confidence": "HIGH"/"MEDIUM"/"LOW",
    "score": 0.0-1.0,
    "reasoning": "Brief explanation"
}}"""
        
        try:
            response = await self.async_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at identity matching and sanctions screening. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=300
            )
            
            result = response.choices[0].message.content.strip()
            
            # Remove markdown code block formatting if present
            if result.startswith('```json'):
                result = result[7:]  # Remove ```json
            if result.startswith('```'):
                result = result[3:]   # Remove ```
            if result.endswith('```'):
                result = result[:-3]  # Remove trailing ```
            result = result.strip()
            
            assessment = json.loads(result)
            
            result_data = {
                'is_match': assessment.get('is_match', False),
                'confidence': assessment.get('confidence', 'LOW'),
                'llm_score': assessment.get('score', 0.0),
                'reasoning': assessment.get('reasoning', '')
            }
            
            logger.info(f"LLM assessment result: match={result_data['is_match']}, confidence={result_data['confidence']}, score={result_data['llm_score']:.3f}")
            
            return result_data
            
        except Exception as e:
            logger.error(f"Error in LLM assessment: {e}")
            # Fallback to original score
            return {
                'is_match': candidate.get('score', 0) > 0.5,
                'confidence': 'LOW',
                'llm_score': candidate.get('score', 0),
                'reasoning': 'LLM assessment failed, using fuzzy match score'
            }
    
    async def assess_matches_parallel(self, query_info: Dict, candidates: List[Dict]) -> List[Dict]:
        """Assess multiple matches in parallel."""
        logger.info(f"Starting parallel assessment of {len(candidates)} matches")
        
        # Create tasks for parallel execution
        tasks = [
            self.assess_match_async(query_info, candidate)
            for candidate in candidates
        ]
        
        # Run all assessments in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results and handle any exceptions
        for i, (candidate, result) in enumerate(zip(candidates, results)):
            if isinstance(result, Exception):
                logger.error(f"Error assessing match for '{candidate['entry'].name}': {result}")
                # Fallback to original score
                candidate.update({
                    'llm_score': candidate.get('score', 0),
                    'confidence': 'LOW',
                    'match_reasons': candidate.get('match_reasons', []) + ['LLM assessment failed, using fuzzy match score']
                })
                # Ensure name_match_score is preserved
                if 'name_match_score' not in candidate:
                    candidate['name_match_score'] = candidate.get('score', 0)
            else:
                candidate.update({
                    'llm_score': result['llm_score'],
                    'confidence': result['confidence'],
                    'match_reasons': candidate.get('match_reasons', []) + [f"LLM assessment: {result['reasoning']}"]
                })
                # Ensure name_match_score is preserved
                if 'name_match_score' not in candidate:
                    candidate['name_match_score'] = candidate.get('score', 0)
        
        logger.info(f"Completed parallel assessment of {len(candidates)} matches")
        return candidates