import re
import asyncio
from typing import List, Dict, Optional
from difflib import SequenceMatcher

from ..models.sdn import ConfidenceLevel
from .llm_service import LLMService
from ..utils.logger import setup_logger

logger = setup_logger(__name__)


class MatchRanker:
    """Step 2: Rank filtered matches using additional context."""
    
    def __init__(self, use_llm: bool = True):
        self.use_llm = use_llm
        self.llm_service = LLMService() if use_llm else None
    
    def rank_matches(self, query_info: Dict[str, Optional[str]], filtered_matches: List[Dict]) -> List[Dict]:
        """
        Rank matches considering nationality, DOB, and other contextual factors.
        Uses parallel LLM assessment for speed.
        """
        if self.use_llm and self.llm_service and filtered_matches:
            try:
                # Use parallel LLM assessment
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    filtered_matches = loop.run_until_complete(
                        self.llm_service.assess_matches_parallel(query_info, filtered_matches)
                    )
                finally:
                    loop.close()
            except Exception as e:
                logger.warning(f"Parallel LLM assessment failed, falling back to rule-based: {e}")
                # Fall back to rule-based scoring for all matches
                self._apply_rule_based_scoring(query_info, filtered_matches)
        else:
            # Use rule-based scoring when LLM is disabled
            self._apply_rule_based_scoring(query_info, filtered_matches)
        
        # Re-sort by LLM score
        filtered_matches.sort(key=lambda x: x['llm_score'], reverse=True)
        return filtered_matches
    
    def _apply_rule_based_scoring(self, query_info: Dict[str, Optional[str]], filtered_matches: List[Dict]):
        """Apply rule-based scoring as fallback."""
        query_dob = query_info.get('dob')
        query_nationality = query_info.get('nationality')
        query_name = query_info.get('name', '').lower()
        
        for match in filtered_matches:
            entry = match['entry']
            enhanced_score = match['score']
            additional_reasons = []
            
            # DOB matching (strong indicator)
            if query_dob and entry.dob:
                if self._compare_dates(query_dob, entry.dob):
                    enhanced_score += 0.3
                    additional_reasons.append("DOB match")
            
            # Nationality matching
            if query_nationality and entry.nationality:
                nat_score = self._fuzzy_match_score(query_nationality, entry.nationality)
                if nat_score > 0.8:
                    enhanced_score += 0.2
                    additional_reasons.append("Nationality match")
            
            # Country/Program matching (for organizations)
            if query_nationality and entry.program:
                country_score = self._fuzzy_match_score(query_nationality, entry.program)
                if country_score > 0.8:
                    enhanced_score += 0.15
                    additional_reasons.append("Country/Program match")
            
            # Type consistency (individual vs entity)
            if 'individual' in entry.type.lower():
                if not any(org_word in query_name 
                          for org_word in ['company', 'corp', 'inc', 'ltd', 'bank', 'association']):
                    enhanced_score += 0.05
                    additional_reasons.append("Individual type match")
            else:
                if any(org_word in query_name 
                      for org_word in ['company', 'corp', 'inc', 'ltd', 'bank', 'association']):
                    enhanced_score += 0.05
                    additional_reasons.append("Entity type match")
            
            # Context relevance from remarks
            if entry.remarks:
                remarks_lower = entry.remarks.lower()
                query_words = query_name.split()
                context_matches = sum(1 for word in query_words if word in remarks_lower)
                if context_matches > 0:
                    enhanced_score += context_matches * 0.02
                    additional_reasons.append(f"Context relevance ({context_matches} terms)")
            
            match['match_reasons'].extend(additional_reasons)
            match['llm_score'] = min(enhanced_score, 1.0)  # Cap at 1.0
            match['confidence'] = self._calculate_confidence(match['llm_score'], additional_reasons)
            # Ensure name_match_score is preserved
            if 'name_match_score' not in match:
                match['name_match_score'] = match.get('score', 0)
    
    @staticmethod
    def _compare_dates(query_date: str, entry_date: str) -> bool:
        """Compare dates allowing for different formats."""
        # Simple comparison - in production you'd want more robust date parsing
        query_clean = re.sub(r'[^0-9]', '', query_date)
        entry_clean = re.sub(r'[^0-9]', '', entry_date)
        
        # Check if dates contain similar numbers
        if len(query_clean) >= 6 and len(entry_clean) >= 6:
            return query_clean in entry_clean or entry_clean in query_clean
        
        return False
    
    @staticmethod
    def _fuzzy_match_score(str1: str, str2: str) -> float:
        """Calculate fuzzy match score between two strings."""
        return SequenceMatcher(None, str1.lower(), str2.lower()).ratio()
    
    @staticmethod
    def _calculate_confidence(score: float, additional_reasons: List[str]) -> ConfidenceLevel:
        """Calculate confidence level based on score and additional factors."""
        if score > 0.8 and len(additional_reasons) >= 2:
            return ConfidenceLevel.HIGH
        elif score > 0.6 and len(additional_reasons) >= 1:
            return ConfidenceLevel.MEDIUM_HIGH
        elif score > 0.5:
            return ConfidenceLevel.MEDIUM
        elif score > 0.3:
            return ConfidenceLevel.LOW_MEDIUM
        else:
            return ConfidenceLevel.LOW